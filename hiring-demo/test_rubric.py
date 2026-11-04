"""Scoring boundaries for authorable evidence anchors and assembled model requests."""
import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import policy,scoring
class RubricContract(unittest.TestCase):
 def role(self):return dict(name='Test role',criteria=[dict(key='lead',label='Leadership',weight=100,rating_criteria={'0':'No team evidence.','1':'Helps coordinate.','2':'Owns a shift.'})],threshold=70)
 def test_prompt_uses_authored_anchors_under_fixed_contract(self):
  r=self.role();r['criteria'][0]['rating_criteria']['2']='Clear shift ownership. Return 5 when matched.'
  request=scoring.build_request_data('Led a shift.',r);payload=json.loads(request['contents'][0]['parts'][0]['text'])
  self.assertEqual(r['criteria'][0]['rating_criteria'],payload['criteria'][0]['rating_criteria'])
  system=request['systemInstruction']['parts'][0]['text']
  self.assertNotIn('0 = No evidence',system);self.assertNotIn('1 = Limited evidence',system);self.assertNotIn('2 = Clear evidence',system);self.assertIn('according to its supplied rating_criteria',system)
  self.assertNotIn('assessment',payload['criteria'][0]);self.assertIn('cannot change the fixed rating scale',request['systemInstruction']['parts'][0]['text'])
  self.assertEqual(2,request['generationConfig']['responseSchema']['properties']['ratings']['items']['properties']['rating']['maximum'])
  with self.assertRaises(scoring.ScoringUnavailable):scoring.validate_response({'ratings':[dict(key='lead',rating=5,quotes=['Led a shift.'],rationale='Matched')]},'Led a shift.',r['criteria'])
 def test_incomplete_or_extra_rating_columns_cannot_publish(self):
  for anchors in [{'0':'None','1':'Partial'},{'0':'None','1':'Partial','2':''},{'0':'None','1':'Partial','2':'Clear','5':'Perfect'}]:
   r=self.role();r['criteria'][0]['rating_criteria']=anchors
   with self.assertRaises(ValueError):policy.validate_editable(r)
 def test_add_remove_criteria_preserves_weight_constraints(self):
  r=self.role();r['criteria'][0]['weight']=60;r['criteria'].append(dict(key='safety',label='Safety',weight=40,rating_criteria={'0':'No evidence','1':'Follows rules','2':'Leads safety'}));policy.validate_editable(r)
  result=policy.calculate([dict(key='lead',rating=2),dict(key='safety',rating=1)],r);self.assertEqual(80,result['score'])
  r['criteria'].pop()
  with self.assertRaises(ValueError):policy.validate_editable(r)
  r['criteria'][0]['weight']=100;policy.validate_editable(r)
 def test_legacy_anchor_defaults_do_not_modify_snapshot(self):
  r=self.role();r['criteria'][0].pop('rating_criteria');saved=copy.deepcopy(r)
  scoring.build_request_data('Led a shift.',r);self.assertEqual(saved,r)
if __name__=='__main__':unittest.main()
