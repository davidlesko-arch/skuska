#!/usr/bin/env python3
"""Štúdia prístavby (NKP) – 1.NP, 2.NP (podkrovie) a schéma delenia na 6 bytov.

Použitie: python3 kresli.py <1np_podklad.png> <2np_podklad.png> <vystup.pdf>
Podklady = schválené výkresy vyrenderované pri 300 dpi (pdftoppm -r 300 -png).
"""
import math
import sys

from PIL import Image
from reportlab.lib.pagesizes import A3
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont("F", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("FB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

# ---------- kalibrácia podkladu (300 dpi) ----------
PXM = 91.6            # px / m
PX0, PY0 = 1137, 3279  # ľavý predný roh starého domu (uličná fasáda)
CROP_TOP = 1027        # nad týmto riadkom je pôvodná (rušená) prístavba
IMG_W, IMG_H = 2481, 3509

# ---------- geometria novej prístavby [m] ----------
EX0, EX1 = -9.95, 7.25      # šírka ako v schválenom návrhu = 17,20 m
Y0 = 24.61                  # koniec spojovacieho krčku (krčok 4,41 m)
T = 0.45                    # obvodová stena
AX = (EX0 + EX1) / 2        # os súmernosti
BD = 9.2                    # hĺbka priečneho (predného) traktu
WW = 9.2                    # šírka zadného krídla
WL = 8.4                    # dĺžka zadného krídla  -> 4,41 + 9,2 + 8,4 = 22,0 m
YF0, YF1 = Y0, Y0 + BD
YW1 = YF1 + WL
WX0, WX1 = AX - WW / 2, AX + WW / 2
HH = 1.5                    # polovica šírky vstupnej haly

WALL = (0.25, 0.25, 0.25)
COL = {"A1": (0.99, 0.87, 0.70), "A2": (0.80, 0.90, 1.0), "B1": (0.82, 0.95, 0.80),
       "B2": (1.0, 0.82, 0.86), "PA": (0.90, 0.84, 1.0), "PB": (1.0, 0.96, 0.70),
       "S": (0.88, 0.88, 0.88)}


class Tr:
    def __init__(self, c, ox, oy, sc, xmin, ymin):
        self.c, self.ox, self.oy, self.sc, self.xmin, self.ymin = c, ox, oy, sc, xmin, ymin

    def X(self, x):
        return self.ox + (x - self.xmin) * self.sc

    def Y(self, y):
        return self.oy + (y - self.ymin) * self.sc

    def rect(self, x0, y0, x1, y1, fill=None, stroke=None, lw=0.3, dash=None):
        c = self.c
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        c.saveState()
        c.setLineWidth(lw)
        if dash:
            c.setDash(list(dash))
        if fill:
            c.setFillColorRGB(*fill)
        if stroke:
            c.setStrokeColorRGB(*stroke)
        c.rect(self.X(x0), self.Y(y0), (x1 - x0) * self.sc, (y1 - y0) * self.sc,
               fill=1 if fill else 0, stroke=1 if stroke else 0)
        c.restoreState()

    def line(self, x0, y0, x1, y1, lw=0.3, col=(0, 0, 0), dash=None):
        c = self.c
        c.saveState()
        c.setLineWidth(lw)
        c.setStrokeColorRGB(*col)
        if dash:
            c.setDash(list(dash))
        c.line(self.X(x0), self.Y(y0), self.X(x1), self.Y(y1))
        c.restoreState()

    def text(self, x, y, s, size=5, bold=False, col=(0, 0, 0), rot=0, align="c"):
        c = self.c
        c.saveState()
        c.setFillColorRGB(*col)
        c.setFont("FB" if bold else "F", size)
        c.translate(self.X(x), self.Y(y))
        if rot:
            c.rotate(rot)
        lines = s.split("\n")
        for i, ln in enumerate(lines):
            yy = (len(lines) - 1) / 2 * size * 1.15 - i * size * 1.15 - size * 0.35
            if align == "c":
                c.drawCentredString(0, yy, ln)
            else:
                c.drawString(0, yy, ln)
        c.restoreState()

    def window(self, x0, y0, x1, y1):
        """okno v stene – obdĺžnik v hrúbke steny"""
        self.rect(x0, y0, x1, y1, fill=(1, 1, 1), stroke=(0, 0, 0), lw=0.3)
        if abs(x1 - x0) > abs(y1 - y0):
            ym = (y0 + y1) / 2
            self.line(x0, ym, x1, ym, lw=0.5, col=(0.1, 0.4, 0.8))
        else:
            xm = (x0 + x1) / 2
            self.line(xm, y0, xm, y1, lw=0.5, col=(0.1, 0.4, 0.8))

    def door(self, x0, y0, x1, y1, hinge, swing, col=(0.85, 0.35, 0.0), dash=None):
        """dvere: otvor (x0,y0)-(x1,y1) v stene; hinge = 0/1 (ktorý koniec), swing=(nx,ny)"""
        self.rect(x0, y0, x1, y1, fill=(1, 1, 1))
        horiz = abs(x1 - x0) > abs(y1 - y0)
        if horiz:
            w = abs(x1 - x0)
            ym = (y0 + y1) / 2
            hx = min(x0, x1) if hinge == 0 else max(x0, x1)
            hy = ym
            d = (1, 0) if hinge == 0 else (-1, 0)
        else:
            w = abs(y1 - y0)
            xm = (x0 + x1) / 2
            hx = xm
            hy = min(y0, y1) if hinge == 0 else max(y0, y1)
            d = (0, 1) if hinge == 0 else (0, -1)
        n = swing
        c = self.c
        c.saveState()
        c.setStrokeColorRGB(*col)
        c.setLineWidth(0.4)
        if dash:
            c.setDash(list(dash))
        c.line(self.X(hx), self.Y(hy), self.X(hx + n[0] * w), self.Y(hy + n[1] * w))
        a0 = math.degrees(math.atan2(d[1], d[0]))
        a1 = math.degrees(math.atan2(n[1], n[0]))
        ext = (a1 - a0 + 540) % 360 - 180
        r = w * self.sc
        p = c.beginPath()
        p.arc(self.X(hx) - r, self.Y(hy) - r, self.X(hx) + r, self.Y(hy) + r, a0, ext)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()


def room(t, x0, y0, x1, y1, name, size=4.2, fill=None, area=True, a=None):
    if fill:
        t.rect(x0, y0, x1, y1, fill=fill)
    if a is None:
        a = abs(x1 - x0) * abs(y1 - y0)
    s = name + (f"\n{a:.1f} m²".replace(".", ",") if area else "")
    t.text((x0 + x1) / 2, (y0 + y1) / 2, s, size=size)



RED = (0.8, 0, 0)
PINK = (0.8, 0, 0.8)
GREEN = (0.0, 0.5, 0.2)


def shell(t, hallfill=None):
    t.rect(EX0, YF0, EX1, YF1, fill=WALL)
    t.rect(WX0, YF1 - 0.01, WX1, YW1, fill=WALL)
    t.rect(EX0 + T, YF0 + T, EX1 - T, YF1 - T, fill=(1, 1, 1))
    t.rect(WX0 + T, YF1, WX1 - T, YW1 - T, fill=(1, 1, 1))
    if hallfill:
        t.rect(AX - HH, YF0 + T, AX + HH, YF1 - T, fill=hallfill)
    for s in (-1, 1):
        t.rect(AX + s * HH, YF0 + T, AX + s * (HH + 0.25), YF1 - T, fill=WALL)
    t.rect(AX - 0.15, YF1, AX + 0.15, YW1 - T, fill=WALL)


def hall(t, upper=False, labels=True):
    y0 = YF0 + T
    # jednoramenné schodisko pri východnej stene haly
    sx0, sx1 = AX + 0.3, AX + HH
    sy0, sy1 = y0 + 1.5, y0 + 5.8
    t.rect(sx0, sy0, sx1, sy1, fill=(1, 1, 1), stroke=(0.3, 0.3, 0.7), lw=0.3)
    for i in range(1, 16):
        y = sy0 + i * (sy1 - sy0) / 16
        t.line(sx0, y, sx1, y, lw=0.25, col=(0.3, 0.3, 0.7))
    t.line((sx0 + sx1) / 2, sy0 + 0.2, (sx0 + sx1) / 2, sy1 - 0.2, lw=0.4, col=(0.3, 0.3, 0.7))
    t.text((sx0 + sx1) / 2, sy1 - 0.35, "▲", size=4, col=(0.3, 0.3, 0.7))
    if labels:
        t.text(sx0 - 0.25, (sy0 + sy1) / 2, "schody 17 × 176/270", size=3, rot=90)
    if upper:
        t.window(AX - 0.7, YF0, AX + 0.7, YF0 + T)
    else:
        t.door(AX - 0.6, YF0, AX + 0.6, YF0 + T, 0, (0, 1), col=RED)
        t.text(AX, YF0 - 0.75, "▲ HLAVNÝ VSTUP z dvora", size=4, bold=True, col=RED)
        t.rect(AX - HH, y0 + 3.2, AX - HH + 0.25, y0 + 4.7, fill=(1, 0.8, 0), stroke=(0, 0, 0))
        if labels:
            t.text(AX - HH + 0.6, y0 + 3.95, "RE 6+2", size=3, rot=90)


def front(t, s, names, fill=None, small=False, kdash=False, swin=None, pk=False):
    """Predná jednotka (51 m²) – polovica priečneho traktu. s=-1 západ, +1 východ."""
    def X(u):
        return AX + s * (HH + 0.25 + u)

    def Yv(v):
        return YF0 + T + v

    def R(u0, v0, u1, v1, **k):
        t.rect(X(u0), Yv(v0), X(u1), Yv(v1), **k)

    if fill:
        R(0, 0, 6.4, 8.3, fill=fill)
    R(2.4, 0, 2.5, 8.3, fill=WALL)
    R(2.5, 4.6, 6.4, 4.7, fill=WALL)
    R(0, 2.9, 1.4, 3.0, fill=WALL)
    R(1.4, 2.9, 1.5, 6.1, fill=WALL)
    R(0, 6.0, 1.4, 6.1, fill=WALL)
    # šachta + kúpeľňa
    R(0, 3.0, 0.35, 3.7, fill=(0.2, 0.5, 0.9))
    t.text(X(0.175), Yv(3.35), "Š", size=3.2, bold=True, col=(1, 1, 1))
    R(0.1, 5.2, 1.3, 5.95, fill=(1, 1, 1), stroke=PINK, lw=0.3)
    R(0.45, 3.1, 0.95, 3.7, fill=(1, 1, 1), stroke=PINK, lw=0.3)
    R(0.05, 4.1, 0.5, 4.7, fill=(1, 1, 1), stroke=PINK, lw=0.3)
    # kuchyňa (pri priečke medzi izbami, napojenie na šachtu cez chodbu)
    R(2.6, 4.0, 5.4, 4.6, fill=(1, 1, 1), stroke=GREEN, lw=0.4, dash=(1.5, 1.5) if kdash else None)
    if not small:
        room(t, X(2.5), Yv(0), X(6.4), Yv(3.9), names[0], a=17.9)
        room(t, X(2.5), Yv(4.7), X(6.4), Yv(8.3), names[1], a=14.0)
        t.text(X(1.2), Yv(1.2), "Chodba\n+ šatník\n15,1 m²", size=3.6)
        t.text(X(0.75), Yv(4.9), "Kúp.\n4,2 m²", size=3)
        t.text(X(1.2), Yv(7.2), "šatník", size=3.2)
    # dvere
    t.door(X(2.4), Yv(1.5), X(2.5), Yv(2.3), 0, (s, 0))
    t.door(X(2.4), Yv(5.0), X(2.5), Yv(5.8), 1, (s, 0))
    t.door(X(1.4), Yv(3.9), X(1.5), Yv(4.6), 0, (-s, 0))
    # okná
    sw = swin if swin is not None else [(3.0, 4.4), (4.9, 6.1)]
    for (u0, u1) in sw:
        t.window(X(u0), YF0, X(u1), YF0 + T)
        if pk:
            t.text(X((u0 + u1) / 2), YF0 - 0.35, "vikier", size=3)
    t.window(X(3.6), YF1 - T, X(5.2), YF1)
    if pk:
        t.text(X(4.4), YF1 + 0.35, "vikier", size=3)
    for vc in (2.3, 6.5):
        t.window(X(6.4), Yv(vc - 0.6), X(6.4 + T), Yv(vc + 0.6))


def rear(t, s, name, fill=None, small=False, kdash=False, pk=False):
    """Zadná jednotka (31 m²) – polovica zadného krídla."""
    def X(p):
        return AX + s * (0.15 + p)

    def Yq(q):
        return YF1 + q

    def R(p0, q0, p1, q1, **k):
        t.rect(X(p0), Yq(q0), X(p1), Yq(q1), **k)

    if fill:
        R(0, 0, 4.0, 7.95, fill=fill)
    R(0, 1.5, 4.0, 1.6, fill=WALL)
    R(1.6, 1.6, 1.7, 4.0, fill=WALL)
    R(0, 3.9, 1.6, 4.0, fill=WALL)
    R(0, 1.6, 0.35, 2.3, fill=(0.2, 0.5, 0.9))
    t.text(X(0.175), Yq(1.95), "Š", size=3.2, bold=True, col=(1, 1, 1))
    R(0.1, 3.1, 1.5, 3.85, fill=(1, 1, 1), stroke=PINK, lw=0.3)
    R(1.1, 2.3, 1.55, 2.9, fill=(1, 1, 1), stroke=PINK, lw=0.3)
    R(0.45, 1.65, 0.95, 2.05, fill=(1, 1, 1), stroke=PINK, lw=0.3)
    R(1.7, 1.7, 2.3, 3.9, fill=(1, 1, 1), stroke=GREEN, lw=0.4, dash=(1.5, 1.5) if kdash else None)
    if not small:
        t.text(X(2.0), Yq(5.9), name + "\n21,1 m²", size=4.2)
        t.text(X(2.6), Yq(0.75), "Chodba 6,0 m²", size=3.2)
        t.text(X(0.8), Yq(2.75), "Kúp. 3,7", size=2.8)
    t.door(X(2.5), Yq(1.5), X(3.3), Yq(1.6), 0 if s > 0 else 1, (0, 1))
    t.door(X(0.5), Yq(1.5), X(1.2), Yq(1.6), 0 if s > 0 else 1, (0, 1))
    for (q0, q1) in ((2.2, 3.4), (5.2, 6.6)):
        t.window(X(4.0), Yq(q0), X(4.0 + T), Yq(q1))
        if pk:
            t.text(X(4.0 + T + 0.35), Yq((q0 + q1) / 2), "vikier", size=3, rot=90)
    t.window(X(1.2), YW1 - T, X(2.8), YW1)


def extension(t, floor, scheme=False):
    pk = floor == 2
    shell(t, hallfill=COL["S"] if scheme else None)
    hall(t, upper=pk, labels=not scheme)
    f = (lambda k: COL[k]) if scheme else (lambda k: None)
    if not pk:
        cw = ("A1", "B1", "A2", "B2")
    else:
        cw = ("PA", "PA", "PB", "PB")
    liv = "Obývačka + kuchyňa"
    prep = "Izba\n(príprava kuchyne)"
    # západ
    front(t, -1, (liv, "Spálňa"), fill=f(cw[0]), small=scheme, pk=pk)
    rear(t, -1, prep, fill=f(cw[1]), small=scheme, kdash=not (scheme and not pk), pk=pk)
    # východ – na 1.NP je južná fasáda sčasti zakrytá krčkom
    front(t, +1, (liv, "Spálňa"), fill=f(cw[2]), small=scheme, pk=pk,
          swin=None if pk else [(4.9, 6.1)])
    rear(t, +1, prep, fill=f(cw[3]), small=scheme, kdash=not (scheme and not pk), pk=pk)
    y0 = YF0 + T
    for s in (-1, 1):
        # vstup do prednej jednotky z haly
        t.door(AX + s * HH, y0 + 0.4, AX + s * (HH + 0.25), y0 + 1.3, 0, (s, 0), col=RED)
        # vstup do zadnej jednotky z haly
        split_rear = scheme and not pk
        if split_rear or not scheme:
            t.door(AX + s * 0.45, YF1 - T, AX + s * 1.35, YF1, 0 if s > 0 else 1, (0, 1),
                   col=RED, dash=None if split_rear else (1.5, 1.2))
        # prepojenie predná–zadná jednotka
        if not split_rear:
            x0, x1 = AX + s * (HH + 0.25 + 0.6), AX + s * (HH + 0.25 + 1.8)
            t.rect(x0, YF1 - T - 0.01, x1, YF1 + 0.01, fill=(1, 1, 1), stroke=RED, lw=0.5,
                   dash=None if (scheme or pk) else (1.5, 1.2))
    if pk and not scheme:
        c = (0.7, 0.1, 0.1)
        ym = (YF0 + YF1) / 2
        t.line(EX0 - 0.6, ym, EX1 + 0.6, ym, lw=0.5, col=c, dash=(6, 2, 1, 2))
        t.line(AX, ym, AX, YW1 + 0.6, lw=0.5, col=c, dash=(6, 2, 1, 2))
        t.text(EX1 + 1.5, ym, "hrebeň", size=3.5, col=c)
        t.text(AX, YW1 + 0.95, "hrebeň", size=3.5, col=c)


def dim(t, x0, y0, x1, y1, txt, size=4):
    col = (0, 0.35, 0.8)
    t.line(x0, y0, x1, y1, lw=0.35, col=col)
    horiz = abs(x1 - x0) > abs(y1 - y0)
    for (x, y) in ((x0, y0), (x1, y1)):
        if horiz:
            t.line(x, y - 0.3, x, y + 0.3, lw=0.35, col=col)
        else:
            t.line(x - 0.3, y, x + 0.3, y, lw=0.35, col=col)
    if horiz:
        t.text((x0 + x1) / 2, y0 + 0.45, txt, size=size, col=col)
    else:
        t.text(x0 - 0.45, (y0 + y1) / 2, txt, size=size, col=col, rot=90)


def underlay(c, t, path):
    im = Image.open(path).convert("RGB").crop((0, CROP_TOP, IMG_W, IMG_H))
    xm0 = (0 - PX0) / PXM
    ym0 = (PY0 - IMG_H) / PXM
    ym1 = (PY0 - CROP_TOP) / PXM
    c.drawImage(ImageReader(im), t.X(xm0), t.Y(ym0), IMG_W / PXM * t.sc, (ym1 - ym0) * t.sc)


def panel(c, x, y, title, lines):
    c.setFont("FB", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x, y, title)
    y -= 13
    for ln in lines:
        bold = ln.startswith("*")
        if bold:
            ln = ln[1:]
        c.setFont("FB" if bold else "F", 6.6)
        c.drawString(x, y, ln)
        y -= 9.2
    return y - 8


def titleblock(c, name, sub):
    W, H = A3
    c.setLineWidth(0.8)
    c.rect(20, 20, W - 40, H - 40)
    x, y = W - 290, 110
    c.rect(x, 20, 270, 90)
    c.setFont("FB", 11)
    c.drawString(x + 8, y - 18, name)
    c.setFont("F", 7.5)
    for i, ln in enumerate(sub):
        c.drawString(x + 8, y - 32 - i * 10, ln)


SUB = ["Bytový dom – NKP, prestavba a prístavba vo dvore",
       "Architektonická štúdia – prístavba 22 m vrátane krčku",
       None,
       "Investor: LEFA Solutions s.r.o., Pažica 23, Prešov",
       None]


def page_floor(c, floor, upath):
    W, H = A3
    sc = 72 / 25.4 * 1000 / 150   # 1:150
    xmin = (0 - PX0) / PXM
    ymin = (PY0 - IMG_H) / PXM
    t = Tr(c, 28, 28, sc, xmin, ymin)
    underlay(c, t, upath)
    t.rect(xmin, Y0 - 0.02, xmin + IMG_W / PXM, YW1 + 3, fill=(1, 1, 1))
    extension(t, floor)
    pk = floor == 2
    xl = (EX0 + WX0) / 2
    xr_ = (EX1 + WX1) / 2
    if not pk:
        t.text(xl, YF1 + 1.3, "BYT 4 – západná polovica\n1.NP, 3-izbový, 82,0 m²", size=5, bold=True, col=RED)
        t.text(xr_, YF1 + 1.3, "BYT 5 – východná polovica\n1.NP, 3-izbový, 82,0 m²", size=5, bold=True, col=RED)
        t.text(AX - 0.65, YF0 + T + 6.9, "Spoločná\nhala\n24,9 m²", size=3.6)
        t.text(xl, YF1 + 4.5, "záhrada / terasa\nbytu 4", size=4.5, col=(0.4, 0.4, 0.4))
        t.text(xr_, YF1 + 4.5, "záhrada / terasa\nbytu 5", size=4.5, col=(0.4, 0.4, 0.4))
    else:
        t.text(EX0 + 1.9, YF1 + 2.2, "BYT 6 – celé podkrovie\n164,0 + hala 19,7 = 183,7 m²", size=5, bold=True, col=RED)
        t.text(AX - 0.65, YF0 + T + 6.9, "Hala\nbytu 6\n19,7 m²", size=3.6)
    dim(t, EX0, YW1 + 2.4, EX1, YW1 + 2.4, "17 200")
    dim(t, WX0, YW1 + 1.5, WX1, YW1 + 1.5, "9 200", size=3.5)
    xr = EX1 + 3.6
    dim(t, xr, 20.2, xr, YF0, "4 410 krčok", size=3.5)
    dim(t, xr, YF0, xr, YF1, "9 200")
    dim(t, xr, YF1, xr, YW1, "8 400")
    dim(t, xr + 1.2, 20.2, xr + 1.2, YW1, "22 000  (prístavba spolu s krčkom)")
    dim(t, xr + 2.4, 0, xr + 2.4, YW1, "42 240  (celková dĺžka zástavby od uličnej čiary)")
    t.text(5.6, 21.5, "EXISTUJÚCI DOM (NKP)\n– podľa posledného odsúhlaseného\nnávrhu, bez zmeny", size=4.5, align="l", col=(0.4, 0.2, 0.2))
    t.text(5.6, 23.6, "krčok – bez zmeny", size=4, align="l", col=(0.4, 0.2, 0.2))

    x = W - 285
    y = H - 45
    if not pk:
        y = panel(c, x, y, "BILANCIA BYTOV – povoľovaný stav", [
            "*Predný dom (NKP) – 3 byty, bez zmeny oproti poslednému návrhu:",
            "  Byt 1 – 1.NP predná časť, Byt 2 – 1.NP zadná časť,",
            "  Byt 3 – podkrovie, bez vikierov do ulice",
            "*Prístavba vo dvore – 3 byty:",
            "  Byt 4 – 1.NP západ, 3-izb. ............. 82,0 m²",
            "  Byt 5 – 1.NP východ, 3-izb. ............ 82,0 m²",
            "  Byt 6 – podkrovie ....................... 183,7 m²",
            "  Spoločná vstupná hala so schodiskom ... 24,9 m²",
            "*Spolu 6 bytov (výhľadovo 9).",
        ])
        y = panel(c, x, y, "PRÍSTAVBA – ZÁKLADNÉ ÚDAJE", [
            "Jeden kompaktný dom v tvare T (ako odsúhlasený návrh,",
            "len so zadným krídlom): priečny trakt 17,2 × 9,2 m",
            "+ zadné krídlo 9,2 × 8,4 m. Zastavaná plocha 235,5 m².",
            "*Dĺžka prístavby vrátane krčku presne 22,0 m.",
            "Šírka 17,2 m – rovnaká ako v odsúhlasenom návrhu.",
            "Vstup spredu z dvora, v osi fasády (ako doteraz);",
            "schodisko do podkrovia hneď vo vstupnej hale.",
            "Strecha sedlová v tvare T, obe ramená rozpon 9,2 m,",
            "rovnaká výška hrebeňa, sklon cca 40°, nadmurovka",
            "do 1,0 m – 2. podlažie je podkrovie.",
            "Obvodové steny 450, medzibytové 250–300, priečky 100 mm.",
        ])
    else:
        y = panel(c, x, y, "PODKROVIE – POZNÁMKY", [
            "*Predný dom: podkrovný byt 3 bez zmeny – len strešné okná",
            "do dvora, žiadne vikiere do ulice.",
            "*Prístavba: Byt 6 = celé podkrovie, prístup schodiskom",
            "zo vstupnej haly.",
            "Presvetlenie: vikiere + okná v štítoch (západ, východ, sever).",
            "Nadmurovka do 1,0 m, sklon cca 40° – podkrovie.",
            "Dispozícia je zhodná s 1.NP – šachty, kúpeľne a kuchyne",
            "sú nad sebou.",
            "Plochy sú podlahové; započítateľná plocha (svetlá výška",
            "nad 1,3 m) bude po spresnení krovu nižšia cca o 8–10 %.",
        ])
    y = panel(c, x, y, "PRÍPRAVA NA DELENIE (3 → 6 bytov)", [
        "Dom tvoria 4 jednotky na podlaží: 2 predné (51,2 m²)",
        "a 2 zadné (30,8 m²). Každá má vlastnú šachtu (Š),",
        "kúpeľňu, kuchynské vývody a dvere z haly.",
        "Na povolenie: predná + zadná jednotka = 1 byt (82 m²).",
        "Červený čiarkovaný otvor – prepojenie prednej a zadnej",
        "jednotky; pri delení sa zamuruje.",
        "Červené čiarkované dvere – pripravený vstup do zadnej",
        "jednotky z haly (preklad osadený od začiatku).",
        "RE 6+2 – elektromerový rozvádzač pre 6 odberných miest",
        "+ 2 rezervy. Podrobne list 3.",
    ])
    y = panel(c, x, y, "LEGENDA", [
        "Tmavosivá – nové murivo prístavby",
        "Ružová / šrafa – existujúci dom a krčok (podklad)",
        "Modrá čiara v stene – okno; „vikier“ – okno vo vikieri",
        "Zelený obdĺžnik – kuchynská linka (čiarkovane = príprava)",
        "Fialové – zariaďovacie predmety",
    ])
    sub = list(SUB)
    sub[2] = f"List {floor}/3   |   formát A3   |   11/2026"
    sub[4] = "Podklad pre rokovanie s KPÚ – nie je projektom pre SP"
    titleblock(c, f"{'2.NP – PODKROVIE' if pk else '1.NP – PRÍZEMIE'}   M 1:150", sub)
    c.showPage()


def page_scheme(c):
    W, H = A3
    sc = 72 / 25.4 * 1000 / 150
    for i, floor in enumerate((1, 2)):
        t = Tr(c, 45 + i * 385, H - 62 - 21.5 * sc, sc, EX0 - 0.8, YF0 - 1.6)
        extension(t, floor, scheme=True)
        t.text(AX, YW1 + 1.3, "1.NP – 4 byty" if floor == 1 else "PODKROVIE – 2 byty", size=10, bold=True)
        xw, xe = EX0 + 2.6, EX1 - 2.6
        if floor == 1:
            t.text(xw, YF0 + 2.6, "BYT A1\n2-izb. 51,2 m²", size=7, bold=True)
            t.text(xe, YF0 + 2.6, "BYT A2\n2-izb. 51,2 m²", size=7, bold=True)
            t.text(AX - 2.3, YW1 - 2.4, "BYT B1\n1-izb.\n30,8 m²", size=6, bold=True)
            t.text(AX + 2.3, YW1 - 2.4, "BYT B2\n1-izb.\n30,8 m²", size=6, bold=True)
        else:
            t.text(xw, YF0 + 2.6, "BYT PA\n3-izb. 82,0 m²", size=7, bold=True)
            t.text(xe, YF0 + 2.6, "BYT PB\n3-izb. 82,0 m²", size=7, bold=True)
            t.text(AX - 2.3, YW1 - 2.4, "(PA)", size=6, bold=True)
            t.text(AX + 2.3, YW1 - 2.4, "(PB)", size=6, bold=True)
    c.setFont("FB", 13)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(40, H - 45, "SCHÉMA BUDÚCEHO DELENIA PRÍSTAVBY: 3 BYTY → 6 BYTOV   (M 1:150)")
    y0 = H - 62 - 21.5 * sc - 25
    xa, xb = 40, 440
    ya = panel(c, xa, y0, "ČO SA PRI DELENÍ UROBÍ (bez zásahu do nosných konštrukcií a fasád)", [
        "*1.NP – z bytov 4 a 5 vzniknú 4 byty (A1, A2 po 51,2 m²; B1, B2 po 30,8 m²):",
        "  1. Zamurovať prepojovací otvor (1,2 m) medzi prednou a zadnou jednotkou – stena je od",
        "     začiatku navrhnutá ako medzibytová (Rw ≥ 53 dB, EI 30).",
        "  2. Osadiť vstupné dvere zadnej jednotky do pripraveného prekladu v čele haly.",
        "  3. V zadnej jednotke osadiť kuchynskú linku na pripravené vývody.",
        "*Podkrovie – z bytu 6 vzniknú 2 byty (PA, PB po 82,0 m²):",
        "  4. Hala v podkroví sa stane spoločnou chodbou, každá polovica má už svoje vstupné dvere.",
        "  5. Podkrovie sa dá deliť aj ďalej rovnako ako 1.NP (2 + 2 byty).",
        "*Administratívne: zmena počtu bytov = zmena stavby / zmena v užívaní; treba doložiť",
        "  parkovacie státia pre nové byty (STN 73 6110).",
    ])
    yb = panel(c, xb, y0, "SIETE – ČO TREBA UROBIŤ UŽ PRI VÝSTAVBE", [
        "*Kanalizácia a voda:",
        "  4 šachty (Š) – v každej jednotke jedna, prechádzajú 1.NP aj podkrovím.",
        "  Ležaté zvody pod podlahou do osi haly, revízia v hale.",
        "  V každej šachte miesto na bytový vodomer pre obe podlažia (8 meracích miest).",
        "*Elektro:",
        "  Rozvádzač RE v hale na 6 elektromerov + 2 rezervy, osadené 3.",
        "  Do každej jednotky (8 ×) samostatná chránička a miesto na bytový rozvádzač.",
        "*Vykurovanie:",
        "  V každej jednotke vlastný rozdeľovač podlahového kúrenia; samostatné zdroje",
        "  alebo spoločný zdroj s meračmi tepla na každej vetve.",
        "*Vetranie a slaboprúd:",
        "  Digestor a odvetranie kúpeľne cez šachtu nad strechu pre každú jednotku.",
        "  Z haly chránička do každej jednotky, videovrátnik na 8 tlačidiel.",
        "*Požiar, akustika, statika:",
        "  Steny medzi jednotkami, stropy a steny k hale od začiatku ako medzibytové.",
        "  Priečky sú nenosné – dispozícia sa dá meniť.",
    ])
    y = min(ya, yb)
    y = panel(c, xa, y, "BILANCIA", [
        "*Povoľovaný stav:  predný dom 3 byty  +  prístavba 3 byty (82,0 + 82,0 + 183,7 m²)  =  6 bytov",
        "*Po rozdelení:       predný dom 3 byty  +  prístavba 6 bytov (2 × 51,2 + 2 × 30,8 + 2 × 82,0 m²)  =  9 bytov   (max. 11 pri delení podkrovia)",
    ])
    lx, ly = 40, y - 5
    for k, n in (("A1", "byt A1"), ("A2", "byt A2"), ("B1", "byt B1"), ("B2", "byt B2"),
                 ("PA", "byt PA"), ("PB", "byt PB"), ("S", "spoločné")):
        c.setFillColorRGB(*COL[k])
        c.rect(lx, ly, 14, 9, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("F", 7)
        c.drawString(lx + 18, ly + 1.5, n)
        lx += 70
    sub = list(SUB)
    sub[2] = "List 3/3   |   formát A3   |   11/2026"
    sub[4] = "Interný podklad – neprikladať k žiadosti"
    titleblock(c, "SCHÉMA DELENIA NA 6 BYTOV", sub)
    c.showPage()


def main():
    u1, u2, out = sys.argv[1:4]
    c = canvas.Canvas(out, pagesize=A3)
    c.setTitle("Štúdia prístavby – 1.NP, podkrovie, schéma delenia")
    page_floor(c, 1, u1)
    page_floor(c, 2, u2)
    page_scheme(c)
    c.save()


if __name__ == "__main__":
    main()
