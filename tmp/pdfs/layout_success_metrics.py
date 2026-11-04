from pathlib import Path
p=Path('tmp/pdfs/build_submission.py');s=p.read_text()
a=s.index('metrics_start=y');b=s.index('metrics_height=y-metrics_start',a)
s=s[:a]+'''metrics_start=y
y=heading('Success metrics and guardrails',y)
y=para('<b>North star</b>  Qualified candidates with a confirmed first-round interview booking each week.',M,y,size=9.2,leading=12.5)+3
y=para('Count once per requisition against approved job criteria.',M,y,size=8,leading=10.5,color=MUTED)+12
columns=[
 ('Business',[
  '<b>1  Time to fill</b><br/>Days to fill a position.',
  '<b>2  Recruiter effort</b><br/>Hours per confirmed booking, including exceptions.',
  '<b>3  Cost per qualified booking</b><br/>Processing, messaging and human effort.']),
 ('Performance',[
  '<b>1  Outreach within 48 hours</b><br/>Meaningful next step; exclude generic acknowledgements.',
  '<b>2  Booking conversion</b><br/>Invitations that become confirmed bookings.',
  '<b>3  WhatsApp resolution</b><br/>Exceptions resolved without human intervention.']),
 ('Guardrails',[
  '<b>1  Screening quality</b><br/>Reduce unsuitable referrals; pilot ceiling of 2% wrongly excluded qualified candidates. Independent sampling and fairness checks.',
  '<b>2  Booking reliability</b><br/>No conflicts or duplicates; track system-caused changes.',
  '<b>3  Accountability</b><br/>Approved thresholds, evidence and review path; escalate unresolved cases at 36 hours.'])]
gap=18;colw=(CW-gap*2)/3;column_ends=[]
for i,(title,items) in enumerate(columns):
 x=M+i*(colw+gap)
 cy=para(title,x,y,width=colw,size=9,bold=True,color=PRIMARY)+7
 for item in items:cy=para(item,x,cy,width=colw,size=8.2,leading=10.8)+6
 column_ends.append(cy)
y=max(column_ends)
for i in [1,2]:
 x=M+i*(colw+gap)-gap/2
 c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(x,H-(metrics_start+62),x,H-y+6)
'''+s[b:]
p.write_text(s);Path('tmp/pdfs/build_decision_only.py').write_text(s.split('# D2\n',1)[0])
p=Path('CASE_THINKING.md');t=p.read_text();t+='\n17. Decision brief success metrics layout: use a full-width north-star statement followed by three clearly separated columns for business metrics, performance and guardrails, with three numbered items each. Keep the entire section within 25% of a page; favor readable structure over dense semicolon-separated paragraphs.\n';p.write_text(t)
