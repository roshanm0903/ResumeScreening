from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path

OUT=Path('output/pdf'); OUT.mkdir(parents=True,exist_ok=True)
F='/System/Library/Fonts/Supplemental/'
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]:pdfmetrics.registerFont(TTFont(n,F+f))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
W,H=595.276,841.89; M=40; CW=W-M*2
INK=HexColor('#172824'); GREEN=HexColor('#256450'); MUTED=HexColor('#64736D'); LINE=HexColor('#D9E1DB'); PALE=HexColor('#EEF4EF'); BLUE=HexColor('#233E48'); GOLD=HexColor('#F4EEDD')
S=ParagraphStyle('body',fontName='Body',fontSize=9.4,leading=13.1,textColor=INK,spaceAfter=0)

def para(text,x,y,width=CW,size=9.4,leading=None,color=INK,bold=False):
 st=ParagraphStyle('p',parent=S,fontName='Bold' if bold else 'Body',fontSize=size,leading=leading or size*1.38,textColor=color)
 p=Paragraph(text,st);_,h=p.wrap(width,800);p.drawOn(c,x,H-y-h);return y+h

def label(text,x,y,color=GREEN):
 c.setFillColor(color);c.setFont('Bold',8);c.drawString(x,H-y-8,text.upper());return y+15

def heading(text,y):
 return para(text,M,y,size=12.3,bold=True)+7

def body(text,y,after=10):return para(text,M,y)+after

def footer(ref,page):
 c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,31,W-M,31)
 c.setFillColor(MUTED);c.setFont('Body',7);c.drawString(M,20,'Roshan Manellore  |  Darwinbox recruitment case  |  4 November 2026');c.drawRightString(W-M,20,f'{ref}  /  {page} of 2')

def page_start(ref,title,subtitle,page):
 label(ref+'  /  RECRUITMENT AT VOLUME',M,33)
 y=para(title,M,55,size=23,leading=27,bold=True)
 y=para(subtitle,M,y+7,size=9.4,color=MUTED)+20
 footer(ref,page);return y

def table(headers,rows,widths,y,size=8.4,padding=8):
 st=ParagraphStyle('cell',parent=S,fontSize=size,leading=size*1.32)
 sh=ParagraphStyle('head',parent=st,fontName='Bold',textColor=white,fontSize=8)
 data=[[Paragraph(h,sh) for h in headers]]+[[Paragraph(str(v),st) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLUE),('GRID',(0,0),(-1,-1),.45,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#F5F8F6')])]))
 _,h=t.wrap(CW,900);t.drawOn(c,M,H-y-h);return y+h+12

def arrow(x1,y1,x2,y2,color=GREEN):
 import math
 c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(1)
 c.line(x1,H-y1,x2,H-y2)
 a=math.atan2(y2-y1,x2-x1);r=4.5
 p=c.beginPath();p.moveTo(x2,H-y2);p.lineTo(x2-r*math.cos(a-.5),H-(y2-r*math.sin(a-.5)));p.lineTo(x2-r*math.cos(a+.5),H-(y2-r*math.sin(a+.5)));p.close();c.drawPath(p,fill=1,stroke=0)

def node(x,y,w,h,title,sub='',fill=PALE):
 c.setFillColor(fill);c.setStrokeColor(LINE);c.roundRect(x,H-y-h,w,h,5,fill=1,stroke=1)
 st=ParagraphStyle('n',parent=S,fontName='Bold',fontSize=8.1,leading=10.3,alignment=TA_CENTER)
 p=Paragraph(title,st);_,ph=p.wrap(w-12,h);p.drawOn(c,x+6,H-y-9-ph)
 if sub:
  st2=ParagraphStyle('ns',parent=S,fontSize=7.3,leading=9.2,alignment=TA_CENTER,textColor=MUTED)
  p=Paragraph(sub,st2);_,ph=p.wrap(w-12,h);p.drawOn(c,x+6,H-y-h+8)

def stats(y):
 values=[('400k','applications each year'),('20k','roles filled each year'),('9 days','median first response'),('4 months','until seasonal peak')]
 col=CW/4
 for i,(v,t) in enumerate(values):
  x=M+i*col
  if i:c.setStrokeColor(LINE);c.line(x-8,H-y-4,x-8,H-y-48)
  para(v,x,y,width=col-15,size=21,leading=25,bold=True,color=GREEN)
  para(t,x,y+30,width=col-15,size=7.8,color=MUTED)
 return y+67

def check(y,page):
 print(page,'content ends at',round(y,1),'of 790')
 if y>790:raise ValueError('Page overflow '+page)

def decision_flow(y):
 # Mandatory checks and a calibrated score can both trigger rejection.
 w=150;gap=(CW-3*w)/2
 xs=[M,M+w+gap,M+2*(w+gap)]
 for i,(t,s) in enumerate([('Application received','Mobile form and resume'),('Parse and redact','Name excluded from scoring'),('Apply approved policy','Mandatory checks then LLM rubric')]):
  node(xs[i],y,w,47,t,s)
  if i<2:arrow(xs[i]+w,y+23.5,xs[i+1]-2,y+23.5)
 mid=xs[2]+w/2
 c.setStrokeColor(GREEN);c.line(mid,H-y-47,mid,H-y-63);c.line(xs[0]+w/2,H-y-63,mid,H-y-63)
 widths=116;outgap=(CW-4*widths)/3
 outxs=[M+i*(widths+outgap) for i in range(4)]
 c.setStrokeColor(GREEN);c.line(outxs[0]+widths/2,H-y-63,outxs[-1]+widths/2,H-y-63)
 for i,(t,s) in enumerate([('Mandatory check failed','Reject with rule reason'),('Score below threshold','Reject with scoring evidence'),('Input missing or unreadable','Clarify through WhatsApp'),('Checks and score pass','Batch then offer interview slots')]):
  arrow(outxs[i]+widths/2,y+63,outxs[i]+widths/2,y+75)
  node(outxs[i],y+76,widths,48,t,s,PALE if i==3 else GOLD)
 return y+134

def timeline(y):
 labels=[('01-02','Agree and baseline'),('03-06','Build core flow'),('07-10','Shadow and evaluate'),('11-16','Pilot then expand')]
 widths=CW/4
 for i,(w,t) in enumerate(labels):
  x=M+i*widths
  c.setFillColor(GREEN);c.circle(x+7,H-y-9,6,fill=1,stroke=0)
  if i<3:c.setStrokeColor(LINE);c.line(x+15,H-y-9,x+widths-3,H-y-9)
  para('WEEKS '+w,x,y+23,width=widths-12,size=7.5,bold=True,color=GREEN)
  para(t,x,y+38,width=widths-12,size=8.5,bold=True)
 return y+73

# D2
def body(text,y,after=5):return para(text,M,y,size=8.6,leading=11.4)+after
c=canvas.Canvas(str(OUT/'D2_Build_Sheet.pdf'),pagesize=(W,H));c.setTitle('Recruitment AI screening build sheet');c.setAuthor('Roshan Manellore')
y=page_start('D2','Recruitment screening build sheet','MVP workflow data contracts and delivery scope',1)
y=body('Reuse recruitment records and scheduling. The LLM rates role evidence; policy rejects failed mandatory checks or scores below threshold and schedules passing candidates. Resolve factual gaps and scheduling exceptions through the candidate\'s messaging channel before escalating.',y)
y=heading('Solution architecture',y)
w=150;gap=(CW-3*w)/2;xs=[M+i*(w+gap) for i in range(3)]
for i,(t,sub) in enumerate([('Recruiter workspace','Requisitions, templates, dashboard'),('Applicant mobile journey','Resume and structured answers'),('Channel adapter','WhatsApp / SMS and consent')]):
 node(xs[i],y,w,34,t,sub)
# The three interfaces share a service boundary; replies return through the same channel.
for x in [xs[0]+75,xs[1]+75,xs[2]+75]:
 c.setStrokeColor(GREEN);c.line(x,H-y-43,x,H-y-55)
c.setStrokeColor(GREEN);c.line(xs[0]+75,H-y-55,xs[2]+75,H-y-55)
arrow(xs[1]+75,y+37,xs[1]+75,y+45)
for i,(t,sub) in enumerate([('Document and scoring service','Parse, redact, extract evidence'),('Workflow and policy engine','Batch, clarify, route and retry'),('MCP calendar gateway','Availability and booking tools')]):
 node(xs[i],y+46,w,38,t,sub)
arrow(xs[1],y+62,xs[0]+w,y+62);arrow(xs[0]+w,y+68,xs[1],y+68)
arrow(xs[1]+w,y+62,xs[2],y+62);arrow(xs[2],y+68,xs[1]+w,y+68)
node(M,y+97,2*w+gap,34,'Application database and audit events','Candidates, scores, evidence, policy versions, messages and bookings')
node(xs[2],y+97,w,34,'External panel calendars','Production via MCP; demo tables')
arrow(xs[0]+75,y+84,xs[0]+75,y+96);arrow(xs[1]+75,y+84,xs[1]+75,y+96);arrow(xs[2]+75,y+84,xs[2]+75,y+96)
y+=136
y=para('Replies return to the workflow engine. Validated answers trigger policy re-evaluation; deterministic actions record the candidate ID and policy version.',M,y,size=8.3,leading=11.2)+12
y=heading('Resume extraction, redaction and injection controls',y)
y=para('<b>Text-first cost choice.</b> Extract text locally; OCR scanned pages. Send only normalized, redacted text and the approved rubric to the LLM, not the PDF or page images. Use rendered-page OCR to cross-check the PDF text layer; measure OCR cost, token cost and extraction accuracy in the pilot.',M,y,size=8.1,leading=10.5)+5
y=para('<b>Before scoring.</b> Remove names, email and phone from all model-bound text, including clarifications; keep identity/contact separately with controlled access. Retain page/span references for evidence. Redaction limits identity exposure; it does not remove every bias proxy.',M,y,size=8.1,leading=10.5)+5
y=para('<b>Hidden-content gate.</b> Compare extracted text with rendered-page OCR; inspect low-contrast/white, transparent, tiny, off-page and hidden-layer text. Exclude metadata, annotations and embedded files from scoring. Flag material discrepancies, Unicode obfuscation, instruction-like text and keyword stuffing. Preserve legitimate multilingual content. Isolate suspicious files for re-upload/clarification or unresolved-case review; do not reject solely on an anomaly.',M,y,size=8.1,leading=10.5)+5
y=para('<b>Contain injection.</b> Treat every resume and reply as untrusted evidence. The scorer has no tools or policy-write access. Validate output schema, ranges and cited evidence; compute totals and apply thresholds outside the model. Filters and OCR are imperfect; test attacks and benign controls before release.',M,y,size=8.1,leading=10.5)+9
y=heading('Role templates and decision rules',y)
y=body('Use organization controls, role templates and requisition adjustments. Warehouse example below. Check shift, site, start date and pay acceptance separately.',y)
y=table(['Scoring parameter','Weight','Example evidence'],[
 ['Order picking and packing','30%','Preparing, checking and packing orders'],
 ['Inventory accuracy','25%','Cycle counts and stock reconciliation'],
 ['Warehouse systems','20%','Barcode scanners or warehouse systems'],
 ['Safety procedures','15%','PPE and safe handling procedures'],
 ['Dispatch and receiving','10%','Goods receipt, dispatch or loading']
],[170,55,290.276],y,size=8.0,padding=3)
y=body('<b>Proposed anchors.</b> 0 = no supporting evidence; 1 = relevant task stated; 2 = task with context or a result. Save source evidence and ratings; compute weighted totals deterministically. Clarify missing form inputs or unreadable text, then score. Exclude non-applicable criteria in the template.',y)
y=body('<b>Routing.</b> Reject failed mandatory checks or scores below threshold; schedule passing candidates. Illustrative threshold: 70. Bands: 0-49 poor, 50-69 fair, 70-85 good, 86-100 excellent. No ranking within bands. Calibrate before activation.',y)
y=body('<b>Scheduling.</b> Offer three slots; accept a choice or find alternatives. Hold, recheck and book once. Bound clarification attempts, persist replies and escalate unresolved cases by 36 hours. No response or capacity limit must not become rejection.',y)

check(y,'D2 page 1');c.showPage()
y=page_start('D2','Impact and delivery checks','Planning assumptions must be replaced with pilot measurements',2)
y=heading('Design for the distribution of demand',y)
y=body('400,000 applications / 20,000 hires = <b>20 applications per hire</b>; this is not a requisition distribution. Assume <b>p90 = 80 applications per requisition</b>. Use searchable queues, filters, bulk actions and 15-row pages. Test 500-applicant requisitions and 11,000 applications/day: a provisional 5x seasonal peak over the annual daily average, with 2x headroom. Validate all load assumptions.',y)
y=heading('Impact table',y)
y=table(['Measure','Baseline or assumption','Pilot target and validation'],[
 ['First meaningful outreach','Case median: 9 days','Every applicant attempted before 48h; p95 delivered <48h. Track all delivery failures and breach rate, not only successes.'],
 ['Screening coverage','Case: not all resumes read','100% ingested; every parse failure visible. No lost or duplicate application events.'],
 ['Scheduling effort','Estimate: 10-20 active minutes per interview','Target 70% less active coordination. Measure time to booking, attendance and panel capacity separately.'],
 ['Qualified candidates missed','Unknown; historical decisions are incomplete labels','Pilot target <=2% of independently judged qualified candidates wrongly held or excluded. Report uncertainty and lawful subgroup cuts.'],
 ['Residual human workload','Scenario: 15% remain unresolved after chat; 4 min each','60,000 escalations/year = 4,000 staff hours. Measure chat resolution and handoff rates; escalate by 36h. Assumption, not measured performance.'],
 ['AI processing cost','Scenario: $0.02-$0.10 per application','$8k-$40k/year at 400k. Budget assumption only; excludes messaging, storage, integrations, review and verification.']
],[103,159,253.276],y,size=7.9)
y=para('<b>Effort scenario.</b> If 20% reach interview, 80,000 interviews x 10-20 minutes = 13,300-26,700 coordination hours/year; a 70% reduction implies 9,300-18,700 hours released before exceptions. Screening all applications at an assumed 2-4 minutes each is another 13,300-26,700 hours of work equivalent, not a claim of current savings. Track time to fill and offer acceptance as downstream outcomes.',M,y,size=8.3,leading=11.4)+12
y=para('<b>Batch policy.</b> Start at 12 hours to compare applicants before allocating panel slots, with 36 hours left for follow-up. Tune the customer setting through experiments; preserve each applicant\'s 48 hour deadline.',M,y,size=8.3,leading=11.4)+8
y=heading('Four month build and release plan',y)
y=para('<b>Weeks 1-2:</b> PM, talent operations and local counsel agree rules, country gates, metrics and escalation owners. <b>Weeks 3-6:</b> engineering builds templates, evidence storage, chat clarification and calendar tools. <b>Weeks 7-10:</b> QA and hiring managers run shadow reviews and failure tests. <b>Weeks 11-16:</b> pilot by role/site, compare results, then expand only where gates pass.',M,y,size=8.8,leading=12)+11
y=heading('Release checks and prototype proof',y)
y=para('<b>Release checks.</b> Re-score a fixed evaluation set, including the disputed best hire; independently assess samples from every band. Test white-on-white, transparent/off-page text, OCR-layer mismatch, Unicode obfuscation, visible instructions, keyword stuffing, PII leaks and benign multilingual/layout controls; also test duplicate applications, calendar conflicts, time zones and outages. Require complete audit records, human escalation coverage, country sign-off and no unexplained quality regression. Retain a kill switch and manual fallback.',M,y,size=8.2,leading=11.0)+9
y=para('<b>Self-guided prototype.</b> Add PDF/TXT or paste a resume; inspect redacted text and per-criterion scores; run a batch; exchange simulated WhatsApp messages; book or cancel a slot; inspect recruiter metrics and stored rows. Real: local SQLite persistence, editable role templates and booking checks. Simulated: MCP calendar calls and WhatsApp delivery. Scoring uses keyword rules, not an LLM. Automatic rejection, structured clarification, production evidence anchors, OCR/hidden-text gates and enterprise approvals remain to be implemented.',M,y,size=8.2,leading=11.0)
y=para('Security reference: <link href="https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html" color="#256450">OWASP prompt injection prevention</link>. Controls above are proposed; no guarantee of complete detection.',M,y+6,size=7.2,leading=9.3)
check(y,'D2 page 2');c.save()
