#!/usr/bin/env python3
"""JalaPath proposal builder (ReportLab). Edit the CONTENT blocks and re-run:
    python3 build_proposal.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, Flowable, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents

F = "/usr/share/fonts/truetype/crosextra/Carlito-"
pdfmetrics.registerFont(TTFont("B", F + "Regular.ttf"))
pdfmetrics.registerFont(TTFont("B-Bold", F + "Bold.ttf"))
pdfmetrics.registerFont(TTFont("B-It", F + "Italic.ttf"))
pdfmetrics.registerFont(TTFont("B-BI", F + "BoldItalic.ttf"))
pdfmetrics.registerFontFamily("B", normal="B", bold="B-Bold", italic="B-It", boldItalic="B-BI")

NAVY = colors.HexColor("#0B2545"); TEAL = colors.HexColor("#0E8C86")
TINT = colors.HexColor("#E8F5F4"); GREY = colors.HexColor("#333333")
LINE = colors.HexColor("#C5D3DF"); GREEN = colors.HexColor("#1B7F4B")
AMBER = colors.HexColor("#F2B01E"); RED = colors.HexColor("#B3261E")

body = ParagraphStyle("body", fontName="B", fontSize=8.8, leading=11.4, textColor=GREY, spaceAfter=3.5)
small = ParagraphStyle("small", parent=body, fontSize=7.9, leading=9.8, spaceAfter=0)
smallb = ParagraphStyle("smallb", parent=small, fontName="B-Bold")
smallw = ParagraphStyle("smallw", parent=small, fontName="B-Bold", textColor=colors.white)
h1 = ParagraphStyle("h1", fontName="B-Bold", fontSize=12.5, leading=15, textColor=NAVY,
                    spaceBefore=7, spaceAfter=3, keepWithNext=1)
bul = ParagraphStyle("bul", parent=body, leftIndent=10, bulletIndent=1, spaceAfter=1.5)
ref = ParagraphStyle("ref", parent=small, fontSize=7.3, leading=8.8, leftIndent=12, firstLineIndent=-12, spaceAfter=1.2)


def P(t, s=body): return Paragraph(t, s)
def B(items): return [Paragraph(i, bul, bulletText="\u2022") for i in items]
def H(t): return Paragraph(t, h1)


def table(data, widths, hdr=True, fs=small):
    rows = [[c if not isinstance(c, str) else Paragraph(c, smallw if (hdr and i == 0) else fs)
             for c in r] for i, r in enumerate(data)]
    t = Table(rows, colWidths=widths, repeatRows=1 if hdr else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, LINE),
          ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
          ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5)]
    if hdr:
        st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for i in range(1 if hdr else 0, len(rows)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), TINT))
    t.setStyle(TableStyle(st))
    return t


def note(text):
    t = Table([[Paragraph(text, small)]], colWidths=[17.4 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT), ("LINEBEFORE", (0, 0), (0, -1), 3, TEAL),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


# ---------- diagrams ----------
class Diagram(Flowable):
    def __init__(self, w, h, fn):
        super().__init__(); self.w, self.h, self.fn = w, h, fn
    def wrap(self, aw, ah): return self.w, self.h
    def draw(self): self.fn(self.canv)


def box(c, x, y, w, h, lines, fill=colors.white, stroke=NAVY, tc=NAVY, fs=7.4, bold_first=True, dash=False):
    c.saveState(); c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.9)
    if dash: c.setDash(3, 2)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1); c.restoreState()
    n = len(lines); lh = fs + 1.8; y0 = y + h / 2 + (n - 1) * lh / 2 - fs * 0.33
    for i, ln in enumerate(lines):
        c.setFillColor(tc); c.setFont("B-Bold" if (i == 0 and bold_first) else "B", fs)
        c.drawCentredString(x + w / 2, y0 - i * lh, ln)


def arrow(c, x1, y1, x2, y2, label=None, lx=0, ly=3):
    import math
    c.saveState(); c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.setLineWidth(1.3)
    c.line(x1, y1, x2, y2)
    a = math.atan2(y2 - y1, x2 - x1); s = 5
    p = c.beginPath(); p.moveTo(x2, y2)
    p.lineTo(x2 - s * math.cos(a - .4), y2 - s * math.sin(a - .4))
    p.lineTo(x2 - s * math.cos(a + .4), y2 - s * math.sin(a + .4)); p.close()
    c.drawPath(p, fill=1, stroke=0)
    if label:
        c.setFont("B-It", 6.8); c.setFillColor(GREY)
        c.drawCentredString((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label)
    c.restoreState()


def group(c, x, y, w, h, title):
    c.saveState(); c.setStrokeColor(LINE); c.setFillColor(colors.HexColor("#F6F9FC")); c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    c.setFillColor(TEAL); c.setFont("B-Bold", 7.6); c.drawString(x + 6, y + h - 11, title); c.restoreState()


def arch(c):
    u = cm
    group(c, 0, 0, 5.4*u, 6.4*u, "FIELD  (at the crossing)")
    box(c, .3*u, 4.0*u, 4.8*u, 1.4*u, ["JSN-SR04T probe", "waterproof ultrasonic sensor", "(distance to water surface)"])
    box(c, .3*u, 1.7*u, 4.8*u, 1.5*u, ["ESP32 DevKit", "median of 9 pings", "depth = baseline - distance"], fill=TINT)
    box(c, .3*u, .35*u, 4.8*u, .8*u, ["USB power bank / 5 V adapter"], bold_first=False, fs=7)
    arrow(c, 2.7*u, 4.0*u, 2.7*u, 3.2*u, "TRIG / ECHO", lx=30, ly=-1)
    group(c, 6.3*u, 0, 4.9*u, 6.4*u, "CLOUD  (free tier)")
    box(c, 6.6*u, 4.1*u, 4.3*u, 1.3*u, ["Firebase Realtime DB", "REST write by node, live read by app"], fs=7)
    box(c, 6.6*u, 2.9*u, 4.3*u, .85*u, ["/nodes: name, lat/lon, baseline"], bold_first=False, fs=7, fill=TINT)
    box(c, 6.6*u, 1.8*u, 4.3*u, .85*u, ["/readings: depth, time, health"], bold_first=False, fs=7, fill=TINT)
    box(c, 6.6*u, .7*u, 4.3*u, .85*u, ["/reports: community (optional)"], bold_first=False, fs=7, fill=TINT, dash=True)
    group(c, 12.2*u, 0, 5.2*u, 6.4*u, "USERS")
    box(c, 12.5*u, 3.9*u, 4.6*u, 1.5*u, ["JalaPath web app (PWA)", "map + profile selector", "decision engine (JS), EN / Tamil, audio"], fill=TINT, fs=7)
    box(c, 12.5*u, 2.3*u, 4.6*u, .9*u, ["QR sign at the crossing -> opens its page"], bold_first=False, fs=7)
    box(c, 12.5*u, .5*u, 4.6*u, .9*u, ["Simulator mode (demo data, labelled)"], bold_first=False, fs=7, dash=True)
    arrow(c, 5.1*u, 2.45*u, 6.6*u, 4.45*u)
    c.setFont("B-It", 6.8); c.setFillColor(GREY); c.drawString(4.55*u, 3.55*u, "HTTPS")
    c.drawString(4.55*u, 3.3*u, "(Wi-Fi)")
    arrow(c, 10.9*u, 4.75*u, 12.5*u, 4.75*u, "live read", ly=3)
    arrow(c, 12.5*u, 4.15*u, 10.9*u, 3.3*u)
    c.setFont("B-It", 6.8); c.drawString(11.15*u, 3.85*u, "reports")
    arrow(c, 14.8*u, 3.2*u, 14.8*u, 3.9*u)


def flow(c):
    u = cm; w = 3.1*u; gap = .475*u; h = 1.15*u
    xs = [i * (w + gap) for i in range(5)]
    c.setFillColor(TEAL); c.setFont("B-Bold", 7.6)
    c.drawString(0, 6.95*u, "NODE LANE  (repeats every 30 s)")
    c.drawString(0, 2.3*u, "APP LANE  (on each visit)")
    top = 5.3*u
    n = [["1. Wake, join Wi-Fi"], ["2. 9 pings", "take the median"], ["3. depth = baseline", "- median distance"],
         ["4. Valid reading?", "20-600 cm, no spike"], ["5. POST depth, time,", "health to database"]]
    for i, t in enumerate(n):
        box(c, xs[i], top, w, h, t, fill=TINT if i != 3 else colors.white, bold_first=True, fs=7.2, dash=(i == 3))
        if i: arrow(c, xs[i-1]+w, top+h/2, xs[i], top+h/2)
    c.setFont("B-It", 6.8); c.setFillColor(RED)
    c.drawString(xs[3]+.2*u, top-.35*u, "No: health = FAULT, last good value kept")
    box(c, xs[1], 3.15*u, 4*w+3*gap, .9*u, ["Firebase Realtime Database  (latest reading + 10-minute history)"], fill=NAVY, tc=colors.white, fs=7.6, bold_first=False)
    arrow(c, xs[4]+w/2, top, xs[4]+w/2, 4.05*u)
    low = .35*u
    a = [["6. Open QR link", "or app"], ["7. Choose profile", "(4 options)"], ["8. Fresh? age <= 5 min", "and health OK"],
         ["9. Compare with profile", "thresholds + rising rule"], ["10. Show colour + icon", "+ text + audio"]]
    for i, t in enumerate(a):
        box(c, xs[i], low, w, h, t, fill=TINT if i != 2 else colors.white, fs=7.2, dash=(i == 2))
        if i: arrow(c, xs[i-1]+w, low+h/2, xs[i], low+h/2)
    arrow(c, xs[1]+w/2, 3.15*u, xs[1]+w/2, low+h, "read latest", lx=28, ly=-2)
    c.setFont("B-It", 6.8); c.setFillColor(RED)
    c.drawString(xs[2]+.2*u, low+h+.18*u, "No: UNKNOWN, treat as unsafe (never Go)")


# ---------- page furniture ----------
def furniture(c, d):
    if d.page == 1: return
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, A4[1]-.55*cm, A4[0], .55*cm, fill=1, stroke=0)
    c.setFillColor(TEAL); c.rect(0, A4[1]-.62*cm, A4[0], .07*cm, fill=1, stroke=0)
    c.setFont("B", 7.5); c.setFillColor(GREY)
    c.drawString(1.8*cm, .85*cm, "JalaPath | Project Proposal | Varshini B, Vaishnavi V, Gopika T | Sri Sairam Engineering College")
    c.drawRightString(A4[0]-1.8*cm, .85*cm, "Page %d" % d.page)
    c.setStrokeColor(LINE); c.line(1.8*cm, 1.2*cm, A4[0]-1.8*cm, 1.2*cm); c.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, fn):
        super().__init__(fn, pagesize=A4, leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.3*cm, bottomMargin=1.5*cm,
                         title="JalaPath - Project Proposal", author="Varshini B, Vaishnavi V, Gopika T",
                         subject="Flood-crossing guidance for Chennai (proposal; prototype not yet built)")
        self.addPageTemplates([PageTemplate(id="p", frames=[Frame(1.8*cm, 1.5*cm, 17.4*cm, A4[1]-2.8*cm, 0, 0, 0, 0)], onPage=furniture)])
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name == "h1":
            self.notify("TOCEntry", (0, f.getPlainText(), self.page))


# ---------- content ----------
ABSTRACT = ("Chennai's monsoon floods turn underpasses and low streets into hazards that are hard to judge by eye. "
            "During Cyclone Michaung in December 2023, at least 17 subways were closed and many residents could not reach relief centres [2]. "
            "Official forecasting systems and a citizen depth-reporting portal now exist [5][6], but a person standing at a flooded crossing "
            "still has to guess whether it is safe for them in particular: a walking adult, a wheelchair or walker user, a two-wheeler rider or a driver. "
            "<b>JalaPath</b> is a low-cost, open-source flood-crossing guide. A waterproof ultrasonic sensor on an ESP32 board measures water depth at one crossing "
            "and uploads it to a free cloud database. A web app turns depth into a plain verdict (Go, Caution, Avoid or Unknown) for each user profile, "
            "in English and Tamil, with large text, high contrast and audio. A fail-safe rule never shows Go when data is old or missing. "
            "A QR sign at the crossing opens the page with no app install. The prototype is planned at about \u20b91,470 and will be demonstrated with a water tub and a simulator. "
            "All thresholds are initial values that must be validated.")

story = []
# cover
story += [Spacer(1, 1.2*cm), P("<font color='#0E8C86'><b>PROJECT PROPOSAL</b></font>", ParagraphStyle("k", parent=body, fontSize=10)),
          P("<font size=44 color='#0B2545'><b>JalaPath</b></font>", ParagraphStyle("t", parent=body, fontSize=44, leading=50)),
          Table([[""]], colWidths=[6*cm], rowHeights=[3], style=[("BACKGROUND", (0, 0), (-1, -1), TEAL)]), Spacer(1, 6),
          P("<font size=13 color='#0B2545'>Flood depth, translated into a clear answer to one question: "
            "<i>can I cross this street, for my own mobility?</i></font>", ParagraphStyle("tag", parent=body, fontSize=13, leading=17)),
          Spacer(1, .7*cm)]
meta = [["Prepared for", "MY Bharat \u2013 Hack for Social Cause (VBYLD 2027); primary theme: Disaster Mitigation &amp; Resilience. Secondary: Assistive Technology &amp; Accessibility, Governance &amp; Civic Technology. [1]"],
        ["Team", "<b>Varshini B</b><br/><b>Vaishnavi V</b><br/><b>Gopika T</b>"],
        ["Institution", "Sri Sairam Engineering College, Chennai, Tamil Nadu"],
        ["Status", "Concept proposal and prototype plan, dated 27 October 2026. No prototype has been built, tested or deployed yet. Not endorsed or approved by MY Bharat."]]
mt = Table([[P("<b>%s</b>" % a, small), P(b, ParagraphStyle("m", parent=body, fontSize=9.3, leading=12))] for a, b in meta], colWidths=[3*cm, 14.4*cm])
mt.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), .4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
story += [mt, Spacer(1, .8*cm), P("<font color='#0B2545'><b>Contents</b></font>", ParagraphStyle("c", parent=body, fontSize=11))]
toc = TableOfContents(); toc.levelStyles = [ParagraphStyle("t0", parent=body, fontSize=9, leading=12.5, leftIndent=0)]
toc.dotsMinLevel = 0
story += [toc, PageBreak()]

# 1 abstract
story += [H("1. Abstract"), P(ABSTRACT)]
# 2 background
story += [H("2. Background and problem"),
          P("Michaung dropped over 40 cm of rain on Chennai in 36 hours; at least 17 subways were closed and arterial roads were flooded [2]. "
            "Early reports noted at least five deaths, including a 70-year-old man electrocuted while walking on a Chennai road [3]. "
            "The US National Weather Service warns that it is impossible to tell the exact depth of water on a road or the condition of the surface beneath it, "
            "and that 6 inches (about 15 cm) of fast-moving water can knock over an adult and 12 inches (about 30 cm) can carry away a small car [4]. "
            "Those figures are for moving water; urban waterlogging is often still, but hidden hazards remain, so we use them only as a conservative anchor."),
          P("Chennai now has a Real-Time Flood Forecasting and Spatial Decision Support System with control rooms [5], and IIT Madras runs a citizen portal for logging waterlogging depth [6]. "
            "Information for the public at the point of crossing is still mostly generic. People with reduced mobility are the most exposed: Census 2011 counted 2.68 crore persons with disabilities (2.21%) [13], "
            "about one in five of them with a movement disability [14], and Section 8 of the RPwD Act 2016 requires equal protection and safety in natural disasters [12].")]
story += [P("<b>Problem statement.</b> At flooded underpasses and low-lying streets in Chennai, people have no quick, trustworthy way to know whether a crossing is safe "
            "<i>for their own mobility</i>. Existing information is aimed at authorities, expressed as generic warnings, or depends on people uploading reports."),
          P("<b>Beneficiaries.</b> Primary: wheelchair, walker and cane users, older adults, and low-vision users (audio output). "
            "Also: pedestrians, two-wheeler riders and drivers. Secondary: NSS units, residents' associations and ward volunteers who can adopt a crossing; civic staff who can use the open data."),
          P("<b>Objectives.</b> (O1) Build a depth-sensing node costing under \u20b91,500. (O2) Convert depth into a transparent, profile-specific verdict with fail-safe behaviour. "
            "(O3) Deliver it accessibly: Tamil and English, high contrast, audio, no login and no install via QR. (O4) Publish code and hardware notes under an open licence and test honestly against ruler measurements.")]

# 3 solution
story += [H("3. Proposed solution and key features"),
          P("<b>How it works.</b> The <b>JalaNode</b> hangs a waterproof ultrasonic probe above the crossing and measures the distance to the water surface. "
            "Depth is the dry-day baseline minus that distance. The ESP32 uploads depth, time and a health flag every 30 seconds. "
            "The <b>JalaPath app</b> reads the latest value and runs a small rule-based <b>Crossing Safety Engine</b>, which gives each profile a verdict. "
            "There is no AI model: the rules are visible and explainable.")]
th = [["Profile", "Go", "Caution", "Avoid", "Basis (all values configurable)"],
      ["Walking adult", "&lt; 10 cm", "10-20 cm", "&gt; 20 cm", "Conservative vs NWS 15 cm moving-water figure [4]"],
      ["Assisted mobility (wheelchair, walker, cane)", "&lt; 5 cm", "5-10 cm", "&gt; 10 cm", "Design assumption; to be validated with users"],
      ["Two-wheeler", "&lt; 10 cm", "10-15 cm", "&gt; 15 cm", "Design assumption; varies by vehicle"],
      ["Car / auto", "&lt; 15 cm", "15-30 cm", "&gt; 30 cm", "NWS 12 in (30 cm) small-car figure [4]"]]
story += [table(th, [4.7*cm, 1.8*cm, 2*cm, 1.8*cm, 7.1*cm]), Spacer(1, 3),
          P("<b>Overrides.</b> Rising 3 cm or more in 10 minutes raises the verdict one level. Data older than 5 minutes or a sensor fault gives <b>Unknown: treat as unsafe</b>, never Go. "
            "A community hazard report (fast water, exposed wires, open drain) can only make the verdict stricter.")]
story += [P("<b>Must-have for the demo:</b> node sensing and upload; profile verdicts; fail-safe staleness rule; installable web app with map, English/Tamil toggle, high contrast and audio "
            "(recorded Tamil clips, since device Tamil voices vary); QR page per crossing; labelled simulator mode. "
            "<b>Optional later:</b> community reports, offline cache, trend arrow, several nodes, on-site LED and buzzer."),
          P("<b>Main innovation.</b> The sensing idea is not new. The distinctive part is the <i>decision layer</i>: depth translated into a verdict per mobility profile, "
            "delivered accessibly at the point of need, with a design that refuses to say Go when it does not know."),
          P("<b>Social impact.</b> Safer crossing choices for people who cannot easily detour, an equity focus on assisted-mobility users, bilingual and audio access without an account, "
            "and open depth data for wards. It supports SDG 11 (targets 11.2 and 11.5) and SDG 13 [27]. We make no measured-impact claim until testing is done.")]

# 4 existing
story += [PageBreak(), H("4. Existing approaches and how JalaPath differs")]
ex = [["Approach", "What it does", "Gap JalaPath targets"],
      ["Chennai RTFF &amp; SDSS [5]", "Web-based flood forecasting, spatial decision support, flood control rooms.", "Built for authorities and forecasting; we did not find per-profile crossing advice in the sources reviewed."],
      ["IIT Madras waterlogging portal [6]", "Residents log depth on a slider; map shows reports.", "Depends on people reporting; an expert notes it can miss people without technology access [6]."],
      ["GCC subway cameras and status posts [7][8]", "Cameras at 22 subways for the control centre; safe-subway lists posted on social media.", "Status is open/closed, not depth per user type."],
      ["FloodNet NYC [9][10]", "350+ open-hardware ultrasonic sensors with public depth data.", "Closest technical precedent. Not tuned for mobility profiles or Tamil/audio access."],
      ["Hong Kong subway flood warning [11]", "Ultrasonic sensor, SMS to staff, warning sign.", "Staff-oriented; single warning level."],
      ["<b>JalaPath (ours)</b>", "Low-cost node + per-profile verdict + fail-safe + QR + Tamil/English audio.", "<b>Novelty is the combination and accessibility-first decision layer, not any single part.</b>"]]
story += [table(ex, [4.1*cm, 6.2*cm, 7.1*cm]), Spacer(1, 4),
          P("We do not claim JalaPath is the first flood sensor or crowdsourced flood map; both exist. Our contribution is a low-cost, open, accessibility-first way to turn depth into a personal go/no-go answer.")]

# 5 architecture
story += [H("5. System architecture"), Diagram(17.4*cm, 6.4*cm, arch),
          P("Data in: ultrasonic distance (and optional community reports). Data out: a coloured, written and spoken verdict per profile. "
            "The decision engine runs in the browser, so no paid server functions are needed. The cloud layer is replaceable with Flask + SQLite on a laptop if Wi-Fi is unreliable on demo day.")]

# 6 workflow
story += [H("6. Workflow"), Diagram(17.4*cm, 7.4*cm, flow)]

# 7 stack
story += [H("7. Technology stack and implementation steps")]
ts = [["Layer", "Choice", "Notes"],
      ["Sensor", "JSN-SR04T waterproof ultrasonic", "20-600 cm range, blind zone about 20 cm; only the probe is waterproof, not the control board [15][16]"],
      ["Controller", "ESP32 DevKit, Arduino core (C++)", "Built-in Wi-Fi; 3.3 V logic, so divide a 5 V ECHO signal with 1k/2k resistors [20][21]"],
      ["Cloud", "Firebase Realtime Database (no-cost plan)", "1 GB stored, 10 GB/month download, 100 simultaneous connections [22]; demo-scale limit"],
      ["Web app", "HTML/CSS/JS PWA, Leaflet + OpenStreetMap", "Free and open source [23][24]; WCAG 2.1 guidance [26]; recorded Tamil audio"],
      ["Repo", "Public GitHub, MIT licence", "README, architecture notes, sample data, unit tests for the engine"]]
story += [table(ts, [2.2*cm, 5.6*cm, 9.6*cm]), Spacer(1, 3),
          P("<b>Steps.</b> (1) Wire probe to ESP32 and print distances. (2) Add median filter and baseline calibration. (3) POST readings to the database. "
            "(4) Build the engine as a pure JS function with table-driven tests. (5) Build the app screens and profile selector. (6) Add Tamil/English text and audio. "
            "(7) Generate QR signs and add the simulator. (8) Run the tub tests and record results. "
            "<i>Proposed roles (team to confirm): Varshini B hardware and firmware; Vaishnavi V web app and engine; Gopika T data, testing, accessibility and documentation.</i>"),
          P("<b>Sample user journey (fictional persona).</b> Meena, 67, uses a walker and lives near a subway during heavy rain. She scans the QR sign on the lane. "
            "The page shows <i>Depth 12 cm, updated 40 s ago, sensor reading</i>. She taps <b>Assisted mobility</b> and sees <b>Avoid</b> (above 10 cm), with an audio line in Tamil. "
            "A neighbour on a scooter sees <b>Caution</b> (10-15 cm); a driver sees <b>Go</b> (below 15 cm). If the node loses power, all three see <b>Unknown</b> after 5 minutes.")]

# 8 budget/timeline/testing
story += [PageBreak(), H("8. Budget (estimates; confirm before buying)")]
items = [("ESP32 DevKit (30-pin)", 1, 550), ("JSN-SR04T waterproof ultrasonic sensor", 1, 350), ("Resistor pack (1k, 2k) for ECHO divider", 1, 20),
         ("Jumper wires (20 pcs)", 1, 70), ("Perfboard / mini breadboard", 1, 60), ("IP65 plastic enclosure", 1, 150),
         ("Cable gland, PVC clamp, zip ties, sealant", 1, 80), ("Plastic water tub (15-20 L) for tests", 1, 120),
         ("Printed QR signs (A4, 2 pages)", 1, 30), ("Tape measure / ruler", 1, 40)]
tot = sum(q*p for _, q, p in items)
bd = [["Item", "Qty", "Unit (\u20b9)", "Total (\u20b9)"]] + [[n, str(q), str(p), str(q*p)] for n, q, p in items] + [["<b>Total</b>", "", "", "<b>%d</b>" % tot]]
story += [table(bd, [10.2*cm, 1.5*cm, 2.8*cm, 2.9*cm]), Spacer(1, 3),
          P("Assumed already owned (\u20b90): laptop, Android phone, USB cable, power bank, Wi-Fi hotspot. Software is free. Price check: sellers list the JSN-SR04T at about \u20b9313 to \u20b9499 [17][19]; "
            "other prices are team estimates. Software-only fallback (simulator): \u20b90. <b>Buy:</b> the items above. <b>Free:</b> Arduino IDE, VS Code, Git, Firebase no-cost plan, Leaflet, OpenStreetMap, Lighthouse.")]
story += [H("9. Timeline and testing plan")]
tl = [["Week", "Hardware", "Software", "Documents / tests"],
      ["1 (28 Oct-3 Nov)", "Wire probe, read distances", "Repo, database, engine + tests", "Confirm portal rules and deadline"],
      ["2 (4-10 Nov)", "Filter, calibrate, upload", "App screens, profiles, Tamil/English", "Draft deck (6-7 slides)"],
      ["3 (11-17 Nov)", "Enclosure and mount", "Audio, QR, simulator", "Tub tests, usability check"],
      ["4 (18-24 Nov)", "Buffer", "Bug fixes", "3-5 min demo video, final README"]]
story += [table(tl, [2.8*cm, 4.3*cm, 5.3*cm, 5*cm]), Spacer(1, 4)]
ts2 = [["Test (planned)", "Method", "Success criterion"],
       ["Depth accuracy", "Tub at 0, 5, 10, 15, 20, 30 cm vs ruler; 10 readings each", "Mean error 2 cm or less"],
       ["Spike rejection", "20 hand-waves under the probe", "At least 95% rejected"],
       ["Engine logic", "40+ boundary-value unit tests", "100% pass"],
       ["Fail-safe", "Unplug node, 5 trials", "Unknown shown within 5 min, 5 of 5"],
       ["Latency and uptime", "30 end-to-end trials; 24-h indoor run", "Median 10 s or less; 95% of readings received"],
       ["Accessibility and usability", "Lighthouse + TalkBack; 8-10 volunteers incl. 2 older adults", "Score 90+; 80% task success unaided"]]
story += [table(ts2, [3.6*cm, 8*cm, 5.8*cm])]

# 10 feasibility/risks
story += [H("10. Feasibility, risks and ethics")]
story += [P("<b>Feasibility and scale.</b> Parts are common, no ML or paid API is needed, and the simulator protects the demo from hardware failure. "
            "Each extra node adds one board and probe; a ward could adopt a crossing through NSS units or residents' associations. The 100-connection database limit [22] is a demo-scale constraint to replace before any public rollout. "
            "Maintenance: calibrate the baseline at install, clean the probe monthly, watch node health in the app. No partnerships with any authority are claimed.")]
rk = [["Risk / limitation", "Mitigation"],
      ["False Go (sensor error, water elsewhere on the route)", "Conservative thresholds, Unknown by default, message that depth is for this spot only"],
      ["Thresholds not validated; wheelchair and two-wheeler values are assumptions", "Mark as initial; review with a civil/disaster-management mentor and disability groups; keep configurable"],
      ["Power or Wi-Fi loss in storms", "5-minute staleness rule; future solar and cellular or LoRa link"],
      ["Ultrasonic limits: blind zone, temperature drift, vehicle under sensor", "Mount high, median filter, optional temperature correction"],
      ["Electrical and personal safety", "Battery/USB only, IP65 box, tub tests only; install on public property only with permission; never work in flood water"],
      ["Privacy and misuse", "No accounts, photos or citizen location stored; reports expire and are rate limited; advisory only, follow official alerts"]]
story += [table(rk, [6.6*cm, 10.8*cm])]
story += [H("11. Expected outcomes, future work and conclusion"),
          P("<b>Planned outcomes:</b> a working node and app, a public repository, a test report with honest error figures, a demo video and a draft threshold table. "
            "<b>Future:</b> solar power and LoRa/cellular links, route suggestions that avoid flooded crossings, data feeds for civic control rooms, SMS or IVR for feature phones, more languages. "
            "<b>Conclusion:</b> JalaPath is an achievable student prototype that turns a depth reading into a safe, accessible, personal decision for one of Chennai's recurring hazards.")]

# 12 compliance
story += [H("12. Event alignment and items to confirm")]
story += [note("<b>Confirm today on the MY Bharat portal.</b> (a) <b>Deadline:</b> the official page lists submissions 1 Sep-27 Oct 2026, while its FAQ says 15 Oct 2026 [1]. "
               "(b) <b>Eligibility:</b> age 18-29 as of 17 Aug 2026 for each member; the page says AICTE-registered while the FAQ says AISHE-registered; each member registers individually and the team designates a Team Lead [1]. "
               "(c) <b>Submission pack:</b> 6-7 slide deck on the IIT Bombay template, public GitHub/GitLab repo with README and licence, preferred 3-5 min video, Annexure 1 with ID proofs, file names <i>State_TeamName_Document.pdf</i> [1]. This report is not that deck. "
               "(d) <b>AI disclosure:</b> this draft was prepared with an AI assistant (Claude); the official submission must state the team's actual extent of AI use [1]. "
               "(e) The 2026 circular describes software-based solutions [28]; our app and simulator are software, and the hardware node is an optional data source. "
               "(f) <i>Design for Bharat</i> is a separate product-design challenge [29]; a third-party listing gives 1 Oct 2026 as its deadline [30], so we do not claim eligibility."), Spacer(1, 3)]

# references
story += [H("References (accessed 27 Oct 2026)")]
refs = [
 "[1] MY Bharat, Hack for Social Cause (VBYLD 2027). https://mybharat.gov.in/pages/hack-for-social-cause",
 "[2] Deccan Herald/PTI, Cyclone Michaung leaves trail of destruction, 5 Dec 2023. https://www.deccanherald.com/amp/story/india%2Ftamil-nadu%2Fcyclone-michaung-leaves-trail-of-destruction-in-tamil-nadu-2797169",
 "[3] Onmanorama, At least five dead in Tamil Nadu due to torrential rain, 4 Dec 2023. https://onmanorama.com/news/india/2023/12/04/cyclone-michaung-death-toll-in-torrential-rain-updates.html",
 "[4] US National Weather Service, Turn Around Don't Drown. https://www.weather.gov/pdt/FSAW_Tuesday",
 "[5] Chennai RTFF &amp; SDSS, About. https://chennaifloodmonitor.tn.gov.in/Master/AboutUs",
 "[6] Citizen Matters, IITM team helps 2,000 residents log flood water levels, 15 Dec 2023. https://citizenmatters.in/iitm-team-log-flood-water-levels-chennai-residents-forecasting/",
 "[7] DT Next, Mayor inspects GCC command centre. https://www.dtnext.in/amp/story/news/chennai/mayor-inspects-gcc-integrated-command-and-control-center-for-monsoon-preparedness-745771",
 "[8] The News Minute, Chennai rains: list of subways not waterlogged, 1 Nov 2022. https://www.thenewsminute.com/tamil-nadu/chennai-rains-list-subways-are-not-waterlogged-169445",
 "[9] NYU, Scaling urban flood monitoring with FloodNet. https://entrepreneur.nyu.edu/blog/2026/04/06/beyond-the-bench-scaling-urban-flood-monitoring-with-floodnet-open-hardware-and-public-data/",
 "[10] FloodSense street-sign flood depth sensor dataset, Zenodo. https://zenodo.org/records/7245376",
 "[11] Hong Kong EMSD, Smart Flooding Detection and Warning System. https://inno.emsd.gov.hk/en/inno-catalogue/details/index_id_61.html",
 "[12] Lok Sabha reply (DEPwD), RPwD Act Section 8. https://eparlib.sansad.in/bitstream/123456789/2983989/1/AU1153_zUTz0b.pdf",
 "[13] Lok Sabha, Census 2011 disability figures. https://eparlib.sansad.in/bitstream/123456789/745242/1/11123.pdf",
 "[14] Deccan Herald, A world with better access for PwDs. https://deccanherald.com/opinion/a-world-with-better-access-for-pwds-1058331.html",
 "[15] JSN-SR04T-2.0 datasheet. https://www.mikrocontroller.net/attachment/541933/JSN-SR04T-2.0.pdf",
 "[16] Proto-Pic, JSN-SR04T product page. https://proto-pic.co.uk/product/waterproof-jsn-sr04t-ultrasonic-distance-sensor",
 "[17] Hubtronics, JSN-SR04T-2.0 price. https://hubtronics.in/peripheral-modules/jsn-sr04t-2.0-ultrasonic-sensor",
 "[18] Zbotic, HC-SR04 vs JSN-SR04T (India prices). https://zbotic.in/ultrasonic-sensor-hc-sr04-vs-jsn-sr04t-which-to-buy/",
 "[19] Probots JSN-SR04T listing. https://m.indiamart.com/proddetail/probots-waterproof-ultrasonic-distance-sensor-module-jsn-sr04t-22686569062.html",
 "[20] Espressif, ESP32 datasheet. https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf",
 "[21] Arduino-ESP32 core. https://github.com/espressif/arduino-esp32",
 "[22] Firebase pricing. https://firebase.google.com/pricing",
 "[23] Leaflet. https://leafletjs.com",
 "[24] OpenStreetMap tile usage policy. https://operations.osmfoundation.org/policies/tiles/",
 "[25] MDN, Web Speech API. https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API",
 "[26] W3C, WCAG 2.1. https://www.w3.org/TR/WCAG21/",
 "[27] UN Sustainable Development Goals. https://sdgs.un.org/goals",
 "[28] Dept. of Youth Affairs circular, Hack for a Social Cause 2026 (college copy). https://www.sadakath.ac.in/newscircular.php?id=13",
 "[29] MY Bharat, Design for Bharat. https://mybharat.gov.in/pages/design_home",
 "[30] fundsforngos, Design for Bharat Open Challenge listing (third party). https://www2.fundsforngos.org/?p=492134"]
story += [Paragraph(r, ref) for r in refs]

Doc("/mnt/user-data/outputs/JalaPath_Project_Proposal.pdf").multiBuild(story)
print("budget total", tot, "abstract words", len(ABSTRACT.replace("<b>", "").replace("</b>", "").split()))
