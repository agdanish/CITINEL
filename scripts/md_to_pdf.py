"""Render the walkthrough markdown to a Times New Roman PDF.

Dark ink only, per the brief. Colour is used to separate three things a reader must
never confuse: a heading, a sentence that is safe to say, and a sentence that must
never be said. Everything else is black.
"""
import re, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

NAVY  = colors.HexColor('#0B1F3A')
GREEN = colors.HexColor('#14532d')
RED   = colors.HexColor('#7f1d1d')
AMBER = colors.HexColor('#7c4a03')
GREY  = colors.HexColor('#3f4a58')
RULE  = colors.HexColor('#c9d2de')
WASH  = colors.HexColor('#f2f5f9')

def st(name, **kw):
    base = dict(fontName='Times-Roman', fontSize=10.5, leading=14.5,
                textColor=colors.HexColor('#101720'), spaceAfter=5)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
 'h1':   st('h1', fontName='Times-Bold', fontSize=21, leading=25, textColor=NAVY,
            spaceBefore=16, spaceAfter=9),
 'h2':   st('h2', fontName='Times-Bold', fontSize=15.5, leading=19, textColor=NAVY,
            spaceBefore=15, spaceAfter=6),
 'h3':   st('h3', fontName='Times-Bold', fontSize=12.5, leading=16, textColor=NAVY,
            spaceBefore=10, spaceAfter=4),
 'h4':   st('h4', fontName='Times-BoldItalic', fontSize=11, leading=14,
            textColor=GREY, spaceBefore=7, spaceAfter=3),
 'body': st('body'),
 'li':   st('li', leftIndent=13, bulletIndent=4, spaceAfter=3.2),
 'num':  st('num', leftIndent=17, bulletIndent=4, spaceAfter=3.2),
 'say':  st('say', textColor=GREEN, leftIndent=9, borderPadding=2),
 'never':st('never', textColor=RED, fontName='Times-Bold', leftIndent=9),
 'warn': st('warn', textColor=AMBER, leftIndent=9),
 'quote':st('quote', fontName='Times-Italic', textColor=GREY, leftIndent=9),
}

def inline(t):
    t = (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
    # !!...!! marks one of the forty catalogued items. They are the reason this
    # document exists, so they carry the only strong colour in the body text.
    t = re.sub(r'!!(.+?)!!', r'<font color="#8B0000"><b>\1</b></font>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![*\w])\*(?![*\s])(.+?)(?<![\s*])\*(?![*\w])', r'<i>\1</i>', t, flags=re.S)
    t = re.sub(r'`(.+?)`', r'<font face="Courier" size="9.2">\1</font>', t)
    t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    # The red marker becomes the word NEVER, unless the sentence already opens with
    # it, which several do. "NEVER: NEVER SAY" reads like a stutter on paper.
    t = t.replace('\U0001F7E2', 'SAY: ')
    t = t.replace('\U0001F7E1', 'CAUTION: ')
    t = re.sub(r'\U0001F534\s*(?=(<b>)?NEVER)', '', t)
    t = t.replace('\U0001F534', 'NEVER: ')
    return t

def build(md, out):
    flow, rows, intable = [], [], False
    buf = []

    def flush():
        if not buf:
            return
        s = ' '.join(buf).strip()
        buf.clear()
        style = 'body'
        if s.startswith('\U0001F7E2'): style = 'say'
        elif s.startswith('\U0001F534') or s.startswith('**NEVER'): style = 'never'
        elif s.startswith('\U0001F7E1'): style = 'warn'
        elif s.startswith('*') and s.endswith('*') and not s.startswith('**'):
            style = 'quote'; s = s[1:-1]
        flow.append(Paragraph(inline(s), S[style]))

    for raw in md.split('\n'):
        line = raw.rstrip()
        if line.startswith('|'):
            flush()
            cells = [c.strip() for c in line.strip('|').split('|')]
            if set(''.join(cells)) <= set('-: '):
                continue
            rows.append([Paragraph(inline(c), S['body']) for c in cells])
            intable = True
            continue
        if intable and not line.startswith('|'):
            if rows:
                n = max(len(r) for r in rows)
                w = [ (168*mm)/n ] * n
                t = Table(rows, colWidths=w, repeatRows=1)
                t.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.4, RULE),
                    ('BACKGROUND', (0,0), (-1,0), WASH),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
                flow.append(t); flow.append(Spacer(1, 7))
            rows, intable = [], False
        if not line.strip():
            flush(); continue
        if line.startswith('---'):
            flush(); flow.append(Spacer(1, 4)); continue
        if line.startswith('#'):
            flush()
            lvl = len(line) - len(line.lstrip('#'))
            key = {1:'h1', 2:'h2', 3:'h3'}.get(lvl, 'h4')
            flow.append(Paragraph(inline(line.lstrip('# ').strip()), S[key]))
            continue
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        if m:
            flush()
            flow.append(Paragraph(inline(m.group(2)), S['num'], bulletText=m.group(1)+'.'))
            continue
        if line.startswith('- '):
            flush()
            flow.append(Paragraph(inline(line[2:]), S['li'], bulletText='•'))
            continue
        st_line = line.strip()
        # a coloured line is its own paragraph; anything else accumulates
        if st_line.startswith(('\U0001F7E2', '\U0001F534', '\U0001F7E1')):
            flush(); buf.append(st_line); flush()
        else:
            buf.append(st_line)
    flush()
    return flow

def deco(canv, doc):
    canv.saveState()
    canv.setStrokeColor(RULE); canv.setLineWidth(0.5)
    canv.line(20*mm, 285*mm, 190*mm, 285*mm)
    canv.setFont('Times-Bold', 8.5); canv.setFillColor(NAVY)
    canv.drawString(20*mm, 288*mm, 'CITINEL')
    canv.setFont('Times-Roman', 8.5); canv.setFillColor(GREY)
    canv.drawRightString(190*mm, 288*mm, 'Operator walkthrough and differentiator map  ·  Decode SIH 2026')
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    canv.setFont('Times-Roman', 8.5)
    canv.drawCentredString(105*mm, 10*mm, 'Page %d' % doc.page)
    canv.restoreState()

md = open(sys.argv[1]).read()
out = sys.argv[2]
doc = BaseDocTemplate(out, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm,
                      topMargin=22*mm, bottomMargin=20*mm, title='CITINEL: operator walkthrough and differentiator map',
                      author='CITINEL')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(20*mm, 18*mm, 170*mm, 262*mm, id='f')],
                                   onPage=deco)])
doc.build(build(md, out))
print('written', out)
