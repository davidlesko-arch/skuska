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
Y0 = 24.61                  # koniec spojovacieho krčku
WD = 7.5                    # hĺbka krídla
LK = 7.0                    # dĺžka spojovacej časti (átriá)
T = 0.45                    # obvodová stena
AX = (EX0 + EX1) / 2        # os súmernosti
LKW = 5.2                   # šírka spojovacej časti
YA0, YA1 = Y0, Y0 + WD
YB0, YB1 = YA1 + LK, YA1 + LK + WD
LX0, LX1 = AX - LKW / 2, AX + LKW / 2

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


def half(t, yin, e, s, living, labels, fill=None, far_windows=None, near_windows=None,
         gable=True, kitchen_dash=False, podkrovie=False, small=False, bathwin=(0.9, 1.5)):
    """Polovica krídla (budúci samostatný 2-izbový byt).
    yin = vnútorná hrana steny so vstupom, e = +1 ak sa od vstupu ide smerom -y (vstup zo severu),
    s = -1 západ / +1 východ, living = 'far'/'near'."""
    def P(u, w):
        return AX + s * (0.15 + u), yin - e * w

    def R(u0, w0, u1, w1, **k):
        a, b = P(u0, w0), P(u1, w1)
        t.rect(a[0], a[1], b[0], b[1], **k)

    if fill:
        R(0, 0, 8.0, 6.6, fill=fill)
    wn = 3.0 if living == "far" else 3.5
    # priečky
    R(2.2, 0, 2.3, 6.6, fill=WALL)
    R(0, 4.4, 2.2, 4.5, fill=WALL)
    R(2.3, wn, 8.0, wn + 0.1, fill=WALL)
    # šachta
    R(0, 4.5, 0.35, 5.2, fill=(0.2, 0.5, 0.9))
    a = P(0.175, 4.85)
    t.text(a[0], a[1], "Š", size=3.2, bold=True, col=(1, 1, 1))
    # kuchyňa
    kw0, kw1 = (wn + 0.1, wn + 0.7) if living == "far" else (wn - 0.6, wn)
    R(3.4, kw0, 6.4, kw1, fill=(1, 1, 1), stroke=(0.0, 0.5, 0.2), lw=0.4,
      dash=(1.5, 1.5) if kitchen_dash else None)
    # zariaďovacie predmety kúpeľne (schematicky)
    R(0.5, 5.85, 2.1, 6.55, fill=(1, 1, 1), stroke=(0.8, 0, 0.8), lw=0.3)   # vaňa/sprcha
    R(1.6, 4.6, 2.1, 5.2, fill=(1, 1, 1), stroke=(0.8, 0, 0.8), lw=0.3)     # WC
    R(0.45, 4.55, 1.0, 4.95, fill=(1, 1, 1), stroke=(0.8, 0, 0.8), lw=0.3)  # umývadlo
    sz = 3.4 if small else 4.2
    if not small:
        nm_near, nm_far, nm_hall, nm_bath = labels
        a, b = P(2.3, 0), P(8.0, wn)
        if living == "near":
            b = P(8.0, wn - 0.6)
        room(t, a[0], a[1], b[0], b[1], nm_near, size=sz, a=5.7 * wn)
        a, b = P(2.3, wn + 0.1), P(8.0, 6.6)
        if living == "far":
            a = P(2.3, wn + 0.7)
        room(t, a[0], a[1], b[0], b[1], nm_far, size=sz, a=5.7 * (6.5 - wn))
        a, b = P(0, 0.6), P(2.2, 4.4)
        room(t, a[0], a[1], b[0], b[1], nm_hall, size=3.6, area=False)
        a, b = P(0.3, 5.1), P(2.2, 5.9)
        t.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, nm_bath + " 4,6 m²", size=3.2)
    # dvere vnútorné
    sw = (s, 0)
    a, b = P(2.2, 1.6), P(2.3, 2.4)
    t.door(a[0], a[1], b[0], b[1], 0 if e < 0 else 1, sw)
    w0 = wn + 0.15
    a, b = P(2.2, w0), P(2.3, w0 + 0.8)
    t.door(a[0], a[1], b[0], b[1], 0 if e < 0 else 1, sw)
    a, b = P(0.9, 4.4), P(1.7, 4.5)
    t.door(a[0], a[1], b[0], b[1], 0 if s > 0 else 1, (0, -e))
    # okná – stena oproti vstupu (far) a stena pri vstupe (near)
    fw = far_windows if far_windows is not None else [(3.4, 5.0), (6.0, 7.4)]
    nw = near_windows if near_windows is not None else [(3.5, 5.0), (6.0, 7.4)]
    yf0, yf1 = yin - e * 6.6, yin - e * (6.6 + T)
    for (u0, u1) in fw + ([bathwin] if bathwin else []):
        t.window(P(u0, 0)[0], yf0, P(u1, 0)[0], yf1)
        if podkrovie and (u0, u1) != bathwin:
            t.text((P(u0, 0)[0] + P(u1, 0)[0]) / 2, yin - e * (6.6 + T + 0.35), "vikier", size=3)
    yn0, yn1 = yin, yin + e * T
    for (u0, u1) in nw:
        t.window(P(u0, 0)[0], yn0, P(u1, 0)[0], yn1)
        if podkrovie:
            t.text((P(u0, 0)[0] + P(u1, 0)[0]) / 2, yin + e * (T + 0.35), "vikier", size=3)
    if gable:
        xg0, xg1 = AX + s * 8.15, AX + s * (8.15 + T)
        for wc in (wn / 2, wn + 0.1 + (6.5 - wn) / 2):
            t.window(xg0, yin - e * (wc - 0.6), xg1, yin - e * (wc + 0.6))


def wing_shell(t, y0, y1):
    t.rect(EX0, y0, EX1, y1, fill=WALL)
    t.rect(EX0 + T, y0 + T, EX1 - T, y1 - T, fill=(1, 1, 1))
    t.rect(AX - 0.15, y0 + T, AX + 0.15, y1 - T, fill=WALL)


def link(t, upper=False, fill=None):
    t.rect(LX0, YA1 - 0.01, LX1, YB0 + 0.01, fill=WALL)
    ix0, ix1 = LX0 + T, LX1 - T
    t.rect(ix0, YA1, ix1, YB0, fill=fill or (1, 1, 1))
    # schodisko
    sx0, sx1 = ix1 - 2.4, ix1
    sy0, sy1 = YA1 + 1.8, YB0 - 1.8
    t.rect(sx0 - 0.1, sy0, sx0, sy1, fill=WALL)
    t.rect(sx0, sy0, sx1, sy1, fill=(1, 1, 1), stroke=(0.3, 0.3, 0.7), lw=0.3)
    xm = (sx0 + sx1) / 2
    t.line(xm, sy0 + 1.2, xm, sy1, lw=0.3, col=(0.3, 0.3, 0.7))
    n = 8
    for i in range(n + 1):
        y = sy0 + 1.2 + i * (sy1 - sy0 - 1.2) / n
        t.line(sx0, y, sx1, y, lw=0.25, col=(0.3, 0.3, 0.7))
    t.text((sx0 + sx1) / 2, sy0 + 0.6, "podesta\n17 × 176/270", size=3)
    t.text(xm + 0.6, sy1 - 0.5, "↓" if upper else "↑", size=6, col=(0.3, 0.3, 0.7))
    t.text(xm - 0.6, sy1 - 0.5, "↓" if not upper else "↑", size=6, col=(0.3, 0.3, 0.7))
    # okná schodiska (východ)
    t.window(LX1 - T, sy0 + 0.9, LX1, sy0 + 2.1)
    if upper:
        t.window(LX0, YA1 + 2.9, LX0 + T, YA1 + 4.1)
    else:
        t.door(LX0, YA1 + 3.0, LX0 + T, YA1 + 4.0, 0, (1, 0))
        t.text(LX0 - 1.3, YA1 + 3.5, "HLAVNÝ\nVSTUP ▶", size=4, bold=True, col=(0.8, 0, 0))
        # elektromerový rozvádzač
        t.rect(ix0, YA1 + 4.4, ix0 + 0.25, YA1 + 5.9, fill=(1, 0.8, 0), stroke=(0, 0, 0))
        t.text(ix0 + 0.75, YA1 + 5.15, "RE 6+2", size=3, rot=90)


def entry_door(t, s, yin, e, dash=False, lab=None):
    """vstupné dvere do polovice krídla zo spojovacej haly"""
    x0, x1 = AX + s * (0.15 + 0.7), AX + s * (0.15 + 1.6)
    t.door(x0, yin, x1, yin + e * T, 0 if s < 0 else 1, (0, -e),
           col=(0.8, 0, 0), dash=(1.5, 1.2) if dash else None)


def opening(t, y0, y1, label=True):
    """prepojovací otvor v stredovej stene (pri delení sa zamuruje)"""
    t.rect(AX - 0.16, y0, AX + 0.16, y1, fill=(1, 1, 1), stroke=(0.8, 0, 0), lw=0.5, dash=(1.5, 1.2))


def extension(t, floor, scheme=False):
    """floor = 1 / 2 ; scheme=True -> farebné rozdelenie na 6 bytov"""
    pk = floor == 2
    wing_shell(t, YA0, YA1)
    wing_shell(t, YB0, YB1)
    fl = (lambda k: COL[k]) if scheme else (lambda k: None)
    link(t, upper=pk, fill=COL["S"] if scheme else None)
    yinA, yinB = YA1 - T, YB0 + T
    if not pk:
        # krídlo A – západ: obývačka na juh (dvor); východ: obývačka k átriu (juh tieni krčok)
        half(t, yinA, +1, -1, "far", ("Spálňa", "Obývačka + kuchyňa", "Chodba\n9,7 m²", "Kúp."),
             fill=fl("A1"), small=scheme)
        half(t, yinA, +1, +1, "near",
             ("Izba / obývačka\n(príprava kuchyne)" if not scheme else "", "Spálňa", "Chodba\n9,7 m²", "Kúp."),
             fill=fl("A2"), far_windows=[(6.5, 7.6)], kitchen_dash=not scheme, small=scheme,
             bathwin=(0.5, 1.1))
        half(t, yinB, -1, -1, "far", ("Spálňa", "Obývačka + kuchyňa", "Chodba\n9,7 m²", "Kúp."),
             fill=fl("B1"), small=scheme)
        half(t, yinB, -1, +1, "far", ("Spálňa", "Izba / obývačka\n(príprava kuchyne)", "Chodba\n9,7 m²", "Kúp."),
             fill=fl("B2"), kitchen_dash=not scheme, small=scheme)
    else:
        nm = ("Izba", "Obývačka + kuchyňa", "Chodba\n9,7 m²", "Kúp.")
        nm2 = ("Izba", "Izba\n(príprava kuchyne)", "Chodba\n9,7 m²", "Kúp.")
        half(t, yinA, +1, -1, "far", nm, fill=fl("PA"), podkrovie=True, small=scheme, bathwin=None)
        half(t, yinA, +1, +1, "far", nm2, fill=fl("PA"), podkrovie=True, kitchen_dash=True,
             small=scheme, bathwin=None)
        half(t, yinB, -1, -1, "far", nm2 if not scheme else nm, fill=fl("PB"), podkrovie=True,
             kitchen_dash=not scheme, small=scheme, bathwin=None)
        half(t, yinB, -1, +1, "far", nm2, fill=fl("PB"), podkrovie=True, kitchen_dash=True,
             small=scheme, bathwin=None)
    # vstupy z haly
    if not scheme:
        entry_door(t, -1, yinA, +1)
        entry_door(t, +1, yinA, +1, dash=not pk)
        entry_door(t, -1, yinB, -1)
        entry_door(t, +1, yinB, -1, dash=not pk)
        opening(t, YA0 + T + 3.4, YA0 + T + 4.6)
        opening(t, YB1 - T - 4.6, YB1 - T - 3.4)
    else:
        for s in (-1, 1):
            if pk:
                # podkrovie: jeden vstup na krídlo, polovice prepojené
                pass
            entry_door(t, s, yinA, +1)
            entry_door(t, s, yinB, -1)
        if pk:
            opening(t, YA0 + T + 3.4, YA0 + T + 4.6)
            opening(t, YB1 - T - 4.6, YB1 - T - 3.4)
    if pk and not scheme:
        # hrebene striech
        for ym in ((YA0 + YA1) / 2, (YB0 + YB1) / 2):
            t.line(EX0 - 0.6, ym, EX1 + 0.6, ym, lw=0.5, col=(0.7, 0.1, 0.1), dash=(6, 2, 1, 2))
            t.text(EX1 + 1.5, ym, "hrebeň", size=3.5, col=(0.7, 0.1, 0.1))
        t.line(AX, (YA0 + YA1) / 2, AX, (YB0 + YB1) / 2, lw=0.5, col=(0.7, 0.1, 0.1), dash=(6, 2, 1, 2))
        for (a, b) in ((YA0, YA1), (YB0, YB1)):
            t.rect(EX0 - 0.6, a - 0.6, EX1 + 0.6, b + 0.6, stroke=(0.7, 0.1, 0.1), lw=0.3, dash=(3, 2))


def dim(t, x0, y0, x1, y1, txt, off=0.0, size=4):
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


def panel(c, x, y, title, lines, w=250):
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


def page_floor(c, floor, upath):
    W, H = A3
    sc = 72 / 25.4 * 1000 / 150   # 1:150
    xmin = (0 - PX0) / PXM
    ymin = (PY0 - IMG_H) / PXM
    t = Tr(c, 28, 28, sc, xmin, ymin)
    underlay(c, t, upath)
    # zakryť zvyšky pôvodnej prístavby nad krčkom
    t.rect(xmin, Y0 - 0.02, xmin + IMG_W / PXM, YB1 + 2, fill=(1, 1, 1))
    extension(t, floor)
    pk = floor == 2
    # byty – nadpisy
    if not pk:
        t.text(AX, YA0 + T + 6.9, "", size=4)
        t.text(EX0 + 3.0, YA1 + 0.8, "▼ BYT 4 – krídlo A, 1.NP\n4-izbový, 102,7 m²", size=5, bold=True, col=(0.8, 0, 0))
        t.text(EX0 + 3.0, YB0 - 0.8, "▲ BYT 5 – krídlo B, 1.NP\n4-izbový, 102,7 m²", size=5, bold=True, col=(0.8, 0, 0))
        t.text(LX0 + T + 0.9, YA1 + 2.3, "Spoločná\nhala\n30,1 m²", size=3.6)
        t.text(EX0 + 2.6, YA1 + 4.6, "ÁTRIUM – vstupný dvor\n7,0 × 6,0 m", size=4.5)
        t.text(EX1 - 3.0, YA1 + 3.5, "ÁTRIUM – záhradka\n7,0 × 6,0 m", size=4.5)
        t.text(AX, YB1 + 1.0, "záhrada", size=4.5)
        t.text(EX0 - 0.75, YA0 + 3.7, "chodník k vstupu  ▶", size=4, rot=90, col=(0.8, 0, 0))
    else:
        t.text(EX0 + 3.0, YA1 + 1.0, "BYT 6 – podkrovie A + B\n205,4 + hala 21,9 = 227,3 m²", size=5, bold=True, col=(0.8, 0, 0))
        t.text(LX0 + T + 0.9, YA1 + 2.3, "Hala\nbytu 6\n21,9 m²", size=3.6)
        t.text(EX0 + 3.0, YA1 + 3.5, "(átrium – voľné)", size=4.5, col=(0.5, 0.5, 0.5))
        t.text(EX1 - 3.0, YA1 + 3.5, "(átrium – voľné)", size=4.5, col=(0.5, 0.5, 0.5))
    # kóty
    dim(t, EX0, YB1 + 2.1, EX1, YB1 + 2.1, "17 200")
    dim(t, EX0, YB1 + 1.4, AX, YB1 + 1.4, "8 600", size=3.5)
    dim(t, AX, YB1 + 1.4, EX1, YB1 + 1.4, "8 600", size=3.5)
    xr = EX1 + 3.6
    dim(t, xr, YA0, xr, YA1, "7 500")
    dim(t, xr, YA1, xr, YB0, "7 000")
    dim(t, xr, YB0, xr, YB1, "7 500")
    dim(t, xr + 1.2, YA0, xr + 1.2, YB1, "22 000  (nová prístavba)")
    dim(t, xr + 1.2, 20.2, xr + 1.2, YA0, "4 410", size=3.5)
    dim(t, xr + 2.4, 0, xr + 2.4, YB1, "46 610  (celková dĺžka zástavby od uličnej čiary)")
    dim(t, LX0, YA1 + 6.4, LX1, YA1 + 6.4, "5 200", size=3.5)
    t.text(5.6, 21.5, "EXISTUJÚCI DOM (NKP)\n– podľa posledného odsúhlaseného\nnávrhu, bez zmeny", size=4.5, align="l", col=(0.4, 0.2, 0.2))
    t.text(5.6, 23.6, "krčok – bez zmeny", size=4, align="l", col=(0.4, 0.2, 0.2))

    # pravý panel
    x = W - 285
    y = H - 45
    if not pk:
        y = panel(c, x, y, "BILANCIA BYTOV – povoľovaný stav", [
            "*Predný dom (NKP) – 3 byty, bez zmeny oproti poslednému návrhu:",
            "  Byt 1 – 1.NP predná časť (2-izb.)",
            "  Byt 2 – 1.NP zadná časť (2-izb.)",
            "  Byt 3 – podkrovie (3-izb.), bez vikierov do ulice",
            "*Prístavba vo dvore – 3 byty:",
            "  Byt 4 – krídlo A, 1.NP, 4-izb. ........ 102,7 m²",
            "  Byt 5 – krídlo B, 1.NP, 4-izb. ........ 102,7 m²",
            "  Byt 6 – podkrovie A+B ............... 227,3 m²",
            "  Spoločná hala + schodisko (1.NP) ...... 30,1 m²",
            "*Spolu 6 bytov (výhľadovo 9).",
        ])
        y = panel(c, x, y, "PRÍSTAVBA – ZÁKLADNÉ ÚDAJE", [
            "Pôdorys v tvare H: 2 krídla 17,2 × 7,5 m + spojovacia",
            "časť 5,2 × 7,0 m so schodiskom. Zastavaná plocha 294,4 m².",
            "Dĺžka do dvora 22,0 m, šírka 17,2 m (ako v schválenom návrhu).",
            "Krídla: sedlová strecha, hrebeň kolmo na os pozemku,",
            "rozpon 7,5 m, sklon cca 40°, nadmurovka do 1,0 m –",
            "2. podlažie je podkrovie, nie plnohodnotné podlažie.",
            "Spojovacia časť: nižšia sedlová strecha, hrebeň v osi.",
            "Obvodové steny 450 mm, stredová (medzibytová) 300 mm,",
            "priečky 100 mm. Svetlá výška 1.NP 2,60 m.",
        ])
    else:
        y = panel(c, x, y, "PODKROVIE – POZNÁMKY", [
            "*Predný dom: podkrovný byt 3 bez zmeny – len strešné okná",
            "do dvora, žiadne vikiere do ulice.",
            "*Prístavba: Byt 6 = podkrovie krídla A + B prepojené halou.",
            "Presvetlenie: vikiere (do dvora, átrií a záhrady) + okná",
            "v štítoch. Nadmurovka do 1,0 m, sklon cca 40° – podlažie",
            "spĺňa definíciu podkrovia.",
            "Dispozícia podkrovia je zhodná s 1.NP – šachty, kúpeľne",
            "a kuchyne sú nad sebou.",
            "Plochy sú podlahové; započítateľná plocha (svetlá výška",
            "nad 1,3 m) bude po spresnení krovu nižšia cca o 8–10 %.",
        ])
    y = panel(c, x, y, "PRÍPRAVA NA DELENIE (3 → 6 bytov)", [
        "Š – inštalačná šachta (kanalizácia, voda, VZT, rezerva).",
        "Každá polovica krídla má vlastnú šachtu, vlastnú kúpeľňu",
        "a kuchynské vývody; samostatné meranie vody v šachte.",
        "RE 6+2 – elektromerový rozvádzač pre 6 odberných miest",
        "+ 2 rezervy, chráničky do každej polovice krídla.",
        "Červené čiarkované dvere – pripravený preklad 2. vstupu.",
        "Červený čiarkovaný otvor v stredovej stene – prepojenie",
        "polovíc; pri delení sa zamuruje (stena je už navrhnutá",
        "ako medzibytová – akustika aj požiarna odolnosť).",
        "Vykurovanie: samostatný rozdeľovač / zdroj na každú",
        "polovicu krídla. Podrobne list 3.",
    ])
    y = panel(c, x, y, "LEGENDA", [
        "Tmavosivá – nové murivo prístavby",
        "Ružová / šrafa – existujúci dom a krčok (podklad)",
        "Modrá čiara v stene – okno; „vikier“ – okno vo vikieri",
        "Zelený obdĺžnik – kuchynská linka (čiarkovane = príprava)",
        "Fialové – zariaďovacie predmety",
    ])
    titleblock(c, f"{'2.NP – PODKROVIE' if pk else '1.NP – PRÍZEMIE'}   M 1:150",
               ["Bytový dom – NKP, prestavba a prístavba vo dvore",
                "Architektonická štúdia – variant „22 m do dvora“",
                f"List {floor}/3   |   formát A3   |   11/2026",
                "Investor: LEFA Solutions s.r.o., Pažica 23, Prešov",
                "Podklad pre rokovanie s KPÚ – nie je projektom pre SP"])
    c.showPage()


def page_scheme(c):
    W, H = A3
    sc = 72 / 25.4 * 1000 / 150   # 1:150
    for i, floor in enumerate((1, 2)):
        t = Tr(c, 45 + i * 385, H - 62 - 25 * sc, sc, EX0 - 0.8, YA0 - 1.2)
        extension(t, floor, scheme=True)
        t.text(AX, YB1 + 1.6, "1.NP – 4 byty" if floor == 1 else "PODKROVIE – 2 byty", size=10, bold=True)
        if floor == 1:
            for (xx, yy, s) in ((EX0 + 3.3, YA0 + 1.6, "BYT A1\n2-izb. 51,4 m²"), (EX1 - 3.3, YA0 + 5.6, "BYT A2\n2-izb. 51,4 m²"),
                                (EX0 + 3.3, YB1 - 1.6, "BYT B1\n2-izb. 51,4 m²"), (EX1 - 3.3, YB1 - 1.6, "BYT B2\n2-izb. 51,4 m²")):
                t.text(xx, yy, s, size=7, bold=True)
        else:
            t.text(EX0 + 3.3, YA0 + 1.6, "BYT PA\n4-izb. 102,7 m²", size=7, bold=True)
            t.text(EX0 + 3.3, YB1 - 1.6, "BYT PB\n4-izb. 102,7 m²", size=7, bold=True)
            t.text(EX1 - 3.3, YA0 + 1.6, "(možnosť ďalšieho\ndelenia na 2+2)", size=5)
        t.text(LX0 + T + 0.9, YA1 + 0.9, "spol.\nchodba", size=4)
    c.setFont("FB", 13)
    c.drawString(40, H - 45, "SCHÉMA BUDÚCEHO DELENIA PRÍSTAVBY: 3 BYTY → 6 BYTOV   (M 1:150)")
    y0 = H - 62 - 25 * sc - 25
    xa, xb = 40, 440
    ya = panel(c, xa, y0, "ČO SA PRI DELENÍ UROBÍ (bez zásahu do nosných konštrukcií a fasád)", [
        "*1.NP – z bytov 4 a 5 vzniknú 4 dvojizbové byty (A1, A2, B1, B2):",
        "  1. Zamurovať prepojovací otvor v stredovej stene krídla (1,2 m) – stena je už od začiatku",
        "     navrhnutá ako medzibytová (300 mm, Rw ≥ 53 dB, EI 30).",
        "  2. Osadiť vstupné dvere do pripraveného prekladu 2. vstupu zo spoločnej haly.",
        "  3. V izbe s „prípravou kuchyne“ osadiť linku na pripravené vývody (voda, odpad, 400 V, odsávanie).",
        "*Podkrovie – z bytu 6 vzniknú 2 byty (PA, PB):",
        "  4. Hala bytu 6 v spojovacej časti sa stane spoločnou chodbou; vstupné dvere bytu 6 pri nástupe",
        "     na schodisko sa odstránia, vstupné dvere sa osadia na vstupoch do krídel (preklady pripravené).",
        "  5. Každé krídlo má už 2 kúpeľne a 2 kuchynské prípravy – podkrovie sa dá deliť aj ďalej (2+2).",
        "*Administratívne: zmena účelu/počtu bytov = ohlásenie / zmena stavby pred dokončením alebo",
        "  neskôr zmena v užívaní; treba doložiť parkovacie státia pre nové byty (STN 73 6110).",
    ])
    yb = panel(c, xb, y0, "SIETE – ČO TREBA UROBIŤ UŽ PRI VÝSTAVBE", [
        "*Kanalizácia a voda: 4 šachty (Š) pri stredovej stene, v každej polovici krídla jedna, prechádzajú",
        "  1.NP aj podkrovím. Ležaté zvody pod podlahou v osi krídla, revízia v hale. V každej šachte",
        "  miesto na bytový vodomer SV+TV pre obe podlažia (spolu 8 meracích miest).",
        "*Elektro: rozvádzač RE v spoločnej hale dimenzovať na 6 elektromerov + 2 rezervy; do každej",
        "  polovice krídla (8 ×) uložiť samostatný prívod / chráničku a miesto na bytový rozvádzač.",
        "  Na začiatku osadené 3 elektromery, ostatné polia prázdne. Hlavný istič a MRK dimenzovať na 8 bytov.",
        "*Vykurovanie: v každej polovici krídla vlastný rozdeľovač podlahového kúrenia. Buď samostatné",
        "  zdroje (TČ / elektrokotol na byt), alebo spoločný zdroj + merače tepla na každej vetve.",
        "*Vetranie: digestory a odvetranie kúpeľní cez šachtu nad strechu – pre každý budúci byt samostatne.",
        "*Slaboprúd: z haly chránička do každej polovice krídla (internet, zvonček, videovrátnik 8 tlačidiel).",
        "*Požiar a akustika: stredové steny, stropy a steny k hale riešiť od začiatku ako medzibytové;",
        "  dvere z haly EI 30 / bezpečnostné.",
        "*Statika: priečne nosné steny (štíty, stredová stena), stropy uložené na obvodové steny a stredovú",
        "  stenu – priečky sú nenosné, dispozícia sa dá meniť.",
    ])
    y = min(ya, yb)
    y = panel(c, xa, y, "BILANCIA", [
        "*Povoľovaný stav:  predný dom 3 byty  +  prístavba 3 byty (102,7 + 102,7 + 227,3 m²)  =  6 bytov",
        "*Po rozdelení:       predný dom 3 byty  +  prístavba 6 bytov (4 × 51,4 m² + 2 × 102,7 m²)  =  9 bytov   (max. 11 pri delení podkrovia 2+2)",
    ])
    # legenda farieb
    lx, ly = 40, y - 5
    for k, n in (("A1", "byt A1"), ("A2", "byt A2"), ("B1", "byt B1"), ("B2", "byt B2"),
                 ("PA", "byt PA"), ("PB", "byt PB"), ("S", "spoločné")):
        c.setFillColorRGB(*COL[k])
        c.rect(lx, ly, 14, 9, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("F", 7)
        c.drawString(lx + 18, ly + 1.5, n)
        lx += 70
    titleblock(c, "SCHÉMA DELENIA NA 6 BYTOV",
               ["Bytový dom – NKP, prestavba a prístavba vo dvore",
                "Architektonická štúdia – variant „22 m do dvora“",
                "List 3/3   |   formát A3   |   11/2026",
                "Investor: LEFA Solutions s.r.o., Pažica 23, Prešov",
                "Interný podklad – neprikladať k žiadosti"])
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
