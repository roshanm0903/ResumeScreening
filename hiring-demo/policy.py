"""Shared scoring contract for runtime, UI and submission documents."""
import copy,json
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP,InvalidOperation
CONTRACT=json.loads(Path(__file__).with_name('scoring_policy.json').read_text())
def D(value):
 try:return Decimal(str(value))
 except (InvalidOperation,ValueError):raise ValueError('Invalid numeric policy value.') from None

def snapshot():return copy.deepcopy(CONTRACT)
def contract_for(role_policy):return role_policy.get('scoring_contract',CONTRACT)
def threshold(value):
 n=D(value)
 if not n.is_finite() or not 0<=n<=100 or n!=n.quantize(D('.01')):raise ValueError('Threshold must be 0-100 with at most two decimals.')
 return n

def validate(role_policy):
 criteria=role_policy.get('criteria',[])
 if not criteria or len(criteria)>12:raise ValueError('Use 1-12 criteria.')
 keys=[x['key'] for x in criteria]
 if len(set(keys))!=len(keys):raise ValueError('Criterion keys must be unique.')
 weights=[D(x['weight']) for x in criteria]
 if any(not w.is_finite() or not 0<w<=100 or w!=w.quantize(D('.01')) for w in weights):raise ValueError('Weights must be positive with at most two decimals.')
 if sum(weights)!=100:raise ValueError('Weights must total exactly 100%.')
 threshold(role_policy.get('threshold',CONTRACT['default_threshold']))
 return role_policy

def rating_criteria(criterion):
 """Read explicit anchors; legacy policies get compatible defaults without rewriting history."""
 if 'rating_criteria' in criterion:return copy.deepcopy(criterion['rating_criteria'])
 known=next((x for x in CONTRACT['warehouse_criteria'] if x['key']==criterion.get('key') and x['label']==criterion.get('label')),None)
 if known:return copy.deepcopy(known['rating_criteria'])
 label=criterion.get('label','this criterion')
 return {'0':'No relevant evidence for '+label+'.','1':'Relevant task evidence for '+label+', with limited context or unclear ownership.','2':'Concrete evidence for '+label+', with clear responsibility and context.'}

def validate_editable(role_policy):
 """Validate the authorable data; numeric rating keys are a fixed application contract."""
 validate(role_policy)
 for criterion in role_policy['criteria']:
  if not isinstance(criterion.get('key'),str) or not criterion['key'].strip():raise ValueError('Each criterion needs a stable key.')
  if not isinstance(criterion.get('label'),str) or not criterion['label'].strip():raise ValueError('Each criterion needs a name.')
  definitions=criterion.get('rating_criteria')
  if not isinstance(definitions,dict) or set(definitions)!={'0','1','2'}:raise ValueError('Define evidence for exactly ratings 0, 1 and 2.')
  if any(not isinstance(v,str) or not v.strip() or len(v)>2000 for v in definitions.values()):raise ValueError('Each rating needs an evidence definition (1-2000 characters).')
 return role_policy

def bucket(score,contract=None):
 contract=contract or CONTRACT
 if score is None:return contract['not_scored']
 n=D(score)
 if not n.is_finite() or not 0<=n<=100:raise ValueError('Match score must be between 0 and 100.')
 for band in contract['buckets']:
  if n>=D(band['min']) and (n<=D(band['max']) if band['max_inclusive'] else n<D(band['max'])):return band['label']
 raise ValueError('Score does not match a bucket.')

def calculate(ratings,role_policy):
 validate(role_policy);contract=contract_for(role_policy)
 by_key={x['key']:x for x in ratings}
 if len(by_key)!=len(ratings) or set(by_key)!={x['key'] for x in role_policy['criteria']}:raise ValueError('Ratings must cover each criterion exactly once.')
 allowed={a['rating'] for a in contract['anchors']};parts=[];total=D(0)
 for criterion in role_policy['criteria']:
  rating=by_key[criterion['key']]['rating']
  if type(rating) is not int or rating not in allowed:raise ValueError('Invalid evidence rating.')
  points=D(criterion['weight'])*rating/contract['rating_max'];total+=points
  parts.append(dict(key=criterion['key'],points=float(points)))
 total=total.quantize(D('.01'),rounding=ROUND_HALF_UP)
 return dict(score=float(total),bucket=bucket(total,contract),passes=total>=threshold(role_policy.get('threshold',CONTRACT['default_threshold'])),contributions=parts,contract_version=contract['version'])

def prioritize(rows,high_volume_trigger=None):
 trigger=high_volume_trigger or CONTRACT['high_volume_trigger'];counts={}
 for row in rows:counts[row['role_id']]=counts.get(row['role_id'],0)+1
 ranks={band['label']:i for i,band in enumerate(CONTRACT['buckets'])}
 return sorted(rows,key=lambda r:(r['role_id'],-ranks.get(r['bucket'],-1) if counts[r['role_id']]>=trigger else 0,r['due_at'],r['id']))
