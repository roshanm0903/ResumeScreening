from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path

import sys
from html import escape
sys.path.insert(0,str(Path('hiring-demo').resolve()))
from policy import CONTRACT
ANCHORS_SHORT='; '.join(str(a['rating'])+' '+a['label'] for a in CONTRACT['anchors'])
BANDS_SHORT='; '.join(b['label']+' '+escape(b['range']) for b in CONTRACT['buckets'])
OUT=Path('output/pdf'); OUT.mkdir(parents=True,exist_ok=True)
F='/System/Library/Fonts/Supplemental/'
for n,f in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]:pdfmetrics.registerFont(TTFont(n,F+f))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
W,H=595.276,841.89; M=40; CW=W-M*2
# Colors sampled from the case statement PDF.
INK=HexColor('#202020'); PRIMARY=HexColor('#014F99'); ACCENT=HexColor('#0183FF'); MUTED=HexColor('#6D6D6D'); LINE=HexColor('#E3E3E3'); PALE=HexColor('#E6F3FF'); BLUE=PRIMARY; SECONDARY_PALE=HexColor('#F0F8FF'); NODE_BORDER=HexColor('#A5CAED')
S=ParagraphStyle('body',fontName='Body',fontSize=9.4,leading=13.1,textColor=INK,spaceAfter=0)

def para(text,x,y,width=CW,size=9.4,leading=None,color=INK,bold=False):
 st=ParagraphStyle('p',parent=S,fontName='Bold' if bold else 'Body',fontSize=size,leading=leading or size*1.38,textColor=color)
 p=Paragraph(text,st);_,h=p.wrap(width,800);p.drawOn(c,x,H-y-h);return y+h

def label(text,x,y,color=PRIMARY):
 c.setFillColor(color);c.setFont('Bold',8);c.drawString(x,H-y-8,text.upper());return y+15

def heading(text,y):
 return para(text,M,y,size=12.3,bold=True)+7

def body(text,y,after=10):return para(text,M,y)+after

def footer(ref,page):
 c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(M,31,W-M,31)
 c.setFillColor(MUTED);c.setFont('Body',7);c.drawString(M,20,'Roshan Manellore  |  Darwinbox recruitment case  |  3 November 2026');c.drawRightString(W-M,20,f'{ref}  /  {page} of 2')

def page_start(ref,title,subtitle,page):
 label(ref+'  /  RECRUITMENT AT VOLUME',M,33)
 y=para(title,M,55,size=23,leading=27,bold=True)
 y=para(subtitle,M,y+7,size=9.4,color=MUTED)+20 if subtitle else y+20
 footer(ref,page);return y

def table(headers,rows,widths,y,size=8.4,padding=8):
 st=ParagraphStyle('cell',parent=S,fontSize=size,leading=size*1.32)
 sh=ParagraphStyle('head',parent=st,fontName='Bold',textColor=white,fontSize=8)
 data=[[Paragraph(h,sh) for h in headers]]+[[Paragraph(str(v),st) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLUE),('GRID',(0,0),(-1,-1),.45,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,SECONDARY_PALE])]))
 _,h=t.wrap(CW,900);t.drawOn(c,M,H-y-h);return y+h+12

def arrow(x1,y1,x2,y2,color=ACCENT):
 import math
 c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(1)
 c.line(x1,H-y1,x2,H-y2)
 a=math.atan2(y2-y1,x2-x1);r=4.5
 p=c.beginPath();p.moveTo(x2,H-y2);p.lineTo(x2-r*math.cos(a-.5),H-(y2-r*math.sin(a-.5)));p.lineTo(x2-r*math.cos(a+.5),H-(y2-r*math.sin(a+.5)));p.close();c.drawPath(p,fill=1,stroke=0)

def node(x,y,w,h,title,sub='',fill=PALE,border=NODE_BORDER):
 c.setFillColor(fill);c.setStrokeColor(border);c.roundRect(x,H-y-h,w,h,5,fill=1,stroke=1)
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
  para(v,x,y,width=col-15,size=21,leading=25,bold=True,color=PRIMARY)
  para(t,x,y+30,width=col-15,size=7.8,color=MUTED)
 return y+67

def check(y,page):
 print(page,'content ends at',round(y,1),'of 790')
 if y>790:raise ValueError('Page overflow '+page)

def decision_flow(y):
 # Mandatory checks and a calibrated score can both trigger rejection.
 w=150;gap=(CW-3*w)/2
 xs=[M,M+w+gap,M+2*(w+gap)]
 for i,(t,s) in enumerate([('Application received','Mobile form and resume'),('Parse and redact','Name excluded from scoring'),('Apply approved policy','Rule-based checks, then LLM-based<br/>scoring against the role rubric.')]):
  node(xs[i],y,w,47,t,s)
  if i<2:arrow(xs[i]+w,y+23.5,xs[i+1]-2,y+23.5)
 mid=xs[2]+w/2
 c.setStrokeColor(ACCENT);c.line(mid,H-y-47,mid,H-y-63);c.line(xs[0]+w/2,H-y-63,mid,H-y-63)
 widths=116;outgap=(CW-4*widths)/3
 outxs=[M+i*(widths+outgap) for i in range(4)]
 c.setStrokeColor(ACCENT);c.line(outxs[0]+widths/2,H-y-63,outxs[-1]+widths/2,H-y-63)
 outcomes=[('FAIL Mandatory check','Reject with rule reason','#FDECEA','#C74B45'),('FAIL Below threshold','Reject with scoring evidence','#FDECEA','#C74B45'),('HOLD Missing input','Clarify through WhatsApp','#FFF4D6','#B68418'),('PASS Screening complete','Agent checks panel calendars','#E6F4EA','#328252')]
 for i,(title,sub,fill,border) in enumerate(outcomes):
  arrow(outxs[i]+widths/2,y+63,outxs[i]+widths/2,y+75)
  node(outxs[i],y+76,widths,48,title,sub,HexColor(fill),HexColor(border))
 return y+134

def timeline(y):
 labels=[('01-02','Agree and baseline.'),('03-04','Build and integrate.'),('05-06','Shadow and evaluate.'),('07-08','Pilot and release.')]
 widths=CW/4
 for i,(w,t) in enumerate(labels):
  x=M+i*widths
  c.setFillColor(PRIMARY);c.circle(x+7,H-y-9,6,fill=1,stroke=0)
  if i<3:c.setStrokeColor(LINE);c.line(x+15,H-y-9,x+widths-3,H-y-9)
  para('WEEKS '+w,x,y+23,width=widths-12,size=7.5,bold=True,color=PRIMARY)
  para(t,x,y+38,width=widths-12,size=8.5,bold=True)
 return y+73

# D1
c=canvas.Canvas(str(OUT/'D1_Decision_Brief.pdf'),pagesize=(W,H));c.setTitle('Recruitment AI screening decision brief');c.setAuthor('Roshan Manellore')
y=page_start('D1','Recruitment screening decision brief','',1)
y=body('<b>Recommendation.</b> Automate screening and first-round booking so qualified applicants reach interviews promptly and panels spend less time on unsuitable applicants. Reject confirmed mandatory-check failures and scores below the approved role threshold. For passing candidates, the agent looks up panel calendars, finds shared availability, offers slots and books the selected time automatically. Resolve missing inputs through WhatsApp or an SMS-linked page; escalate only unresolved, contested or required interventions.',y)
y=heading('Main issues',y)
y=body('The customer receives <b>400,000 applications a year for 20,000 roles</b>. The process must address three issues:',y,5)
y=body('<b>1. Good profiles can be missed.</b> Heavy screening workloads can favor familiar brands and resume keywords over evidence of the quality of work.',y,4)
y=body('<b>2. Good candidates can be lost.</b> Delays in contacting candidates and scheduling first rounds give competing employers time to hire them.',y,4)
y=body('<b>3. Interview time is costly.</b> Screening must protect panel time by keeping unsuitable applicants out of interviews.',y,5)
y=para('Research context: Ladders reported a 7.4 second initial resume scan [1]; Cronofy found 42% had left a process over scheduling delays [2]. Validate the customer\'s screening errors and brand bias in the pilot.',M,y,size=8.3,leading=11.2)+10
y=heading('Recruiter journey',y)
y=body('Open the requisition. The role defaults job-specific requirements (salary range and expectations, visa/work authorization, shift and location) and a job-matching rubric (criteria, weights and threshold). Review and modify defaults where enterprise permissions allow, then approve the version. Add the first-round panel members; the agent reads their calendars and books interviews. Monitor scores, rejection rates, outreach and bookings; handle escalations. On role closure, stop invitations and notify remaining applicants.',y,6)
y=heading('Applicant Journey',y)
y=body('Apply on mobile, upload a resume and provide role requirements. Explicitly opt in for WhatsApp. Receive a decision or clarification within 48 hours. Use WhatsApp or an SMS link to a mobile page with the same journey: supply missing inputs, choose a slot or request alternatives, receive confirmation/reminders and reschedule. Request reasons or human review without an employee login.',y)
y=heading('Approach',y)
y=body('After deterministic checks, rate warehouse shift manager evidence: <b>'+ANCHORS_SHORT+'</b>. <b>Match score = '+CONTRACT['formula']+'</b>, rounded to two decimals. Reject below the job threshold (default '+str(CONTRACT['default_threshold'])+'; equality passes). Buckets: <b>'+BANDS_SHORT+'</b>. Use buckets only for high-volume priority; order by deadline within each.',y,4)
y=decision_flow(y)
y=body('Process applications in <b>12-hour batches by requisition</b>. At high volume, prioritize higher passing buckets, then applicants with the earliest original outreach deadline. This compares applicants before allocating scarce panel slots. Twelve hours is provisional, leaving up to 36 hours for follow-up within the <b>48-hour outreach limit</b>. Test intervals against booking quality, panel effort and SLA breaches. Preserve original deadlines. If calendars are full, keep passing applicants eligible while the agent finds alternatives.',y,0)
check(y,'D1 page 1');c.showPage()
y=page_start('D1','Launch controls and success metrics','',2)
metrics_start=y
y=heading('Success metrics and guardrails',y)
y=para('<b>North star.</b> % of qualified applicants with a confirmed first-round interview booking <b>within 5 days of application.</b>',M,y,size=9.2,leading=12.5)+3
y=para('Time to book, not just reach out: own both scheduling coverage and speed. Measure receipt to booking confirmation.',M,y,size=8,leading=10.5,color=MUTED)+9
columns=[
 ('Business',[
  '<b>1. Time to first interview scheduled.</b><br/>Days from application to confirmed booking.',
  '<b>2. Booking conversion.</b><br/>% of genuinely qualified applicants booked within a defined observation window.',
  '<b>3. Human intervention rate.</b><br/>% of applications needing manual screening or scheduling; exclude planned audits.']),
 ('Performance &amp; efficiency',[
  '<b>1. Outreach within 48 hours.</b><br/>Meaningful next step; exclude generic acknowledgements.',
  '<b>2. Applicant response rate.</b><br/>% of contacted qualified applicants responding within 12 hours.',
  '<b>3. Cost per qualified booking.</b><br/>Model, hosting, messaging and human exception costs / qualified bookings.',
  '<b>4. WhatsApp opt-in rate.</b><br/>% of applicants shown the consent prompt who explicitly opt in.']),
 ('Guardrails',[
  '<b>1. Screening quality.</b><br/>Independently audited false-negative and false-positive rates; fairness checks.',
  '<b>2. Booking reliability.</b><br/>% without duplicates, conflicts, incorrect details or system-caused changes.',
  '<b>3. Candidate experience &amp; accountability.</b><br/>Complaints, opt-outs and unresolved exceptions.'])]
gap=18;colw=(CW-gap*2)/3;column_ends=[]
for i,(title,items) in enumerate(columns):
 x=M+i*(colw+gap)
 cy=para(title,x,y,width=colw,size=9,bold=True,color=PRIMARY)+7
 for item in items:cy=para(item,x,cy,width=colw,size=8.2,leading=10.4)+1
 column_ends.append(cy)
y=max(column_ends)
for i in [1,2]:
 x=M+i*(colw+gap)-gap/2
 c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(x,H-(metrics_start+62),x,H-y+6)
metrics_height=y-metrics_start
print('Success metrics height',round(metrics_height,1),'points;',round(metrics_height/H*100,1),'percent of page')
assert metrics_height <= .25*H, 'Metrics exceed one quarter of page height'
y+=8
y=heading('Country approval and decision evidence',y)
y=body('Employment counsel and the privacy lead approve each market: <b>India</b> hiring and privacy requirements; <b>US</b> federal, state and local hiring, accessibility and automated-tool duties; <b>Germany</b> GDPR, applicable EU AI Act duties and works council involvement. Confirm notices, data handling and candidate rights before launch.',y,6)
y=body('Talent acquisition owns versioned rules and their job-related reasons. Redact names; decide further proxy controls during design. Keep evidence, policy/model/prompt versions, overrides, delivery and tool results with access and retention controls. Treat resumes as untrusted data; test injection and extraction failures.',y,10)
y=heading('Make LLM scoring robust before launch',y)
y=body('Use role-specific anchored ratings and source-linked evidence; compute the weighted total deterministically. Test scoring stability, transferable experience, resume formatting, keyword stuffing and prompt injection. Use historical binary interview/no-interview labels. Manually review both LLM disagreement types and correct the evaluation set; historical bias can persist. Version the rubric, threshold, model and prompt; revalidate changes before activation.',y,10)
y=heading('Two month launch plan',y)
y=timeline(y)
y=body('<b>Weeks 1-2:</b> agree role policy, baseline metrics and country requirements. <b>Weeks 3-4:</b> build screening and booking; integrate WhatsApp and SMS scheduling links, consent and delivery tracking. <b>Weeks 5-6:</b> shadow-test scoring, channel retries and calendar conflicts. <b>Weeks 7-8:</b> pilot selected sites and release where gates pass. Pause harmful automation and retain a manual fallback.',y,6)
y=para('<b>Post-pilot optimization.</b> Test message delivery at different local times of day to improve applicant response rates. Preserve the 48-hour outreach deadline and track five-day booking conversion alongside response rates.',M,y,size=8.6,leading=11.8)+9
y=para('[1] Ladders, 2018 eye-tracking study announcement. <link href="https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html" color="#0169cc">Source</link>. [2] Cronofy, Candidate Expectations Report 2024; 12,000 respondents in seven countries, including the US and Germany, excluding India. <link href="https://www.cronofy.com/reports/candidate-expectations-report-2024" color="#0169cc">Source</link>. Both are vendor studies; validate local behavior in the pilot.',M,y,size=7.1,leading=9.5,color=MUTED)
check(y,'D1 page 2');c.save()

# D2
def body(text,y,after=6):return para(text,M,y)+after
c=canvas.Canvas(str(OUT/'D2_Build_Sheet.pdf'),pagesize=(W,H));c.setTitle('Recruitment AI screening build sheet');c.setAuthor('Roshan Manellore')
y=page_start('D2','Recruitment screening build sheet','Workflows, enterprise data and delivery scope',1)
y=heading('Solution architecture',y)
w=150;gap=(CW-3*w)/2;xs=[M+i*(w+gap) for i in range(3)];step=50;boxh=40
# Distinct production service boundaries. Workflow is the hub; tools remain separate.
components=[
 (0,0,'Recruiter / applicant UI','Admin setup, jobs and uploads','ui'),
 (1,0,'LLM service (Gemini)','Rubrics, evidence ratings, intent','llm'),
 (2,0,'Communication service','WhatsApp / SMS / email adapters','service'),
 (0,1,'Document processing','Local text/OCR, then redaction','service'),
 (1,1,'Workflow / policy API','Rules, state, SLA and routing','service'),
 (2,1,'MCP calendar gateway','Availability, recheck and booking','service'),
 (0,2,'Queue + workers','Rubric setup, batches and retries','service'),
 (1,2,'Application / audit database','Policies, evidence, chat, bookings','data'),
 (2,2,'Enterprise panel calendars','Authorized calendar connections','external')]
def architecture_icon(kind,x,top):
 c.saveState();c.translate(x,H-top-30);c.setLineWidth(1.05)
 c.setStrokeColor(HexColor('#754CB3') if kind=='llm' else PRIMARY)
 c.setFillColor(HexColor('#EEE8FC') if kind=='llm' else PALE)
 if kind=='data':
  # Conventional database cylinder, with stacked data layers.
  c.rect(1,2,17,14,fill=1,stroke=0)
  c.line(1,2,1,16);c.line(18,2,18,16)
  c.ellipse(1,-1,18,5,fill=1,stroke=1)
  c.arc(1,5,18,11,startAng=180,extent=180)
  c.ellipse(1,13,18,19,fill=1,stroke=1)
 elif kind=='llm':
  # AI processor, using vector strokes rather than font-dependent emoji.
  c.roundRect(1,1,16,16,2,fill=0,stroke=1)
  for n in [4,8,12]:
   c.line(n,17,n,20);c.line(n,1,n,-2);c.line(1,n,-2,n);c.line(17,n,20,n)
  c.setFillColor(HexColor('#754CB3'));c.setFont('Bold',6);c.drawCentredString(9,6.8,'AI')
 elif kind=='ui':
  # Two people denote the recruiter/admin and applicant surfaces.
  c.circle(5,14,3,fill=0,stroke=1);c.circle(14,14,2.7,fill=0,stroke=1)
  path=c.beginPath();path.moveTo(0,2);path.lineTo(0,5);path.curveTo(0,10,10,10,10,5);path.lineTo(10,2);c.drawPath(path)
  path=c.beginPath();path.moveTo(11,8);path.curveTo(16,10,19,7,19,4);path.lineTo(19,2);c.drawPath(path)
 c.restoreState()

def architecture_node(x,top,title,sub,kind):
 if kind not in ['ui','llm','data']:
  node(x,top,w,boxh,title,sub);return
 fill=HexColor('#EEE8FC') if kind=='llm' else PALE
 border=HexColor('#B9A2DB') if kind=='llm' else NODE_BORDER
 c.setFillColor(fill);c.setStrokeColor(border);c.roundRect(x,H-top-boxh,w,boxh,5,fill=1,stroke=1)
 architecture_icon(kind,x+8,top)
 tw=w-38
 st=ParagraphStyle('arch-title',parent=S,fontName='Bold',fontSize=8.1,leading=10.3,alignment=TA_CENTER)
 title_p=Paragraph(title,st);_,th=title_p.wrap(tw,100)
 sub_p=Paragraph(sub,ParagraphStyle('arch-sub',parent=S,fontSize=7.3,leading=9.2,alignment=TA_CENTER,textColor=MUTED));_,sh=sub_p.wrap(tw,100)
 if th+sh>23:raise ValueError('Architecture label wraps too far: '+title)
 title_p.drawOn(c,x+31,H-top-9-th);sub_p.drawOn(c,x+31,H-top-boxh+8)

for col,row,title,sub,kind in components:
 architecture_node(xs[col],y+row*step,title,sub,kind)
def bi(x1,y1,x2,y2):
 arrow(x1,y1,x2,y2);arrow(x2,y2,x1,y1)
# UI requests; document ingestion; model calls; messaging webhooks/delivery; tools; storage.
bi(xs[0]+w,y+20,xs[1],y+step+10)
arrow(xs[0]+75,y+boxh,xs[0]+75,y+step)
arrow(xs[0]+w,y+step+20,xs[1],y+step+20)
bi(xs[1]+75,y+boxh,xs[1]+75,y+step)
bi(xs[1]+w,y+step+10,xs[2],y+20)
bi(xs[1]+w,y+step+20,xs[2],y+step+20)
bi(xs[1],y+step+30,xs[0]+w,y+step*2+20)
bi(xs[1]+75,y+step+boxh,xs[1]+75,y+step*2)
bi(xs[2]+75,y+step+boxh,xs[2]+75,y+step*2)
y+=step*2+boxh+5
y=para('Production components; arrows show calls and returned data. Demo: SQLite + Gemini; messaging/calendar adapters simulated.',M,y,size=7.4,leading=10)+7

def workflow_row(items,y):
 width=118;gap=(CW-4*width)/3
 for i,(title,sub,kind) in enumerate(items):
  x=M+i*(width+gap)
  node(x,y,width,40,title,sub,HexColor('#EEE8FC') if kind=='llm' else PALE,HexColor('#B9A2DB') if kind=='llm' else NODE_BORDER)
  if i<3:arrow(x+width,y+23,x+width+gap-2,y+23)
 return y+49

y=heading('1. Screening workflow',y)
y=workflow_row([('Parse and redact','Resume + application answers','data'),('Deterministic checks','Application form input','rule'),('Build prompt + LLM','0/1/2 definitions + resume','llm'),('Calculate Match score','Validated ratings + policy','rule')],y)
y=para('<b>Ingestion:</b> extract text locally; OCR scans before inference. Send normalized text, <b>not full PDF/images</b>, to reduce model costs. <b>Redact name and location</b>; legal/privacy checks determine further masking (e.g. education institute), retaining relevant qualifications. Unreadable inputs/model errors pause scoring. <b>Prototype:</b> name/contact masking exists; OCR and location/institute masking remain to build.',M,y,size=8.4,leading=11.4)+7
y=para('<b>LLM output - illustrative, one of six criteria:</b> {"ratings": [{"key": "leadership", "rating": 2, "quotes": ["Led 24 associates across two shifts"], "rationale": "Direct evidence of shift team leadership."}]}<br/>Code compiles editable 0/1/2 definitions into a fixed prompt/schema, validates output and computes Match score. Store ratings, evidence, rationale and policy/model/prompt versions.',M,y,size=8.1,leading=10.8)+6
y=heading('2. WhatsApp conversation workflow',y)
y=workflow_row([('Receive message','Application ID + opt-in + reply','data'),('Rules / LLM intent','Validate against stored state','llm'),('Fetch / update data','Application or panel tools','data'),('Reply and persist','Buttons, slot list, confirmation','rule')],y)
y=para('<b>SMS links to a mobile page with the WhatsApp scheduling experience</b>; reuse state, routing, tools and storage. Rules handle buttons; Gemini handles free text, validated against state. Re-screen missing answers. Fetch shared slots; exclude prior offers/bookings. Recheck and book/replace atomically, keeping the original until confirmed. Log results; escalate by 36h. <b>SMS page not prototyped.</b>',M,y,size=8.4,leading=11.4)+10
y=heading('Warehouse shift manager role scoring rubric',y)
y=para('Shift manager defaults: 3+ years preferred, not a hard gate. Demo gates: shift/site/start; salary/visa checks planned.',M,y,size=8.5,leading=11.5)+7
y=table(['Scoring parameter','Weight','Evidence assessed semantically'],[[escape(cr['label']),str(cr['weight'])+'%',escape(cr['evidence'])] for cr in CONTRACT['warehouse_criteria']],[170,55,290.276],y,size=8.1,padding=2)
y=para('<b>Ratings:</b> '+ANCHORS_SHORT+'. Use criterion anchors; impact requires measurable results. <b>Match score = '+CONTRACT['formula']+'</b>; round to two decimals. Threshold (default): '+str(CONTRACT['default_threshold'])+'; below rejects, equality passes. <b>Buckets:</b> '+BANDS_SHORT+'. At '+str(CONTRACT['high_volume_trigger'])+' eligible applicants/role/batch (provisional), prioritize buckets then deadlines; otherwise deadlines only. Never rank scores within buckets.',M,y,size=8.1,leading=11)
check(y,'D2 page 1');c.showPage()
y=page_start('D2','Impact and delivery checks','Planning assumptions must be replaced with pilot measurements',2)
y-=10
y=heading('Design for the distribution of demand',y)-4
y=body('400k applications / 20k hires = <b>20 per hire</b>. Assume <b>p90 = 80 applications/requisition</b>; use search, filters, bulk actions and 15-row pages. Load-test 500-applicant roles and 11k/day (5x average, 2x headroom). Validate assumptions.',y)
y=heading('Impact table',y)-4
y=table(['Measure','Baseline or assumption','Pilot target and validation'],[
 ['First meaningful outreach','Case median: 9 days','Attempt outreach before 48h; p95 delivered <48h. Track failures and breaches.'],
 ['Screening coverage','Case: not all resumes read','100% ingested; visible parse failures; no lost/duplicate application events.'],
 ['Scheduling effort','Estimate: 10-20 active minutes per interview','70% less coordination; track booking time, attendance and capacity separately.'],
 ['Qualified candidates missed','Unknown; historical decisions are incomplete labels','<=2% FNR on reviewed interview labels; report uncertainty and fairness checks.'],
 ['Residual human workload','Scenario: 15% remain unresolved after chat; 4 min each','60k escalations = 4k staff hours/year; measure handoffs. Escalate by 36h. Unvalidated.'],
 ['AI processing cost','Scenario: $0.02-$0.10 per application','$8k-$40k/year at 400k. Excludes messaging, storage, integrations and review; unvalidated.']
],[103,159,253.276],y,size=7.9,padding=2)
y-=8
y=para('<b>Model alternative (not selected for MVP).</b> Models such as <link href="https://typesafe.ai/blog/introducing-system-one-models-and-jev" color="#0169cc">TypeSafe Jev</link> could lower costs with typed scores/decisions. <b>We prioritize explainability over cost:</b> ratings need rationale and resume evidence; score-only models need an extra evidence layer.',M,y,size=8.4,leading=11.4)+8
y=heading('System administrator journey',y)-4
y=para('<b>One-time setup:</b> toggle feature opt-in; select channels (WhatsApp, SMS, email); connect an enterprise email account for panel-calendar access. Choose enterprise-managed role rubrics or job-level rubrics, and whether hiring managers may override the rubric. Reuse existing jobs and JDs. <b>The detailed administrator experience is not covered in this design.</b>',M,y,size=8.6,leading=11.8)+2
y=para('<b>Asynchronous provisioning:</b> enabling the feature enqueues all existing jobs. Background workers use JDs and enterprise settings to generate thousands of role/job rubrics, validate and store versions, and track per-job readiness. Show progress and retry failed jobs; scoring starts for each job when its rubric is ready. Enterprise mode controls role rubrics; job mode attaches them to jobs. Version permitted overrides.',M,y,size=8.6,leading=11.8)+2

y=heading('Two month build and release plan',y)-4
y=para('<b>Weeks 1-2:</b> PM, talent operations and local counsel agree rules, country gates and metrics. <b>Weeks 3-4:</b> build admin settings, async rubric provisioning, scoring and booking; integrate WhatsApp and SMS scheduling links, consent and delivery tracking. <b>Weeks 5-6:</b> shadow-test scoring, channel retries and calendar conflicts. <b>Weeks 7-8:</b> pilot selected sites and release where gates pass.',M,y,size=8.8,leading=12)+3
y=heading('Release checks',y)-4
y=para('<b>Historical quality gate.</b> Use historical binary <b>send for interview / do not send</b> labels, not per-score labels. History can carry bias; non-hires do not prove poor fit. Manually review both disagreements: <b>apparent false positives</b> (LLM passes, no historical interview) and <b>apparent false negatives</b> (LLM rejects, historical interview). Correct labels and version the evaluation set, then re-evaluate. <b>FNR = rejected interview-positive cases / all interview-positive cases</b>, using reviewed labels. Provisional: <b>FNR &lt;=2%; true-positive rate &gt;=98%</b>. Review disagreements, not every score.',M,y,size=8.6,leading=11.8)+3
y=para('<b>Scheduling constraint (not prototyped).</b> Intersect free/busy with each panel member\'s local working hours, using IANA time zones and daylight-saving rules; compare in UTC. DB fields are prepared. <b>Checks:</b> extraction/injection, duplicates, conflicts, outages and closure; require audit, escalation, country sign-off, kill switch and manual fallback.',M,y,size=8.6,leading=11.8)+4
y=heading('LLM pitfalls and controls',y)-4
y=para('<b>1. Resume prompt injection.</b> Isolate untrusted text; constrain outputs; test hidden instructions.<br/><b>2. Non-linear careers.</b> Assess transferable work, not career gaps or conventional job titles.<br/><b>3. Brand/jargon bias.</b> Redact agreed proxies; test niche vocabulary and equivalent experience.<br/><b>4. Complex PDF layouts.</b> Check text/OCR reading order; failed extraction pauses scoring.<br/><b>5. AI-tailored resumes.</b> Require concrete work evidence, not JD similarity; claims remain unverified.',M,y,size=8.4,leading=11.4)+4

y=para('<b>Evaluation coverage.</b> Prepare evaluation data for all five scenarios above. Test each and iteratively refine the prompt until agreed quality and robustness thresholds are met.',M,y,size=8.4,leading=11.4)+4

y=para('<b>Demo:</b> Live Gemini and saved scores/bookings; calendar access and WhatsApp delivery are simulated.',M,y+2,size=8,leading=10.5)
check(y,'D2 page 2');c.save()
