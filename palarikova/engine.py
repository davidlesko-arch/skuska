# -*- coding: utf-8 -*-
"""Kresliaci engine pre pôdorysy štúdie BD Palárikova (reportlab, A3, 1:100)."""
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("F", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("FB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

MM = 2.83465
PW, PH = landscape(A3)

C = dict(
    struct=HexColor("#7d7d7d"), part=HexColor("#9a9a9a"), new=HexColor("#d8402f"),
    ink=HexColor("#1f2d3d"), dim=HexColor("#2f5d8a"), grid=HexColor("#c9ced6"),
    common=HexColor("#ecebe6"), terr=HexColor("#f5efd9"), green=HexColor("#dfe9cf"),
    park=HexColor("#f4f4f4"), split=HexColor("#b0188f"),
    t1=HexColor("#dce9f5"), t2=HexColor("#e2efda"), t3=HexColor("#fbe9d0"),
    t4=HexColor("#e9e1f3"), nb=HexColor("#d6eeee"), furn=HexColor("#6b7785"),
    win=HexColor("#2f79b5"),
)
TYPCOL = {"1": "t1", "2": "t2", "3": "t3", "4": "t4", "nb": "nb"}


def r(x1, y1, x2, y2):
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def area(rects):
    return sum((b[2] - b[0]) * (b[3] - b[1]) for b in rects)


class Room:
    def __init__(self, name, rects, lab=None, small=False, hide=False):
        self.name = name
        self.rects = rects if isinstance(rects, list) else [rects]
        self.lab = lab
        self.small = small
        self.hide = hide

    @property
    def a(self):
        return area(self.rects)


class Flat:
    def __init__(self, fid, typ, tname, rooms, ext="–", note="", head=None, count=True):
        self.id, self.typ, self.tname, self.rooms = fid, typ, tname, rooms
        self.ext, self.note, self.head, self.count = ext, note, head, count

    @property
    def a(self):
        return sum(x.a for x in self.rooms)


class Plan:
    """Jeden pôdorys: zbiera prvky a vykreslí ich v správnom poradí."""

    def __init__(self):
        self.flats, self.common, self.terr = [], [], []
        self.struct, self.new, self.part, self.newpart = [], [], [], []
        self.doors, self.windows, self.furn = [], [], []
        self.splits, self.texts, self.extra, self.fills = [], [], [], []
        self.dims = []

    # ---------- transformácia ----------
    ox, oy = 28.0, 250.0  # mm

    def X(self, x):
        return (self.ox + x * 10) * MM

    def Y(self, y):
        return (self.oy - y * 10) * MM

    def rect(self, c, b, fill=None, stroke=None, lw=0.3):
        x1, y1, x2, y2 = b
        if fill is not None:
            c.setFillColor(fill)
        if stroke is not None:
            c.setStrokeColor(stroke)
            c.setLineWidth(lw)
        c.rect(self.X(x1), self.Y(y2), (x2 - x1) * 10 * MM, (y2 - y1) * 10 * MM,
               fill=1 if fill is not None else 0, stroke=1 if stroke is not None else 0)

    def line(self, c, x1, y1, x2, y2, col=None, lw=0.3, dash=None):
        if col is not None:
            c.setStrokeColor(col)
        c.setLineWidth(lw)
        c.setDash(dash or [])
        c.line(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2))
        c.setDash([])

    def text(self, c, x, y, s, size=5, bold=False, col=None, align="c"):
        c.setFont("FB" if bold else "F", size)
        c.setFillColor(col or C["ink"])
        if align == "c":
            c.drawCentredString(self.X(x), self.Y(y), s)
        elif align == "l":
            c.drawString(self.X(x), self.Y(y), s)
        else:
            c.drawRightString(self.X(x), self.Y(y), s)

    # ---------- nábytok ----------
    def f_kitchen(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)
        x1, y1, x2, y2 = b
        horiz = (x2 - x1) >= (y2 - y1)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        c.setStrokeColor(C["furn"])
        c.setLineWidth(0.3)
        if horiz:
            self.rect(c, r(x1 + 0.15, cy - 0.17, x1 + 0.6, cy + 0.17), stroke=C["furn"])
            for i in range(2):
                c.circle(self.X(x2 - 0.25 - i * 0.3), self.Y(cy), 0.1 * 10 * MM, fill=0)
        else:
            self.rect(c, r(cx - 0.17, y1 + 0.15, cx + 0.17, y1 + 0.6), stroke=C["furn"])
            for i in range(2):
                c.circle(self.X(cx), self.Y(y2 - 0.25 - i * 0.3), 0.1 * 10 * MM, fill=0)

    def f_bed(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)
        x1, y1, x2, y2 = b
        if (x2 - x1) >= (y2 - y1):  # hlava vľavo
            n = 2 if (y2 - y1) > 1.3 else 1
            h = (y2 - y1) / n
            for i in range(n):
                self.rect(c, r(x1 + 0.08, y1 + i * h + 0.1, x1 + 0.45, y1 + (i + 1) * h - 0.1), stroke=C["furn"])
        else:  # hlava hore
            n = 2 if (x2 - x1) > 1.3 else 1
            w = (x2 - x1) / n
            for i in range(n):
                self.rect(c, r(x1 + i * w + 0.1, y1 + 0.08, x1 + (i + 1) * w - 0.1, y1 + 0.45), stroke=C["furn"])

    def f_box(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)

    def f_table(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)
        x1, y1, x2, y2 = b
        if (x2 - x1) >= (y2 - y1):
            n = max(1, int((x2 - x1) / 0.6))
            for i in range(n):
                cx = x1 + (i + 0.5) * (x2 - x1) / n
                self.rect(c, r(cx - 0.2, y1 - 0.42, cx + 0.2, y1 - 0.07), fill=white, stroke=C["furn"])
                self.rect(c, r(cx - 0.2, y2 + 0.07, cx + 0.2, y2 + 0.42), fill=white, stroke=C["furn"])
        else:
            n = max(1, int((y2 - y1) / 0.6))
            for i in range(n):
                cy = y1 + (i + 0.5) * (y2 - y1) / n
                self.rect(c, r(x1 - 0.42, cy - 0.2, x1 - 0.07, cy + 0.2), fill=white, stroke=C["furn"])
                self.rect(c, r(x2 + 0.07, cy - 0.2, x2 + 0.42, cy + 0.2), fill=white, stroke=C["furn"])

    def f_shower(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)
        self.line(c, b[0], b[1], b[2], b[3], C["furn"], 0.25)
        self.line(c, b[0], b[3], b[2], b[1], C["furn"], 0.25)

    def f_bath(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)
        c.setStrokeColor(C["furn"])
        c.roundRect(self.X(b[0] + 0.07), self.Y(b[3] - 0.07), (b[2] - b[0] - 0.14) * 10 * MM,
                    (b[3] - b[1] - 0.14) * 10 * MM, 1.2 * MM, fill=0, stroke=1)

    def f_wc(self, c, b):
        c.setFillColor(white)
        c.setStrokeColor(C["furn"])
        c.setLineWidth(0.35)
        c.ellipse(self.X(b[0]), self.Y(b[3]), self.X(b[2]), self.Y(b[1]), fill=1, stroke=1)

    def f_basin(self, c, b):
        self.rect(c, b, fill=white, stroke=C["furn"], lw=0.35)
        c.ellipse(self.X(b[0] + 0.08), self.Y(b[3] - 0.08), self.X(b[2] - 0.08), self.Y(b[1] + 0.08), fill=0, stroke=1)

    def f_tub(self, c, b):  # vírivka
        c.setFillColor(HexColor("#cfe6f2"))
        c.setStrokeColor(C["win"])
        c.setLineWidth(0.5)
        c.roundRect(self.X(b[0]), self.Y(b[3]), (b[2] - b[0]) * 10 * MM, (b[3] - b[1]) * 10 * MM, 3 * MM, fill=1, stroke=1)

    # ---------- dvere / okná ----------
    def draw_door(self, c, d):
        b, hinge, dr = d[0], d[1], d[2]
        bg = d[3] if len(d) > 3 else white
        x1, y1, x2, y2 = b
        self.rect(c, b, fill=bg)
        if hinge is None:
            return
        c.setStrokeColor(C["ink"])
        c.setLineWidth(0.3)
        horiz = (x2 - x1) >= (y2 - y1)
        if horiz:
            w = x2 - x1
            hx = x1 if hinge == "l" else x2
            hy = y2 if dr > 0 else y1
            ex, ey = hx, hy + dr * w  # otvorené krídlo
            a0 = 0 if hinge == "l" else 180
            pts = []
            for i in range(0, 13):
                t = math.radians(i * 7.5)
                px = hx + (1 if hinge == "l" else -1) * w * math.cos(t)
                py = hy + dr * w * math.sin(t)
                pts.append((px, py))
        else:
            w = y2 - y1
            hy = y1 if hinge == "t" else y2
            hx = x2 if dr > 0 else x1
            ex, ey = hx + dr * w, hy
            pts = []
            for i in range(0, 13):
                t = math.radians(i * 7.5)
                py = hy + (1 if hinge == "t" else -1) * w * math.cos(t)
                px = hx + dr * w * math.sin(t)
                pts.append((px, py))
        c.line(self.X(hx), self.Y(hy), self.X(ex), self.Y(ey))
        c.setDash([1.2, 1])
        p = c.beginPath()
        p.moveTo(self.X(pts[0][0]), self.Y(pts[0][1]))
        for q in pts[1:]:
            p.lineTo(self.X(q[0]), self.Y(q[1]))
        c.drawPath(p, stroke=1, fill=0)
        c.setDash([])

    def draw_window(self, c, b):
        self.rect(c, b, fill=white, stroke=C["win"], lw=0.35)
        x1, y1, x2, y2 = b
        if (x2 - x1) >= (y2 - y1):
            m = (y1 + y2) / 2
            self.line(c, x1, m - 0.04, x2, m - 0.04, C["win"], 0.4)
            self.line(c, x1, m + 0.04, x2, m + 0.04, C["win"], 0.4)
        else:
            m = (x1 + x2) / 2
            self.line(c, m - 0.04, y1, m - 0.04, y2, C["win"], 0.4)
            self.line(c, m + 0.04, y1, m + 0.04, y2, C["win"], 0.4)

    # ---------- kóty ----------
    def dim_h(self, c, y, xs, size=4.2):
        c.setStrokeColor(C["dim"])
        c.setLineWidth(0.3)
        self.line(c, xs[0], y, xs[-1], y, C["dim"], 0.3)
        for x in xs:
            c.line(self.X(x) - 2, self.Y(y) - 2, self.X(x) + 2, self.Y(y) + 2)
        for a, b in zip(xs, xs[1:]):
            if b - a >= 0.39:
                self.text(c, (a + b) / 2, y - 0.12, f"{round((b - a) * 1000):,}".replace(",", " "), size, col=C["dim"])

    def dim_v(self, c, x, ys, size=4.2):
        self.line(c, x, ys[0], x, ys[-1], C["dim"], 0.3)
        for y in ys:
            c.line(self.X(x) - 2, self.Y(y) - 2, self.X(x) + 2, self.Y(y) + 2)
        for a, b in zip(ys, ys[1:]):
            if b - a >= 0.39:
                c.saveState()
                c.translate(self.X(x - 0.12), self.Y((a + b) / 2))
                c.rotate(90)
                c.setFont("F", size)
                c.setFillColor(C["dim"])
                c.drawCentredString(0, 0, f"{round((b - a) * 1000):,}".replace(",", " "))
                c.restoreState()

    # ---------- hlavné vykreslenie ----------
    def draw(self, c):
        for rects, col in self.fills:
            for b in rects:
                self.rect(c, b, fill=col)
        for name, b, col in self.terr:
            self.rect(c, b, fill=C[col], stroke=HexColor("#b9ad7d"), lw=0.3)
        for name, rects in self.common:
            for b in rects:
                self.rect(c, b, fill=C["common"])
        for f in self.flats:
            for rm in f.rooms:
                for b in rm.rects:
                    self.rect(c, b, fill=C[TYPCOL[f.typ]])
        for kind, b in self.furn:
            getattr(self, "f_" + kind)(c, b)
        for b in self.part:
            self.rect(c, b, fill=C["part"])
        for b in self.newpart:
            self.rect(c, b, fill=C["new"])
        for b in self.struct:
            self.rect(c, b, fill=C["struct"])
        for b in self.new:
            self.rect(c, b, fill=C["new"])
        for d in self.doors:
            self.draw_door(c, d)
        for b in self.windows:
            self.draw_window(c, b)
        for fn in self.extra:
            fn(self, c)
        for (x1, y1, x2, y2) in self.splits:
            self.line(c, x1, y1, x2, y2, C["split"], 1.1, [4, 2.5])
        # popisy miestností
        for name, rects in self.common:
            b = rects[0]
            self.text(c, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2 - 0.05, name, 4.6)
            self.text(c, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2 + 0.22, f"{area(rects):.2f} m²".replace(".", ","), 4.2)
        for name, b, col in self.terr:
            if name:
                self.text(c, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2 - 0.02, name, 4.4)
                self.text(c, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2 + 0.24, f"{area([b]):.1f} m²".replace(".", ","), 4.0)
        for f in self.flats:
            for rm in f.rooms:
                if rm.hide:
                    continue
                b = rm.rects[0]
                lx, ly = rm.lab if rm.lab else ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
                if rm.small:
                    self.text(c, lx, ly - 0.02, rm.name, 3.8)
                    self.text(c, lx, ly + 0.2, f"{rm.a:.1f}".replace(".", ","), 3.6)
                else:
                    self.text(c, lx, ly - 0.02, rm.name, 4.6)
                    self.text(c, lx, ly + 0.24, f"{rm.a:.2f} m²".replace(".", ","), 4.2)
            if f.head:
                hx, hy = f.head
                self.text(c, hx, hy, f.id, 7.5, bold=True)
                self.text(c, hx, hy + 0.36, f.tname + " · " + f"{f.a:.1f}".replace(".", ",") + " m²", 5, bold=True)
        for t in self.texts:
            self.text(c, *t[:3], **(t[3] if len(t) > 3 else {}))
        for d in self.dims:
            if d[0] == "h":
                self.dim_h(c, d[1], d[2])
            else:
                self.dim_v(c, d[1], d[2])


# ---------- rozloženie listu ----------
def wrap(c, s, font, size, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(c, x, y, s, width, size=6, lead=None, font="F", col=None):
    """x,y v mm (y = horná účiarie); vráti nové y."""
    lead = lead or size * 0.50
    c.setFillColor(col or C["ink"])
    c.setFont(font, size)
    for ln in wrap(c, s, font, size, width * MM):
        c.drawString(x * MM, y * MM, ln)
        y -= lead
    return y


def frame(c, title, sub, sheet, n, total, scale="1:100 (A3)", date="14. 11. 2026"):
    c.setStrokeColor(C["ink"])
    c.setLineWidth(0.6)
    c.rect(8 * MM, 8 * MM, PW - 16 * MM, PH - 16 * MM)
    c.setFillColor(C["ink"])
    c.setFont("FB", 15)
    c.drawString(14 * MM, 281 * MM, title)
    c.setFont("F", 7.5)
    c.drawString(14 * MM, 275.5 * MM, sub)
    c.setFont("FB", 8.5)
    c.drawRightString(PW - 14 * MM, 282 * MM, "Bytový dom Palárikova, Prešov")
    c.setFont("F", 7)
    c.drawRightString(PW - 14 * MM, 276.5 * MM, f"štúdia – variant C · list {n}/{total}")
    # rozpiska
    x0, y0, w, h = 292, 12, 114, 31
    c.setLineWidth(0.5)
    c.rect(x0 * MM, y0 * MM, w * MM, h * MM)
    rows = [("Stavba", "Bytový dom Palárikova, Prešov – k. ú. Solivar, parc. č. 937/2, 937/3"),
            ("Investor", "LIVENZA s.r.o.  ·  gen. dodávateľ LEFA Solutions s.r.o."),
            ("Podklad", "PD pre stavebné povolenie, J&L STAV (Ing. Lech), výkresy ASR 002–009"),
            ("Stupeň", "Pracovná štúdia – podklad na rokovanie s projektantom, nie je PD")]
    yy = y0 + h - 4.2
    for k, v in rows:
        c.setFont("F", 5.2)
        c.setFillColor(HexColor("#5a6675"))
        c.drawString((x0 + 3) * MM, yy * MM, k)
        c.setFillColor(C["ink"])
        c.setFont("F", 5.6)
        c.drawString((x0 + 20) * MM, yy * MM, v)
        yy -= 3.6
    c.setLineWidth(0.3)
    c.line(x0 * MM, (y0 + 14.5) * MM, (x0 + w) * MM, (y0 + 14.5) * MM)
    c.setFont("F", 5.2)
    c.setFillColor(HexColor("#5a6675"))
    c.drawString((x0 + 3) * MM, (y0 + 10) * MM, "Výkres")
    c.setFillColor(C["ink"])
    c.setFont("FB", 8)
    c.drawString((x0 + 20) * MM, (y0 + 9.6) * MM, sheet)
    c.line(x0 * MM, (y0 + 7.2) * MM, (x0 + w) * MM, (y0 + 7.2) * MM)
    for i, (k, v) in enumerate([("Mierka", scale), ("Dátum", date), ("Číslo", f"C-{n:02d}")]):
        xx = x0 + 3 + i * 38
        c.setFont("F", 4.6)
        c.setFillColor(HexColor("#5a6675"))
        c.drawString(xx * MM, (y0 + 4.6) * MM, k)
        c.setFillColor(C["ink"])
        c.setFont("FB", 6)
        c.drawString(xx * MM, (y0 + 1.6) * MM, v)


def north(c, x=392, y=262):
    """Orientácia: horná hrana výkresu = strana k parkovisku / ul. Palárikova (SZ)."""
    c.setStrokeColor(C["ink"])
    c.setFillColor(C["ink"])
    c.setLineWidth(0.5)
    c.circle(x * MM, y * MM, 5 * MM, fill=0)
    # sever smeruje vpravo hore (dom je pootočený, pozdĺžna os JZ–SV)
    a = math.radians(40)
    dx, dy = math.cos(a), math.sin(a)
    p = c.beginPath()
    p.moveTo((x + 4.6 * dx) * MM, (y + 4.6 * dy) * MM)
    p.lineTo((x - 3 * dx + 1.8 * dy) * MM, (y - 3 * dy - 1.8 * dx) * MM)
    p.lineTo((x - 1.2 * dx) * MM, (y - 1.2 * dy) * MM)
    p.lineTo((x - 3 * dx - 1.8 * dy) * MM, (y - 3 * dy + 1.8 * dx) * MM)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setFont("FB", 6)
    c.drawString((x + 5.6 * dx) * MM, (y + 5.6 * dy) * MM, "S")


def legend(c, items, x=14, y=62, title="LEGENDA"):
    c.setFont("FB", 6.5)
    c.setFillColor(C["ink"])
    c.drawString(x * MM, y * MM, title)
    y -= 5
    for kind, col, label in items:
        if kind == "fill":
            c.setFillColor(C[col])
            c.setStrokeColor(HexColor("#888888"))
            c.setLineWidth(0.3)
            c.rect(x * MM, (y - 0.8) * MM, 7 * MM, 3.2 * MM, fill=1, stroke=1)
        elif kind == "dash":
            c.setStrokeColor(C[col])
            c.setLineWidth(1.1)
            c.setDash([4, 2.5])
            c.line(x * MM, (y + 0.8) * MM, (x + 7) * MM, (y + 0.8) * MM)
            c.setDash([])
        c.setFillColor(C["ink"])
        c.setFont("F", 5.6)
        c.drawString((x + 10) * MM, y * MM, label)
        y -= 4.6


def table(c, x, y, cols, rows, title=None, size=5.6, lead=4.3, bold_last=False):
    """cols = [(hlavička, šírka mm, align)]"""
    if title:
        c.setFont("FB", 6.5)
        c.setFillColor(C["ink"])
        c.drawString(x * MM, y * MM, title)
        y -= 5
    c.setFont("F", size - 0.6)
    c.setFillColor(HexColor("#5a6675"))
    xx = x
    for h, w, al in cols:
        if al == "r":
            c.drawRightString((xx + w - 2) * MM, y * MM, h)
        else:
            c.drawString(xx * MM, y * MM, h)
        xx += w
    tw = sum(w for _, w, _ in cols)
    c.setStrokeColor(HexColor("#8a94a0"))
    c.setLineWidth(0.3)
    c.line(x * MM, (y - 1.3) * MM, (x + tw) * MM, (y - 1.3) * MM)
    y -= lead + 0.4
    for i, row in enumerate(rows):
        last = bold_last and i == len(rows) - 1
        if last:
            c.line(x * MM, (y + lead - 1.2) * MM, (x + tw) * MM, (y + lead - 1.2) * MM)
        c.setFillColor(C["ink"])
        xx = x
        for j, ((h, w, al), v) in enumerate(zip(cols, row)):
            c.setFont("FB" if (last or j == 0) else "F", size)
            if al == "r":
                c.drawRightString((xx + w - 2) * MM, y * MM, str(v))
            else:
                c.drawString(xx * MM, y * MM, str(v))
            xx += w
        y -= lead
    return y


def notes(c, x, y, title, lines, width=110, size=5.6):
    c.setFont("FB", 6.5)
    c.setFillColor(C["ink"])
    c.drawString(x * MM, y * MM, title)
    y -= 4.6
    for ln in lines:
        y = para(c, x, y, ln, width, size=size, lead=3.5) - 0.5
    return y


def m2(v, d=2):
    return f"{v:.{d}f}".replace(".", ",") + " m²"
