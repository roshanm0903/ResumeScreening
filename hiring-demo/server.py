import base64, json, os, re, sqlite3, subprocess, tempfile, threading
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import scoring
import intent
import policy as match_policy
import workflow as trace
from urllib.parse import urlsplit

ROOT=Path(__file__).parent
DB=Path(os.environ.get('HIRING_DB',str(ROOT/'data/hiring.sqlite3')))
DB.parent.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock()
def now(): return datetime.now(timezone.utc).isoformat()
class ClosingConnection(sqlite3.Connection):
 def __exit__(self,*args):
  try: return super().__exit__(*args)
  finally: self.close()
def conn():
 c=sqlite3.connect(DB,timeout=15,factory=ClosingConnection); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c

trace.configure(conn)

def log(c,kind,cid,payload):
 c.execute('INSERT INTO events(kind,candidate_id,payload,created_at) VALUES(?,?,?,?)',(kind,cid,json.dumps(payload),now()))
def msg(c,cid,direction,body,component=None):
 payload=component or {}
 c.execute('INSERT INTO messages(candidate_id,direction,body,created_at,component) VALUES(?,?,?,?,?)',(cid,direction,body,now(),json.dumps(payload)))
 if direction=='out':trace.record('channel.render_reply','Compose WhatsApp reply','deterministic',dict(candidate_id=cid,component=payload.get('type','text')),dict(text=body,component=payload,stored_in='messages',delivery='simulated'))
ASSESSMENTS={
 'picking':'Assess relevant experience preparing customer orders, selecting the correct items, checking accuracy and packaging goods. Accept equivalent or transferable tasks.',
 'inventory':'Assess evidence of counting physical stock, reconciling records, investigating differences or maintaining stock accuracy.',
 'scanner':'Assess experience using handheld product-identification devices or digital warehouse/inventory systems. Do not require a particular brand or acronym.',
 'safety':'Assess concrete examples of protective equipment, safe lifting or handling, clear work areas and adherence to workplace procedures.',
 'dispatch':'Assess experience checking incoming goods, matching deliveries to records, staging outbound goods, loading or arranging dispatch.',
 'customers':'Assess concrete experience helping customers, understanding requests and resolving service needs.',
 'pos':'Assess experience processing purchases or payments accurately using checkout systems or equivalent tools.',
 'stock':'Assess evidence of replenishing shelves, handling goods and maintaining accurate stock records.',
 'returns':'Assess experience handling returns, refunds, complaints or equivalent customer issues.'}
def template(role,criteria):
 return dict(name=role,version=1,threshold=match_policy.CONTRACT['default_threshold'],scoring_contract=match_policy.snapshot(),criteria=[dict(key=k,label=l,weight=w,assessment=ASSESSMENTS[k],rating_criteria=match_policy.rating_criteria(dict(key=k,label=l))) for k,l,w in criteria])
ASSESSMENTS.update({x['key']:x['assessment'] for x in match_policy.CONTRACT['warehouse_criteria']})
WAREHOUSE=template(match_policy.CONTRACT['warehouse_role_name'],[(x['key'],x['label'],x['weight']) for x in match_policy.CONTRACT['warehouse_criteria']])
RETAIL=template('Retail service associate',[
 ('customers','Customer support',35),('pos','Point of sale',25),('stock','Shelf & stock handling',20),('returns','Returns & issue resolution',20)])

def init():
 with conn() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS roles(id INTEGER PRIMARY KEY,title TEXT,site TEXT,policy TEXT);
  CREATE TABLE IF NOT EXISTS candidates(id INTEGER PRIMARY KEY,name TEXT,role_id INTEGER REFERENCES roles(id),resume_text TEXT,structured TEXT,score INTEGER,bucket TEXT,status TEXT,created_at TEXT,due_at TEXT,first_outreach TEXT,policy_version INTEGER,policy_snapshot TEXT,synthetic INTEGER DEFAULT 0);
  CREATE TABLE IF NOT EXISTS scores(id INTEGER PRIMARY KEY,candidate_id INTEGER REFERENCES candidates(id),criterion TEXT,weight REAL,rating INTEGER,evidence TEXT,points REAL,policy_version INTEGER);
  CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,candidate_id INTEGER REFERENCES candidates(id),direction TEXT,body TEXT,created_at TEXT);
  CREATE TABLE IF NOT EXISTS availability(id INTEGER PRIMARY KEY,role_id INTEGER REFERENCES roles(id),interviewer TEXT,start TEXT,end TEXT,available INTEGER);
  CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY,candidate_id INTEGER UNIQUE REFERENCES candidates(id),role_id INTEGER REFERENCES roles(id),start TEXT,end TEXT,created_at TEXT,UNIQUE(role_id,start));
  CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,kind TEXT,candidate_id INTEGER,payload TEXT,created_at TEXT);''')
  migrate(c)
  if c.execute('SELECT COUNT(*) FROM roles').fetchone()[0]: return
  for i,(p,site) in enumerate([(WAREHOUSE,'Bengaluru · India'),(RETAIL,'Pune · India')],1):
   c.execute('INSERT INTO roles VALUES(?,?,?,?)',(i,p['name'],site,json.dumps(p)))
  for rid in [1,2]:
   for day in range(1,8):
    for hour in [4,5,8,9]:
     start=(datetime.now(timezone.utc)+timedelta(days=day)).replace(hour=hour,minute=0,second=0,microsecond=0)
     for panel in ['Site supervisor','Operations lead']:
      c.execute('INSERT INTO availability(role_id,interviewer,start,end,available) VALUES(?,?,?,?,1)',(rid,panel,start.isoformat(),(start+timedelta(minutes=30)).isoformat()))
 for i in range(80):
  create_candidate(dict(name=f'Demo applicant {i+1:02}',role_id=1,resume=SAMPLE_RESUME,shift='yes',site='yes',start='yes',consent=True),synthetic=True,age=2+i%34)

REQUIREMENTS={
 1:dict(shift='06:00–14:00 IST, Monday–Saturday',site='Bengaluru distribution centre',start='within 14 days'),
 2:dict(shift='10:00–18:00 IST, Monday–Saturday',site='Pune retail store',start='within 14 days')}
FIELDS=['shift','site','start']
def migrate(c):
 # Schema only: working-hour filtering is deliberately not enabled in the prototype.
 c.executescript((ROOT/'panel_scheduling_schema.sql').read_text())
 trace.init_schema(c)
 if 'component' not in {x['name'] for x in c.execute('PRAGMA table_info(messages)')}:c.execute("ALTER TABLE messages ADD COLUMN component TEXT DEFAULT '{}'")
 columns={x['name'] for x in c.execute('PRAGMA table_info(candidates)')}
 for name,definition in [('pending_field',"TEXT DEFAULT ''"),('decision_reason',"TEXT DEFAULT ''"),('clarification_attempts','INTEGER DEFAULT 0'),('evaluation_version','INTEGER DEFAULT 1'),('rescheduling','INTEGER DEFAULT 0')]:
  if name not in columns:c.execute(f'ALTER TABLE candidates ADD COLUMN {name} {definition}')
 if 'evaluation_version' not in {x['name'] for x in c.execute('PRAGMA table_info(scores)')}:
  c.execute('ALTER TABLE scores ADD COLUMN evaluation_version INTEGER DEFAULT 1')
 for name,definition in [('rationale',"TEXT DEFAULT ''"),('evaluator',"TEXT DEFAULT 'Historical assessment'")]:
  if name not in {x['name'] for x in c.execute('PRAGMA table_info(scores)')}:c.execute(f'ALTER TABLE scores ADD COLUMN {name} {definition}')
 for role in c.execute('SELECT * FROM roles').fetchall():
  policy=json.loads(role['policy'])
  if any('terms' in x for x in policy['criteria']):
   for x in policy['criteria']:
    x.pop('terms',None);x['assessment']=ASSESSMENTS.get(x['key'],'Assess concrete job-related evidence for '+x['label'])
   policy['version']+=1;policy.setdefault('threshold',70)
   c.execute('UPDATE roles SET policy=? WHERE id=?',(json.dumps(policy),role['id']))
   log(c,'policy.semantic_rubric_migrated',None,dict(role_id=role['id'],version=policy['version']))
 for row in c.execute('SELECT id,policy FROM roles').fetchall():
  old=json.loads(row['policy'])
  if old.get('name')=='Warehouse associate' and {x['key'] for x in old['criteria']}=={'picking','inventory','scanner','safety','dispatch'}:
   updated=json.loads(json.dumps(WAREHOUSE));updated['version']=old['version']+1
   c.execute('UPDATE roles SET title=?,policy=? WHERE id=?',(updated['name'],json.dumps(updated),row['id']))
   log(c,'policy.manager_example_installed',None,dict(role_id=row['id'],previous_policy=old,version=updated['version']))
 for row in c.execute('SELECT id,policy FROM roles').fetchall():
  p=json.loads(row['policy'])
  if 'scoring_contract' not in p or p['scoring_contract'].get('version')!=match_policy.CONTRACT['version']:
   p['scoring_contract']=match_policy.snapshot();p['version']+=1
   c.execute('UPDATE roles SET policy=? WHERE id=?',(json.dumps(p),row['id']));log(c,'policy.contract_attached',None,dict(role_id=row['id'],version=p['version'],contract_version=match_policy.CONTRACT['version']))
 for row in c.execute('SELECT id,policy FROM roles').fetchall():
  p=json.loads(row['policy'])
  if any('rating_criteria' not in cr for cr in p['criteria']):
   for cr in p['criteria']:cr['rating_criteria']=match_policy.rating_criteria(cr)
   p['version']+=1
   c.execute('UPDATE roles SET policy=? WHERE id=?',(json.dumps(p),row['id']))
   log(c,'policy.rating_criteria_migrated',None,dict(role_id=row['id'],version=p['version']))
 # Preserve old records and their score evidence; upgrade only superseded review routes.
 for row in c.execute("SELECT * FROM candidates WHERE status IN ('Needs review','Requirement mismatch')").fetchall():
  facts=json.loads(row['structured']);missing=next((k for k in FIELDS if facts.get(k,'unknown')=='unknown'),'')
  failed=next((k for k in FIELDS if facts.get(k)=='no'),'')
  status='Rejected' if failed else 'Awaiting details' if missing else 'Rejected'
  reason=f'Confirmed mandatory requirement not met: {failed}.' if failed else 'Required details are missing.' if missing else f"Score {row['score']}/100 is below the configured threshold."
  c.execute('UPDATE candidates SET status=?,pending_field=?,decision_reason=? WHERE id=?',(status,missing,reason,row['id']))
  log(c,'policy.routing_migrated',row['id'],dict(status=status,reason=reason,previous_status=row['status']))

def extract_resume(d):
 text=str(d.get('resume',''))[:100000]
 if d.get('file'):
  raw=base64.b64decode(d['file'],validate=True)
  if len(raw)>5*1024*1024:raise ValueError('Maximum file size is 5 MB.')
  if raw.startswith(b'%PDF'):
   with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'resume.pdf';p.write_bytes(raw)
    result=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,timeout=15)
    text=result.stdout if result.returncode==0 else ''
  else:
   if not str(d.get('filename','')).lower().endswith('.txt'):raise ValueError('Upload a PDF or plain text file.')
   text=raw.decode('utf-8-sig')
 return text if len(text.strip())>=20 else ''

def redact(text,name):
 text=re.sub(re.escape(name),'[NAME REDACTED]',text,flags=re.I)
 text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[EMAIL REDACTED]',text)
 return re.sub(r'(?<!\w)(?:\+?\d[\d ()-]{8,}\d)(?!\w)','[PHONE REDACTED]',text)

def requirement_question(row,field):
 req=REQUIREMENTS.get(row['role_id'],REQUIREMENTS[1])
 return {'shift':f"Can you work {req['shift']}?",'site':f"Can you work onsite at {req['site']}?",'start':f"Can you start {req['start']}?"}[field]+' Reply YES or NO.'

def assess(c,cid):
 row=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
 trace.bind_candidate(cid)
 facts=json.loads(row['structured']);policy=json.loads(row['policy_snapshot']);threshold=policy.get('threshold',match_policy.CONTRACT['default_threshold'])
 trace.record('screening.load_policy','Load enterprise role policy','data',dict(candidate_id=cid,role_id=row['role_id'],source='candidate policy snapshot'),dict(policy_version=policy['version'],threshold=threshold,criteria=policy['criteria']))
 failed=next((k for k in FIELDS if facts.get(k)=='no'),'')
 missing=next((k for k in FIELDS if facts.get(k,'unknown')=='unknown'),'')
 trace.record('screening.mandatory_checks','Deterministic checks from application form input','deterministic',dict(answers={k:facts.get(k,'unknown') for k in FIELDS}),dict(failed=failed or None,missing=missing or None,next_node='decision.reject' if failed else 'clarification.collect' if missing else 'screening.resume_check'))
 pending='';score=None;bucket='Not scored';status='Awaiting batch';reason=''
 if failed:
  status='Rejected';reason='You confirmed that you cannot meet the advertised requirement: '+requirement_question(row,failed).split(' Reply')[0]+' This application cannot proceed. Reply REVIEW to request a human review.'
 elif missing:
  pending=missing;status='Awaiting details';reason='Waiting for confirmation of a required application detail.'
 elif len(row['resume_text'].strip())<20:
  pending='resume';status='Awaiting résumé';reason='We could not read your résumé. This is not a rejection.'
 else:
  total=0;version=row['evaluation_version']+1
  try:
   request_data=trace.execute('screening.build_prompt','Assemble screening prompt','deterministic',dict(role=policy['name'],criteria=policy['criteria'],fixed_ratings=[0,1,2],prompt_version=scoring.PROMPT_VERSION),lambda:scoring.build_request_data(row['resume_text'],policy))
   result=trace.execute('screening.llm_assess','LLM evidence ratings','llm',dict(redacted_resume=row['resume_text'],role=policy['name'],policy_version=policy['version'],criteria=policy['criteria'],model=scoring.MODEL,prompt_version=scoring.PROMPT_VERSION,request_data=request_data),lambda:dict(zip(['ratings','provenance'],scoring.evaluate(row['resume_text'],policy,request_data=request_data))))
   ratings,provenance=result['ratings'],result['provenance']
   try:assessment=match_policy.calculate(ratings,policy)
   except ValueError as e:raise scoring.ScoringUnavailable('Scoring policy or ratings could not be validated: '+str(e)) from None
  except scoring.ScoringUnavailable as e:
   reason=str(e);status='Scoring pending'
   c.execute("UPDATE candidates SET status=?,pending_field='',decision_reason=?,score=NULL,bucket='Not scored' WHERE id=?",(status,reason,cid))
   log(c,'scoring.unavailable',cid,dict(reason=reason,model=scoring.MODEL,prompt_version=scoring.PROMPT_VERSION))
   if not facts.get('consent'):c.execute("UPDATE candidates SET status='Channel needed' WHERE id=?",(cid,))
   return status
  by_key={x['key']:x for x in ratings}
  for cr in policy['criteria']:
   result=by_key[cr['key']];rating=result['rating'];points=next(x['points'] for x in assessment['contributions'] if x['key']==cr['key']);total+=points
   c.execute('INSERT INTO scores(candidate_id,criterion,weight,rating,evidence,points,policy_version,evaluation_version,rationale,evaluator) VALUES(?,?,?,?,?,?,?,?,?,?)',(cid,cr['label'],cr['weight'],rating,' | '.join(result['quotes']) or 'No supporting evidence in the resume.',points,policy['version'],version,result['rationale'],provenance['provider']+' / '+provenance['model']))
  log(c,'llm.assessment_completed',cid,dict(**provenance,evaluation_version=version,criterion_count=len(ratings)))
  trace.record('screening.aggregate','Calculate Match score','deterministic',dict(ratings=ratings,weights={x['key']:x['weight'] for x in policy['criteria']},threshold=threshold),dict(weighted_total=assessment['score'],formula=match_policy.CONTRACT['formula'],rounding=match_policy.CONTRACT['rounding'],bucket=assessment['bucket'],passes=assessment['passes'],contract_version=assessment['contract_version']))
  score=assessment['score'];bucket=assessment['bucket']
  c.execute('UPDATE candidates SET evaluation_version=? WHERE id=?',(version,cid))
  if not assessment['passes']:
   status='Rejected';weak=[x['criterion'] for x in c.execute('SELECT criterion FROM scores WHERE candidate_id=? AND evaluation_version=? AND rating<2',(cid,version))]
   reason=f'Your application scored {score:g}/100 against the published role criteria, below the required {threshold:g}. Limited supporting evidence was found for: '+', '.join(weak)+'. This application cannot proceed. Reply REVIEW to request human review.'
  else:reason=f'Your application meets the screening requirements. We will send interview options in the next hiring batch, before {datetime.fromisoformat(row["due_at"]).astimezone(timezone(timedelta(hours=5,minutes=30))).strftime("%d %b %I:%M %p IST")}.'
 if not facts.get('consent'):status='Channel needed'
 c.execute('UPDATE candidates SET status=?,pending_field=?,decision_reason=?,score=?,bucket=? WHERE id=?',(status,pending,reason,score,bucket,cid))
 trace.record('screening.persist_decision','Store decision and evidence','data',dict(candidate_id=cid,threshold=threshold),dict(status=status,score=score,bucket=bucket,reason=reason,pending_field=pending,stored_in=['candidates','scores','events']))
 log(c,'screening.completed',cid,dict(score=score,status=status,pending_field=pending,reason=reason,threshold=threshold,policy_version=policy['version'],engine='Gemini semantic assessment with deterministic aggregation' if score is not None else 'mandatory checks or clarification'))
 return status

REJECTION_MESSAGE='We regret to inform you that, while we appreciate your time, we cannot move forward with your application.'

def candidate_notice(row):
 if row['status']=='Rejected':return REJECTION_MESSAGE
 return {
  'Awaiting batch':'Your application has been received. We will contact you when interview times are available.',
  'Capacity wait':'Your application has been received. We will contact you when interview times are available.',
  'Invited':'Please choose one of the available interview times.',
  'Booked':'Your interview booking is confirmed.',
  'Review requested':'Your request for a human review has been received.',
  'Human support':'The hiring team will help with your application.',
  'Channel needed':'Opt in to WhatsApp updates to continue.',
  'Awaiting details':'Please confirm the missing application details in the conversation.',
  'Awaiting résumé':'Please provide a readable resume to complete your application.',
  'Scoring pending':'We are processing your application. You may try again later.'
 }.get(row['status'],'Your application is with the hiring team.')

def candidate_messages(messages):
 """Candidate-safe projection of legacy chats; preserve original database/audit records."""
 result=[]
 for message in messages:
  message=dict(message)
  if message['direction']=='out':
   text=message['body']
   if text.startswith('Your application meets the screening requirements.'):continue
   if text.startswith(('Your application scored ','You confirmed that you cannot meet the advertised requirement:')):message['body']=REJECTION_MESSAGE
  result.append(message)
 return result

def communicate(c,cid):
 row=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
 if row['status'] in ['Channel needed','Awaiting batch','Capacity wait']:return
 if row['status']=='Rejected':
  msg(c,cid,'out',REJECTION_MESSAGE)
 elif row['pending_field'] in FIELDS:
  msg(c,cid,'out','We need one detail to continue your application. '+requirement_question(row,row['pending_field']),dict(type='buttons',buttons=[dict(id='YES',title='Yes'),dict(id='NO',title='No')]))
 elif row['pending_field']=='resume':
  msg(c,cid,'out','We could not read a résumé for this application. Please upload a text-based PDF or TXT using Add résumé, or reply RESUME: followed by your work experience. Your application remains open.')
 elif row['status']=='Scoring pending':
  msg(c,cid,'out',row['decision_reason']+' Reply RETRY to try scoring again.',dict(type='buttons',buttons=[dict(id='RETRY',title='Retry screening')]))
 else:msg(c,cid,'out',row['decision_reason'])
 # A specific question, decision or explained next step counts as first outreach.
 c.execute('UPDATE candidates SET first_outreach=COALESCE(first_outreach,?) WHERE id=?',(now(),cid))

@trace.workflow('Screening')
def create_candidate(d,synthetic=False,age=0):
 name=str(d.get('name','')).strip()[:120]
 if not name:raise ValueError('Enter the candidate name.')
 rid=int(d.get('role_id',1));text=trace.execute('screening.parse_redact','Extract resume and redact identity','deterministic',dict(has_file=bool(d.get('file')),role_id=rid),lambda:redact(extract_resume(d),name))
 facts={k:d.get(k,'unknown') for k in FIELDS}
 if any(v not in ['yes','no','unknown'] for v in facts.values()):raise ValueError('Requirement answers must be yes, no or unknown.')
 facts['consent']=d.get('consent') is True
 with LOCK,conn() as c:
  role=c.execute('SELECT * FROM roles WHERE id=?',(rid,)).fetchone()
  if not role:raise ValueError('Role not found.')
  policy=json.loads(role['policy']);created=(datetime.now(timezone.utc)-timedelta(hours=age)).isoformat()
  cid=c.execute('INSERT INTO candidates(name,role_id,resume_text,structured,status,created_at,due_at,policy_version,policy_snapshot,synthetic,evaluation_version) VALUES(?,?,?,?,?,?,?,?,?,?,0)',(name,rid,text,json.dumps(facts),'Received',created,(datetime.fromisoformat(created)+timedelta(hours=48)).isoformat(),policy['version'],json.dumps(policy),int(synthetic))).lastrowid
  trace.bind_candidate(cid)
  if synthetic:
   c.execute("UPDATE candidates SET status='Sample record',decision_reason='Synthetic volume sample; no live assessment requested.' WHERE id=?",(cid,))
  else:
   assess(c,cid);communicate(c,cid)
 return cid

@trace.workflow('Screening from resume update')
def add_resume(cid,d):
 text=extract_resume(d)
 if not text:raise ValueError('Still no readable text. Try a text-based PDF/TXT or paste your experience.')
 with LOCK,conn() as c:
  row=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
  if not row or row['pending_field']!='resume':raise ValueError('This application is not waiting for a résumé.')
  c.execute('UPDATE candidates SET resume_text=?,clarification_attempts=0 WHERE id=?',(redact(text,row['name']),cid))
  log(c,'candidate.resume_received',cid,dict(source='candidate upload or paste'))
  assess(c,cid);communicate(c,cid)

SAMPLE_RESUME=match_policy.CONTRACT['warehouse_sample_resume']
def start_scenario(kind):
 configs={
 'positive':dict(name='Ananya Rao',shift='yes',site='yes',start='yes',resume=SAMPLE_RESUME),
 'missing_details':dict(name='Meera Patel',shift='unknown',site='yes',start='unknown',resume=SAMPLE_RESUME),
 'missing_resume':dict(name='Rahul Verma',shift='yes',site='yes',start='yes',resume=''),
 'mandatory_failure':dict(name='Kabir Das',shift='no',site='yes',start='yes',resume=SAMPLE_RESUME),
 'low_score':dict(name='Neha Singh',shift='yes',site='yes',start='yes',resume='Community centre receptionist. Assisted visitors, answered telephone calls and managed appointment enquiries.')}
 if kind not in configs:raise ValueError('Unknown demo scenario.')
 cid=create_candidate(dict(configs[kind],role_id=1,consent=True))
 with conn() as c:
  c.execute('UPDATE candidates SET synthetic=1 WHERE id=?',(cid,));log(c,'demo.scenario_started',cid,dict(scenario=kind))
 return cid

IST=timezone(timedelta(hours=5,minutes=30))
def intent_context(c,row):
 event=c.execute("SELECT payload FROM events WHERE candidate_id=? AND kind='slots.offered' ORDER BY id DESC LIMIT 1",(row['id'],)).fetchone()
 booking=c.execute('SELECT start,end FROM bookings WHERE candidate_id=?',(row['id'],)).fetchone()
 last=c.execute("SELECT body FROM messages WHERE candidate_id=? AND direction='out' ORDER BY id DESC LIMIT 1",(row['id'],)).fetchone()
 return dict(current_date_local=datetime.now(IST).date().isoformat(),timezone='Asia/Kolkata',state=row['status'],pending_field=row['pending_field'],pending_question=requirement_question(row,row['pending_field']) if row['pending_field'] in FIELDS else '',current_booking=dict(booking) if booking else None,rescheduling=bool(row['rescheduling']),offered_slots=json.loads(event[0])['slots'] if event else [],last_business_message=last[0] if last else '')

def resolve_message(c,row,body):
 text=body.lower();data=dict(intent='unknown',answer='unknown',date='',period='any',time='',slot_index=0,ambiguous=False,clarification='')
 known={'yes','no','1','2','3','none','other times','other options','none of these','cancel','reschedule','keep','review','why','retry','morning','afternoon','evening'}
 bypass=row['status'] in ['Human support','Review requested'] or (row['pending_field']=='resume' and text.startswith('resume:'))
 direct=text in known or bypass
 trace.record('conversation.input_gate','Check structured reply or free text','deterministic',dict(state=row['status'],pending_field=row['pending_field'],message=body),dict(path='rules' if direct else 'llm_intent',llm_needed=not direct))
 if direct:
  if text in ['yes','no']:data.update(intent='answer',answer=text)
  elif text in ['1','2','3']:data.update(intent='choose_slot',slot_index=int(text))
  elif text in ['none','other times','other options','none of these','morning','afternoon','evening']:data.update(intent='find_alternatives',period=text if text in ['morning','afternoon','evening'] else 'any')
  elif text=='reschedule':data['intent']='reschedule'
  elif text=='cancel':data['intent']='cancel'
  elif text=='review':data['intent']='request_review'
  elif text=='why':data['intent']='explain'
  else:data['intent']='status'
  source='rules'
 else:
  context=intent_context(c,row);request=intent.build_request_data(context,body)
  try:
   result=trace.execute('conversation.llm_intent','Interpret free-text intent with Gemini','llm',dict(context=context,message=body,model=intent.MODEL,prompt_version=intent.PROMPT_VERSION,request_data=request),lambda:intent.interpret(context,body,request))
   data=intent.validate(result['interpretation']);source='gemini'
  except intent.IntentUnavailable:
   return dict(route='conversation.intent_unavailable',body=body,preferences={},source='unavailable',interpretation=None)
 prefs={}
 if data['date']:prefs['date']=data['date']
 if data['period']!='any':prefs.update(period=data['period'],hours={'morning':[6,12],'afternoon':[12,18],'evening':[18,22]}[data['period']])
 if data['time']:prefs['time']=data['time']
 route='conversation.status_or_help';normalized=body
 if row['status'] in ['Human support','Review requested']:route='conversation.human_handoff'
 elif data['ambiguous']:route='conversation.clarify'
 elif row['status']=='Rejected':route='decision.review_request' if data['intent']=='request_review' else 'decision.explain'
 elif row['pending_field'] in FIELDS:
  route='clarification.collect';normalized=data['answer'] if data['intent']=='answer' else body
 elif row['pending_field']=='resume':route='screening.resume_update'
 elif row['status']=='Scoring pending':route='screening.retry' if text=='retry' else 'conversation.status_or_help'
 elif row['status']=='Awaiting batch':route='conversation.await_batch'
 elif row['status'] not in ['Invited','Booked','Capacity wait']:route='conversation.invalid_state'
 elif data['intent']=='cancel':route='calendar.cancel_booking' if text=='cancel' else 'calendar.confirm_cancel'
 elif text=='keep':route='calendar.keep_booking'
 elif data['intent'] in ['find_alternatives','reschedule']:route='calendar.find_alternatives'
 elif data['intent']=='choose_slot' and data['slot_index'] and (row['status']!='Booked' or row['rescheduling']):route='calendar.validate_and_book';normalized=str(data['slot_index'])
 elif row['status']=='Booked':route='conversation.booking_status'
 if prefs.get('date'):
  day=datetime.fromisoformat(prefs['date']).date();today=datetime.now(IST).date()
  if day<today or day>today+timedelta(days=90):route='conversation.clarify';data['clarification']='Please choose an upcoming date within 90 days.'
 return dict(route=route,body=normalized,preferences=prefs,source=source,interpretation=data)

def parse_preferences(body):
 text=body.lower();prefs={};today=datetime.now(IST).date()
 if 'tomorrow' in text:prefs['date']=(today+timedelta(days=1)).isoformat()
 elif 'today' in text:prefs['date']=today.isoformat()
 else:
  for i,day in enumerate(['monday','tuesday','wednesday','thursday','friday','saturday','sunday']):
   if day in text:prefs['date']=(today+timedelta(days=(i-today.weekday())%7 or 7)).isoformat();break
 for name,hours in [('morning',[6,12]),('afternoon',[12,18]),('evening',[18,22])]:
  if name in text:prefs['period']=name;prefs['hours']=hours
 return prefs

def available(c,rid,excluded=None,preferences=None):
 excluded=set(excluded or []);preferences=preferences or {}
 def query():
  rows=[dict(x) for x in c.execute("SELECT interviewer,start,end,available FROM availability WHERE role_id=? AND start>? ORDER BY start",(rid,now()))]
  booked={r['start'] for r in c.execute('SELECT start FROM bookings WHERE role_id=?',(rid,))}
  groups={}
  for r in rows:
   if r['available']:groups.setdefault((r['start'],r['end']),set()).add(r['interviewer'])
  slots=[]
  for (start,end),panel in groups.items():
   local=datetime.fromisoformat(start).astimezone(IST)
   if not {'Site supervisor','Operations lead'}.issubset(panel) or start in booked or start in excluded:continue
   if preferences.get('date') and local.date().isoformat()!=preferences['date']:continue
   if preferences.get('hours') and not preferences['hours'][0]<=local.hour<preferences['hours'][1]:continue
   if preferences.get('time') and local.strftime('%H:%M')!=preferences['time']:continue
   slots.append(dict(start=start,end=end))
  return dict(source='availability and bookings tables; simulated MCP calendar tool',panel=['Site supervisor','Operations lead'],calendar_rows_read=len(rows),booked_slots=len(booked),matched_slots=slots[:12])
 result=trace.execute('mcp.calendar.get_availability','Fetch fresh panel availability','tool',dict(role_id=rid,required_panel=['Site supervisor','Operations lead'],after=now(),excluded_previous_slots=sorted(excluded),preferences=preferences),query)
 return result['matched_slots']

def slot_text(slots):
 return '\n'.join(f'{i+1}. '+datetime.fromisoformat(s['start']).astimezone(IST).strftime('%a %d %b, %I:%M %p IST') for i,s in enumerate(slots))

def offer(c,cid,rid,alternatives=False,preferences=None):
 existing=c.execute('SELECT start,end FROM bookings WHERE candidate_id=?',(cid,)).fetchone()
 excluded=[]
 if alternatives:
  for event in c.execute("SELECT payload FROM events WHERE candidate_id=? AND kind='slots.offered'",(cid,)):
   excluded.extend(x['start'] for x in json.loads(event['payload'])['slots'])
 slots=available(c,rid,excluded,preferences)[:3]
 log(c,'calendar.get_availability (simulated MCP)',cid,dict(source='availability table',required_panel=['Site supervisor','Operations lead'],slots=slots,preferences=preferences or {},excluded=excluded))
 if not slots:
  if not alternatives and not existing:
   c.execute("UPDATE candidates SET status='Capacity wait' WHERE id=?",(cid,));return
  msg(c,cid,'out',('No new panel times match that request right now. Your current booking is unchanged. Try another day, or reply KEEP to keep your original time.' if existing else 'No new panel times match that request right now. Your application is still active. Try another day or say "morning" or "afternoon".'),dict(type='buttons',buttons=[dict(id='morning',title='Morning'),dict(id='afternoon',title='Afternoon')]+([dict(id='KEEP',title='Keep booking')] if existing else [])))
  c.execute("UPDATE candidates SET status=?,rescheduling=?,first_outreach=COALESCE(first_outreach,?) WHERE id=?",('Booked' if existing else 'Capacity wait',int(bool(existing)),now(),cid));return
 rows=[dict(id=str(i+1),title=datetime.fromisoformat(x['start']).astimezone(IST).strftime('%a %d %b · %I:%M %p'),description='30 min · IST · First-round interview') for i,x in enumerate(slots)]
 rows.append(dict(id='NONE',title='Find other times',description='Check the panel calendars again'))
 if existing:rows.append(dict(id='KEEP',title='Keep current booking',description='Leave the original time unchanged'))
 component=dict(type='list',button='Choose interview time',section='Available panel times',rows=rows)
 text=('I checked the panel calendars again and found these alternatives.' if alternatives else 'We would like to invite you to a first-round interview. I found times when both interviewers are available.')+' Choose a time below, or tell me a preferred day and morning/afternoon.\n'+slot_text(slots)
 if existing:text='Your current booking stays confirmed until you choose a replacement. '+text+'\nReply KEEP to retain the original time.'
 trace.record('calendar.build_options','Build choices from fetched availability','deterministic',dict(candidate_id=cid,available_slots=slots,preferences=preferences or {}),dict(component=component,excluded_previous_count=len(excluded)))
 msg(c,cid,'out',text,component)
 log(c,'slots.offered',cid,dict(slots=slots,preferences=preferences or {},reschedule=bool(existing)))
 c.execute("UPDATE candidates SET status=?,rescheduling=?,first_outreach=COALESCE(first_outreach,?) WHERE id=?",('Booked' if existing else 'Invited',int(bool(existing)),now(),cid))
@trace.workflow('Scheduling batch')
def batch(force=False,candidate_id=None):
 count=0
 with LOCK,conn() as c:
  rows=c.execute("SELECT * FROM candidates WHERE status IN ('Awaiting batch','Capacity wait','Awaiting details','Awaiting résumé','Rejected') ORDER BY due_at,id").fetchall()
  eligible=[r for r in rows if r['status'] in ['Awaiting batch','Capacity wait'] and json.loads(r['structured']).get('consent') and (force or (datetime.now(timezone.utc)-datetime.fromisoformat(r['created_at'])).total_seconds()>=12*3600)]
  ranked=match_policy.prioritize(eligible);priority={r['id']:i for i,r in enumerate(ranked)}
  rows=sorted(rows,key=lambda r:(r['role_id'],priority.get(r['id'],-1),r['due_at'],r['id']))
  trace.record('batch.prioritize','Choose batch priority','deterministic',dict(eligible_count=len(eligible),high_volume_trigger=match_policy.CONTRACT['high_volume_trigger']),dict(ordered_candidate_ids=[r['id'] for r in ranked],policy='Bucket priority only at high volume; original outreach deadline within each bucket. Otherwise deadline only.'))
  for row in rows:
   if candidate_id is not None and row['id']!=candidate_id:continue
   facts=json.loads(row['structured'])
   if not facts.get('consent'):continue
   age=(datetime.now(timezone.utc)-datetime.fromisoformat(row['created_at'])).total_seconds()
   if row['status'] in ['Awaiting details','Awaiting résumé']:
    if not row['first_outreach']:communicate(c,row['id'])
    if age>=36*3600:
     c.execute("UPDATE candidates SET status='Human support' WHERE id=?",(row['id'],));msg(c,row['id'],'out','Your application is still open. We are asking our hiring team to help resolve the missing information. This is not a rejection.');log(c,'clarification.escalated',row['id'],dict(reason='36-hour safeguard'))
    continue
   if row['status']=='Rejected':
    if not row['first_outreach']:communicate(c,row['id'])
    continue
   if force or age>=12*3600:
    if row['status']=='Capacity wait':
     last=c.execute("SELECT created_at FROM events WHERE candidate_id=? AND kind='calendar.get_availability (simulated MCP)' ORDER BY id DESC LIMIT 1",(row['id'],)).fetchone()
     if not force and last and (datetime.now(timezone.utc)-datetime.fromisoformat(last[0])).total_seconds()<3600:continue
    offer(c,row['id'],row['role_id']);count+=1
  log(c,'batch.completed',candidate_id,dict(processed=count,manual_demo=force))
 return count

@trace.workflow('WhatsApp conversation')
def reply(cid,body,display=None):
 body=str(body).strip()[:1000]
 if not body:raise ValueError('Enter a reply.')
 with LOCK,conn() as c:
  row=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
  if not row:raise ValueError('Candidate not found.')
  if row['status']=='Channel needed':raise ValueError('Enable candidate channel consent before using the simulated chat.')
  trace.record('channel.receive','Receive candidate message','data',dict(candidate_id=cid,message=body),dict(channel='WhatsApp simulation',status=row['status']))
  original=body
  msg(c,cid,'in',str(display)[:1000] if display else original)
  resolved=resolve_message(c,row,body);route=resolved['route'];body=resolved['body']
  trace.record('conversation.route','Validate state and route','deterministic',dict(status=row['status'],pending_field=row['pending_field'],text=original,interpretation=resolved['interpretation']),dict(route=route,source=resolved['source'],preferences=resolved['preferences']))
  if route in ['conversation.intent_unavailable','conversation.clarify']:
   if route=='conversation.intent_unavailable':text='I could not interpret that message right now. Please use a reply button, type RESCHEDULE for other times, or try again. Your application and booking are unchanged.'
   else:text='Please clarify your request. '+(resolved['interpretation'].get('clarification') or 'Do you want other interview times, a booking update, or help with your application?')
   if route=='conversation.clarify' and row['pending_field'] in FIELDS:
    attempts=row['clarification_attempts']+1;c.execute('UPDATE candidates SET clarification_attempts=? WHERE id=?',(attempts,cid))
    if attempts>=3:
     c.execute("UPDATE candidates SET status='Human support' WHERE id=?",(cid,));text='We could not confirm this detail. The hiring team will help you here. Your application has not been rejected.';log(c,'clarification.escalated',cid,dict(reason='three ambiguous answers'))
   msg(c,cid,'out',text);return
  if route in ['decision.review_request','decision.explain']:
   if route=='decision.review_request':
    c.execute("UPDATE candidates SET status='Review requested' WHERE id=?",(cid,));msg(c,cid,'out','Your request for a human review has been recorded. The hiring team will review your application and reply here. No interview has been booked.');log(c,'candidate.review_requested',cid,{})
   else:msg(c,cid,'out','We assessed the information provided against the role criteria and cannot progress this application. You may reply REVIEW to request a human review.')
   return
  if route=='conversation.human_handoff':
   msg(c,cid,'out','Your message has been saved for the hiring team. Your case is awaiting a human response.');return
  if route=='clarification.collect':
   answer=body.lower()
   if answer not in ['yes','no']:
    attempts=row['clarification_attempts']+1
    c.execute('UPDATE candidates SET clarification_attempts=? WHERE id=?',(attempts,cid))
    if attempts>=3:
     c.execute("UPDATE candidates SET status='Human support' WHERE id=?",(cid,));msg(c,cid,'out','We have not been able to confirm this detail. A hiring-team member will help you here. Your application has not been rejected.');log(c,'clarification.escalated',cid,dict(reason='three unrecognized answers'))
    else:msg(c,cid,'out','Please reply YES or NO so we can record your answer. '+requirement_question(row,row['pending_field']))
    return
   facts=json.loads(row['structured']);facts[row['pending_field']]=answer
   c.execute('UPDATE candidates SET structured=?,clarification_attempts=0 WHERE id=?',(json.dumps(facts),cid));log(c,'candidate.detail_collected',cid,dict(field=row['pending_field'],answer=answer))
   trace.record('clarification.save_answer','Validate and save required answer','data',dict(field=row['pending_field'],answer=answer),dict(candidate_id=cid,stored_in='candidates.structured',next_node='screening.mandatory_checks'))
   assess(c,cid);communicate(c,cid);return
  if route=='screening.resume_update':
   if body.lower().startswith('resume:') and len(body[7:].strip())>=20:
    text=redact(body[7:].strip(),row['name']);c.execute('UPDATE candidates SET resume_text=? WHERE id=?',(text,cid));log(c,'candidate.resume_received',cid,dict(source='chat'));assess(c,cid);communicate(c,cid)
   else:msg(c,cid,'out','Use Add résumé to upload a readable file, or send RESUME: followed by at least 20 characters of work experience. You have not been rejected.')
   return
  if route in ['screening.retry','conversation.status_or_help'] and row['status']=='Scoring pending':
   if route=='screening.retry':assess(c,cid);communicate(c,cid)
   else:msg(c,cid,'out','Your assessment is pending. Reply RETRY to try again. You have not been rejected.')
   return
  if route=='conversation.await_batch':
   msg(c,cid,'out','Your details are complete. Interview options will arrive in the next hiring batch.');return
  if route=='conversation.invalid_state':raise ValueError('This application is not ready for scheduling.')
  if route=='calendar.confirm_cancel':
   msg(c,cid,'out','Do you want to cancel your current booking? Choose Cancel booking, or Keep booking.',dict(type='buttons',buttons=[dict(id='CANCEL',title='Cancel booking'),dict(id='KEEP',title='Keep booking')]));return
  if route=='calendar.keep_booking':
   c.execute('UPDATE candidates SET rescheduling=0 WHERE id=?',(cid,));msg(c,cid,'out','Your current booking is unchanged.' if row['status']=='Booked' else 'Your application is still active.');return
  if route=='calendar.cancel_booking':
   c.execute('DELETE FROM bookings WHERE candidate_id=?',(cid,));trace.record('calendar.cancel_booking','Release previous booking','data',dict(candidate_id=cid),dict(booking_released=True));offer(c,cid,row['role_id']);return
  if route=='conversation.booking_status':msg(c,cid,'out','Your interview is confirmed. Reply RESCHEDULE to explore other times, or CANCEL to cancel it.');return
  if route=='calendar.find_alternatives':
   offer(c,cid,row['role_id'],alternatives=True,preferences=resolved['preferences']);return
  if route=='calendar.validate_and_book':
   event=c.execute("SELECT payload FROM events WHERE candidate_id=? AND kind='slots.offered' ORDER BY id DESC LIMIT 1",(cid,)).fetchone()
   slots=json.loads(event[0])['slots'] if event else []
   if int(body)>len(slots):raise ValueError('That slot was not offered.')
   chosen=slots[int(body)-1]
   if chosen['start'] not in [s['start'] for s in available(c,row['role_id'],preferences={'date':datetime.fromisoformat(chosen['start']).astimezone(IST).date().isoformat()})]:
    msg(c,cid,'out','That time is no longer available. Please choose a new slot.');offer(c,cid,row['role_id']);return
   trace.record('calendar.validate_selection','Recheck selected slot','deterministic',dict(candidate_id=cid,chosen=chosen),dict(available=True,next_node='calendar.persist_booking'))
   previous=c.execute('SELECT start,end FROM bookings WHERE candidate_id=?',(cid,)).fetchone()
   c.execute('INSERT INTO bookings(candidate_id,role_id,start,end,created_at) VALUES(?,?,?,?,?) ON CONFLICT(candidate_id) DO UPDATE SET role_id=excluded.role_id,start=excluded.start,end=excluded.end,created_at=excluded.created_at',(cid,row['role_id'],chosen['start'],chosen['end'],now()))
   trace.record('calendar.persist_booking','Confirm booking and reserve panel time','data',dict(candidate_id=cid,role_id=row['role_id'],slot=chosen),dict(stored_in='bookings',status='confirmed',previous_booking=dict(previous) if previous else None,rescheduled=bool(previous),duplicate_protection='unique role/time and candidate constraints'))
   c.execute("UPDATE candidates SET status='Booked',rescheduling=0 WHERE id=?",(cid,))
   msg(c,cid,'out','Confirmed: '+slot_text([chosen]).removeprefix('1. ')+' · 30 minutes with Site supervisor and Operations lead.',dict(type='confirmation',start=chosen['start'],end=chosen['end'],buttons=[dict(id='RESCHEDULE',title='Reschedule')]))
   log(c,'calendar.book_interview (simulated MCP)',cid,chosen);return
  msg(c,cid,'out','Choose a time from the list, ask for other times, or tell me a day and morning/afternoon, such as "tomorrow afternoon".')

def state():
 with conn() as c:
  roles=[dict(x) for x in c.execute('SELECT * FROM roles')]
  for r in roles:r['policy']=json.loads(r['policy']);r['requirements']=REQUIREMENTS.get(r['id'],REQUIREMENTS[1])
  return dict(scoring=scoring.connection_status(),sample_resume=SAMPLE_RESUME,scoring_contract=match_policy.snapshot(),roles=roles,candidates=[dict(x) for x in c.execute('SELECT id,name,role_id,score,bucket,status,created_at,due_at,first_outreach,synthetic,pending_field,decision_reason,json_extract(policy_snapshot,\'$.name\') AS role_title,EXISTS(SELECT 1 FROM scores s WHERE s.candidate_id=candidates.id AND s.evaluator=\'Historical assessment\') AS legacy_assessment FROM candidates ORDER BY id DESC')],bookings=[dict(x) for x in c.execute('SELECT * FROM bookings')],server_time=now())
def detail(cid):
 with conn() as c:
  row=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
  if not row:raise ValueError('Candidate not found.')
  messages=[dict(x) for x in c.execute('SELECT * FROM messages WHERE candidate_id=? ORDER BY id',(cid,))]
  return dict(candidate=dict(row),candidate_notice=candidate_notice(row),candidate_messages=candidate_messages(messages),scores=[dict(x) for x in c.execute('SELECT * FROM scores WHERE candidate_id=? AND evaluation_version=?',(cid,row['evaluation_version']))],messages=messages,events=[dict(x) for x in c.execute('SELECT * FROM events WHERE candidate_id=? ORDER BY id DESC',(cid,))])
# Only these implemented nodes may expose source. No arbitrary file/function lookup.
NODE_CODE={
 'screening.parse_redact':['extract_resume','redact'], 'batch.prioritize':['batch'],
 'screening.load_policy':['assess'], 'screening.mandatory_checks':['assess'],
 'screening.build_prompt':['assess'], 'screening.aggregate':['assess'], 'screening.persist_decision':['assess'],
 'conversation.input_gate':['resolve_message'], 'conversation.route':['resolve_message'],
 'clarification.save_answer':['reply'], 'calendar.validate_selection':['reply'],
 'calendar.persist_booking':['reply'], 'calendar.cancel_booking':['reply'],
 'calendar.build_options':['offer'], 'mcp.calendar.get_availability':['available'],
 'channel.receive':['reply'], 'channel.render_reply':['msg','communicate']}

def node_code(node_id):
 import ast,hashlib
 if node_id not in NODE_CODE:raise ValueError('Source is not available for this node.')
 source=Path(__file__).read_text();lines=source.splitlines();tree=ast.parse(source)
 functions={f.name:f for f in tree.body if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef))}
 blocks=[]
 for name in NODE_CODE[node_id]:
  f=functions[name];start=min([f.lineno]+[d.lineno for d in f.decorator_list]);end=f.end_lineno
  focus=[i for i in range(start,end+1) if node_id in lines[i-1]]
  if node_id=='conversation.route':focus=[i for i in range(start,end+1) if "route='conversation.status_or_help';normalized=body" in lines[i-1]]
  blocks.append(dict(function=name,start_line=start,end_line=end,code='\n'.join(lines[start-1:end]),focus_lines=focus))
 if node_id in ['screening.aggregate','screening.build_prompt']:
  helper_file='scoring.py' if node_id=='screening.build_prompt' else 'policy.py'
  helper=Path(__file__).with_name(helper_file).read_text();helper_lines=helper.splitlines();source+='\n'+helper
  for f in ast.parse(helper).body:
   if isinstance(f,ast.FunctionDef) and f.name in (['build_request_data','instructions_for'] if node_id=='screening.build_prompt' else ['calculate','bucket','validate']):
    blocks.append(dict(function=helper_file.removesuffix('.py')+'.'+f.name,file='hiring-demo/'+helper_file,start_line=f.lineno,end_line=f.end_lineno,code='\n'.join(helper_lines[f.lineno-1:f.end_lineno]),focus_lines=[]))
 return dict(node_id=node_id,language='Python',file='hiring-demo/server.py',source_version=hashlib.sha256(source.encode()).hexdigest()[:12],blocks=blocks,note='Current implementation. Related nodes share functions; the complete function is shown for context. Historical executions may use earlier code.')

class Handler(BaseHTTPRequestHandler):
 def send(self,data,status=200):
  body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def do_GET(self):
  try:
   if self.path=='/api/state':return self.send(state())
   if self.path.startswith('/api/node-code/'):
    from urllib.parse import unquote
    return self.send(node_code(unquote(self.path.split('/api/node-code/',1)[1])))
   if self.path=='/api/intent-prompt':return self.send(dict(prompt_version=intent.PROMPT_VERSION,model=intent.MODEL,request_data=intent.build_request_data(dict(current_date_local=datetime.now(IST).date().isoformat(),timezone='Asia/Kolkata',state='{{stored_state}}',pending_field='{{pending_field}}',current_booking='{{stored_booking}}',offered_slots='{{last_offered_slots}}'),'{{candidate_message}}'),candidate_id=None,source='Current chat intent prompt template'))
   if self.path=='/api/prompt' or self.path.startswith('/api/prompt/'):
    cid=int(self.path.split('/')[-1]) if self.path.startswith('/api/prompt/') else None
    if cid:
     row=detail(cid)['candidate'];policy=json.loads(row['policy_snapshot']);resume=row['resume_text']
    else:
     with conn() as c:policy=json.loads(c.execute('SELECT policy FROM roles WHERE id=1').fetchone()[0])
     resume='{{redacted_resume}}'
    return self.send(dict(prompt_version=scoring.PROMPT_VERSION,model=scoring.MODEL,request_data=scoring.build_request_data(resume,policy),candidate_id=cid,policy_version=policy['version'],source='Reconstructed from saved application policy and redacted resume' if cid else 'Current prompt template'))
   if self.path.startswith('/api/workflow/'):return self.send({'runs':trace.get_runs(int(self.path.split('/')[-1]))})
   if self.path.startswith('/api/candidate/'):return self.send(detail(int(self.path.split('/')[-1])))
   if self.path=='/api/database':
    with conn() as c:return self.send({t:[dict(x) for x in c.execute(f'SELECT * FROM {t} ORDER BY id DESC LIMIT 100')] for t in ['scores','bookings','availability','messages','events','workflow_runs']})
   request_path=urlsplit(self.path).path
   file=ROOT/'static'/('index.html' if request_path=='/' else request_path.lstrip('/'))
   if file.resolve().parent != (ROOT/'static').resolve() or not file.is_file():self.send_error(404);return
   body=file.read_bytes();self.send_response(200);self.send_header('Content-Type','text/html' if file.suffix=='.html' else 'text/css' if file.suffix=='.css' else 'application/javascript');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
  except Exception as e:self.send({'error':str(e)},400)
 def do_POST(self):
  try:
   length=int(self.headers.get('Content-Length',0))
   if length>8*1024*1024:raise ValueError('Request too large.')
   d=json.loads(self.rfile.read(length) or '{}')
   if self.path=='/api/candidates':return self.send({'id':create_candidate(d)})
   if self.path=='/api/scenario':return self.send({'id':start_scenario(d['kind'])})
   if self.path=='/api/consent':
    with LOCK,conn() as c:
     row=c.execute('SELECT * FROM candidates WHERE id=?',(int(d['id']),)).fetchone()
     if not row:raise ValueError('Candidate not found.')
     if row['status']!='Channel needed':raise ValueError('This application already has a channel.')
     facts=json.loads(row['structured']);facts['consent']=True;c.execute('UPDATE candidates SET structured=? WHERE id=?',(json.dumps(facts),row['id']));log(c,'candidate.channel_opt_in',row['id'],dict(channel='simulated WhatsApp'));assess(c,row['id']);communicate(c,row['id'])
    return self.send({'ok':True})
   if self.path=='/api/batch':return self.send({'processed':batch(force=True,candidate_id=int(d['id']) if d.get('id') else None)})
   if self.path=='/api/resume':add_resume(int(d['id']),d);return self.send({'ok':True})
   if self.path=='/api/reply':reply(int(d['id']),d['body'],d.get('display'));return self.send({'ok':True})
   if self.path in ['/api/policy','/api/policy/preview']:
    rid=int(d['role_id'])
    with conn() as c:
     row=c.execute('SELECT policy FROM roles WHERE id=?',(rid,)).fetchone()
     if not row:raise ValueError('Role not found.')
     p=json.loads(row[0]);p['criteria']=d['criteria'];p['threshold']=d.get('threshold',p.get('threshold',70))
     match_policy.validate_editable(p)
     if self.path=='/api/policy/preview':return self.send(dict(prompt_version=scoring.PROMPT_VERSION,request_data=scoring.build_request_data('{{redacted_resume}}',p)))
     p['version']+=1
     c.execute('UPDATE roles SET policy=? WHERE id=?',(json.dumps(p),rid));log(c,'policy.published',None,dict(role_id=rid,policy=p,owner='Demo recruiter'))
    return self.send({'ok':True})
   self.send({'error':'Unknown route'},404)
  except Exception as e:self.send({'error':str(e)},400)
 def log_message(self,*args):pass

def loop():
 import time
 while True:
  time.sleep(30)
  try:batch()
  except Exception:pass
if __name__=='__main__':
 init();threading.Thread(target=loop,daemon=True).start()
 port=int(os.environ.get('PORT','8765'));print(f'Hiring demo running at http://127.0.0.1:{port}',flush=True)
 ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
