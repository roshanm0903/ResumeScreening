"""Real execution traces, streamed from memory while running and persisted on completion."""
import contextvars,copy,functools,inspect,json,threading,time,uuid
from datetime import datetime,timezone

_current=contextvars.ContextVar('workflow_run',default=None)
_runs={};_lock=threading.RLock();_factory=None

def configure(factory):
 global _factory
 _factory=factory
 with _lock:_runs.clear()

def timestamp():return datetime.now(timezone.utc).isoformat()
def init_schema(c):
 c.execute('CREATE TABLE IF NOT EXISTS workflow_runs(id TEXT PRIMARY KEY,candidate_id INTEGER,kind TEXT,status TEXT,started_at TEXT,finished_at TEXT,steps TEXT)')
def bind_candidate(cid):
 run=_current.get()
 if run:
  with _lock:run['candidate_id']=cid

def execute(node,label,kind,inputs,fn):
 run=_current.get()
 if not run:return fn()
 step=dict(index=len(run['steps'])+1,node=node,label=label,kind=kind,status='running',inputs=inputs,outputs=None,started_at=timestamp(),duration_ms=None)
 with _lock:run['steps'].append(step)
 start=time.monotonic()
 try:
  result=fn()
  with _lock:step.update(status='completed',outputs=result,duration_ms=round((time.monotonic()-start)*1000,1))
  return result
 except Exception as e:
  with _lock:step.update(status='failed',outputs={'error':str(e)},duration_ms=round((time.monotonic()-start)*1000,1))
  raise

def record(node,label,kind,inputs,outputs):return execute(node,label,kind,inputs,lambda:outputs)

def workflow(kind):
 def decorate(fn):
  signature=inspect.signature(fn)
  @functools.wraps(fn)
  def wrapped(*args,**kwargs):
   if _current.get() or kwargs.get('synthetic'):return fn(*args,**kwargs)
   values=signature.bind_partial(*args,**kwargs).arguments
   run=dict(id=uuid.uuid4().hex,candidate_id=values.get('cid',values.get('candidate_id')),kind=kind,status='running',started_at=timestamp(),finished_at=None,steps=[])
   with _lock:
    _runs[run['id']]=run
    while len(_runs)>100:_runs.pop(next(iter(_runs)))
   token=_current.set(run)
   try:
    result=fn(*args,**kwargs)
    if fn.__name__=='create_candidate':bind_candidate(result)
    run['status']='completed';return result
   except Exception:
    run['status']='failed';raise
   finally:
    run['finished_at']=timestamp();_current.reset(token)
    with _lock:payload=copy.deepcopy(run)
    if _factory:
     with _factory() as c:c.execute('INSERT OR REPLACE INTO workflow_runs VALUES(?,?,?,?,?,?,?)',(payload['id'],payload['candidate_id'],kind,payload['status'],payload['started_at'],payload['finished_at'],json.dumps(payload['steps'])))
  return wrapped
 return decorate

def get_runs(cid):
 results={}
 if _factory:
  with _factory() as c:
   for row in c.execute('SELECT * FROM workflow_runs WHERE candidate_id=? ORDER BY started_at DESC LIMIT 20',(cid,)):
    run=dict(row);run['steps']=json.loads(run['steps']);results[run['id']]=run
 with _lock:
  for run in _runs.values():
   if run['candidate_id']==cid:results[run['id']]=copy.deepcopy(run)
 return sorted(results.values(),key=lambda r:r['started_at'],reverse=True)[:20]
