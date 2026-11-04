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

