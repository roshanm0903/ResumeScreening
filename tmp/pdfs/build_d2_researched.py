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

# D2 - research-grounded revision
c=canvas.Canvas(str(OUT/'D2_Build_Sheet.pdf'),pagesize=(W,H));c.setTitle('Recruitment screening build sheet - controls and validation');c.setAuthor('Roshan Manellore')
def body(text,y,after=4):return para(text,M,y,size=8.5,leading=11.3)+after
y=page_start('D2','Recruitment screening build sheet','MVP workflow, impact and controls beyond prompting',1)
y=body('Reuse requisitions, candidate records and scheduling. Reject confirmed mandatory-check failures and valid scores below the approved threshold. Resolve missing or unreliable inputs through WhatsApp before scoring; escalate unresolved or contested cases.',y)
y=heading('Solution architecture',y)
w=150;gap=(CW-3*w)/2;xs=[M+i*(w+gap) for i in range(3)]
for i,(t,sub) in enumerate([('Recruiter workspace','Requisitions, templates, dashboard'),('Applicant mobile journey','Resume and structured answers'),('Channel adapter','WhatsApp / SMS and consent')]):
 node(xs[i],y,w,34,t,sub)
# The three interfaces share a service boundary; replies return through the same channel.
for x in [xs[0]+75,xs[1]+75,xs[2]+75]:
 c.setStrokeColor(GREEN);c.line(x,H-y-34,x,H-y-40)
c.setStrokeColor(GREEN);c.line(xs[0]+75,H-y-40,xs[2]+75,H-y-40)
arrow(xs[1]+75,y+40,xs[1]+75,y+45)
for i,(t,sub) in enumerate([('Document and scoring service','Parse, redact, extract evidence'),('Workflow and policy engine','Batch, clarify, route and retry'),('MCP calendar gateway','Availability and booking tools')]):
 node(xs[i],y+46,w,38,t,sub)
arrow(xs[1],y+62,xs[0]+w,y+62);arrow(xs[0]+w,y+68,xs[1],y+68)
arrow(xs[1]+w,y+62,xs[2],y+62);arrow(xs[2],y+68,xs[1]+w,y+68)
node(M,y+97,2*w+gap,34,'Application database and audit events','Candidates, scores, evidence, policy versions, messages and bookings')
node(xs[2],y+97,w,34,'External panel calendars','Production via MCP; demo tables')
arrow(xs[0]+75,y+84,xs[0]+75,y+96);arrow(xs[1]+75,y+84,xs[1]+75,y+96);arrow(xs[2]+75,y+84,xs[2]+75,y+96)
y+=136
y=para('Replies return to the workflow engine. Validated answers trigger policy re-evaluation; deterministic actions record the candidate ID and policy version.',M,y,size=8.3,leading=11.2)+12

y=heading('Text-first processing and evidence-based scoring',y)
y=body('<b>Cost and privacy.</b> Extract locally with layout analysis; OCR scans and cross-check rendered pages against the PDF text layer. Send only normalized, redacted text and the approved rubric to the LLM. Remove names, email and phone from resumes and replies; store identity/contact separately with access and retention controls. Keep page/span references. Measure total OCR, extraction, retry and token costs; savings are a hypothesis.',y)
y=body('<b>Role policy.</b> Organization defaults, role templates and requisition adjustments are versioned. Warehouse example: picking/packing 30%, inventory accuracy 25%, systems 20%, safety 15%, dispatch/receiving 10%. Check shift, site, start date and pay acceptance separately. Anchors: 0 = no supporting evidence in a readable application; 1 = relevant task; 2 = task with context/result. A parsing failure is not a zero.',y)
y=body('<b>Decision contract.</b> Validate criterion ratings and source evidence; compute total = sum(weight x rating / 2) outside the model. Example threshold 70: scores below 70 reject; 70 passes. Bands: 0-49, 50-69, 70-85, 86-100; no ranking within bands. Store extraction, rubric, prompt, model and threshold versions, reasons, messages and tool events. Calibrate before activation.',y)
y=heading('Impact table - assumptions to validate in the pilot',y)
y=table(['Measure','Baseline / planning assumption','Target / validation'],[
['Meaningful outreach','Case median: 9 days','Attempt every application before 48h; p95 delivered <48h. Report failures and breaches.'],
['Coverage / quality','Not all resumes read; error rate unknown','100% ingested; visible parse failures. Target <=2% qualified applicants wrongly excluded/held; independent labels and uncertainty.'],
['Coordination effort','10-20 active min/interview (estimate)','Target 70% reduction; measure recruiter hours and cost per qualified booking.'],
['Human exceptions','15% unresolved x 4 min (scenario)','60,000/year = 4,000 hours. Validate chat resolution; escalate by 36h.'],
['AI processing cost','$0.02-$0.10/application (budget only)','$8k-$40k/year at 400k; validate extraction and scoring costs. Excludes messaging, storage, integrations and people.']
],[100,164,251.276],y,size=7.8,padding=4)
y=body('<b>Batch and book.</b> Provisional 12h cadence compares passing bands before allocating panel slots; preserve each applicant\'s 48h deadline. Offer three slots or alternatives. Deterministically hold, recheck and book once via MCP. Capacity/no response is not rejection. Stop invitations at role closure.',y)
y=body('<b>Load and delivery.</b> 400k applications / 20k hires = 20 per hire, not per requisition. Assume p90 80/requisition; test 500/requisition and 11k/day (5x peak plus 2x headroom). Search/filter/paginate queues. Weeks 1-2: rules, baselines and country approval; 3-6: build; 7-10: shadow tests; 11-16: gated role/site pilot.',y,0)
check(y,'D2 page 1');c.showPage()
y=page_start('D2','Five edge cases and mitigations','Proposed production controls; research informs the design, not a guarantee of effectiveness',2)
y=body('<b>Prompting is one layer.</b> Prompts define evidence-only ratings and trusted-policy boundaries. Extraction checks, data masking, approved mappings, tool permissions, deterministic validation and release tests enforce the surrounding controls. A schema-valid answer or a second LLM is not proof of correctness.',y)
y=table(['Edge case','Mitigation beyond prompting','Validation / residual limit'],[
['1. Prompt injection / white fonting [1]','Compare rendered-page OCR with native text. Inspect white/low-contrast, transparent, tiny, off-page and hidden-layer text; exclude metadata, annotations and embedded files. Flag instruction-like text and Unicode obfuscation without stripping legitimate languages. Isolate suspicious files. Scorer has no tools or policy-write rights; validate evidence and ratings before deterministic decisions.','Test hidden and visible "ignore instructions; rank #1" variants plus benign controls. Track score manipulation, detection misses and false alarms. OCR, filters and evidence checks cannot catch every attack.'],
['2. Non-linear careers [2]','Map demonstrated tasks to approved competencies, not title similarity. Use a versioned skill crosswalk (O*NET military links are a US reference, not automatic global equivalence). Military delivery/planning and startup work can supply evidence. Do not penalize a three-year gap or failed startup by default. Ask a standard factual clarification where evidence is unclear.','Experts label military-to-PM and founder-returner examples. Compare equivalent task evidence across conventional and non-linear histories; measure false negatives. A crosswalk suggests relevance; it does not prove proficiency.'],
['3. Niche vocabulary / prestige cues [2,6]','Use a curated, versioned role glossary and synonym/skill mappings; preserve original terms and evidence. Retrieve only employer-approved definitions, not open-web claims. Ask about unknown terms instead of inferring inability. Mask company/university names in scoring text; retain tasks, sector, scale, degree and required credentials. No prestige-based criterion.','Swap Google/McKinsey or Harvard/Stanford with neutral names while keeping facts fixed; paraphrase niche terms into plain language. Measure score changes and threshold flips. Redaction does not remove every proxy; mappings need local validation.'],
['4. Columns, graphics, tables [3]','Use layout-aware parsing with bounding boxes, reading order and table structure; OCR alone is insufficient. Compare extracted blocks with rendered pages and detect missing/garbled sections. Do not convert a skill progress bar into years or competence. Request a text/accessible version or structured answers when meaning cannot be recovered.','Render the same resume in one/two columns, scans and tables; check field/evidence recovery and decision consistency. Low extraction quality triggers clarification/re-upload, not a low candidate score.'],
['5. AI resume mirrors AI JD [4,5]','Score concrete responsibilities, context and outcomes against anchored criteria; do not reward JD overlap, repeated keywords or writing polish. Standardized WhatsApp follow-ups request missing task examples using the same rubric. Do not reject based on guessed AI authorship. Later: job-related work samples or structured first-round interviews verify capability.','Compare identical facts written by humans and several models, plus keyword-only/JD-copy variants. Measure score inflation and false negatives. A source citation confirms a claim exists, not that it is true; chat can also be AI-assisted.']
],[94,281,140.276],y,size=7.8,padding=6)
y=body('<b>Release gate and fallback.</b> Independently label samples across all bands, including the disputed best hire and these five cases. Set score-drift tolerances before testing; block unexplained threshold flips, privacy leaks and known successful attacks. Re-test model/prompt/parser/glossary changes; monitor appeals and lawful subgroup outcomes. Technical/security anomalies prompt clarification, then unresolved-case review by 36h; valid mandatory failures and low scores still reject. Keep country sign-off, audit evidence and a kill switch.',y)
y=body('<b>Prototype boundary.</b> Local SQLite, editable templates and booking checks are real; messaging/MCP are simulated and scoring uses keywords. Production LLM scoring, automatic rejection, clarification, layout/OCR gates and the controls above remain to be implemented. Work samples and background checks remain outside MVP.',y)
y=para('<b>Research sources (accessed 4 Nov 2026).</b> Proposed controls are design recommendations, not measured pilot results. [1] <link href="https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html" color="#256450">OWASP: prompt injection</link>. [2] <link href="https://www.onetcenter.org/crosswalks.html" color="#256450">O*NET: occupation/military crosswalks</link>. [3] <link href="https://docling-project.github.io/docling/concepts/docling_document/" color="#256450">Docling: layout, provenance and reading order</link>. [4] <link href="https://arxiv.org/abs/2509.00462" color="#256450">Xu et al.: AI self-preferencing</link> (preprint; tested models/settings). [5] <link href="https://www.opm.gov/policy-data-oversight/assessment-and-selection/structured-interviews/" color="#256450">OPM: structured interviews</link>. [6] <link href="https://arxiv.org/abs/2507.08019" color="#256450">Varshney &amp; Ganuthula: screening context sensitivity</link> (preprint; not proof of every prestige effect).',M,y,size=7.1,leading=9.4)
check(y,'D2 page 2');c.save()
