from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import (
    HexColor, black, white, Color
)
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Flowable
from reportlab.lib import colors

W, H = A4

# ── Palette ─────────────────────────────────────────────────────────────────
PURPLE      = HexColor("#534AB7")
PURPLE_LIGHT= HexColor("#EEEDFE")
PURPLE_DARK = HexColor("#3C3489")

TEAL        = HexColor("#1D9E75")
TEAL_LIGHT  = HexColor("#E1F5EE")
TEAL_DARK   = HexColor("#085041")

CORAL       = HexColor("#D85A30")
CORAL_LIGHT = HexColor("#FAECE7")

AMBER       = HexColor("#BA7517")
AMBER_LIGHT = HexColor("#FAEEDA")

BLUE        = HexColor("#185FA5")
BLUE_LIGHT  = HexColor("#E6F1FB")

RED         = HexColor("#A32D2D")
RED_LIGHT   = HexColor("#FCEBEB")

GREEN       = HexColor("#3B6D11")
GREEN_LIGHT = HexColor("#EAF3DE")

GRAY_BG     = HexColor("#F1EFE8")
GRAY_BORDER = HexColor("#5F5E5A")
GRAY_TEXT   = HexColor("#444441")
GRAY_LIGHT  = HexColor("#D3D1C7")

CODE_BG     = HexColor("#F5F4F0")
TEXT_MAIN   = HexColor("#1A1A18")
TEXT_SEC    = HexColor("#5F5E5A")

# ── Styles ───────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s['h1'] = ParagraphStyle('h1', fontSize=26, fontName='Helvetica-Bold',
        textColor=TEXT_MAIN, spaceAfter=6, spaceBefore=0, leading=32)
    s['h2'] = ParagraphStyle('h2', fontSize=18, fontName='Helvetica-Bold',
        textColor=PURPLE_DARK, spaceAfter=4, spaceBefore=20, leading=24)
    s['h3'] = ParagraphStyle('h3', fontSize=14, fontName='Helvetica-Bold',
        textColor=TEXT_MAIN, spaceAfter=4, spaceBefore=14, leading=18)
    s['h4'] = ParagraphStyle('h4', fontSize=12, fontName='Helvetica-Bold',
        textColor=TEXT_MAIN, spaceAfter=3, spaceBefore=10, leading=16)
    s['body'] = ParagraphStyle('body', fontSize=10, fontName='Helvetica',
        textColor=TEXT_MAIN, spaceAfter=4, leading=15)
    s['body_sec'] = ParagraphStyle('body_sec', fontSize=10, fontName='Helvetica',
        textColor=TEXT_SEC, spaceAfter=4, leading=15)
    s['small'] = ParagraphStyle('small', fontSize=9, fontName='Helvetica',
        textColor=TEXT_SEC, spaceAfter=2, leading=13)
    s['code'] = ParagraphStyle('code', fontSize=8.5, fontName='Courier',
        textColor=HexColor("#2C2C2A"), spaceAfter=2, leading=13,
        backColor=CODE_BG, leftIndent=8, rightIndent=8,
        borderPadding=(6,8,6,8))
    s['code_inline'] = ParagraphStyle('code_inline', fontSize=9, fontName='Courier',
        textColor=HexColor("#3C3489"))
    s['label'] = ParagraphStyle('label', fontSize=9, fontName='Helvetica-Bold',
        textColor=PURPLE_DARK, spaceAfter=6, leading=12)
    s['step'] = ParagraphStyle('step', fontSize=10, fontName='Helvetica',
        textColor=TEXT_MAIN, leftIndent=20, spaceAfter=3, leading=14)
    s['center'] = ParagraphStyle('center', fontSize=10, fontName='Helvetica',
        textColor=TEXT_SEC, alignment=TA_CENTER, leading=14)
    s['tag'] = ParagraphStyle('tag', fontSize=8, fontName='Helvetica-Bold',
        textColor=PURPLE_DARK, spaceAfter=2, leading=10)
    return s

ST = make_styles()

# ── Helpers ──────────────────────────────────────────────────────────────────
class ColorRect(Flowable):
    def __init__(self, w, h, fill, radius=4):
        Flowable.__init__(self)
        self.w, self.h, self.fill, self.r = w, h, fill, radius
    def draw(self):
        self.canv.setFillColor(self.fill)
        self.canv.roundRect(0, 0, self.w, self.h, self.r, fill=1, stroke=0)
    def wrap(self, *args):
        return self.w, self.h

class HLine(Flowable):
    def __init__(self, w, color=GRAY_LIGHT, thickness=0.5):
        Flowable.__init__(self)
        self.w, self.color, self.t = w, color, thickness
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.t)
        self.canv.line(0, 0, self.w, 0)
    def wrap(self, *args):
        return self.w, self.t + 4

def P(text, style='body'):
    return Paragraph(text, ST[style])

def code_block(lines):
    """Return a list of flowables for a code block."""
    text = '\n'.join(lines)
    text_escaped = text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    lines_html = text_escaped.split('\n')
    joined = '<br/>'.join(lines_html)
    return [Paragraph(joined, ST['code']), Spacer(1, 4)]

def section_header(title, color=PURPLE, light=PURPLE_LIGHT):
    return [
        Spacer(1, 4),
        Table([[Paragraph(title, ParagraphStyle('sh', fontSize=11,
            fontName='Helvetica-Bold', textColor=color, leading=14))]],
            colWidths=[16.5*cm],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), light),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ('ROUNDEDCORNERS', [4]),
            ])),
        Spacer(1, 6),
    ]

def method_badge(method, color, bg):
    return Paragraph(
        f'<font color="#{bg.hexval()[2:]}" size="8"><b>{method}</b></font>',
        ParagraphStyle('mb', fontSize=8, fontName='Helvetica-Bold',
            textColor=color, backColor=bg, borderPadding=(2,6,2,6), leading=12))

def endpoint_card(method, path, auth, steps, method_color=BLUE, method_bg=BLUE_LIGHT):
    """Build an endpoint card as a table."""
    header_data = [[
        Paragraph(f'<font name="Helvetica-Bold" color="#{method_color.hexval()[2:]}">{method}</font>',
            ParagraphStyle('ep_m', fontSize=9, fontName='Helvetica-Bold',
                textColor=method_color, leading=12)),
        Paragraph(f'<font name="Courier" size="10"><b>{path}</b></font>',
            ParagraphStyle('ep_p', fontSize=10, fontName='Courier',
                textColor=TEXT_MAIN, leading=12)),
        Paragraph(auth, ParagraphStyle('ep_a', fontSize=8, fontName='Helvetica',
            textColor=TEXT_SEC, leading=11, alignment=TA_RIGHT)),
    ]]
    header = Table(header_data, colWidths=[2*cm, 9.5*cm, 5*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), method_bg),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
    step_items = []
    for i, step in enumerate(steps):
        num = str(i+1) if not step.startswith('→') and not step.startswith('!') else ('→' if step.startswith('→') else '!')
        text = step.lstrip('→').lstrip('!').strip()
        step_items.append([
            Paragraph(num, ParagraphStyle('sn', fontSize=9, fontName='Helvetica-Bold',
                textColor=PURPLE, alignment=TA_CENTER, leading=12)),
            Paragraph(text, ParagraphStyle('st', fontSize=9.5, fontName='Helvetica',
                textColor=TEXT_MAIN, leading=13)),
        ])
    body = Table(step_items, colWidths=[0.8*cm, 15.7*cm],
        style=TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (0,-1), 10),
            ('LEFTPADDING', (1,0), (1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEBELOW', (0,0), (-1,-2), 0.3, GRAY_LIGHT),
        ]))
    outer = Table([
        [header],
        [body],
    ], colWidths=[16.5*cm],
        style=TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, GRAY_LIGHT),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('ROUNDEDCORNERS', [4]),
        ]))
    return [outer, Spacer(1, 8)]

def db_table(table_name, columns, description=""):
    """columns = list of (name, type, notes)"""
    header = [
        Paragraph(f'Table: <font name="Courier" size="10"><b>{table_name}</b></font>',
            ParagraphStyle('th', fontSize=11, fontName='Helvetica-Bold',
                textColor=TEAL_DARK, leading=14)),
    ]
    if description:
        header.append(Paragraph(description,
            ParagraphStyle('td', fontSize=9, fontName='Helvetica',
                textColor=TEXT_SEC, leading=12)))

    col_header = Table([['Column', 'Type', 'Description / Constraints']],
        colWidths=[3.5*cm, 4*cm, 9*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), TEAL_LIGHT),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('TEXTCOLOR', (0,0), (-1,-1), TEAL_DARK),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
    rows = []
    for i, (col, typ, desc) in enumerate(columns):
        bg = white if i % 2 == 0 else GRAY_BG
        rows.append([
            Paragraph(col, ParagraphStyle('cn', fontSize=9, fontName='Courier',
                textColor=PURPLE_DARK, leading=12)),
            Paragraph(typ, ParagraphStyle('ct', fontSize=8.5, fontName='Courier',
                textColor=TEAL_DARK, leading=12)),
            Paragraph(desc, ParagraphStyle('cd', fontSize=9, fontName='Helvetica',
                textColor=TEXT_MAIN, leading=12)),
        ])
    col_body = Table(rows, colWidths=[3.5*cm, 4*cm, 9*cm],
        style=TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEBELOW', (0,0), (-1,-2), 0.3, GRAY_LIGHT),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [white, GRAY_BG]),
        ]))
    outer = Table([
        [Table([[Paragraph(f'Table: <font name="Courier"><b>{table_name}</b></font>',
            ParagraphStyle('thn', fontSize=11, fontName='Helvetica-Bold',
                textColor=TEAL_DARK, leading=14))]+
            ([Paragraph(description, ParagraphStyle('tds', fontSize=9,
                fontName='Helvetica', textColor=TEXT_SEC, leading=12))]
             if description else [])],
            colWidths=[16.5*cm],
            style=TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), TEAL_LIGHT),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))],
        [col_header],
        [col_body],
    ], colWidths=[16.5*cm],
        style=TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, TEAL),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
    return [outer, Spacer(1, 10)]

def ws_event(name, direction, direction_label, json_sample, desc=""):
    dir_colors = {
        'c2s': (BLUE, BLUE_LIGHT, 'client → server'),
        's2c': (GREEN, GREEN_LIGHT, 'server → you only'),
        's2all': (CORAL, CORAL_LIGHT, 'server → broadcast to room'),
    }
    dc, dl, dlabel = dir_colors.get(direction, (GRAY_BORDER, GRAY_BG, direction_label))
    header_content = [
        [Paragraph(f'<font name="Courier" size="10"><b>{name}</b></font>',
            ParagraphStyle('wen', fontSize=10, fontName='Courier',
                textColor=PURPLE_DARK, leading=14)),
         Paragraph(dlabel, ParagraphStyle('wed', fontSize=8,
            fontName='Helvetica-Bold', textColor=dc, leading=10,
            alignment=TA_RIGHT))],
    ]
    if desc:
        header_content.append([
            Paragraph(desc, ParagraphStyle('wedesc', fontSize=9, fontName='Helvetica',
                textColor=TEXT_SEC, leading=12, colSpan=2)),
            '',
        ])
    items = [Table(header_content, colWidths=[10*cm, 6.5*cm],
        style=TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (-1,-1), dl),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('SPAN', (0,1), (1,1)) if desc else ('TOPPADDING',(0,0),(-1,-1),0),
        ]))]
    if json_sample:
        escaped = json_sample.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        lines = escaped.split('\n')
        joined = '<br/>'.join(lines)
        items.append(Paragraph(joined, ParagraphStyle('wecode', fontSize=8.5,
            fontName='Courier', textColor=HexColor("#2C2C2A"), leading=13,
            leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4)))
    outer = Table([[i] for i in items], colWidths=[16.5*cm],
        style=TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, PURPLE),
            ('LINEAFTER', (0,0), (0,-1), 3, PURPLE),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
    return [outer, Spacer(1, 7)]

def phase_cover(num, title, desc, color, light):
    items = [
        Table([[
            Paragraph(f'Phase {num}', ParagraphStyle('pn', fontSize=12,
                fontName='Helvetica-Bold', textColor=color, leading=14)),
            Paragraph(title, ParagraphStyle('pt', fontSize=20,
                fontName='Helvetica-Bold', textColor=TEXT_MAIN, leading=24)),
            Paragraph(desc, ParagraphStyle('pd', fontSize=10, fontName='Helvetica',
                textColor=TEXT_SEC, leading=14)),
        ]], colWidths=[16.5*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light),
            ('TOPPADDING', (0,0), (-1,-1), 14),
            ('BOTTOMPADDING', (0,0), (-1,-1), 14),
            ('LEFTPADDING', (0,0), (-1,-1), 14),
            ('RIGHTPADDING', (0,0), (-1,-1), 14),
            ('LINERIGHT', (0,0), (0,-1), 4, color),
        ])),
        Spacer(1, 14),
    ]
    return items

def info_box(title, items_list, color=AMBER, light=AMBER_LIGHT):
    rows = []
    for item in items_list:
        rows.append([Paragraph(f'• {item}', ParagraphStyle('ib', fontSize=9.5,
            fontName='Helvetica', textColor=TEXT_MAIN, leading=13))])
    t = Table([
        [Paragraph(title, ParagraphStyle('ibt', fontSize=10, fontName='Helvetica-Bold',
            textColor=color, leading=13))],
    ] + rows, colWidths=[16.5*cm],
    style=TableStyle([
        ('BACKGROUND', (0,0), (-1,0), light),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, color),
        ('LINEBEFORE', (0,0), (0,-1), 3, color),
    ]))
    return [t, Spacer(1, 8)]

# ── Page template ─────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(PURPLE_DARK)
    canvas.rect(0, H - 1*cm, W, 1*cm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawString(1.5*cm, H - 0.65*cm, 'Bhabbi / Getaway — Engineering Roadmap')
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(W - 1.5*cm, H - 0.65*cm, f'Page {doc.page}')
    # Footer
    canvas.setFillColor(GRAY_LIGHT)
    canvas.rect(0, 0, W, 0.7*cm, fill=1, stroke=0)
    canvas.setFillColor(TEXT_SEC)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(1.5*cm, 0.22*cm, 'Confidential — internal project document')
    canvas.drawRightString(W - 1.5*cm, 0.22*cm, 'FastAPI · Next.js · PostgreSQL · WebSocket')
    canvas.restoreState()

# ── Build content ─────────────────────────────────────────────────────────────
def build_pdf(path):
    doc = SimpleDocTemplate(path, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.2*cm,
        title='Bhabbi Card Game — Engineering Roadmap',
        author='Project Document')

    story = []

    # ── COVER PAGE ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 2*cm))
    story.append(Table([[
        Paragraph('BHABBI / GETAWAY', ParagraphStyle('cover_tag', fontSize=11,
            fontName='Helvetica-Bold', textColor=PURPLE, leading=14,
            alignment=TA_CENTER)),
    ]], colWidths=[16.5*cm], style=TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
    ])))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph('Engineering Roadmap',
        ParagraphStyle('cover_title', fontSize=36, fontName='Helvetica-Bold',
            textColor=TEXT_MAIN, alignment=TA_CENTER, leading=44)))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('Full-stack multiplayer card game — phase-by-phase build guide',
        ParagraphStyle('cover_sub', fontSize=13, fontName='Helvetica',
            textColor=TEXT_SEC, alignment=TA_CENTER, leading=18)))
    story.append(Spacer(1, 0.8*cm))
    story.append(HLine(16.5*cm, PURPLE, 2))
    story.append(Spacer(1, 0.8*cm))

    # Stack summary
    stack_data = [
        ['Layer', 'Technology', 'Purpose'],
        ['Backend API', 'FastAPI (Python)', 'Async HTTP + native WebSocket, auto OpenAPI docs'],
        ['Database', 'PostgreSQL + SQLAlchemy', 'JSONB for card hands, async sessions via asyncpg'],
        ['Migrations', 'Alembic', 'Version-controlled schema changes'],
        ['Real-time', 'WebSocket (FastAPI)', 'Bidirectional events — no polling'],
        ['Cache / Pub-Sub', 'Redis', 'Multi-instance WS coordination (Phase 5+)'],
        ['Frontend', 'Next.js 14 App Router', 'React 18, client components for live game'],
        ['Styling', 'Tailwind CSS', 'Rapid iteration on card & game UI'],
        ['Identity', 'UUID token / localStorage', 'No login required — guest player system'],
    ]
    stack_tbl = Table(stack_data, colWidths=[3.5*cm, 4.5*cm, 8.5*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PURPLE),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, PURPLE_LIGHT]),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 0.5, PURPLE),
            ('INNERGRID', (0,0), (-1,-1), 0.3, GRAY_LIGHT),
        ]))
    story.append(stack_tbl)
    story.append(Spacer(1, 0.8*cm))

    # Phase timeline summary
    timeline = [
        ['Phase', 'Name', 'What gets built', 'Est.'],
        ['1', 'Project Setup', 'FastAPI skeleton, DB, Alembic, config', '1–2 days'],
        ['2', 'Identity System', 'Guest token, players table, 3 endpoints', '1 day'],
        ['3', 'Room System', 'Create/join/leave/kick, 6 endpoints, 2 tables', '2–3 days'],
        ['4', 'Game Engine', 'Card logic, state machine, 4 HTTP endpoints, 4 tables', '3–4 days'],
        ['5', 'WebSocket Layer', 'Real-time events, connection manager, 15 WS events', '3–4 days'],
        ['6', 'Chat System', 'Persistent chat, system messages, 1 endpoint', '1 day'],
        ['7', 'Frontend Shell', 'Next.js setup, identity hook, lobby, waiting room', '3–4 days'],
        ['8', 'Game UI', 'Card hand, board, WS hook, chat panel, game over', '5–7 days'],
        ['9', 'Edge Cases', 'Disconnects, timers, host transfer, play again', '2–3 days'],
        ['10', 'Deployment', 'Docker Compose, Railway/Render, Redis pub-sub', '2 days'],
        ['Total', '', '', '23–31 days'],
    ]
    tl_tbl = Table(timeline, colWidths=[1.5*cm, 3*cm, 8.5*cm, 3.5*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), TEAL_DARK),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [white, TEAL_LIGHT]),
            ('BACKGROUND', (0,-1), (-1,-1), TEAL),
            ('TEXTCOLOR', (0,-1), (-1,-1), white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 7),
            ('BOX', (0,0), (-1,-1), 0.5, TEAL),
            ('INNERGRID', (0,0), (-1,-1), 0.3, GRAY_LIGHT),
        ]))
    story.append(tl_tbl)
    story.append(PageBreak())

    # ── GAME RULES PAGE ───────────────────────────────────────────────────────
    story.append(P('Game Rules — Bhabbi / Getaway', 'h2'))
    story.append(HLine(16.5*cm, PURPLE_LIGHT))
    story.append(Spacer(1, 6))
    rules = [
        ('Players & Deck', '2–6 players. Standard 52-card deck dealt equally. If not divisible, extra cards go to earlier seats.'),
        ('First Turn', 'Whoever holds the Ace of Spades plays first and MUST play it as the opening card of the game.'),
        ('Valid Play', 'Play a card with the same suit AND strictly higher rank than the top card. OR play any Ace (resets the round). OR play a 2 of any suit (beats everything — highest possible card).'),
        ('Cannot Play', 'If a player cannot or does not play, they pick up the ENTIRE pile. The pile clears. The next player starts a completely fresh round — top_card becomes NULL and any card is valid.'),
        ('Card Rank Order', '3 < 4 < 5 < 6 < 7 < 8 < 9 < 10 < J < Q < K < A < 2. The 2 is the nuclear card — always wins.'),
        ('Winning', 'First player to empty their hand wins and leaves the game. Second player to finish ranks 2nd, and so on.'),
        ('The Bhabbi', 'The very last player still holding cards is the Bhabbi (loser). This is the central comedic element of the game.'),
        ('Strategy Note', 'Picking up voluntarily (even when you have a valid card) is legal and can be strategic — accumulating cards for a 2 to dominate later.'),
    ]
    rule_rows = [[
        Paragraph(title, ParagraphStyle('rt', fontSize=10, fontName='Helvetica-Bold',
            textColor=PURPLE_DARK, leading=13)),
        Paragraph(body, ParagraphStyle('rb', fontSize=10, fontName='Helvetica',
            textColor=TEXT_MAIN, leading=14)),
    ] for title, body in rules]
    rule_tbl = Table(rule_rows, colWidths=[4*cm, 12.5*cm],
        style=TableStyle([
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [white, PURPLE_LIGHT]),
            ('BOX', (0,0), (-1,-1), 0.5, PURPLE_LIGHT),
            ('INNERGRID', (0,0), (-1,-1), 0.3, PURPLE_LIGHT),
        ]))
    story.append(rule_tbl)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1 — PROJECT SETUP
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(1, 'Project Skeleton & Configuration',
        'Repository structure, FastAPI app, async PostgreSQL connection, Alembic migrations. Nothing game-specific yet — just a working, testable API server.',
        TEAL, TEAL_LIGHT)

    story += section_header('Repository structure', TEAL, TEAL_LIGHT)
    story += code_block([
        'bhabbi/',
        '├── backend/',
        '│   ├── main.py              # FastAPI app entry point',
        '│   ├── database.py          # Async engine + session factory',
        '│   ├── config.py            # Pydantic Settings, reads .env',
        '│   ├── deps.py              # FastAPI dependency functions (get_db, get_current_player)',
        '│   ├── models/',
        '│   │   └── base.py          # DeclarativeBase + UUID primary key mixin',
        '│   ├── schemas/             # Pydantic request/response models',
        '│   ├── routers/             # FastAPI routers — one per domain',
        '│   ├── services/            # Business logic (pure functions, no DB calls)',
        '│   ├── ws/                  # WebSocket manager + router',
        '│   └── alembic/             # Migration files',
        '├── frontend/',
        '│   ├── app/                 # Next.js App Router',
        '│   ├── components/',
        '│   ├── hooks/',
        '│   └── lib/',
        '├── docker-compose.yml',
        '└── .env',
    ])

    story += section_header('config.py — Pydantic Settings', TEAL, TEAL_LIGHT)
    story += code_block([
        'from pydantic_settings import BaseSettings',
        '',
        'class Settings(BaseSettings):',
        '    DATABASE_URL: str',
        '    REDIS_URL: str = "redis://localhost:6379"',
        '    SECRET_KEY: str = "change-me-in-prod"',
        '    MAX_ROOM_SIZE: int = 6',
        '    TURN_TIMEOUT_SECONDS: int = 30',
        '',
        '    class Config:',
        '        env_file = ".env"',
        '',
        'settings = Settings()',
    ])

    story += section_header('database.py — Async SQLAlchemy engine', TEAL, TEAL_LIGHT)
    story += code_block([
        'from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession',
        'from sqlalchemy.orm import sessionmaker, DeclarativeBase',
        'from .config import settings',
        '',
        'engine = create_async_engine(settings.DATABASE_URL, echo=False)',
        'AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession,',
        '                                  expire_on_commit=False)',
        '',
        'class Base(DeclarativeBase):',
        '    pass',
    ])

    story += section_header('deps.py — Dependency injection', TEAL, TEAL_LIGHT)
    story += code_block([
        'async def get_db() -> AsyncSession:',
        '    async with AsyncSessionLocal() as session:',
        '        yield session',
        '',
        'async def get_current_player(',
        '    x_player_token: str = Header(...),',
        '    db: AsyncSession = Depends(get_db)',
        ') -> Player:',
        '    player = await db.scalar(',
        '        select(Player).where(Player.token == x_player_token))',
        '    if not player:',
        '        raise HTTPException(401, "Invalid player token")',
        '    player.last_seen = datetime.utcnow()',
        '    await db.commit()',
        '    return player',
    ])

    story += section_header('main.py — FastAPI application', TEAL, TEAL_LIGHT)
    story += code_block([
        'from fastapi import FastAPI',
        'from fastapi.middleware.cors import CORSMiddleware',
        'from .routers import identity, rooms, games',
        'from .ws.router import ws_router',
        '',
        'app = FastAPI(title="Bhabbi API")',
        'app.add_middleware(CORSMiddleware,',
        '    allow_origins=["http://localhost:3000"],',
        '    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])',
        '',
        'app.include_router(identity.router, prefix="/api/identity")',
        'app.include_router(rooms.router, prefix="/api/rooms")',
        'app.include_router(games.router, prefix="/api/games")',
        'app.include_router(ws_router)',
        '',
        '@app.get("/api/health")',
        'async def health(): return {"status": "ok"}',
    ])

    story += section_header('Alembic setup commands', TEAL, TEAL_LIGHT)
    story += code_block([
        'pip install fastapi uvicorn sqlalchemy asyncpg alembic pydantic-settings redis',
        '',
        'cd backend',
        'alembic init alembic',
        '',
        '# Edit alembic.ini: set sqlalchemy.url = your DATABASE_URL',
        '# Edit alembic/env.py:',
        '#   from backend.database import Base',
        '#   target_metadata = Base.metadata',
        '',
        'alembic revision --autogenerate -m "initial tables"',
        'alembic upgrade head',
    ])

    story += info_box('Phase 1 — Done when:', [
        'uvicorn backend.main:app --reload starts without errors',
        'http://localhost:8000/docs shows the OpenAPI Swagger UI',
        'Alembic migrations run cleanly against your Postgres instance',
        'GET /api/health returns {"status": "ok"}',
    ], TEAL, TEAL_LIGHT)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2 — IDENTITY
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(2, 'Guest Identity System',
        'No login required. On first visit the browser generates a UUID token stored in localStorage. The backend maps that token to a Player row. Every request proves identity via X-Player-Token header.',
        BLUE, BLUE_LIGHT)

    story += section_header('How guest identity works', BLUE, BLUE_LIGHT)
    story.append(P('The flow is: user enters a nickname → POST /api/identity/register → backend generates a UUID token → frontend stores token in localStorage → every subsequent API call and WebSocket connection sends this token → backend validates it and resolves the Player record.', 'body'))
    story.append(P('If the user clears localStorage or visits from a new device, they get a new identity. This is intentional — no account recovery is needed for a casual card game.', 'body_sec'))
    story.append(Spacer(1, 6))

    story += db_table('players', [
        ('id', 'UUID PK', 'Internal identifier. Never sent to other players — only nicknames are shared.'),
        ('token', 'UUID UNIQUE NOT NULL', 'The secret stored in the browser. Must be indexed for fast lookup on every request.'),
        ('nickname', 'VARCHAR(32) NOT NULL', 'Display name chosen by user. 2–32 chars. Validated server-side.'),
        ('created_at', 'TIMESTAMP', 'Set to NOW() by default. Never updated.'),
        ('last_seen', 'TIMESTAMP', 'Updated on every authenticated request via the get_current_player dependency. Useful for analytics and stale cleanup.'),
    ], 'One row per unique browser session. Grows indefinitely — add a cleanup job later.')

    story += section_header('Endpoint 2.1 — POST /api/identity/register', BLUE, BLUE_LIGHT)
    story += endpoint_card('POST', '/api/identity/register', 'No authentication required', [
        '→ Request body: { "nickname": "Ali" } — validate 2–32 chars server-side, strip whitespace',
        '1. Generate UUID v4 as the player token using uuid.uuid4()',
        '2. Generate a second UUID v4 as the player id',
        '3. INSERT into players table. Wrap in try/except IntegrityError for the (astronomically rare) duplicate token collision — retry with a new UUID.',
        '4. Return { "player_token": "...", "player_id": "...", "nickname": "Ali" }',
        '→ Frontend action: localStorage.setItem("bhabbi_token", data.player_token)',
        '→ Error 422: nickname shorter than 2 chars or longer than 32 chars',
    ], BLUE, BLUE_LIGHT)

    story += section_header('Endpoint 2.2 — GET /api/identity/me', BLUE, BLUE_LIGHT)
    story += endpoint_card('GET', '/api/identity/me', 'Header: X-Player-Token', [
        '1. Read X-Player-Token header (FastAPI Header(...) parameter)',
        '2. SELECT * FROM players WHERE token = header_value. If not found → raise HTTPException(401)',
        '3. UPDATE players SET last_seen = NOW() WHERE id = player.id',
        '4. Return { "player_id": "...", "nickname": "Ali", "created_at": "..." }',
        '→ Frontend calls this on every app load to validate the stored token',
        '→ If 401 response: clear localStorage, set needsNickname = true, show NicknameModal',
    ], BLUE, BLUE_LIGHT)

    story += section_header('Endpoint 2.3 — PATCH /api/identity/me', BLUE, BLUE_LIGHT)
    story += endpoint_card('PATCH', '/api/identity/me', 'Header: X-Player-Token', [
        '→ Request body: { "nickname": "NewName" }',
        '1. Authenticate via get_current_player dependency',
        '2. Validate new nickname: 2–32 chars, strip whitespace',
        '3. UPDATE players SET nickname = ? WHERE id = player.id',
        '4. Return { "nickname": "NewName" }',
        '→ If player is currently in a room, the WS layer broadcasts a nickname change event to the room (implemented in Phase 5)',
    ], BLUE, BLUE_LIGHT)

    story += section_header('Frontend — identity module (lib/identity.ts)', BLUE, BLUE_LIGHT)
    story += code_block([
        'const TOKEN_KEY = "bhabbi_token"',
        'const NICKNAME_KEY = "bhabbi_nickname"',
        '',
        'export const getToken = () => localStorage.getItem(TOKEN_KEY)',
        'export const saveToken = (t: string) => localStorage.setItem(TOKEN_KEY, t)',
        'export const clearToken = () => localStorage.removeItem(TOKEN_KEY)',
        'export const getNickname = () => localStorage.getItem(NICKNAME_KEY)',
        'export const saveNickname = (n: string) => localStorage.setItem(NICKNAME_KEY, n)',
    ])

    story += section_header('Frontend — useIdentity hook (hooks/useIdentity.ts)', BLUE, BLUE_LIGHT)
    story += code_block([
        'export function useIdentity() {',
        '  const [player, setPlayer] = useState(null)',
        '  const [loading, setLoading] = useState(true)',
        '  const [needsNickname, setNeedsNickname] = useState(false)',
        '',
        '  useEffect(() => {',
        '    const token = getToken()',
        '    if (!token) { setNeedsNickname(true); setLoading(false); return }',
        '    api.get("/identity/me", token)',
        '      .then(setPlayer)',
        '      .catch(() => { clearToken(); setNeedsNickname(true) })',
        '      .finally(() => setLoading(false))',
        '  }, [])',
        '',
        '  const register = async (nickname: string) => {',
        '    const data = await api.post("/identity/register", { nickname })',
        '    saveToken(data.player_token)',
        '    saveNickname(nickname)',
        '    setPlayer(data)',
        '    setNeedsNickname(false)',
        '  }',
        '  return { player, loading, needsNickname, register }',
        '}',
    ])
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3 — ROOMS
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(3, 'Room System',
        'Players create rooms with a 6-char human-readable code. Others join by entering that code. Rooms track who is seated where and move through waiting → playing → finished states.',
        CORAL, CORAL_LIGHT)

    story += db_table('rooms', [
        ('id', 'UUID PK', 'Internal ID used in all API paths and foreign keys.'),
        ('code', 'VARCHAR(6) UNIQUE', 'Human-readable join code e.g. "BHB4F2". Generated with random.choices(string.ascii_uppercase + digits, k=6). Add DB index.'),
        ('host_id', 'UUID FK → players', 'Who created the room. Only they can start the game and kick players. Changes if host leaves.'),
        ('status', 'ENUM', "Values: 'waiting' | 'playing' | 'finished'. Only 'waiting' rooms accept new joins."),
        ('max_players', 'SMALLINT default 4', '2–6 players. Enforced on join.'),
        ('created_at', 'TIMESTAMP', 'For stale room cleanup cron (delete rooms older than 24h with no activity).'),
    ], 'One row per game room. The code is what players share with each other.')

    story += db_table('room_players', [
        ('id', 'UUID PK', ''),
        ('room_id', 'UUID FK → rooms', 'CASCADE DELETE so cleaning up a room removes all seat entries automatically.'),
        ('player_id', 'UUID FK → players', 'UNIQUE(room_id, player_id) — one entry per player per room. A player cannot be in two rooms simultaneously.'),
        ('seat', 'SMALLINT NOT NULL', '0, 1, 2, 3, 4, 5. Seat 0 = host. Determines turn order. UNIQUE(room_id, seat).'),
        ('is_active', 'BOOLEAN default TRUE', 'Set FALSE when player leaves or is kicked. Seat stays reserved so turn order does not shift mid-game.'),
        ('joined_at', 'TIMESTAMP', 'Useful for ordering when assigning new host on host departure.'),
    ], 'Join table between rooms and players with extra metadata.')

    story += section_header('Endpoint 3.1 — POST /api/rooms/create', CORAL, CORAL_LIGHT)
    story += endpoint_card('POST', '/api/rooms/create', 'Header: X-Player-Token', [
        '→ Body: { "max_players": 4 } — optional, default 4, valid range 2–6',
        '1. Authenticate player via get_current_player dependency',
        '2. Check if player already has an active room entry (status=waiting or playing). If yes → return 409 with existing room_id. Prevents duplicate rooms.',
        '3. Generate 6-char uppercase alphanumeric code. SELECT to check uniqueness. Retry loop max 5 times on collision.',
        '4. INSERT into rooms with status="waiting", host_id=player.id, max_players from body',
        '5. INSERT into room_players with room_id, player_id, seat=0, is_active=TRUE',
        '6. Return { room_id, code, status, max_players, host_id, players: [{player_id, nickname, seat}] }',
    ], CORAL, CORAL_LIGHT)

    story += section_header('Endpoint 3.2 — POST /api/rooms/join', CORAL, CORAL_LIGHT)
    story += endpoint_card('POST', '/api/rooms/join', 'Header: X-Player-Token', [
        '→ Body: { "code": "BHB4F2" } — uppercase the code server-side before lookup',
        '1. SELECT room WHERE code = upper(body.code). 404 if not found.',
        '2. If room.status != "waiting" → 400 "Game already in progress"',
        '3. COUNT active room_players WHERE room_id. If >= max_players → 422 "Room is full"',
        '4. SELECT room_players WHERE room_id AND player_id. If found and is_active=TRUE → 409 "Already in room". If is_active=FALSE → 403 "You were removed from this room".',
        '5. Find lowest unoccupied seat number. INSERT into room_players.',
        '6. Broadcast room_update WS event to all existing room members (wire this up in Phase 5)',
        '7. Return full room state including all players',
    ], CORAL, CORAL_LIGHT)

    story += section_header('Endpoint 3.3 — GET /api/rooms/{room_id}', CORAL, CORAL_LIGHT)
    story += endpoint_card('GET', '/api/rooms/{room_id}', 'Header: X-Player-Token', [
        '1. Verify player is in the room via SELECT room_players. 403 if not a member.',
        '2. JOIN rooms + room_players + players to get full player list with nicknames',
        '3. Return { room_id, code, status, max_players, host_id, players: [{player_id, nickname, seat, is_active}] }',
    ], CORAL, CORAL_LIGHT)

    story += section_header('Endpoint 3.4 — GET /api/rooms/public', CORAL, CORAL_LIGHT)
    story += endpoint_card('GET', '/api/rooms/public', 'No auth required', [
        '1. SELECT rooms WHERE status="waiting". JOIN to count active room_players. Filter where count < max_players.',
        '2. JOIN to get host nickname. Order by created_at DESC. Limit 20.',
        '3. Return { rooms: [{ room_id, code, player_count, max_players, host_nickname }] }',
        '→ Optional feature for v1. The primary join flow is by code — this is just a discovery list.',
    ], CORAL, CORAL_LIGHT)

    story += section_header('Endpoint 3.5 — POST /api/rooms/{room_id}/leave', CORAL, CORAL_LIGHT)
    story += endpoint_card('POST', '/api/rooms/{room_id}/leave', 'Header: X-Player-Token', [
        '1. Verify player is in room and is_active=TRUE',
        '2. SET is_active=FALSE for this room_player row',
        '3. If player was host AND status="waiting": find next active player by seat order, assign them as host. If no one remains → DELETE the room entirely.',
        '4. If game is "playing": mark player inactive. Their turns will be auto-skipped (Phase 9 edge case handling).',
        '5. Broadcast room_update WS event to remaining players',
    ], CORAL, CORAL_LIGHT)

    story += section_header('Endpoint 3.6 — POST /api/rooms/{room_id}/kick', CORAL, CORAL_LIGHT)
    story += endpoint_card('POST', '/api/rooms/{room_id}/kick', 'Header: X-Player-Token (host only)', [
        '→ Body: { "player_id": "uuid-of-player-to-kick" }',
        '1. Verify the requester is the room host. 403 if not.',
        '2. Verify room.status = "waiting". Cannot kick during a game.',
        '3. SET is_active=FALSE for the target player row',
        '4. Send kicked WS event { "type": "kicked" } to the kicked player specifically',
        '5. Broadcast room_update to all remaining players so their UI refreshes',
    ], CORAL, CORAL_LIGHT)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4 — GAME ENGINE
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(4, 'Game Logic Engine',
        'The heart of the project. Pure Python game logic for Bhabbi, then HTTP endpoints to exercise it. Build and test these endpoints before adding WebSocket — it is much easier to debug with curl.',
        AMBER, AMBER_LIGHT)

    story += db_table('games', [
        ('id', 'UUID PK', ''),
        ('room_id', 'UUID FK → rooms', 'One game per room at a time.'),
        ('started_at', 'TIMESTAMP', ''),
        ('ended_at', 'TIMESTAMP NULL', 'Set when game_state.phase = "finished".'),
        ('winner_id', 'UUID FK → players NULL', 'First player to empty their hand.'),
        ('bhabbi_id', 'UUID FK → players NULL', 'Last player still holding cards.'),
    ], 'One row per completed or in-progress game.')

    story += db_table('game_state', [
        ('game_id', 'UUID PK FK → games', '1:1 with games. The single source of truth for the live game.'),
        ('current_turn', 'UUID FK → players', 'Whose turn it is RIGHT NOW.'),
        ('pile', 'JSONB', 'Cards currently on the table: [{"suit":"spades","rank":"A"}, ...]. Empty array = fresh round.'),
        ('top_card', 'JSONB NULL', 'The card that must be beaten. NULL = fresh round, any card is valid.'),
        ('turn_started_at', 'TIMESTAMP', 'For 30-second timeout (Phase 9). Updated on every turn change.'),
        ('phase', 'ENUM', '"in_progress" | "finished"'),
    ], 'Updated atomically on every move.')

    story += db_table('player_hands', [
        ('game_id', 'UUID FK → games', 'Part of composite PK.'),
        ('player_id', 'UUID FK → players', 'Part of composite PK. UNIQUE(game_id, player_id).'),
        ('cards', 'JSONB', 'Current hand as array: [{"suit":"hearts","rank":"K"}, ...]. Updated atomically with game_state.'),
        ('finished_at', 'TIMESTAMP NULL', 'Set when hand becomes empty. NULL = still playing.'),
        ('finish_rank', 'SMALLINT NULL', '1=winner, 2=second, etc. Last player gets rank = total_players (they are the Bhabbi).'),
    ], 'One row per player per game. Private data — never exposed to other players.')

    story += db_table('game_moves', [
        ('id', 'UUID PK', ''),
        ('game_id', 'UUID FK → games', 'Indexed for replay and audit queries.'),
        ('player_id', 'UUID FK → players', ''),
        ('move_type', 'ENUM', '"play_card" | "pickup" | "timeout_pickup" | "finish"'),
        ('card_played', 'JSONB NULL', 'Only populated for move_type="play_card".'),
        ('created_at', 'TIMESTAMP', 'Sequence by this for replay. Immutable — never updated.'),
    ], 'Append-only audit log of every game action. Used for replay and debugging.')

    story += section_header('Card representation and rank order', AMBER, AMBER_LIGHT)
    story += code_block([
        'SUITS = ["spades", "hearts", "diamonds", "clubs"]',
        'RANKS = ["3","4","5","6","7","8","9","10","J","Q","K","A","2"]',
        '',
        '# Rank order for comparison. 2 = 15 (highest). A = 14.',
        'RANK_ORDER = {',
        '    "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9,',
        '    "10":10, "J":11, "Q":12, "K":13, "A":14, "2":15',
        '}',
        '',
        'def create_deck() -> list[dict]:',
        '    return [{"suit":s, "rank":r} for s in SUITS for r in RANKS]',
        '    # 4 suits x 13 ranks = 52 cards total',
    ])

    story += section_header('Game logic service — services/game_logic.py', AMBER, AMBER_LIGHT)
    story += code_block([
        'import random',
        '',
        'def shuffle_and_deal(player_ids: list) -> dict[str, list]:',
        '    deck = create_deck()',
        '    random.shuffle(deck)',
        '    hands = {pid: [] for pid in player_ids}',
        '    for i, card in enumerate(deck):',
        '        hands[player_ids[i % len(player_ids)]].append(card)',
        '    return hands   # {player_id: [card, ...]}',
        '',
        'def find_first_player(hands: dict) -> str:',
        '    for pid, cards in hands.items():',
        '        if {"suit": "spades", "rank": "A"} in cards:',
        '            return pid',
        '    raise ValueError("Ace of Spades not found in any hand")',
        '',
        'def can_play(card: dict, top_card: dict | None) -> bool:',
        '    if top_card is None:',
        '        return True  # Fresh round — anything goes',
        '    if card["rank"] == "2":',
        '        return True  # 2 beats everything unconditionally',
        '    if card["suit"] != top_card["suit"]:',
        '        return False  # Must match suit (unless it is an Ace)',
        '    return RANK_ORDER[card["rank"]] > RANK_ORDER[top_card["rank"]]',
        '',
        'def get_playable_cards(hand: list, top_card: dict | None) -> list:',
        '    return [c for c in hand if can_play(c, top_card)]',
        '',
        'def remove_card(hand: list, card: dict) -> list:',
        '    hand = list(hand)',
        '    hand.remove(card)  # Raises ValueError if card not in hand',
        '    return hand',
        '',
        'def next_active_player(',
        '    current_id: str,',
        '    seat_order: list[str],   # player_ids ordered by seat',
        '    finished: set[str],',
        '    inactive: set[str]',
        ') -> str:',
        '    skip = finished | inactive',
        '    n = len(seat_order)',
        '    idx = seat_order.index(current_id)',
        '    for i in range(1, n + 1):',
        '        candidate = seat_order[(idx + i) % n]',
        '        if candidate not in skip:',
        '            return candidate',
        '    raise ValueError("No active players remaining — game should have ended")',
    ])

    story += section_header('Endpoint 4.1 — POST /api/games/start', AMBER, AMBER_LIGHT)
    story += endpoint_card('POST', '/api/games/start', 'Header: X-Player-Token (host only)', [
        '→ Body: { "room_id": "uuid" }',
        '1. Verify caller == room.host_id. 403 if not.',
        '2. Count active room_players. Must be >= 2. 422 "Need at least 2 players" if not.',
        '3. Collect player_ids in seat order (ORDER BY seat ASC).',
        '4. Call shuffle_and_deal(player_ids) to get {player_id: [cards]}',
        '5. Call find_first_player(hands) to find who has Ace of Spades',
        '6. SET room.status = "playing"',
        '7. INSERT games row with room_id, started_at=NOW()',
        '8. INSERT game_state row: current_turn=first_player, pile=[], top_card=NULL, phase="in_progress"',
        '9. INSERT one player_hands row per player with their dealt cards',
        '10. Broadcast game_started WS event. Send hand_update privately to each player with their own hand.',
        '11. Return { game_id, your_hand: [...], current_turn: "uuid", top_card: null }',
    ], AMBER, AMBER_LIGHT)

    story += section_header('Endpoint 4.2 — GET /api/games/{game_id}/state', AMBER, AMBER_LIGHT)
    story += endpoint_card('GET', '/api/games/{game_id}/state', 'Header: X-Player-Token', [
        '1. Verify player is in the game room',
        '2. Fetch game_state + all player_hands',
        '3. For other players: return only card COUNT, not card contents',
        '4. For yourself: return full hand',
        '→ Used for reconnect recovery in Phase 5. Not needed during normal play.',
        'Return: { game_id, current_turn, top_card, pile_count, your_hand, players: [{player_id, nickname, card_count, finish_rank}] }',
    ], AMBER, AMBER_LIGHT)

    story += section_header('Endpoint 4.3 — POST /api/games/{game_id}/play', AMBER, AMBER_LIGHT)
    story += endpoint_card('POST', '/api/games/{game_id}/play', 'Header: X-Player-Token', [
        '→ Body: { "card": {"suit": "hearts", "rank": "K"} }',
        '1. Verify game_state.current_turn == player.id. 400 error code NOT_YOUR_TURN if not.',
        '2. Fetch player hand from player_hands table.',
        '3. Verify card exists in hand. 400 INVALID_CARD if not.',
        '4. Call can_play(card, game_state.top_card). 400 INVALID_PLAY if false.',
        '5. Call remove_card(hand, card). Save updated hand to player_hands.',
        '6. Append card to game_state.pile. Set game_state.top_card = card.',
        '7. If hand now empty: set player_hands.finished_at=NOW(), assign finish_rank. Log "finish" move.',
        '8. Call next_active_player() to find who goes next. Update game_state.current_turn. Update turn_started_at=NOW().',
        '9. If only 1 active player remains (the Bhabbi): set game_state.phase="finished", games.ended_at, games.bhabbi_id. Broadcast game_over.',
        '10. Log "play_card" move in game_moves. Broadcast card_played WS event to all in room.',
    ], AMBER, AMBER_LIGHT)

    story += section_header('Endpoint 4.4 — POST /api/games/{game_id}/pickup', AMBER, AMBER_LIGHT)
    story += endpoint_card('POST', '/api/games/{game_id}/pickup', 'Header: X-Player-Token', [
        '1. Verify it is the player turn. 400 NOT_YOUR_TURN if not.',
        '2. (Optional) Check player has no valid card to play. Can skip — allow voluntary pickups.',
        '3. Append all cards in game_state.pile to player hand. Update player_hands.',
        '4. Set game_state.pile = [], game_state.top_card = NULL. Fresh round starts.',
        '5. Call next_active_player(). Update current_turn and turn_started_at.',
        '6. Log "pickup" move. Broadcast pickup WS event — include card COUNT picked up, NOT the cards themselves.',
    ], AMBER, AMBER_LIGHT)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5 — WEBSOCKET
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(5, 'WebSocket Real-time Layer',
        'Replace HTTP request-response with persistent bidirectional connections. Every player in a room shares one WS connection. All game events, room updates, and chat flow through this single channel.',
        PURPLE, PURPLE_LIGHT)

    story += section_header('Connection manager — ws/manager.py', PURPLE, PURPLE_LIGHT)
    story += code_block([
        'from fastapi import WebSocket',
        'import json',
        '',
        'class ConnectionManager:',
        '    def __init__(self):',
        '        # room_id -> { player_id -> WebSocket }',
        '        self._rooms: dict[str, dict[str, WebSocket]] = {}',
        '',
        '    async def connect(self, ws: WebSocket, room_id: str, player_id: str):',
        '        await ws.accept()',
        '        if room_id not in self._rooms:',
        '            self._rooms[room_id] = {}',
        '        self._rooms[room_id][player_id] = ws',
        '',
        '    def disconnect(self, room_id: str, player_id: str):',
        '        if room_id in self._rooms:',
        '            self._rooms[room_id].pop(player_id, None)',
        '            if not self._rooms[room_id]:',
        '                del self._rooms[room_id]',
        '',
        '    async def broadcast(self, room_id: str, msg: dict,',
        '                        exclude: str | None = None):',
        '        if room_id not in self._rooms: return',
        '        dead = []',
        '        for pid, ws in self._rooms[room_id].items():',
        '            if pid == exclude: continue',
        '            try:',
        '                await ws.send_json(msg)',
        '            except Exception:',
        '                dead.append(pid)',
        '        for pid in dead: self.disconnect(room_id, pid)',
        '',
        '    async def send_to(self, room_id: str, player_id: str, msg: dict):',
        '        ws = self._rooms.get(room_id, {}).get(player_id)',
        '        if ws:',
        '            try: await ws.send_json(msg)',
        '            except: self.disconnect(room_id, player_id)',
        '',
        'manager = ConnectionManager()  # singleton — import everywhere',
    ])

    story += section_header('WebSocket endpoint — WS /ws/{room_id}', PURPLE, PURPLE_LIGHT)
    story += code_block([
        '@ws_router.websocket("/ws/{room_id}")',
        'async def game_ws(ws: WebSocket, room_id: str,',
        '                  token: str = Query(...),',
        '                  db: AsyncSession = Depends(get_db)):',
        '',
        '    # 1. Authenticate',
        '    player = await get_player_by_token(db, token)',
        '    if not player:',
        '        await ws.close(code=4001); return',
        '',
        '    # 2. Verify player is in room',
        '    rp = await get_room_player(db, room_id, player.id)',
        '    if not rp or not rp.is_active:',
        '        await ws.close(code=4003); return',
        '',
        '    # 3. Connect',
        '    await manager.connect(ws, room_id, str(player.id))',
        '',
        '    # 4. Send full current state to this player (for reconnect)',
        '    state = await build_full_state(db, room_id, player.id)',
        '    await manager.send_to(room_id, str(player.id),',
        '                          {"type": "connected", **state})',
        '',
        '    # 5. Notify others that this player is present',
        '    await manager.broadcast(room_id,',
        '        {"type": "player_connected", "player_id": str(player.id),',
        '         "nickname": player.nickname}, exclude=str(player.id))',
        '',
        '    try:',
        '        while True:',
        '            data = await ws.receive_json()',
        '            await handle_message(db, room_id, player, data)',
        '    except WebSocketDisconnect:',
        '        manager.disconnect(room_id, str(player.id))',
        '        await manager.broadcast(room_id,',
        '            {"type": "player_disconnected",',
        '             "player_id": str(player.id),',
        '             "nickname": player.nickname})',
    ])

    story += section_header('Client → Server messages', PURPLE, PURPLE_LIGHT)

    story += ws_event('start_game', 'c2s', 'client → server',
        '{ "type": "start_game" }',
        'Sent by host only. Server validates caller is host, calls game start logic from Phase 4, broadcasts game_started to room.')

    story += ws_event('play_card', 'c2s', 'client → server',
        '{ "type": "play_card", "card": {"suit": "spades", "rank": "A"} }',
        'Server runs Phase 4 play logic. On success → broadcast card_played. On error → send error event to this player only.')

    story += ws_event('pickup', 'c2s', 'client → server',
        '{ "type": "pickup" }',
        'Run pickup logic. Send hand_update privately to this player. Broadcast pickup to all with card COUNT only, never card contents.')

    story += ws_event('chat', 'c2s', 'client → server',
        '{ "type": "chat", "text": "bhai bhabbi kar diya!" }',
        'Validate max 500 chars, strip whitespace. Save to chat_messages. Broadcast to all in room including sender.')

    story += ws_event('ping', 'c2s', 'client → server',
        '{ "type": "ping" }',
        'Reply immediately with pong. Frontend sends this every 30s to keep connection alive through proxies and load balancers.')

    story += ws_event('play_again', 'c2s', 'client → server',
        '{ "type": "play_again" }',
        'Host only. After game_over. Server resets game state, deals new hands, broadcasts game_started.')

    story += section_header('Server → Client messages', PURPLE, PURPLE_LIGHT)

    story += ws_event('connected', 's2c', 'server → you only',
        '{ "type": "connected",\n  "room": { ...room fields... },\n  "game": null | {\n    "current_turn": "uuid", "top_card": null | {...},\n    "pile_count": 0, "your_hand": [...],\n    "players": [{player_id, nickname, card_count, finish_rank}]\n  }\n}',
        'Sent immediately on connect/reconnect. Full state so frontend can rebuild UI from scratch.')

    story += ws_event('game_started', 's2all', 'server → broadcast + private hand_update',
        '{ "type": "game_started", "game_id": "uuid", "current_turn": "uuid",\n  "player_order": [{player_id, nickname, seat, card_count}] }\n\n// Also sends privately to each player:\n{ "type": "hand_update", "your_hand": [{suit, rank}, ...] }',
        '')

    story += ws_event('card_played', 's2all', 'server → broadcast to room',
        '{ "type": "card_played", "player_id": "uuid", "nickname": "Ali",\n  "card": {"suit": "spades", "rank": "A"},\n  "new_top_card": {"suit": "spades", "rank": "A"},\n  "pile_count": 3, "next_turn": "uuid",\n  "card_counts": {"uuid1": 7, "uuid2": 12} }',
        'Never broadcast other players card contents. Only card counts and the card just played.')

    story += ws_event('hand_update', 's2c', 'server → you only',
        '{ "type": "hand_update", "your_hand": [{"suit": "hearts", "rank": "K"}, ...] }',
        'Sent after every change to your hand — after deal, after playing, after pickup.')

    story += ws_event('pickup', 's2all', 'server → broadcast to room',
        '{ "type": "pickup", "player_id": "uuid", "nickname": "Ali",\n  "cards_picked": 6, "next_turn": "uuid",\n  "card_counts": {"uuid1": 18, "uuid2": 12} }',
        '')

    story += ws_event('player_finished', 's2all', 'server → broadcast to room',
        '{ "type": "player_finished", "player_id": "uuid",\n  "nickname": "Ali", "finish_rank": 1 }',
        '')

    story += ws_event('game_over', 's2all', 'server → broadcast to room',
        '{ "type": "game_over", "winner_id": "uuid", "bhabbi_id": "uuid",\n  "results": [{player_id, nickname, finish_rank}] }',
        '')

    story += ws_event('error', 's2c', 'server → you only',
        '{ "type": "error",\n  "code": "NOT_YOUR_TURN" | "INVALID_CARD" | "INVALID_PLAY"\n       | "GAME_NOT_STARTED" | "NOT_HOST",\n  "message": "Human readable error message" }',
        '')

    story += ws_event('room_update', 's2all', 'server → broadcast on join/leave/kick',
        '{ "type": "room_update",\n  "players": [{player_id, nickname, seat, is_active}],\n  "host_id": "uuid", "status": "waiting" }',
        '')

    story += ws_event('turn_timer', 's2all', 'server → broadcast every 5 seconds',
        '{ "type": "turn_timer", "player_id": "uuid", "seconds_left": 25 }',
        'Broadcast every 5s during a turn so all frontends can show a countdown.')

    story += ws_event('kicked', 's2c', 'server → kicked player only',
        '{ "type": "kicked", "reason": "Host removed you from the room" }',
        'Frontend should show a toast and redirect to lobby on receiving this.')
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 6 — CHAT
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(6, 'Chat System',
        'Persistent in-room chat visible across reconnects. System messages narrate game events automatically. Leverages the same WebSocket connection from Phase 5.',
        TEAL, TEAL_LIGHT)

    story += db_table('chat_messages', [
        ('id', 'UUID PK', ''),
        ('room_id', 'UUID FK → rooms', 'Indexed. Chat is room-scoped — persists during waiting and playing phases.'),
        ('player_id', 'UUID FK → players NULL', 'NULL for system messages (game narration).'),
        ('text', 'VARCHAR(500) NOT NULL', 'Stripped and trimmed server-side before saving.'),
        ('is_system', 'BOOLEAN default FALSE', 'TRUE for auto-generated game narration messages. Styled differently in frontend.'),
        ('sent_at', 'TIMESTAMP default NOW()', 'Indexed for paginated history queries.'),
    ], 'Stores all chat messages. Grows per room — add a cleanup job to prune old rooms.')

    story += section_header('Endpoint 6.1 — GET /api/rooms/{room_id}/chat', TEAL, TEAL_LIGHT)
    story += endpoint_card('GET', '/api/rooms/{room_id}/chat', 'Header: X-Player-Token', [
        '→ Query params: ?limit=50&before=ISO_TIMESTAMP (for pagination)',
        '1. Verify player is in room',
        '2. SELECT chat_messages WHERE room_id = ? AND sent_at < before ORDER BY sent_at DESC LIMIT limit',
        '3. JOIN players to get nickname for each non-system message',
        '4. Return in chronological order (reverse the DESC query result before returning)',
        '5. Return { messages: [{id, player_id, nickname, text, is_system, sent_at}], has_more: bool }',
        '→ Frontend calls this on room join to pre-load recent history before WS connects',
    ], TEAL, TEAL_LIGHT)

    story += section_header('System messages — auto-generated by server', TEAL, TEAL_LIGHT)
    story += code_block([
        'async def system_msg(db, room_id: str, text: str):',
        '    """Insert system message to DB and broadcast to room."""',
        '    msg = ChatMessage(room_id=room_id, player_id=None,',
        '                      text=text, is_system=True)',
        '    db.add(msg)',
        '    await db.commit()',
        '    await manager.broadcast(room_id, {',
        '        "type": "chat", "player_id": None, "nickname": None,',
        '        "text": text, "is_system": True, "sent_at": msg.sent_at.isoformat()',
        '    })',
        '',
        '# Call these after game events:',
        '# game_started   -> "Game started! Ali has the Ace of Spades."',
        '# card_played    -> "Ali played Ace of Hearts — fresh round!"',
        '# card "2" played-> "Bilal played 2 of Clubs — nuclear card!"',
        '# pickup         -> "Sara picked up 6 cards"',
        '# player_finished-> "Umar finished in position #1!"',
        '# game_over      -> "Hamza is the Bhabbi! Game over."',
    ])
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 7 — FRONTEND SHELL
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(7, 'Frontend Shell — Lobby & Waiting Room',
        'Next.js app setup, identity integration, lobby page (create/join room), and the pre-game waiting room. No card rendering yet — just the room setup flow end to end.',
        BLUE, BLUE_LIGHT)

    story += section_header('Next.js project structure', BLUE, BLUE_LIGHT)
    story += code_block([
        'frontend/',
        '├── app/',
        '│   ├── layout.tsx         # Root layout — wraps IdentityProvider',
        '│   ├── page.tsx           # Lobby (create / join room)',
        '│   └── room/[code]/',
        '│       └── page.tsx       # WaitingRoom + GameBoard (client component)',
        '├── components/',
        '│   ├── NicknameModal.tsx  # Blocks UI until nickname is set',
        '│   ├── Lobby.tsx          # Create room, join by code, public list',
        '│   ├── WaitingRoom.tsx    # Seat grid, player list, start button',
        '│   └── game/',
        '│       ├── GameBoard.tsx  # Center pile + turn indicator',
        '│       ├── PlayerHand.tsx # Your cards (Phase 8)',
        '│       ├── OpponentSeat.tsx',
        '│       └── GameOverModal.tsx',
        '├── components/chat/',
        '│   └── ChatPanel.tsx',
        '├── hooks/',
        '│   ├── useIdentity.ts',
        '│   └── useGameSocket.ts   # Phase 8',
        '└── lib/',
        '    ├── api.ts             # Typed fetch wrapper',
        '    └── identity.ts        # localStorage helpers',
    ])

    story += section_header('lib/api.ts — typed fetch wrapper', BLUE, BLUE_LIGHT)
    story += code_block([
        'const BASE = process.env.NEXT_PUBLIC_API_URL',
        '',
        'export const api = {',
        '  get: async (path: string, token?: string) => {',
        '    const r = await fetch(BASE + path, {',
        '      headers: token ? { "X-Player-Token": token } : {}',
        '    })',
        '    if (!r.ok) throw await r.json()',
        '    return r.json()',
        '  },',
        '  post: async (path: string, body: any, token?: string) => {',
        '    const r = await fetch(BASE + path, {',
        '      method: "POST",',
        '      headers: {',
        '        "Content-Type": "application/json",',
        '        ...(token ? { "X-Player-Token": token } : {})',
        '      },',
        '      body: JSON.stringify(body)',
        '    })',
        '    if (!r.ok) throw await r.json()',
        '    return r.json()',
        '  },',
        '}',
    ])

    story += section_header('WaitingRoom.tsx — what to build', BLUE, BLUE_LIGHT)
    story.append(P('The waiting room is the first interactive screen players share. Build these features:', 'body'))
    items = [
        'Display the room code prominently in a large monospace font so players can share it easily',
        'Show a seat grid: each seat as a card — occupied seats show the player nickname, empty seats show "Waiting..."',
        'Host sees a Start Game button, enabled only when >= 2 players are active. Show a disabled state with tooltip "Need at least 2 players"',
        'Host sees a kick button (X icon) on each other player seat card',
        'Connect the WebSocket here and listen for room_update events to refresh the player list without polling',
        'When WS sends kicked event to you: show a toast notification, then redirect to lobby after 2 seconds',
        'Show a copy-to-clipboard button next to the room code',
    ]
    story += info_box('WaitingRoom component checklist', items, BLUE, BLUE_LIGHT)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 8 — GAME UI
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(8, 'Game UI — Cards, Board & Live Play',
        'The actual card game interface. Players see their hand, the pile, whose turn it is, and can play cards or pick up. Everything driven by the WebSocket hook.',
        PURPLE, PURPLE_LIGHT)

    story += section_header('useGameSocket hook — hooks/useGameSocket.ts', PURPLE, PURPLE_LIGHT)
    story += code_block([
        'export function useGameSocket(roomId: string) {',
        '  const token = getToken()',
        '  const wsRef = useRef<WebSocket>()',
        '',
        '  const [gameState, setGameState] = useState<GameState|null>(null)',
        '  const [hand, setHand] = useState<Card[]>([])',
        '  const [messages, setMessages] = useState<ChatMsg[]>([])',
        '  const [connected, setConnected] = useState(false)',
        '',
        '  useEffect(() => {',
        '    const WS_URL = process.env.NEXT_PUBLIC_WS_URL',
        '    const ws = new WebSocket(`${WS_URL}/ws/${roomId}?token=${token}`)',
        '    wsRef.current = ws',
        '',
        '    ws.onopen = () => setConnected(true)',
        '    ws.onclose = (e) => {',
        '      setConnected(false)',
        '      if (e.code !== 1000) setTimeout(reconnect, 2000)  // auto-reconnect',
        '    }',
        '    ws.onmessage = (e) => {',
        '      const msg = JSON.parse(e.data)',
        '      switch(msg.type) {',
        '        case "connected":      handleConnected(msg); break',
        '        case "game_started":   setGameState(msg); break',
        '        case "card_played":    handleCardPlayed(msg); break',
        '        case "hand_update":    setHand(msg.your_hand); break',
        '        case "pickup":         handlePickup(msg); break',
        '        case "player_finished":handleFinish(msg); break',
        '        case "game_over":      handleGameOver(msg); break',
        '        case "chat":           setMessages(m => [...m, msg]); break',
        '        case "room_update":    handleRoomUpdate(msg); break',
        '        case "error":          toast.error(msg.message); break',
        '        case "turn_timer":     setSecondsLeft(msg.seconds_left); break',
        '      }',
        '    }',
        '    // Ping every 30s to keep connection alive',
        '    const pingInterval = setInterval(() =>',
        '      ws.readyState === 1 && ws.send(JSON.stringify({type:"ping"})), 30000)',
        '    return () => { clearInterval(pingInterval); ws.close(1000) }',
        '  }, [roomId])',
        '',
        '  const playCard = (card: Card) =>',
        '    wsRef.current?.send(JSON.stringify({type:"play_card", card}))',
        '  const pickup = () =>',
        '    wsRef.current?.send(JSON.stringify({type:"pickup"}))',
        '  const sendChat = (text: string) =>',
        '    wsRef.current?.send(JSON.stringify({type:"chat", text}))',
        '  const startGame = () =>',
        '    wsRef.current?.send(JSON.stringify({type:"start_game"}))',
        '',
        '  return { gameState, hand, messages, connected,',
        '           playCard, pickup, sendChat, startGame }',
        '}',
    ])

    story += section_header('PlayerHand.tsx — card display logic', PURPLE, PURPLE_LIGHT)
    items = [
        'Render cards in a horizontal fan at the bottom. Apply slight CSS rotation to each card based on its index position for arc effect.',
        'Implement can_play() in TypeScript too (same logic as backend) to highlight playable cards client-side without a round-trip.',
        'Playable cards: bright border, cursor pointer, slight scale-up on hover.',
        'Non-playable cards: opacity 0.4, cursor not-allowed. Do not let them be clicked.',
        'On card click: only fires if it is your turn AND card is playable. Send play_card WS message. Optimistically remove from hand immediately. Add it back if server sends an error response.',
        'Card component: suit symbols rendered as Unicode (spades, hearts, diamonds, clubs). Red fill for hearts and diamonds. Black for spades and clubs.',
        'Show rank in top-left and bottom-right of each card face.',
    ]
    story += info_box('PlayerHand component implementation', items, PURPLE, PURPLE_LIGHT)

    story += section_header('GameBoard.tsx — center table', PURPLE, PURPLE_LIGHT)
    items = [
        'Pile display: show top card face-up in the center of the screen. If pile > 1, fan 2–3 card backs behind it for visual depth.',
        'Fresh round indicator: when top_card is null, show a subtle "Play anything" text in the pile area.',
        'Turn indicator: pulsing ring or colored border around the active player seat. Show "Your turn!" banner if it is you.',
        'Pick Up button: large red button, enabled only when it is your turn. Clicking calls pickup(). Optimistically clear pile in UI and show cards flying to hand animation.',
        'Card counts: small badge on each opponent seat showing remaining card count. Updates on every WS event.',
        'Turn timer: show countdown ring around the active player avatar when timer is under 10 seconds.',
    ]
    story += info_box('GameBoard component implementation', items, PURPLE, PURPLE_LIGHT)

    story += section_header('ChatPanel.tsx — sidebar', PURPLE, PURPLE_LIGHT)
    items = [
        'Fixed right sidebar, 300px wide on desktop. Full-screen overlay triggered by a button on mobile.',
        'Pre-load chat history on mount: GET /api/rooms/{room_id}/chat?limit=50.',
        'System messages: gray italic text, no avatar, slightly smaller font.',
        'Player messages: player initial avatar circle + nickname bold + message text.',
        'Input at bottom. Send on Enter key (not Shift+Enter which inserts newline). Character counter showing X/500.',
        'Auto-scroll to bottom when new message arrives ONLY if user is within 100px of the bottom — do not hijack scroll if they are reading older messages.',
    ]
    story += info_box('ChatPanel component implementation', items, PURPLE, PURPLE_LIGHT)
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 9 — EDGE CASES
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(9, 'Edge Cases, Timers & Reconnection',
        'The game should never get stuck. Handle every way a player can disappear, time out, or misbehave. These are the scenarios that break untested multiplayer games.',
        RED, RED_LIGHT)

    edge_cases = [
        ('Player disconnects mid-game', [
            'On WebSocketDisconnect: broadcast player_disconnected to room. Do NOT immediately end the game.',
            'Start a 60-second reconnect window. Store disconnect_at timestamp in Redis or an in-memory dict keyed by player_id.',
            'If they reconnect within 60s: send full connected state event. They resume normally. Broadcast player_reconnected.',
            'If 60s elapses and it is their turn: trigger auto-pickup (same logic as manual pickup). Broadcast with reason: "timeout".',
            'If 60s elapses and it is not their turn: continue game normally, skip them each time their turn comes.',
        ]),
        ('Turn timer — 30 seconds per turn', [
            'On every turn change: set game_state.turn_started_at = NOW(). Create an asyncio.Task that fires after 30s.',
            'Every 5 seconds broadcast turn_timer event so all frontends show a countdown.',
            'If timer fires: run auto-pickup for the current player. Log as timeout_pickup move type.',
            'Cancel the old task and restart on every move. Store tasks in a dict keyed by game_id.',
            'Implementation: asyncio.create_task(turn_timer_coro(game_id, player_id, 30))',
        ]),
        ('Host leaves room — pre-game', [
            'Find next active player by seat order: seat 1 first, then 2, etc.',
            'UPDATE rooms SET host_id = next_player.player_id',
            'Broadcast room_update with new host_id so frontend updates the Start Game button visibility.',
            'If no other players remain: DELETE the room entirely.',
        ]),
        ('Host leaves mid-game', [
            'Host has no special powers during a game — no need to transfer host role.',
            'Mark host player inactive. Skip their turns. Game continues normally.',
            'If only 1 active player remains after host leaves: trigger game over with that player as Bhabbi.',
        ]),
        ('Play Again flow', [
            'Host sends { "type": "play_again" } WS event after game_over.',
            'Verify game phase = "finished". 400 if not.',
            'INSERT new game row. Clear game_state (reset pile, top_card, current_turn). Deal new hands.',
            'SET room.status = "playing". Broadcast game_started with new game data.',
            'Send private hand_update to each player with their new hand.',
            'Frontend GameOverModal listens for game_started event: close modal, reset game UI.',
        ]),
        ('All players disconnect simultaneously', [
            'Room and game state remain in DB.',
            'If all reconnect within 60s: game resumes normally.',
            'If no one reconnects: stale cleanup cron (hourly) marks game as abandoned.',
            'Room status set to "finished" by cleanup job.',
        ]),
        ('Only one active player remains (forced Bhabbi)', [
            'After every pickup, disconnect, or auto-skip: check if only 1 non-finished, active player remains.',
            'If yes: they are the Bhabbi by default. SET games.bhabbi_id. SET game_state.phase="finished".',
            'Broadcast game_over immediately. No further turns.',
        ]),
        ('Stale room cleanup cron', [
            'Add a background task (asyncio loop or APScheduler) running every hour.',
            'DELETE rooms WHERE status="waiting" AND created_at < NOW() - INTERVAL 24 hours AND no active WS connections.',
            'DELETE rooms WHERE status="playing" AND game_state.updated_at < NOW() - INTERVAL 3 hours (abandoned games).',
            'CASCADE deletes handle room_players, game_state, player_hands automatically.',
        ]),
    ]

    for title, steps in edge_cases:
        story.append(KeepTogether([
            P(title, 'h4'),
        ] + [P(f'{i+1}. {step}', 'step') for i, step in enumerate(steps)] + [Spacer(1, 8)]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 10 — DEPLOYMENT
    # ═══════════════════════════════════════════════════════════════════════════
    story += phase_cover(10, 'Docker, Deployment & Production',
        'Containerize everything, set up environment configs, and ship. Use Docker Compose locally. Deploy backend to Railway or Render, frontend to Vercel.',
        CORAL, CORAL_LIGHT)

    story += section_header('docker-compose.yml — full development stack', CORAL, CORAL_LIGHT)
    story += code_block([
        'services:',
        '  db:',
        '    image: postgres:16-alpine',
        '    environment:',
        '      POSTGRES_DB: bhabbi',
        '      POSTGRES_USER: bhabbi',
        '      POSTGRES_PASSWORD: bhabbi',
        '    ports: ["5432:5432"]',
        '    volumes: [pgdata:/var/lib/postgresql/data]',
        '    healthcheck:',
        '      test: ["CMD-SHELL", "pg_isready -U bhabbi"]',
        '      interval: 5s',
        '      retries: 5',
        '',
        '  redis:',
        '    image: redis:7-alpine',
        '    ports: ["6379:6379"]',
        '',
        '  backend:',
        '    build: ./backend',
        '    environment:',
        '      DATABASE_URL: postgresql+asyncpg://bhabbi:bhabbi@db/bhabbi',
        '      REDIS_URL: redis://redis:6379',
        '    ports: ["8000:8000"]',
        '    depends_on:',
        '      db: {condition: service_healthy}',
        '      redis: {condition: service_started}',
        '    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload',
        '    volumes: [./backend:/app]',
        '',
        '  frontend:',
        '    build: ./frontend',
        '    environment:',
        '      NEXT_PUBLIC_API_URL: http://localhost:8000/api',
        '      NEXT_PUBLIC_WS_URL: ws://localhost:8000',
        '    ports: ["3000:3000"]',
        '    depends_on: [backend]',
        '',
        'volumes:',
        '  pgdata:',
    ])

    story += section_header('backend/Dockerfile', CORAL, CORAL_LIGHT)
    story += code_block([
        'FROM python:3.12-slim',
        'WORKDIR /app',
        'COPY requirements.txt .',
        'RUN pip install --no-cache-dir -r requirements.txt',
        'COPY . .',
        'CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]',
    ])

    story += section_header('Redis pub-sub for multi-instance WebSocket', CORAL, CORAL_LIGHT)
    story.append(P('When running 2+ backend instances (for reliability/scale), a WebSocket client connected to instance A cannot be reached by code running on instance B. Redis pub-sub bridges them.', 'body'))
    story += code_block([
        'import redis.asyncio as aioredis',
        '',
        'redis = aioredis.from_url(settings.REDIS_URL)',
        '',
        'async def broadcast_via_redis(room_id: str, msg: dict):',
        '    """Publish to Redis — all instances will receive and deliver."""',
        '    await redis.publish(f"room:{room_id}", json.dumps(msg))',
        '',
        'async def start_redis_subscriber(room_id: str):',
        '    """Each instance subscribes to rooms it has live clients for."""',
        '    pubsub = redis.pubsub()',
        '    await pubsub.subscribe(f"room:{room_id}")',
        '    async for message in pubsub.listen():',
        '        if message["type"] == "message":',
        '            data = json.loads(message["data"])',
        '            # Deliver to local WS clients only',
        '            await manager.broadcast(room_id, data)',
    ])

    story += section_header('Production environment variables', CORAL, CORAL_LIGHT)
    story += code_block([
        '# Backend .env',
        'DATABASE_URL=postgresql+asyncpg://user:pass@host/bhabbi',
        'REDIS_URL=redis://redis-host:6379',
        'SECRET_KEY=a-very-long-random-string-generated-with-openssl-rand',
        'MAX_ROOM_SIZE=6',
        'TURN_TIMEOUT_SECONDS=30',
        '',
        '# Frontend .env.production',
        'NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api',
        'NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com',
    ])

    story += section_header('Production go-live checklist', CORAL, CORAL_LIGHT)
    checklist = [
        'Change CORS allow_origins from * to your exact frontend domain only',
        'Set SECRET_KEY to a long random string. Generate with: openssl rand -hex 32',
        'Use HTTPS and WSS in production. WebSocket over plain HTTP is blocked by browsers on HTTPS pages.',
        'Set DB_POOL_SIZE and DB_MAX_OVERFLOW on SQLAlchemy engine for production load.',
        'Add rate limiting on POST /api/rooms/create (max 5 per minute per IP) to prevent spam.',
        'Run alembic upgrade head as part of your deployment process, not inside the Dockerfile.',
        'Set up periodic PostgreSQL backups. Railway and Render both have this built in.',
        'Add sentry-sdk error tracking to both backend (FastAPI middleware) and frontend (Next.js).',
        'Configure health check endpoint for your load balancer / deploy platform.',
        'Test WebSocket reconnection manually by disabling network for 30 seconds mid-game.',
    ]
    story += info_box('Before going live', checklist, CORAL, CORAL_LIGHT)

    # ── ENDPOINT REFERENCE TABLE ──────────────────────────────────────────────
    story.append(PageBreak())
    story.append(P('Complete Endpoint Reference', 'h2'))
    story.append(HLine(16.5*cm, PURPLE_LIGHT))
    story.append(Spacer(1, 8))

    all_endpoints = [
        ['Method', 'Path', 'Auth', 'Phase', 'Description'],
        ['POST', '/api/identity/register', 'None', '2', 'Create guest identity, get player token'],
        ['GET', '/api/identity/me', 'Token', '2', 'Validate token, get my profile'],
        ['PATCH', '/api/identity/me', 'Token', '2', 'Update nickname'],
        ['POST', '/api/rooms/create', 'Token', '3', 'Create a room, get 6-char code'],
        ['POST', '/api/rooms/join', 'Token', '3', 'Join room by code'],
        ['GET', '/api/rooms/{room_id}', 'Token', '3', 'Get room details and player list'],
        ['GET', '/api/rooms/public', 'None', '3', 'List open public rooms'],
        ['POST', '/api/rooms/{room_id}/leave', 'Token', '3', 'Leave a room'],
        ['POST', '/api/rooms/{room_id}/kick', 'Token (host)', '3', 'Kick a player (host only, pre-game)'],
        ['POST', '/api/games/start', 'Token (host)', '4', 'Deal cards, start the game'],
        ['GET', '/api/games/{game_id}/state', 'Token', '4', 'Get current game state (reconnect)'],
        ['POST', '/api/games/{game_id}/play', 'Token', '4', 'Play a card (HTTP fallback)'],
        ['POST', '/api/games/{game_id}/pickup', 'Token', '4', 'Pick up pile (HTTP fallback)'],
        ['GET', '/api/rooms/{room_id}/chat', 'Token', '6', 'Load chat history (paginated)'],
        ['WS', '/ws/{room_id}?token=...', 'Query param', '5', 'Primary real-time connection'],
        ['GET', '/api/health', 'None', '1', 'Health check for load balancer'],
    ]
    ep_tbl = Table(all_endpoints, colWidths=[1.5*cm, 5*cm, 2.5*cm, 1.2*cm, 6.3*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PURPLE_DARK),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, PURPLE_LIGHT]),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, PURPLE),
            ('INNERGRID', (0,0), (-1,-1), 0.3, GRAY_LIGHT),
            ('FONTNAME', (0,1), (1,-1), 'Courier'),
        ]))
    story.append(ep_tbl)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF written to {path}")

build_pdf('bhabbi_roadmap.pdf')

