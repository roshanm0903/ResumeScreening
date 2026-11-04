"""Isolated state-machine tests. Model calls are mocked here; live scoring is verified separately."""
import os,tempfile,unittest,importlib.util,json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import scoring
import intent

class Workflow(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();os.environ['HIRING_DB']=str(Path(self.tmp.name)/'test.sqlite3')
  spec=importlib.util.spec_from_file_location('demo',Path(__file__).with_name('server.py'));self.s=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.s)
  def fake(resume,policy,request_data=None):
   relevant='Warehouse shift supervisor' in resume
   return [dict(key=c['key'],rating=2 if relevant else 0,quotes=[resume] if relevant else [],rationale='Controlled model response for workflow tests.') for c in policy['criteria']],dict(provider='Test double',model='workflow-only',prompt_version='test')
  self.model=patch('scoring.evaluate',side_effect=fake);self.model_mock=self.model.start()
  def fake_intent(context,message,request_data=None):
   prefs=self.s.parse_preferences(message)
   return dict(interpretation=dict(intent='reschedule' if prefs else 'unknown',answer='unknown',date=prefs.get('date',''),period=prefs.get('period','any'),time='',slot_index=0,ambiguous=False,clarification=''),model='test-intent',prompt_version='test')
  self.intent_patch=patch('intent.interpret',side_effect=fake_intent);self.intent_mock=self.intent_patch.start();self.s.init()
 def tearDown(self):self.intent_patch.stop();self.model.stop();self.tmp.cleanup();os.environ.pop('HIRING_DB',None)
 def add(self,name='Test Person',age=0,**changes):
  d=dict(name=name,role_id=1,resume=name+'\nContact test@example.com\n'+self.s.SAMPLE_RESUME,shift='yes',site='yes',start='yes',consent=True);d.update(changes);return self.s.create_candidate(d,age=age)
 def test_redaction_storage_and_policy_snapshot(self):
  cid=self.add();d=self.s.detail(cid);self.assertNotIn('Test Person',d['candidate']['resume_text']);self.assertNotIn('test@example.com',d['candidate']['resume_text']);self.assertEqual(100,d['candidate']['score']);self.assertEqual(len(self.s.WAREHOUSE['criteria']),len(d['scores']))
  with self.s.conn() as c:c.execute("UPDATE roles SET policy=json_set(policy,'$.version',2,'$.threshold',95) WHERE id=1")
  self.assertEqual(1,self.s.detail(cid)['candidate']['policy_version']);self.assertEqual(2,self.s.detail(self.add('Another Person'))['candidate']['policy_version'])
 def test_booking_conflict_and_cancel(self):
  a,b=self.add(),self.add('Another Person');self.s.batch(force=True)
  self.s.reply(a,'1');self.s.reply(b,'1')
  with self.s.conn() as c:self.assertEqual(1,c.execute('SELECT COUNT(*) FROM bookings').fetchone()[0])
  self.assertEqual('Booked',self.s.detail(a)['candidate']['status']);self.assertEqual('Invited',self.s.detail(b)['candidate']['status']);self.assertTrue(any('no longer available' in m['body'] for m in self.s.detail(b)['messages']))
  self.s.reply(a,'CANCEL')
  with self.s.conn() as c:self.assertEqual(0,c.execute('SELECT COUNT(*) FROM bookings').fetchone()[0])
 def test_batch_age_and_fixed_deadline(self):
  fresh,old=self.add(),self.add('Older Person',age=13)
  due=self.s.detail(old)['candidate']['due_at'];self.s.batch()
  self.assertEqual('Awaiting batch',self.s.detail(fresh)['candidate']['status']);self.assertEqual('Invited',self.s.detail(old)['candidate']['status']);self.assertEqual(due,self.s.detail(old)['candidate']['due_at'])
 def test_missing_details_recover_through_chat(self):
  cid=self.add(shift='unknown',start='unknown');due=self.s.detail(cid)['candidate']['due_at']
  self.assertEqual('shift',self.s.detail(cid)['candidate']['pending_field']);self.assertIsNone(self.s.detail(cid)['candidate']['score'])
  self.s.reply(cid,'maybe');self.assertEqual('shift',self.s.detail(cid)['candidate']['pending_field'])
  self.s.reply(cid,'YES');self.assertEqual('start',self.s.detail(cid)['candidate']['pending_field'])
  self.s.reply(cid,'YES');self.assertEqual('Awaiting batch',self.s.detail(cid)['candidate']['status'])
  self.s.batch(force=True,candidate_id=cid);self.s.reply(cid,'1');self.assertEqual('Booked',self.s.detail(cid)['candidate']['status']);self.assertEqual(due,self.s.detail(cid)['candidate']['due_at'])
  self.assertEqual(2,sum(e['kind']=='candidate.detail_collected' for e in self.s.detail(cid)['events']))
 def test_negative_answer_rejects_without_model_call(self):
  cid=self.add(shift='unknown');calls=self.model_mock.call_count
  self.s.reply(cid,'NO');d=self.s.detail(cid)
  self.assertEqual('Rejected',d['candidate']['status']);self.assertEqual(calls,self.model_mock.call_count)
  self.assertIn('06:00',d['candidate']['decision_reason']);self.s.batch(force=True,candidate_id=cid)
  self.assertFalse(any(e['kind']=='slots.offered' for e in self.s.detail(cid)['events']))
 def test_missing_resume_then_upload(self):
  cid=self.add(resume='');self.assertEqual('Awaiting résumé',self.s.detail(cid)['candidate']['status']);self.assertEqual([],self.s.detail(cid)['scores'])
  with self.assertRaises(ValueError):self.s.add_resume(cid,dict(resume=''))
  self.s.add_resume(cid,dict(resume=self.s.SAMPLE_RESUME));self.assertEqual('Awaiting batch',self.s.detail(cid)['candidate']['status']);self.assertEqual(len(self.s.WAREHOUSE['criteria']),len(self.s.detail(cid)['scores']))
 def test_missing_resume_through_chat(self):
  cid=self.add(resume='');self.s.reply(cid,'RESUME: '+self.s.SAMPLE_RESUME);self.assertEqual('Awaiting batch',self.s.detail(cid)['candidate']['status'])
 def test_below_threshold_rejects_and_review_request_is_saved(self):
  cid=self.add(resume='Helped visitors with telephone enquiries and maintained appointment records.')
  self.assertEqual('Rejected',self.s.detail(cid)['candidate']['status']);self.assertIn('below the required 70',self.s.detail(cid)['candidate']['decision_reason'])
  self.s.reply(cid,'REVIEW');self.assertEqual('Review requested',self.s.detail(cid)['candidate']['status'])
 def test_unrecognized_answers_escalate_without_rejection(self):
  cid=self.add(shift='unknown')
  for _ in range(3):self.s.reply(cid,'maybe')
  self.assertEqual('Human support',self.s.detail(cid)['candidate']['status']);self.assertIsNone(self.s.detail(cid)['candidate']['score'])
 def test_provider_failure_does_not_reject(self):
  self.model_mock.side_effect=scoring.ScoringUnavailable('Temporary provider problem')
  cid=self.add();detail=self.s.detail(cid);due=detail['candidate']['due_at'];self.assertEqual('Scoring pending',detail['candidate']['status']);self.assertEqual([],detail['scores'])
  self.assertEqual('RETRY',json.loads(detail['messages'][-1]['component'])['buttons'][0]['id'])
  self.model_mock.side_effect=lambda resume,policy,request_data=None:([dict(key=cr['key'],rating=2,quotes=[resume],rationale='Recovered model response.') for cr in policy['criteria']],dict(provider='Test',model='recovered',prompt_version='test'))
  self.s.reply(cid,'RETRY');self.assertEqual('Awaiting batch',self.s.detail(cid)['candidate']['status']);self.assertEqual(due,self.s.detail(cid)['candidate']['due_at'])
 def test_pass_first_outreach_waits_for_slots(self):
  cid=self.add();d=self.s.detail(cid)
  self.assertEqual([],d['messages']);self.assertIsNone(d['candidate']['first_outreach'])
  self.assertNotIn('screening',d['candidate_notice'])
  self.s.batch(force=True,candidate_id=cid);d=self.s.detail(cid)
  self.assertEqual(1,len(d['messages']));self.assertEqual('list',json.loads(d['messages'][0]['component'])['type'])
  self.assertIsNotNone(d['candidate']['first_outreach']);self.assertNotIn('screening requirements',d['messages'][0]['body'])
 def test_no_capacity_does_not_count_as_outreach(self):
  cid=self.add()
  with self.s.conn() as c:c.execute('UPDATE availability SET available=0')
  self.s.batch(force=True,candidate_id=cid);d=self.s.detail(cid)
  self.assertEqual('Capacity wait',d['candidate']['status']);self.assertIsNone(d['candidate']['first_outreach']);self.assertEqual([],d['messages'])
 def test_rejection_uses_generic_candidate_message(self):
  cid=self.add(resume='Helped visitors with telephone enquiries and maintained appointment records.');d=self.s.detail(cid)
  self.assertEqual(self.s.REJECTION_MESSAGE,d['messages'][0]['body']);self.assertEqual(self.s.REJECTION_MESSAGE,d['candidate_notice'])
  self.assertIn('below the required',d['candidate']['decision_reason']);self.assertTrue(d['scores'])
  self.s.reply(cid,'WHY');self.assertNotIn('/100',self.s.detail(cid)['messages'][-1]['body'])
  self.s.reply(cid,'REVIEW');self.assertNotIn('scored',self.s.detail(cid)['candidate_notice'])
 def test_legacy_candidate_projection_preserves_audit(self):
  cid=self.add()
  with self.s.conn() as c:
   self.s.msg(c,cid,'out','Your application meets the screening requirements. Wait for a batch.')
   self.s.msg(c,cid,'out','Your application scored 20/100 against the published role criteria.')
  d=self.s.detail(cid);self.assertEqual(2,len(d['messages']));self.assertEqual(1,len(d['candidate_messages']))
  self.assertEqual(self.s.REJECTION_MESSAGE,d['candidate_messages'][0]['body'])
 def test_invalid_model_evidence_is_rejected(self):
  with self.assertRaises(scoring.ScoringUnavailable):scoring.validate_response({'ratings':[{'key':'picking','rating':2,'quotes':['Invented work experience'],'rationale':'Unsupported'}]},self.s.SAMPLE_RESUME,self.s.WAREHOUSE['criteria'])
 def test_no_consent_no_chat(self):
  cid=self.add(consent=False);self.assertEqual('Channel needed',self.s.detail(cid)['candidate']['status']);self.assertEqual([],self.s.detail(cid)['messages'])
  with self.assertRaises(ValueError):self.s.reply(cid,'YES')
 def latest_slots(self,cid):
  return next(json.loads(e['payload'])['slots'] for e in self.s.detail(cid)['events'] if e['kind']=='slots.offered')
 def test_alternatives_requery_current_calendar_and_exclude_previous_offers(self):
  cid=self.add();self.s.batch(force=True,candidate_id=cid);first=self.latest_slots(cid);calls=self.model_mock.call_count
  # Introduce an earlier available time after the original offer, proving a fresh read.
  start=(self.s.datetime.now(self.s.timezone.utc)+self.s.timedelta(hours=1)).replace(microsecond=0)
  end=start+self.s.timedelta(minutes=30)
  with self.s.conn() as c:
   for panel in ['Site supervisor','Operations lead']:c.execute('INSERT INTO availability(role_id,interviewer,start,end,available) VALUES(1,?,?,?,1)',(panel,start.isoformat(),end.isoformat()))
  self.s.reply(cid,'NONE','Find other times');second=self.latest_slots(cid)
  self.assertIn(start.isoformat(),[x['start'] for x in second]);self.assertFalse({x['start'] for x in first}&{x['start'] for x in second})
  self.assertEqual(calls,self.model_mock.call_count)
  run=self.s.trace.get_runs(cid)[0];steps={x['node']:x for x in run['steps']}
  self.assertEqual('calendar.find_alternatives',steps['conversation.route']['outputs']['route'])
  self.assertEqual(sorted(x['start'] for x in first),steps['mcp.calendar.get_availability']['inputs']['excluded_previous_slots'])
  self.assertEqual('completed',run['status'])
  with self.s.conn() as c:self.assertIsNotNone(c.execute('SELECT id FROM workflow_runs WHERE id=?',(run['id'],)).fetchone())
  self.assertEqual('list',json.loads(self.s.detail(cid)['messages'][-1]['component'])['type'])
  self.assertEqual('Find other times',self.s.detail(cid)['messages'][-2]['body'])
 def test_preferred_day_period_filters_then_books(self):
  cid=self.add();self.s.batch(force=True,candidate_id=cid)
  # Day seven lies past the first twelve global slots; selection still rechecks correctly.
  target=self.s.datetime.now(self.s.IST).date()+self.s.timedelta(days=7)
  # Explicit local-date fixture avoids UTC/IST midnight changing the seeded final day.
  start=self.s.datetime.fromisoformat(target.isoformat()+'T13:00:00+05:30').astimezone(self.s.timezone.utc)
  with self.s.conn() as c:
   for member in ['Site supervisor','Operations lead']:
    c.execute('INSERT INTO availability(role_id,interviewer,start,end,available) VALUES(?,?,?,?,1)',(1,member,start.isoformat(),(start+self.s.timedelta(minutes=30)).isoformat()))
  with patch.object(self.s,'parse_preferences',return_value={'date':target.isoformat(),'period':'afternoon','hours':[12,18]}):self.s.reply(cid,'next week afternoon')
  slots=self.latest_slots(cid);self.assertTrue(slots)
  for slot in slots:
   local=self.s.datetime.fromisoformat(slot['start']).astimezone(self.s.IST)
   self.assertEqual(target,local.date());self.assertTrue(12<=local.hour<18)
  self.s.reply(cid,'1');self.assertEqual('Booked',self.s.detail(cid)['candidate']['status'])
  self.assertEqual('confirmation',json.loads(self.s.detail(cid)['messages'][-1]['component'])['type'])
 def test_only_required_panel_intersection_counts(self):
  with self.s.conn() as c:
   c.execute("UPDATE availability SET interviewer='Unrelated interviewer' WHERE interviewer='Operations lead'")
   self.assertEqual([],self.s.available(c,1))
 def test_unavailable_preference_stays_active_and_does_not_reject(self):
  cid=self.add();self.s.batch(force=True,candidate_id=cid);self.s.reply(cid,'evening')
  self.assertEqual('Capacity wait',self.s.detail(cid)['candidate']['status'])
  self.assertIn('No new panel times',self.s.detail(cid)['messages'][-1]['body'])
 def test_screening_trace_separates_model_from_policy(self):
  cid=self.add();steps=self.s.trace.get_runs(cid)[0]['steps'];by_node={s['node']:s for s in steps}
  self.assertEqual('deterministic',by_node['screening.build_prompt']['kind'])
  self.assertEqual(by_node['screening.build_prompt']['outputs'],by_node['screening.llm_assess']['inputs']['request_data'])
  self.assertLess(by_node['screening.build_prompt']['index'],by_node['screening.llm_assess']['index'])
  self.assertEqual('llm',by_node['screening.llm_assess']['kind'])
  self.assertNotIn('Test Person',by_node['screening.llm_assess']['inputs']['redacted_resume'])
  self.assertEqual(100,by_node['screening.aggregate']['outputs']['weighted_total'])
  cid=self.add(shift='no');self.assertNotIn('screening.llm_assess',[s['node'] for s in self.s.trace.get_runs(cid)[0]['steps']])
 def interpretation(self,**changes):
  data=dict(intent='reschedule',answer='unknown',date='',period='any',time='',slot_index=0,ambiguous=False,clarification='');data.update(changes)
  return dict(interpretation=data,model='test-intent',prompt_version='chat-intent-v1')
 def booking(self,cid):
  with self.s.conn() as c:
   row=c.execute('SELECT * FROM bookings WHERE candidate_id=?',(cid,)).fetchone();return dict(row) if row else None
 def booked(self):
  cid=self.add();self.s.batch(force=True,candidate_id=cid);self.s.reply(cid,'1');return cid
 def test_structured_actions_skip_intent_model(self):
  cid=self.booked();self.s.reply(cid,'RESCHEDULE');self.s.reply(cid,'1');self.assertEqual(0,self.intent_mock.call_count)
 def test_free_text_reschedule_keeps_then_replaces_booking(self):
  cid=self.booked();old=self.booking(cid);self.intent_mock.side_effect=None;self.intent_mock.return_value=self.interpretation(period='afternoon')
  self.s.reply(cid,'Could we move this to an afternoon instead?');self.assertEqual(old,self.booking(cid));self.assertEqual(1,self.s.detail(cid)['candidate']['rescheduling'])
  run=self.s.trace.get_runs(cid)[0];self.assertIn('conversation.llm_intent',[s['node'] for s in run['steps']]);self.assertTrue(next(s for s in run['steps'] if s['node']=='conversation.llm_intent')['inputs']['request_data'])
  self.s.reply(cid,'1');self.assertNotEqual(old['start'],self.booking(cid)['start']);self.assertEqual(0,self.s.detail(cid)['candidate']['rescheduling']);self.assertEqual(1,self.intent_mock.call_count)
 def test_no_matching_reschedule_retains_booking(self):
  cid=self.booked();old=self.booking(cid);self.intent_mock.side_effect=None;self.intent_mock.return_value=self.interpretation(period='evening')
  self.s.reply(cid,'I need an evening appointment');self.assertEqual(old,self.booking(cid));self.assertEqual('Booked',self.s.detail(cid)['candidate']['status']);self.assertIn('current booking is unchanged',self.s.detail(cid)['messages'][-1]['body'])
 def test_competing_replacement_does_not_lose_original(self):
  cid=self.booked();other=self.add('Other Person');self.s.reply(cid,'RESCHEDULE');slot=self.latest_slots(cid)[0];old=self.booking(cid)
  with self.s.conn() as c:c.execute('INSERT INTO bookings(candidate_id,role_id,start,end,created_at) VALUES(?,?,?,?,?)',(other,1,slot['start'],slot['end'],self.s.now()))
  self.s.reply(cid,'1');self.assertEqual(old,self.booking(cid));self.assertIn('no longer available',' '.join(m['body'] for m in self.s.detail(cid)['messages']))
 def test_intent_failure_never_changes_booking_or_candidate_answers(self):
  cid=self.booked();old=self.booking(cid);self.intent_mock.side_effect=intent.IntentUnavailable('Unavailable')
  self.s.reply(cid,'Please find next Tuesday afternoon');self.assertEqual(old,self.booking(cid));self.assertIn('could not interpret',self.s.detail(cid)['messages'][-1]['body'])
  self.s.reply(cid,'RESCHEDULE');self.assertEqual(old,self.booking(cid))
 def test_state_validation_prevents_scheduling_rejected_candidate(self):
  cid=self.add(shift='no');self.intent_mock.side_effect=None;self.intent_mock.return_value=self.interpretation()
  self.s.reply(cid,'Book any interview for me');self.assertIsNone(self.booking(cid));self.assertEqual('Rejected',self.s.detail(cid)['candidate']['status'])
 def test_ambiguous_intent_does_not_act_and_cancel_requires_confirmation(self):
  cid=self.booked();old=self.booking(cid);self.intent_mock.side_effect=None;self.intent_mock.return_value=self.interpretation(ambiguous=True,clarification='Which day do you prefer?')
  self.s.reply(cid,'Move it or keep it maybe');self.assertEqual(old,self.booking(cid));self.assertIn('clarify',self.s.detail(cid)['messages'][-1]['body'])
  self.intent_mock.return_value=self.interpretation(intent='cancel');self.s.reply(cid,'I want to cancel');self.assertEqual(old,self.booking(cid));self.assertEqual('buttons',json.loads(self.s.detail(cid)['messages'][-1]['component'])['type'])
  self.s.reply(cid,'KEEP');self.assertEqual(old,self.booking(cid));self.s.reply(cid,'CANCEL');self.assertIsNone(self.booking(cid))
 def test_free_text_answer_is_validated_against_pending_field(self):
  cid=self.add(shift='unknown');self.intent_mock.side_effect=None;self.intent_mock.return_value=self.interpretation(intent='answer',answer='yes')
  self.s.reply(cid,'I can work the advertised shift');self.assertEqual('yes',json.loads(self.s.detail(cid)['candidate']['structured'])['shift'])
 def test_invalid_intent_payload_and_past_date_do_not_act(self):
  with self.assertRaises(intent.IntentUnavailable):intent.validate(dict(intent='delete_all'))
  cid=self.booked();old=self.booking(cid);self.intent_mock.side_effect=None;self.intent_mock.return_value=self.interpretation(date='2020-01-01')
  self.s.reply(cid,'Please move to an old date');self.assertEqual(old,self.booking(cid));self.assertIn('upcoming date',self.s.detail(cid)['messages'][-1]['body'])
if __name__=='__main__':unittest.main()
