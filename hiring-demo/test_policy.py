"""Meaningful boundaries for the shared scoring/queue contract; no model calls."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import policy

class ScoringPolicy(unittest.TestCase):
 def role(self,weights=(40,60),threshold=70):
  return dict(threshold=threshold,scoring_contract=policy.snapshot(),criteria=[dict(key=str(i),weight=w) for i,w in enumerate(weights)])
 def ratings(self,*values):return [dict(key=str(i),rating=v) for i,v in enumerate(values)]
 def test_all_bucket_edges_including_fractions(self):
  for score,expected in [(0,'Poor'),(49.99,'Poor'),(50,'Fair'),(69.99,'Fair'),(70,'Good'),(85,'Good'),(85.99,'Good'),(86,'Excellent'),(100,'Excellent'),(None,'Not scored')]:
   with self.subTest(score=score):self.assertEqual(expected,policy.bucket(score))
 def test_round_once_half_up_before_decision(self):
  result=policy.calculate(self.ratings(2,1),self.role((39.99,60.01)))
  self.assertEqual(70,result['score']);self.assertEqual('Good',result['bucket']);self.assertTrue(result['passes'])
  result=policy.calculate(self.ratings(2,1),self.role((39.97,60.03)))
  self.assertEqual(69.99,result['score']);self.assertFalse(result['passes'])
 def test_threshold_and_bucket_are_independent(self):
  result=policy.calculate(self.ratings(2,1),self.role((50,50),80));self.assertEqual(75,result['score']);self.assertEqual('Good',result['bucket']);self.assertFalse(result['passes'])
  self.assertTrue(policy.calculate(self.ratings(2,1),self.role((50,50),75))['passes'])
 def test_invalid_weights_ratings_and_nonfinite_values(self):
  for role in [self.role((40,59.99)),self.role((40.001,59.999)),self.role((float('nan'),100)),self.role(threshold=float('inf'))]:
   with self.assertRaises(ValueError):policy.calculate(self.ratings(2,1),role)
  with self.assertRaises(ValueError):policy.calculate(self.ratings(3,1),self.role())
  with self.assertRaises(ValueError):policy.calculate([dict(key='0',rating=2),dict(key='0',rating=1)],self.role())
 def test_manager_example_needs_leadership_at_default_threshold(self):
  role=dict(criteria=policy.CONTRACT['warehouse_criteria'],threshold=70,scoring_contract=policy.snapshot())
  ratings=[dict(key=c['key'],rating=0 if c['key']=='leadership' else 2) for c in role['criteria']]
  result=policy.calculate(ratings,role);self.assertEqual(65,result['score']);self.assertFalse(result['passes'])
 def test_snapshot_is_immutable_copy(self):
  snapshot=policy.snapshot();snapshot['buckets'][0]['label']='Changed';self.assertEqual('Poor',policy.CONTRACT['buckets'][0]['label'])
 def test_low_volume_uses_deadline_high_volume_uses_bucket_then_deadline(self):
  rows=[dict(id=1,role_id=1,bucket='Good',score=70,due_at='2026-11-01'),dict(id=2,role_id=1,bucket='Excellent',score=90,due_at='2026-11-02'),dict(id=3,role_id=1,bucket='Good',score=85,due_at='2026-11-03')]
  self.assertEqual([1,2,3],[r['id'] for r in policy.prioritize(rows,80)])
  self.assertEqual([2,1,3],[r['id'] for r in policy.prioritize(rows,3)])
if __name__=='__main__':unittest.main()
