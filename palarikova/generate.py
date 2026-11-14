# -*- coding: utf-8 -*-
"""BD Palárikova – variant C (rev. 3): 18 bytov (16 + 2 na ustúpenom 4.NP), výťah, jednotka v 1.PP.
Súradnice v metroch: x = pozdĺž domu (0 = JZ štít), y = 0 fasáda k parkovisku, y rastie do záhrady."""
import sys
from engine import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "BD_Palarikova_variant_C_rev3_2026-11-14.pdf"
SUB = "18 bytov: 1.NP 5 + 2.NP 5 + 3.NP 6 + ustúpené 4.NP 2 · výťah 1.PP–4.NP · nebytový priestor (1-izb.) v 1.PP · fasáda 1.–3.NP bez zmeny"
TOTAL = 9
ZAST = 467.0  # zastavaná plocha podľa PD

WIN_P = [(0.8, 2.8), (3.5, 5.5), (9.5, 11.5), (12.725, 14.725), (15.5, 17.5),
         (18.725, 20.725), (21.5, 23.5), (27.5, 29.5), (30.4, 32.4)]


def k(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")


def mx(x):
    return 33.2 - x - (0.2 if x >= 5.9 - 1e-9 else 0)


class Zone:
    """Pomocník: pridáva prvky do plánu, voliteľne zrkadlovo (severný štít)."""

    def __init__(self, p, mirror=False):
        self.p, self.m = p, mirror

    def R(self, b):
        if not self.m:
            return r(*b)
        return r(mx(b[2]), b[1], mx(b[0]), b[3])

    def rooms(self, lst, col=None):
        out = []
        for name, rects, kw in lst:
            rects = rects if isinstance(rects, list) else [rects]
            kw = dict(kw)
            if col and "col" not in kw:
                kw["col"] = col
            if self.m and kw.get("lab"):
                kw["lab"] = (mx(kw["lab"][0]) + 0.1, kw["lab"][1])
            out.append(Room(name, [self.R(b) for b in rects], **kw))
        return out

    def part(self, *bs, new=False):
        (self.p.newpart if new else self.p.part).extend(self.R(b) for b in bs)

    def door(self, b, hinge, dr, bg=white):
        b2 = self.R(b)
        if self.m and hinge is not None:
            horiz = (b[2] - b[0]) >= (b[3] - b[1])
            if horiz:
                hinge = "r" if hinge == "l" else "l"
            else:
                dr = -dr
        self.p.doors.append((b2, hinge, dr, bg))

    def furn(self, kind, b):
        if self.m and kind in ("bedL", "bedR"):
            kind = "bedR" if kind == "bedL" else "bedL"
        self.p.furn.append((kind, self.R(b)))

    def bath(self, sh=None, wc=None, bs=None, tub=None, box=None):
        for kind, b in (("shower", sh), ("wc", wc), ("basin", bs), ("bath", tub), ("box", box)):
            if b:
                self.furn(kind, b)

    def text(self, x, y, s, **kw):
        if self.m:
            x = mx(x) + 0.1
        self.p.texts.append((x, y, s, kw))


# =====================================================================
#  TYPICKÉ PODLAŽIE (1.–3.NP)
# =====================================================================
def structure_typ(p, ground=False):
    S = p.struct
    S += [r(0, 0, 6.3, 0.4), r(5.9, 0, 6.3, 1.4), r(5.9, 1.0, 9.1, 1.4), r(8.7, 0, 9.1, 1.4),
          r(8.7, 0, 24.3, 0.4), r(23.9, 0, 24.3, 1.4), r(23.9, 1.0, 27.1, 1.4), r(26.7, 0, 27.1, 1.4),
          r(26.7, 0, 33.2, 0.4), r(0, 0, 0.4, 13.22), r(32.8, 0, 33.2, 13.22),
          r(0, 12.82, 6.1, 13.22), r(5.7, 12.82, 6.1, 15.048), r(5.7, 14.648, 9.3, 15.048),
          r(8.9, 13.648, 9.3, 15.048), r(8.9, 13.648, 12.1, 14.048), r(11.7, 13.648, 12.1, 15.048),
          r(11.7, 14.648, 27.3, 15.048), r(26.9, 12.82, 27.3, 15.048), r(26.9, 12.82, 33.2, 13.22),
          r(5.9, 0.4, 6.1, 12.82), r(8.9, 8.474, 9.1, 13.648),
          r(11.9, 0.4, 12.1, 6.574), r(11.9, 8.474, 12.1, 14.648),
          r(17.9, 0.4, 18.1, 6.574), r(17.9, 8.474, 18.1, 14.648),
          r(23.9, 0.4, 24.1, 6.574), r(23.9, 8.474, 24.1, 14.648),
          r(26.9, 0.4, 27.1, 12.82),
          r(6.1, 6.574, 26.9, 6.774), r(8.9, 8.274, 26.9, 8.474)]
    p.part += [r(17.5, 4.7, 17.9, 6.574), r(18.1, 4.7, 18.5, 6.574),
               r(17.5, 8.474, 17.9, 10.348), r(18.1, 8.474, 18.5, 10.348)]
    W = p.windows
    for a, b in WIN_P:
        W.append(r(a, 0.05, b, 0.35))
    W += [r(7.1, 1.05, 8.2, 1.35), r(25.1, 1.05, 26.2, 1.35),
          r(1.1, 12.87, 4.1, 13.17), r(9.95, 13.7, 11.05, 14.0),
          r(13.145, 14.7, 16.145, 15.0), r(19.856, 14.7, 22.856, 15.0), r(24.926, 14.7, 26.026, 15.0),
          r(29.1, 12.87, 32.1, 13.17), r(0.05, 7.125, 0.35, 7.725), r(32.85, 7.125, 33.15, 7.725)]
    if ground:
        p.doors.append((r(7.8, 14.648, 8.9, 15.048), "r", 1))
        p.texts.append((8.35, 16.75, "zadný vstup ±0,000", dict(size=4.6, bold=True)))
        p.texts.append((8.35, 17.0, "bezbariérovo k výťahu", dict(size=4.2)))
    else:
        W.append(r(6.5, 14.7, 8.5, 15.0))
    tn = "Terasa" if ground else "Balkón"
    p.terr += [("Lodžia", r(6.3, 0, 8.7, 1.0), "terr"), ("Lodžia", r(24.3, 0, 26.7, 1.0), "terr"),
               (tn, r(0, 13.22, 5.7, 15.048), "terr"), ("", r(9.3, 14.048, 11.7, 15.048), "terr"),
               (tn, r(12.9, 15.048, 16.4, 16.4), "terr"), (tn, r(19.6, 15.048, 23.1, 16.4), "terr"),
               ("", r(24.7, 15.048, 26.3, 16.4), "terr"),
               (tn, r(27.3, 13.22, 35.0 if ground else 33.2, 15.048), "terr")]
    p.dims += [("h", -1.5, [0, 33.2]),
               ("h", -0.8, [0, 0.4, 5.9, 6.1, 11.9, 12.1, 17.9, 18.1, 23.9, 24.1, 26.9, 27.1, 32.8, 33.2]),
               ("v", -0.9, [0, 15.048]), ("v", -0.4, [0, 0.4, 6.574, 6.774, 8.274, 8.474, 14.648, 15.048])]


def stairs(p, c):
    """Schodisko podľa PD: rameno 14 st. + medzipodesta pri fasáde + 3 st. späť."""
    for i in range(15):
        y = 8.5 + i * 0.3
        p.line(c, 6.1, y, 7.4, y, C["ink"], 0.3)
    p.line(c, 7.4, 8.5, 7.4, 12.7, C["ink"], 0.5)
    p.line(c, 7.45, 8.5, 7.45, 12.7, C["ink"], 0.3)
    for i in range(4):
        y = 11.8 + i * 0.3
        p.line(c, 7.5, y, 8.9, y, C["ink"], 0.3)
    p.line(c, 6.75, 12.5, 6.75, 8.7, C["ink"], 0.4)
    p.line(c, 6.75, 8.7, 6.65, 8.95, C["ink"], 0.4)
    p.line(c, 6.75, 8.7, 6.85, 8.95, C["ink"], 0.4)
    p.text(c, 7.5, 13.75, "Schodisko", 4.6)
    p.text(c, 7.5, 14.0, "17,85 m²", 4.2)


def lift(p, pp=False):
    p.new += [r(8.9, 8.274, 10.9, 8.474), r(10.7, 8.474, 10.9, 10.424), r(9.1, 10.224, 10.9, 10.424)]
    if pp:
        p.new.append(r(8.9, 8.274, 9.1, 10.424))
    p.fills.append(([r(9.1, 8.474, 10.7, 10.224)], HexColor("#fbd9b5")))
    p.doors.append((r(9.45, 8.274, 10.35, 8.474), None, 0, HexColor("#fbd9b5")))

    def cab(p, c):
        p.rect(c, r(9.35, 8.6, 10.45, 10.0), fill=white, stroke=C["new"], lw=0.5)
        p.line(c, 9.35, 8.6, 10.45, 10.0, C["new"], 0.3)
        p.line(c, 9.35, 10.0, 10.45, 8.6, C["new"], 0.3)
        p.rect(c, r(9.5, 9.05, 10.3, 9.6), fill=white)
        p.text(c, 9.9, 9.25, "VÝŤAH", 4.4, bold=True, col=C["new"])
        p.text(c, 9.9, 9.47, "630 kg", 3.6, col=C["new"])
        p.text(c, 9.9, 10.19, "šachta 1600×1750", 3.0, col=C["new"])
    p.extra.append(cab)


def tag(z, x, y, a, what="1-izb."):
    """Štítok odčleniteľnej jednotky."""
    z.text(x, y, "ODČLENITEĽNÁ JEDNOTKA", size=3.9, bold=True, col=C["split"])
    z.text(x, y + 0.24, f"{what} · {k(a)} m²", size=3.9, bold=True, col=C["split"])


def end_bay(p, mode, mirror=False, ca=None, cb=None):
    """Štítový byt (B01 juh / B06 sever). mode: off | split | merge.
    Vráti (rooms1, rooms2, zadv_rect). ca/cb = farba základnej / odčleniteľnej časti."""
    z = Zone(p, mirror)
    z.part(r(0.4, 4.9, 5.9, 5.0), r(2.2, 5.0, 2.3, 6.7), r(0.4, 6.7, 5.9, 6.8),
           r(2.9, 6.8, 3.0, 8.1), r(4.4, 6.8, 4.5, 8.1), r(0.4, 8.1, 3.0, 8.2), r(4.4, 8.1, 5.9, 8.2))
    z.door(r(5.9, 6.95, 6.1, 7.95), "t", -1)                      # vstup z chodby – krídlo k stene
    z.door(r(2.2, 5.85, 2.3, 6.65), "b", 1)                       # kúpeľňa 1 – von, k stene
    z.door(r(2.9, 6.85, 3.0, 7.65), "t", -1)                      # kúpeľňa 2 – dnu, k stene
    z.bath(sh=r(0.45, 5.05, 1.35, 5.95), wc=r(0.45, 6.1, 1.0, 6.5), bs=r(1.55, 5.05, 2.15, 5.5))
    z.bath(sh=r(1.2, 7.15, 2.1, 8.05), wc=r(0.45, 7.2, 1.0, 7.6), bs=r(1.3, 6.85, 1.9, 7.1))
    kup1 = ("Kúp.", r(0.4, 5.0, 2.2, 6.7), dict(small=True, lab=(1.75, 6.25)))
    kup2 = ("Kúp.", r(0.4, 6.8, 2.9, 8.1), dict(small=True, lab=(2.5, 7.85)))
    pred = ("Predsieň", r(2.3, 5.0, 5.9, 6.7), dict(lab=(4.1, 5.8)))
    zadv = z.R(r(4.5, 6.8, 5.9, 8.1))
    if mode == "off":
        z.part(r(3.2, 0.4, 3.3, 4.9))
        z.door(r(2.35, 4.9, 3.15, 5.0), "r", -1)
        z.door(r(3.35, 4.9, 4.15, 5.0), "l", -1)
        z.door(r(5.05, 6.7, 5.85, 6.8), None, 0)
        z.door(r(4.4, 6.85, 4.5, 7.65), None, 0)
        z.furn("bedL", r(0.5, 1.3, 2.5, 2.9))
        z.furn("bedR", r(3.85, 2.3, 5.85, 3.2))
        z.furn("kitchen", r(0.5, 8.25, 2.9, 8.85))
        z.furn("table", r(3.7, 9.9, 5.3, 10.7))
        z.furn("box", r(0.5, 10.0, 1.4, 12.2))
        r1 = z.rooms([("Izba", r(0.4, 0.4, 3.2, 4.9), dict(lab=(1.8, 3.7))),
                      ("Izba", r(3.3, 0.4, 5.9, 4.9), dict(lab=(4.6, 4.1))), kup1, pred], col=cb)
        r2 = z.rooms([("Zádv.", r(4.5, 6.8, 5.9, 8.1), dict(small=True)), kup2,
                      ("Obývacia izba + KK", [r(0.4, 8.2, 5.9, 12.82), r(3.0, 6.8, 4.4, 8.2)], dict(lab=(2.4, 9.4)))], col=ca)
        tag(z, 2.9, 0.75, sum(x.a for x in r1))
        return r2 + r1, [], None
    # split / merge: dve samostatné jednotky + spoločné zádverie
    z.door(r(3.35, 4.9, 4.15, 5.0), "l", -1)
    if mode == "split":
        z.door(r(5.05, 6.7, 5.85, 6.8), "r", -1)                  # vstup jednotky 1 – k stene
        z.door(r(4.4, 6.85, 4.5, 7.65), "t", -1)                  # vstup jednotky 2 – k stene
        z.part(r(3.0, 8.1, 4.4, 8.2))
        z.door(r(3.05, 8.1, 3.85, 8.2), "l", 1)
        z.furn("kitchen", r(0.5, 4.3, 3.1, 4.9))
        z.furn("bedL", r(0.5, 0.9, 2.5, 2.5))
        z.furn("table", r(3.9, 2.5, 5.1, 3.3))
        z.furn("kitchen", r(0.5, 8.25, 2.9, 8.85))
        z.furn("bedR", r(3.85, 10.4, 5.85, 12.0))
        z.furn("table", r(1.0, 10.4, 2.2, 11.2))
        r1 = z.rooms([("Obytná izba + KK", r(0.4, 0.4, 5.9, 4.9), dict(lab=(3.6, 3.8))), kup1, pred])
        r2 = z.rooms([("Obytná izba + KK", r(0.4, 8.2, 5.9, 12.82), dict(lab=(3.0, 9.6))),
                      ("Pred.", r(3.0, 6.8, 4.4, 8.1), dict(small=True)), kup2])
    else:  # merge – jednotky sú izbami susedných bytov (B04 / B05); 2. vstupy len pripravené
        z.door(r(5.05, 6.7, 5.85, 6.8), None, 0, C["split"])
        z.door(r(4.4, 6.85, 4.5, 7.65), None, 0, C["split"])
        z.furn("bedL", r(0.5, 1.2, 2.5, 2.8))
        z.furn("box", r(4.2, 0.5, 5.8, 1.1))
        z.furn("bedL", r(0.5, 10.2, 2.5, 11.8))
        z.furn("box", r(0.5, 8.25, 2.9, 8.85))
        r1 = z.rooms([("Izba (spálňa + pracovňa)", r(0.4, 0.4, 5.9, 4.9), dict(lab=(3.4, 3.9))), kup1,
                      ("Predsieň / šatník", r(2.3, 5.0, 5.9, 6.7), dict(lab=(4.0, 5.8)))], col=ca)
        r2 = z.rooms([("Izba (spálňa)", [r(0.4, 8.2, 5.9, 12.82), r(3.0, 6.8, 4.4, 8.2)], dict(lab=(3.4, 9.6))), kup2], col=cb)
        tag(z, 4.3, 2.2, sum(x.a for x in r1))
        tag(z, 4.2, 12.0, sum(x.a for x in r2))
    return r1, r2, zadv


def typical(p, floor, south="off", b02="off", north="b06", ids=None):
    """Zostaví podlažie. Vráti zoznam bytov."""
    g = floor == 1
    off = south == "off"            # stav do povolenia → farebné rozlíšenie častí
    structure_typ(p, ground=g)
    lift(p)
    p.extra.append(stairs)
    p.common.append(("Spoločná chodba", [r(6.1, 6.774, 26.9, 8.274)]))
    p.fills.append(([r(6.1, 8.274, 8.9, 14.648)], C["common"]))
    tn = "terasa" if g else "balkón"
    F = []
    n = [0]

    def fid():
        n[0] += 1
        return f"B{floor}.{n[0]:02d}" if ids is None else ids[n[0] - 1]

    z = Zone(p)
    # ---------- JUH (B01) ----------
    if off:
        r1, r2, zadv = end_bay(p, "off", ca="a1", cb="b1")
        F.append(Flat(fid(), "3", "3-izb.", r1, f"{tn} 10,4", "PD B01 · → 2× 1-izb.", head=(3.3, 11.8)))
        p.splits += [(0.4, 6.75, 4.45, 6.75), (4.45, 6.75, 4.45, 8.15), (4.45, 8.15, 5.9, 8.15)]
    else:
        r1, r2, zadv = end_bay(p, south)
        F.append(Flat(fid(), "1", "1-izb.", r1, "–", "z B01", head=(4.3, 1.2)))
        f2 = Flat(fid(), "1", "1-izb.", r2, f"{tn} 10,4", "z B01", head=(3.0, 11.6))
        p.common.append(("Zádv.", [zadv]))
    # ---------- B02 ----------
    z.part(r(12.1, 4.6, 17.9, 4.7), r(15.5, 4.7, 15.6, 6.574))
    z.door(r(14.5, 6.574, 15.5, 6.774), "r", -1)                  # vstup – krídlo k priečke kúpeľne
    z.door(r(12.9, 4.6, 13.8, 4.7), None, 0)
    z.door(r(15.5, 4.75, 15.6, 5.55), "t", -1)                    # kúpeľňa – von, k stene
    z.bath(sh=r(16.55, 4.75, 17.45, 5.65), bs=r(15.7, 6.07, 16.3, 6.52), wc=r(16.9, 5.95, 17.45, 6.35))
    z.furn("kitchen", r(14.9, 4.0, 17.8, 4.6))
    z.furn("table", r(12.7, 2.0, 14.3, 2.8))
    u3 = [("Obývacia izba + KK", r(12.1, 0.4, 17.9, 4.6), dict(lab=(15.6, 2.9))),
          ("Predsieň", r(12.1, 4.7, 15.5, 6.574), dict(lab=(13.4, 5.6))),
          ("Kúp.", r(15.6, 4.7, 17.5, 6.574), dict(small=True, lab=(16.2, 5.6)))]
    if b02 == "off":
        z.part(r(9.0, 1.4, 9.1, 6.574), r(9.1, 4.874, 11.9, 4.974))
        z.door(r(11.9, 5.25, 12.1, 6.15), None, 0)
        z.door(r(9.15, 4.874, 9.95, 4.974), "l", -1)
        z.door(r(9.0, 5.72, 9.1, 6.52), "b", -1)
        z.furn("bedL", r(6.2, 2.6, 8.2, 4.2))
        z.furn("bedL", r(9.2, 1.2, 11.2, 2.8))
        ra = z.rooms([("Izba", r(6.1, 1.4, 9.0, 6.574), dict(lab=(7.55, 5.0))),
                      ("Izba", r(9.1, 0.4, 11.9, 4.874), dict(lab=(10.7, 3.7))),
                      ("Chodba", r(9.1, 4.974, 11.9, 6.574), dict(lab=(10.5, 5.5)))], col="b2")
        F.append(Flat(fid(), "3", "3-izb.", z.rooms(u3, col="a2") + ra, "lodžia 2,4", "PD B02 · → 2× 1-izb.", head=(16.2, 1.3)))
        p.splits.append((12.0, 0.4, 12.0, 6.574))
        tag(z, 10.5, 0.75, sum(x.a for x in ra))
        p.texts.append((10.5, 6.35, "príprava ZTI (kúpeľňa)", dict(size=3.6, col=C["split"])))
        p.texts.append((7.6, 6.42, "pripravený 2. vstup", dict(size=3.6, col=C["split"])))
    else:
        z.part(r(9.0, 4.874, 9.1, 6.574), r(9.1, 4.874, 11.9, 4.974))
        p.new.append(r(11.9, 5.25, 12.1, 6.15))
        z.door(r(6.15, 6.574, 7.15, 6.774), "l", -1)
        z.door(r(9.0, 5.72, 9.1, 6.52), "b", -1)
        z.bath(sh=r(10.95, 5.02, 11.85, 5.92), bs=r(9.9, 5.02, 10.5, 5.47), wc=r(11.3, 6.1, 11.85, 6.5))
        z.furn("kitchen", r(6.15, 2.2, 6.75, 4.8))
        z.furn("bedR", r(9.85, 0.9, 11.85, 2.5))
        z.furn("table", r(7.6, 2.2, 8.8, 3.0))
        ra = z.rooms([("Obytná izba + KK", [r(6.1, 1.4, 9.0, 6.574), r(9.0, 0.4, 11.9, 4.874)], dict(lab=(8.4, 4.2))),
                      ("Kúp.", r(9.1, 4.974, 11.9, 6.574), dict(small=True, lab=(10.3, 6.1)))])
        F.append(Flat(fid(), "1", "1-izb.", ra, "lodžia 2,4", "z B02", head=(10.4, 3.4)))
        F.append(Flat(fid(), "1", "1-izb.", z.rooms(u3), "–", "z B02", head=(16.2, 1.3)))
    # ---------- B03 (pri výťahu) ----------
    z.part(r(12.1, 10.348, 17.9, 10.448), r(15.5, 8.474, 15.6, 10.348))
    z.door(r(14.5, 8.274, 15.5, 8.474), "r", 1)
    z.door(r(12.9, 10.348, 13.8, 10.448), None, 0)
    z.door(r(11.9, 8.52, 12.1, 9.32), "t", -1)
    z.door(r(15.5, 9.5, 15.6, 10.3), "b", -1)
    z.bath(sh=r(16.55, 9.4, 17.45, 10.3), bs=r(15.7, 8.52, 16.3, 8.97), wc=r(16.9, 8.6, 17.45, 9.0))
    z.furn("kitchen", r(14.9, 10.45, 17.8, 11.05))
    z.furn("table", r(12.7, 12.4, 14.3, 13.2))
    z.furn("bedL", r(9.2, 11.4, 11.2, 13.0))
    rooms = z.rooms([("Obývacia izba + KK", r(12.1, 10.448, 17.9, 14.648), dict(lab=(15.4, 12.2))),
                     ("Predsieň", r(12.1, 8.474, 15.5, 10.348), dict(lab=(13.4, 9.5))),
                     ("Kúp.", r(15.6, 8.474, 17.5, 10.348), dict(small=True, lab=(16.2, 9.4))),
                     ("Izba", [r(9.1, 10.424, 11.9, 13.648), r(10.9, 8.474, 11.9, 10.424)], dict(lab=(10.5, 10.9)))],
                    col="n1" if off else None)
    b03 = Flat("", "2", "2-izb.", rooms, f"{tn} 2,4 + 4,7", "PD B03 − výťah", head=(16.2, 13.6))
    # ---------- B04 ----------
    z.part(r(18.1, 4.6, 23.9, 4.7), r(20.4, 4.7, 20.5, 6.574))
    z.door(r(20.5, 6.574, 21.5, 6.774), "l", -1)
    z.door(r(22.2, 4.6, 23.1, 4.7), None, 0)
    z.door(r(20.4, 4.75, 20.5, 5.55), "t", 1)
    z.bath(sh=r(18.55, 4.75, 19.45, 5.65), bs=r(19.7, 6.07, 20.3, 6.52), wc=r(18.55, 5.95, 19.1, 6.35))
    z.furn("kitchen", r(18.2, 4.0, 21.1, 4.6))
    z.furn("table", r(21.7, 2.0, 23.3, 2.8))
    b04 = [("Obývacia izba + KK", r(18.1, 0.4, 23.9, 4.6), dict(lab=(20.4, 2.9))),
           ("Predsieň", r(20.5, 4.7, 23.9, 6.574), dict(lab=(22.6, 5.6))),
           ("Kúp.", r(18.5, 4.7, 20.4, 6.574), dict(small=True, lab=(19.8, 5.6)))]
    # ---------- B05 ----------
    z.part(r(18.1, 10.348, 23.9, 10.448), r(20.4, 8.474, 20.5, 10.348))
    z.door(r(20.5, 8.274, 21.5, 8.474), "l", 1)
    z.door(r(22.2, 10.348, 23.1, 10.448), None, 0)
    z.door(r(20.4, 9.5, 20.5, 10.3), "b", 1)
    z.door(r(23.9, 8.52, 24.1, 9.32), "t", 1)
    z.bath(sh=r(18.55, 9.4, 19.45, 10.3), bs=r(19.7, 8.52, 20.3, 8.97), wc=r(18.55, 8.6, 19.1, 9.0))
    z.furn("kitchen", r(18.2, 10.45, 21.1, 11.05))
    z.furn("table", r(21.7, 12.4, 23.3, 13.2))
    z.furn("bedL", r(24.2, 12.0, 26.2, 13.6))
    b05 = [("Obývacia izba + KK", r(18.1, 10.448, 23.9, 14.648), dict(lab=(20.6, 12.2))),
           ("Predsieň", r(20.5, 8.474, 23.9, 10.348), dict(lab=(22.6, 9.5))),
           ("Kúp.", r(18.5, 8.474, 20.4, 10.348), dict(small=True, lab=(19.8, 9.4)))]
    # ---------- SEVER ----------
    if north == "merge":
        r1, r2, zadv = end_bay(p, "merge", mirror=True, ca="b4", cb="b5")
        z.part(r(24.1, 4.9, 26.9, 5.0), new=True)
        z.door(r(24.15, 4.9, 24.95, 5.0), "l", -1)
        z.door(r(23.9, 5.3, 24.1, 6.2), None, 0)
        z.door(r(26.9, 5.72, 27.1, 6.52), "b", 1)
        z.furn("bedL", r(24.2, 1.6, 26.2, 3.2))
        z.furn("box", r(25.2, 5.05, 26.85, 5.6))
        ra = z.rooms(b04 + [("Izba", r(24.1, 1.4, 26.9, 4.9), dict(lab=(25.6, 4.0))),
                            ("Chodba / šatník", r(24.1, 5.0, 26.9, 6.574), dict(lab=(25.5, 6.0)))], col="a4") + r1
        z.part(r(24.1, 10.348, 26.9, 10.448))
        z.door(r(24.15, 10.348, 24.95, 10.448), "l", 1)
        z.door(r(26.9, 8.52, 27.1, 9.32), "t", 1)
        z.furn("box", r(25.2, 9.7, 26.85, 10.3))
        rb = z.rooms(b05 + [("Chodba / šatník", r(24.1, 8.474, 26.9, 10.348), dict(lab=(25.6, 9.3))),
                            ("Izba", r(24.1, 10.448, 26.9, 14.648), dict(lab=(25.5, 11.3)))], col="a5") + r2
        b03.id = fid()
        F.append(b03)
        F.append(Flat(fid(), "3", "3-izb.", ra, "lodžia 2,4", "B04 + ½ B06 → 2-izb. + 1-izb.", head=(19.9, 1.3)))
        F.append(Flat(fid(), "3", "3-izb.", rb, f"{tn} 4,7 + 2,2 + {'14,1' if g else '10,8'}",
                      "B05 + ½ B06 → 2-izb. + 1-izb.", head=(19.9, 13.6)))
        p.common.append(("Zádv.", [zadv]))
        p.splits += [(27.0, 0.4, 27.0, 6.574), (27.0, 8.474, 27.0, 12.82)]
        p.texts.append((28.6, 6.62, "2. vstup", dict(size=3.4, col=C["split"])))
        p.texts.append((29.3, 7.3, "2. vstup", dict(size=3.4, col=C["split"])))
    else:
        z.door(r(23.9, 5.72, 24.1, 6.52), "b", 1)
        z.furn("bedL", r(24.2, 2.2, 26.2, 3.8))
        z.furn("box", r(26.25, 8.55, 26.85, 10.3))
        ra = z.rooms(b04 + [("Izba", r(24.1, 1.4, 26.9, 6.574), dict(lab=(25.5, 4.8)))], col="n2" if off else None)
        rb = z.rooms(b05 + [("Izba so šatníkom", r(24.1, 8.474, 26.9, 14.648), dict(lab=(25.4, 11.0)))], col="n1" if off else None)
        b03.id = fid()
        F.append(b03)
        if off:
            F.append(Flat(fid(), "2", "2-izb.", ra, "lodžia 2,4", "PD B04", head=(19.9, 1.3)))
            F.append(Flat(fid(), "2", "2-izb.", rb, f"{tn} 4,7 + 2,2", "PD B05 · bez 2. predsiene", head=(19.9, 13.6)))
            r1, r2, zadv = end_bay(p, "off", mirror=True, ca="a5", cb="b5")
            F.append(Flat(fid(), "3", "3-izb.", r1, f"{tn} 10,8", "PD B06 · → 2× 1-izb.", head=(29.9, 11.8)))
            p.splits += [(32.8, 6.75, 28.75, 6.75), (28.75, 6.75, 28.75, 8.15), (28.75, 8.15, 27.1, 8.15)]
        else:  # všetko rozdelené
            F.append(Flat(fid(), "2", "2-izb.", ra, "lodžia 2,4", "B04", head=(19.9, 1.3)))
            F.append(Flat(fid(), "2", "2-izb.", rb, f"{tn} 4,7 + 2,2", "B05", head=(19.9, 13.6)))
            r1, r2, zadv = end_bay(p, "split", mirror=True)
            F.append(Flat(fid(), "1", "1-izb.", r1, "–", "z B06", head=(29.0, 1.2)))
            F.append(Flat(fid(), "1", "1-izb.", r2, f"{tn} 10,8", "z B06", head=(30.2, 11.6)))
            p.common.append(("Zádv.", [zadv]))
    if not off:
        F.insert(1, f2)
        for i, f in enumerate(F):
            f.id = ids[i] if ids else f"B{floor}.{i + 1:02d}"
    p.flats = F
    return F


# =====================================================================
#  1.PP
# =====================================================================
def plan_pp(p):
    S = p.struct
    S += [r(0, 6.376, 2.4, 6.776), r(3.9, 6.376, 6.95, 6.776), r(9.49, 6.376, 14.265, 6.776),
          r(15.765, 6.376, 20.265, 6.776), r(21.765, 6.376, 24.745, 6.776), r(26.245, 6.376, 29.249, 6.776),
          r(30.749, 6.376, 33.2, 6.776),
          r(0, 6.376, 0.4, 13.22), r(32.8, 6.376, 33.2, 13.22),
          r(0, 12.82, 6.1, 13.22), r(5.7, 12.82, 6.1, 15.048), r(5.7, 14.648, 27.3, 15.048),
          r(26.9, 12.82, 27.3, 15.048), r(26.9, 12.82, 33.2, 13.22),
          r(5.9, 6.776, 6.1, 12.82), r(7.5, 9.676, 12.1, 9.876), r(8.9, 9.876, 9.1, 14.648),
          r(11.9, 6.776, 12.1, 14.648), r(12.1, 8.276, 26.9, 8.476), r(17.9, 8.476, 18.1, 14.648),
          r(23.9, 8.476, 24.1, 14.648), r(26.9, 6.776, 27.1, 12.82)]
    p.part += [r(7.4, 9.876, 7.5, 13.2)]
    for x in (0.15, 5.9, 11.9, 17.9, 23.9, 26.9, 32.75):
        S.append(r(x, 0.77, x + 0.3, 5.48))
    p.fills.append(([r(0, 0, 33.2, 6.376)], C["park"]))
    p.windows += [r(2.4, 6.43, 3.9, 6.73), r(14.265, 6.43, 15.765, 6.73), r(20.265, 6.43, 21.765, 6.73),
                  r(24.745, 6.43, 26.245, 6.73), r(29.249, 6.43, 30.749, 6.73), r(8.1, 6.43, 9.49, 6.73)]
    p.doors += [(r(6.95, 6.376, 8.05, 6.776), "l", -1),              # hlavný vstup – von
                (r(5.9, 6.95, 6.1, 7.95), "t", -1),                 # vstup do NP0.01 z vestibulu
                (r(11.9, 6.85, 12.1, 7.75), "t", 1),
                (r(7.55, 9.676, 8.4, 9.876), "l", 1),
                (r(11.0, 9.676, 11.85, 9.876), "r", 1),
                (r(12.15, 8.276, 13.05, 8.476), "l", 1), (r(18.15, 8.276, 19.05, 8.476), "l", 1),
                (r(24.15, 8.276, 25.05, 8.476), "l", 1), (r(26.9, 6.85, 27.1, 7.75), "t", 1)]
    lift(p, pp=True)
    p.common += [("104 Vestibul", [r(7.5, 6.776, 11.9, 8.274), r(6.1, 6.776, 7.5, 8.476), r(7.5, 8.274, 8.9, 9.676),
                                    r(10.9, 8.274, 11.9, 9.676)]),
                 ("102 Pod schod.", [r(7.5, 9.876, 8.9, 14.648)]),
                 ("103 Kočíky / bicykle", [r(9.1, 10.424, 11.9, 14.648), r(10.9, 9.876, 11.9, 10.424)]),
                 ("105 Chodba", [r(12.1, 6.776, 26.9, 8.276)]),
                 ("106 Kobky 1", [r(12.1, 8.476, 17.9, 14.648)]), ("107 Kobky 2", [r(18.1, 8.476, 23.9, 14.648)]),
                 ("108 Rezerva / upratovanie", [r(24.1, 8.476, 26.9, 14.648)]),
                 ("109 Technika", [r(27.1, 6.776, 32.8, 12.82)])]
    p.fills.append(([r(6.1, 8.476, 7.4, 14.648)], C["common"]))

    def st(p, c):
        for i in range(16):
            y = 8.476 + i * 0.28
            p.line(c, 6.1, y, 7.4, y, C["ink"], 0.3)
        p.line(c, 6.75, 8.6, 6.75, 12.5, C["ink"], 0.4)
        p.text(c, 15.0, 3.2, "kryté parkovacie státia pod domom (bez zmeny)", 6, col=HexColor("#7a7a7a"))
        p.text(c, 9.6, 5.6, "HLAVNÝ VSTUP", 5.5, bold=True)
        p.text(c, 9.6, 5.9, "z parkoviska −2,800", 4.4)
        p.rect(c, r(0, 7.3, 0.4, 8.3), fill=C["new"])
        p.text(c, -0.15, 7.75, "dvere z PD zrušené", 4, col=C["new"], align="r")
        p.text(c, -0.15, 8.0, "(zamurované)", 4, col=C["new"], align="r")
    p.extra.append(st)
    # ---- nebytový priestor rozkreslený ako 1-izbový byt (vstup len z vestibulu) ----
    z = Zone(p)
    z.part(r(4.3, 6.776, 4.4, 8.3), r(3.5, 8.3, 5.9, 8.4), r(3.5, 8.4, 3.6, 10.4), r(3.5, 10.3, 5.9, 10.4), new=True)
    z.door(r(4.3, 7.45, 4.4, 8.25), "b", 1)          # predsieň → izba, krídlo k priečke
    z.door(r(3.5, 8.45, 3.6, 9.25), "t", 1)          # kúpeľňa, krídlo dnu k stene
    z.bath(sh=r(4.95, 9.35, 5.85, 10.25), wc=r(5.3, 8.5, 5.85, 8.9), bs=r(3.7, 9.8, 4.3, 10.25))
    z.furn("kitchen", r(0.5, 6.83, 3.6, 7.43))
    z.furn("table", r(1.0, 8.7, 2.2, 9.5))
    z.furn("bedR", r(3.85, 10.75, 5.85, 12.35))      # čelo postele pri stene
    z.furn("box", r(0.5, 10.6, 1.1, 12.7))
    rooms = z.rooms([("Obytná izba + KK", [r(0.4, 6.776, 4.3, 8.4), r(0.4, 8.4, 3.5, 10.4), r(0.4, 10.4, 5.9, 12.82)],
                      dict(lab=(2.3, 10.2))),
                     ("Pred.", r(4.4, 6.776, 5.9, 8.3), dict(small=True, lab=(5.2, 8.0))),
                     ("Kúp.", r(3.6, 8.4, 5.9, 10.3), dict(small=True, lab=(4.5, 9.3)))])
    f = Flat("NP0.01", "nb", "1-izb. (nebyt.)", rooms, "–", "PD 1.01 Domovník", head=(2.4, 11.6), count=False)
    p.flats = [f]
    p.dims += [("h", -0.4, [0, 33.2]), ("v", -0.9, [6.376, 15.048])]
    return [f]


# =====================================================================
#  4.NP – ustúpené podlažie, tri varianty (celá strecha = terasy bytov)
#  V1: krídlo izieb – chodba popri schodisku s terasou vpredu – výbežok obývačky
#  V2: bez chodby – obývačky oboch bytov vedľa seba v strede
#  V3: jeden veľký byt
# =====================================================================
VAR = {1: dict(x1=21.1), 2: dict(x1=19.0), 3: dict(x1=27.15)}
WING = (0, 2.9, 5.85, 13.22)
YS3 = 3.4


def gross_rects(v):
    x1 = VAR[v]["x1"]
    if v == 1:
        return [WING, (5.85, 2.9, 6.3, 4.674), (5.85, 4.674, 10.9, 6.574), (10.9, 1.0, 16.6, 6.574),
                (5.85, 6.574, x1, 15.048), (16.6, 6.374, x1, 6.574)]
    if v == 2:
        return [WING, (5.7, 1.0, 16.6, 2.9), (5.85, 2.9, 16.6, 6.574), (5.85, 6.574, x1, 15.048), (16.6, 6.374, x1, 6.574)]
    return [(5.85, 6.574, 10.7, 15.048), (10.7, YS3, x1, 15.048)]


def gross_4np(v):
    return area(gross_rects(v))


def core4(p, x1):
    p.new += [r(5.9, 6.574, 6.1, 12.82), r(5.7, 12.82, 6.1, 15.048), r(5.7, 14.648, x1, 15.048),
              r(8.9, 8.474, 9.1, 14.648), r(10.9, 6.774, 11.1, 10.424), r(9.1, 10.224, 11.1, 10.424)]
    p.struct += [r(0, 0, 33.2, 0.3), r(32.9, 0, 33.2, 13.22), r(27.0, 12.92, 33.2, 13.22)]
    if x1 < 27.0:
        p.struct += [r(27.0, 12.92, 27.3, 15.048), r(x1, 14.748, 27.3, 15.048)]
    lift(p)
    p.extra.append(stairs)
    p.common.append(("Chodba pred výťahom", [r(6.1, 6.774, 10.9, 8.274)]))
    p.fills.append(([r(6.1, 8.274, 8.9, 14.648)], C["common"]))
    p.windows.append(r(6.5, 14.7, 8.5, 15.0))


def wing4(p, z, hall_to_living):
    """Ľavé krídlo B4.01: izba 1, izba 2, spoločná kúpeľňa s WC a spálňa so šatníkom a vlastnou kúpeľňou."""
    p.new += [r(0, 2.9, 0.4, 13.22), r(0, 2.9, 6.1, 3.3), r(0, 12.82, 6.1, 13.22)]
    p.struct.append(r(0, 0, 0.3, 2.9))
    z.part(r(3.8, 3.3, 3.9, 5.074), r(3.9, 4.974, 5.9, 5.074), r(4.6, 5.074, 4.7, 9.0), r(0.4, 6.2, 4.6, 6.3),
           r(0.4, 9.0, 5.9, 9.1), r(3.9, 9.1, 4.0, 12.82), r(4.0, 10.6, 5.9, 10.7), new=True)
    z.door(r(4.9, 4.974, 5.7, 5.074), "r", -1)       # kúpeľňa – krídlo k stene
    z.door(r(4.6, 5.3, 4.7, 6.1), "b", -1)           # izba 1 – k priečke
    z.door(r(4.6, 6.4, 4.7, 7.2), "t", -1)           # izba 2 – k priečke
    z.door(r(4.9, 9.0, 5.7, 9.1), "r", 1)            # šatník spálne – k stene
    z.door(r(3.9, 9.3, 4.0, 10.3), None, 0, C["t4"])  # šatník → spálňa (priechod)
    z.door(r(4.3, 10.6, 5.1, 10.7), "l", 1)          # kúpeľňa spálne – k priečke
    z.bath(sh=r(3.95, 3.35, 4.85, 4.25), wc=r(5.3, 3.4, 5.85, 3.8), bs=r(4.0, 4.45, 4.6, 4.9))
    z.bath(sh=r(4.95, 11.9, 5.85, 12.77), wc=r(5.3, 11.0, 5.85, 11.4), bs=r(4.05, 12.2, 4.5, 12.75))
    z.furn("bedL", r(0.5, 4.3, 2.5, 5.2))
    z.furn("bedL", r(0.5, 7.2, 2.5, 8.1))
    z.furn("bedL", r(0.5, 10.2, 2.5, 11.8))
    z.furn("box", r(4.05, 9.15, 4.6, 10.5))
    p.windows += [r(0.9, 2.95, 3.3, 3.25), r(4.4, 2.95, 5.4, 3.25), r(0.05, 3.9, 0.35, 5.5), r(0.05, 6.8, 0.35, 8.5),
                  r(0.05, 9.8, 0.35, 11.8), r(1.0, 12.87, 3.4, 13.17), r(4.5, 12.87, 5.5, 13.17)]
    return [("Izba 1", [r(0.4, 3.3, 3.8, 6.2), r(3.8, 5.074, 4.6, 6.2)], dict(lab=(2.9, 3.9))),
            ("Izba 2", r(0.4, 6.3, 4.6, 9.0), dict(lab=(3.5, 7.2))),
            ("Kúpeľňa + WC", r(3.9, 3.3, 5.9, 4.974), dict(small=True, lab=(5.25, 4.6))),
            ("Spálňa", r(0.4, 9.1, 3.9, 12.82), dict(lab=(3.0, 10.9))),
            ("Šatník", r(4.0, 9.1, 5.9, 10.6), dict(small=True, lab=(5.25, 9.9))),
            ("Kúpeľňa + WC", r(4.0, 10.7, 5.9, 12.82), dict(small=True, lab=(4.9, 11.6)))]


def suite_b(z):
    """Spálňa B4.02 so šatníkom a vlastnou kúpeľňou za výťahom."""
    z.part(r(11.0, 10.424, 11.1, 14.648), r(9.1, 12.0, 11.0, 12.1), new=True)
    z.door(r(11.0, 10.7, 11.1, 11.7), None, 0, C["t4"])   # spálňa → šatník
    z.door(r(9.3, 12.0, 10.1, 12.1), "l", 1)              # kúpeľňa – k stene
    z.bath(tub=r(9.15, 13.85, 10.95, 14.6), wc=r(10.4, 12.4, 10.95, 12.8), bs=r(10.3, 13.15, 10.9, 13.6))
    z.furn("box", r(9.15, 10.5, 9.7, 11.9))
    return [("Šatník", r(9.1, 10.424, 11.0, 12.0), dict(small=True, lab=(10.4, 11.2))),
            ("Kúpeľňa + WC", r(9.1, 12.1, 11.0, 14.648), dict(small=True, lab=(9.8, 13.1)))]


def plan_4np(p, v):
    x1 = VAR[v]["x1"]
    xr = x1 - 0.4
    N, W = p.new, p.windows
    z = Zone(p)
    core4(p, x1)
    if v == 3:
        return plan_4np_single(p, z, x1, xr)
    A = wing4(p, z, v == 1)
    N += [r(5.9, 6.574, 16.6, 6.774), r(16.2, 6.374, x1, 6.774), r(xr, 6.374, x1, 15.048), r(16.2, 1.0, 16.6, 6.774)]
    z.door(r(10.9, 6.95, 11.1, 7.85), "t", 1)              # vstup B4.02 – krídlo k stene
    if v == 1:
        # ---------- B4.01: chodba popri schodisku + výbežok obývačky ----------
        N += [r(5.9, 2.9, 6.3, 5.074), r(5.9, 4.674, 11.3, 5.074), r(10.9, 1.0, 11.3, 5.074), r(10.9, 1.0, 16.6, 1.4)]
        z.door(r(8.6, 6.574, 9.5, 6.774), "r", -1)         # vstup B4.01
        W += [r(6.8, 4.724, 10.4, 5.024), r(11.9, 1.05, 15.6, 1.35), r(10.95, 1.7, 11.25, 3.9)]
        z.furn("kitchen", r(15.6, 1.8, 16.2, 5.2))
        z.furn("table", r(12.3, 2.3, 13.9, 3.1))
        z.furn("box", r(12.2, 5.65, 14.6, 6.5))
        A = [("Obývacia izba + kuchyňa", r(11.3, 1.4, 16.2, 6.574), dict(lab=(13.4, 4.95))),
             ("Chodba", [r(5.9, 5.074, 11.3, 6.574), r(4.7, 5.074, 5.9, 9.0)], dict(lab=(7.4, 5.75), small=True))] + A
        ta = [r(0.3, 0.3, 10.9, 2.9), r(6.3, 2.9, 10.9, 4.674), r(10.9, 0.3, 16.6, 1.0)]
        p.terr += [("Terasa B4.01", ta[0], "terr"), ("Terasa pri schodisku", ta[1], "terr"), ("", ta[2], "terr")]
        hA = (13.3, 3.95)
        # ---------- B4.02 ----------
        z.part(r(12.5, 6.774, 12.6, 8.4), r(12.5, 8.4, 14.8, 8.5), r(14.7, 6.774, 14.8, 9.6), r(11.1, 9.6, 16.7, 9.7),
               r(13.7, 9.7, 13.8, 14.648), r(16.6, 9.6, 16.7, 14.648), r(16.7, 11.7, xr, 11.8), new=True)
        z.door(r(12.7, 8.4, 13.5, 8.5), "l", -1)
        z.door(r(11.2, 9.6, 12.0, 9.7), "l", 1)
        z.door(r(13.85, 9.6, 14.65, 9.7), "l", 1)
        z.door(r(16.8, 11.7, 17.6, 11.8), "l", 1)
        z.door(r(14.7, 8.6, 14.8, 9.5), None, 0, C["t4"])
        p.doors.append((r(11.1, 8.4, 12.5, 8.5), None, 0, C["t4"]))
        z.bath(sh=r(13.75, 6.82, 14.65, 7.72), wc=r(13.0, 6.85, 13.4, 7.4), bs=r(13.9, 7.9, 14.5, 8.35))
        z.furn("kitchen", r(14.9, 6.83, 17.3, 7.43))
        z.furn("table", r(17.9, 9.0, 19.5, 9.8))
        z.furn("box", r(17.0, 10.95, 19.4, 11.6))
        z.furn("bedL", r(11.2, 11.6, 13.2, 13.2))
        z.furn("bedL", r(13.9, 11.6, 15.9, 12.5))
        z.furn("bedL", r(16.8, 12.6, 18.8, 13.5))
        W += [r(17.7, 6.424, xr - 0.3, 6.724), r(x1 - 0.35, 7.4, x1 - 0.05, 11.2), r(x1 - 0.35, 12.3, x1 - 0.05, 14.0),
              r(18.8, 14.7, xr - 0.2, 15.0), r(14.4, 14.7, 16.2, 15.0), r(11.6, 14.7, 13.3, 15.0), r(9.5, 14.7, 10.6, 15.0)]
        B = [("Obývacia izba + kuchyňa", [r(14.8, 6.774, xr, 9.6), r(16.7, 9.6, xr, 11.7)], dict(lab=(15.9, 8.6))),
             ("Predsieň", r(11.1, 6.774, 12.5, 8.5), dict(small=True, lab=(11.8, 8.0))),
             ("Kúp. + WC", r(12.6, 6.774, 14.7, 8.4), dict(small=True, lab=(13.45, 7.75))),
             ("Chodba", r(11.1, 8.5, 14.7, 9.6), dict(small=True, lab=(13.0, 9.05))),
             ("Spálňa", r(11.1, 9.7, 13.7, 14.648), dict(lab=(12.4, 10.6))),
             ("Izba 2", r(13.8, 9.7, 16.6, 14.648), dict(lab=(15.2, 10.6))),
             ("Izba 3", r(16.7, 11.8, xr, 14.648), dict(lab=(19.7, 13.0)))] + suite_b(z)
        tb = [r(16.6, 0.3, x1, 6.374), r(x1, 0.3, 32.9, 12.92), r(x1, 12.92, 27.0, 14.748)]
        p.terr += [("Terasa B4.02", tb[0], "terr"), ("Terasa B4.02", tb[1], "terr"), ("", tb[2], "terr")]
        hB = (18.9, 7.95)
        tubs = [(8.6, 0.6, 10.6, 2.6), (18.0, 1.0, 20.2, 3.2)]
        split_x = 16.6
        dims = [0, 10.9, 16.6, x1, 33.2]
    else:
        # ---------- B4.01: obývačka hneď pri izbách, bez chodby ----------
        N += [r(5.7, 1.0, 6.1, 3.3), r(5.9, 2.9, 6.1, 6.574), r(5.7, 1.0, 16.6, 1.4), r(10.8, 1.0, 11.1, 6.774)]
        z.door(r(5.9, 5.2, 6.1, 6.4), None, 0, C["t4"])     # priechod obývačka → izby
        z.door(r(6.3, 6.574, 7.2, 6.774), "l", -1)         # vstup B4.01
        W += [r(6.6, 1.05, 10.2, 1.35), r(5.75, 1.5, 6.05, 2.8)]
        z.furn("kitchen", r(10.2, 1.8, 10.8, 5.0))
        z.furn("table", r(7.0, 2.3, 8.6, 3.1))
        z.furn("box", r(7.7, 5.65, 10.1, 6.5))
        A = [("Obývacia izba + kuchyňa", r(6.1, 1.4, 10.8, 6.574), dict(lab=(8.3, 4.9))),
             ("Chodba", r(4.7, 5.074, 5.9, 9.0), dict(lab=(5.3, 7.9), small=True))] + A
        ta = [r(0.3, 0.3, 5.7, 2.9), r(5.7, 0.3, 10.95, 1.0)]
        p.terr += [("Terasa B4.01", ta[0], "terr"), ("", ta[1], "terr")]
        hA = (8.3, 3.9)
        # ---------- B4.02: obývačka vo výbežku v strede, izby vzadu a na konci ----------
        z.part(r(12.5, 6.774, 12.6, 8.4), r(11.1, 9.6, 14.0, 9.7), r(13.9, 9.7, 14.0, 14.648), r(14.0, 11.9, 15.9, 12.0),
               r(15.9, 6.774, 16.0, 14.648), r(16.0, 10.6, xr, 10.7), r(11.1, 8.4, 12.5, 8.5), new=True)
        z.door(r(13.0, 6.574, 15.4, 6.774), None, 0, C["t4"])   # široký priechod do obývačky
        z.door(r(11.2, 8.4, 12.4, 8.5), None, 0, C["t4"])
        z.door(r(11.2, 9.6, 12.0, 9.7), "l", 1)                 # spálňa
        z.door(r(15.9, 8.6, 16.0, 9.4), "t", 1)                 # izba 3
        z.door(r(15.9, 10.9, 16.0, 11.7), "t", 1)               # izba 2
        z.door(r(14.2, 11.9, 15.0, 12.0), "l", 1)               # kúpeľňa
        z.bath(sh=r(14.95, 13.7, 15.85, 14.6), wc=r(15.3, 12.3, 15.85, 12.7), bs=r(14.05, 14.1, 14.65, 14.55))
        z.furn("kitchen", r(11.15, 1.8, 11.75, 5.0))
        z.furn("table", r(13.2, 2.4, 14.8, 3.2))
        z.furn("box", r(15.3, 3.7, 16.15, 6.0))
        z.furn("bedL", r(11.2, 11.6, 13.2, 13.2))
        z.furn("bedR", r(xr - 2.05, 7.6, xr - 0.05, 8.5))
        z.furn("bedR", r(xr - 2.05, 12.6, xr - 0.05, 13.5))
        W += [r(12.2, 1.05, 15.6, 1.35), r(16.9, 6.424, 18.2, 6.724), r(x1 - 0.35, 8.9, x1 - 0.05, 10.3),
              r(x1 - 0.35, 11.2, x1 - 0.05, 12.8), r(16.5, 14.7, 18.1, 15.0), r(14.5, 14.7, 15.4, 15.0),
              r(11.6, 14.7, 13.4, 15.0), r(9.5, 14.7, 10.6, 15.0)]
        B = [("Obývacia izba + kuchyňa", [r(11.1, 1.4, 16.2, 6.574), r(12.6, 6.574, 15.9, 8.5)], dict(lab=(13.5, 5.2))),
             ("Predsieň", r(11.1, 6.774, 12.5, 8.4), dict(small=True, lab=(11.8, 7.9))),
             ("Chodba", [r(11.1, 8.5, 15.9, 9.6), r(14.0, 9.6, 15.9, 11.9)], dict(small=True, lab=(13.3, 9.05))),
             ("Spálňa", r(11.1, 9.7, 13.9, 14.648), dict(lab=(12.5, 10.6))),
             ("Kúp. + WC", r(14.0, 12.0, 15.9, 14.648), dict(small=True, lab=(14.6, 13.3))),
             ("Izba 3", r(16.0, 6.774, xr, 10.6), dict(lab=(17.2, 9.6))),
             ("Izba 2", r(16.0, 10.7, xr, 14.648), dict(lab=(17.2, 11.6)))] + suite_b(z)
        tb = [r(10.95, 0.3, 16.6, 1.0), r(16.6, 0.3, 32.9, 6.374), r(x1, 6.374, 32.9, 12.92), r(x1, 12.92, 27.0, 14.748)]
        p.terr += [("", tb[0], "terr"), ("Terasa B4.02", tb[1], "terr"), ("Terasa B4.02", tb[2], "terr"), ("", tb[3], "terr")]
        hB = (13.5, 4.15)
        tubs = [(0.6, 0.7, 2.1, 2.4), (18.5, 1.5, 20.7, 3.7)]
        split_x = 10.95
        dims = [0, 5.7, 16.6, x1, 33.2]
    F = [Flat("B4.01", "4", "4-izb.", z.rooms(A), f"terasa {area(ta):.0f}", "nový", head=hA),
         Flat("B4.02", "4", "4-izb.", z.rooms(B), f"terasa {area(tb):.0f}", "nový", head=hB)]
    p.flats = F

    def ex(p, c):
        p.line(c, split_x, 0.3, split_x, 1.0, C["ink"], 1.4)      # deliaca stena terás
        for i, t in enumerate(tubs):
            p.f_tub(c, r(*t))
            p.text(c, (t[0] + t[2]) / 2, (t[1] + t[3]) / 2 + 0.1, "vírivka", 4)
    p.extra.append(ex)
    p.dims += [("h", -1.5, [0, 33.2]), ("h", -0.8, dims), ("v", -0.9, [0, 1.0, 2.9, 6.574, 15.048])]
    return F


def plan_4np_single(p, z, x1, xr):
    """Variant 3: jeden veľký byt."""
    ys, yf = YS3, YS3 + 0.4
    N, W = p.new, p.windows
    N += [r(10.7, ys, x1, yf), r(10.7, ys, 11.1, 6.774), r(5.9, 6.574, 11.1, 6.774), r(xr, ys, x1, 15.048)]
    p.struct += [r(0, 0, 0.3, 13.22), r(0, 12.92, 5.7, 13.22)]
    z.part(r(11.1, 6.674, 13.4, 6.774), r(11.1, 9.4, 13.3, 9.5), r(13.3, 9.4, 13.4, 14.648), r(11.1, 11.0, 13.3, 11.1),
           r(11.0, 10.424, 11.1, 14.648), r(17.2, 9.5, 17.3, 14.648), r(17.2, 9.4, 24.7, 9.5), r(18.1, 8.1, xr, 8.2),
           r(19.2, yf, 19.3, 8.1), r(22.1, yf, 22.2, 8.1), r(24.7, 8.2, 24.8, 14.648), r(24.8, 9.9, xr, 10.0),
           r(20.0, 9.5, 20.1, 14.648), r(21.9, 9.5, 22.0, 14.648), r(20.1, 12.2, 21.9, 12.3), new=True)
    z.door(r(10.9, 6.95, 11.1, 7.85), "t", 1)             # vstup – k stene
    z.door(r(11.3, 9.4, 12.1, 9.5), "l", 1)               # WC hostí
    z.door(r(13.3, 11.3, 13.4, 12.1), "t", -1)            # komora z kuchyne
    z.door(r(11.0, 11.15, 11.1, 11.95), "t", -1)          # práčovňa
    z.door(r(19.35, 8.1, 20.15, 8.2), "l", -1)            # izba 3
    z.door(r(22.25, 8.1, 23.05, 8.2), "l", -1)            # spálňa
    z.door(r(25.2, 8.1, 26.2, 8.2), None, 0, C["t4"])     # spálňa → šatník
    z.door(r(24.85, 9.9, 25.65, 10.0), "l", 1)            # kúpeľňa spálne
    z.door(r(19.15, 9.4, 19.95, 9.5), "r", 1)             # izba 1
    z.door(r(20.15, 9.4, 20.95, 9.5), "l", 1)             # kúpeľňa 2
    z.door(r(22.05, 9.4, 22.85, 9.5), "l", 1)             # izba 2
    z.door(r(21.9, 12.6, 22.0, 13.5), None, 0, C["t4"])   # šatník izby 2
    z.door(r(18.1, 8.25, 18.2, 9.35), None, 0, C["t4"])   # obývačka → nočná chodba
    z.bath(wc=r(12.7, 10.4, 13.25, 10.8), bs=r(12.6, 9.6, 13.2, 10.05))
    z.bath(sh=r(20.95, 11.25, 21.85, 12.15), wc=r(21.3, 9.7, 21.85, 10.1), bs=r(20.15, 11.6, 20.75, 12.05))
    z.bath(tub=r(24.85, 13.85, xr - 0.05, 14.6), sh=r(xr - 0.95, 12.6, xr - 0.05, 13.5), wc=r(xr - 0.6, 10.9, xr - 0.05, 11.3),
           bs=r(24.85, 11.4, 25.3, 12.6))
    z.bath(box=r(9.15, 13.9, 10.95, 14.55))
    z.furn("kitchen", r(16.6, 9.9, 17.2, 13.8))
    z.furn("box", r(14.6, 12.4, 15.9, 13.4))              # ostrov
    z.furn("table", r(14.0, 10.5, 15.8, 11.3))
    z.furn("box", r(13.8, 6.6, 16.6, 7.5))                # sedačka
    z.furn("box", r(11.2, 8.7, 13.0, 9.3))                # šatníková skriňa pri vstupe
    z.furn("bedL", r(22.3, 5.0, 24.3, 6.6))
    z.furn("bedL", r(19.4, 4.6, 21.4, 5.5))
    z.furn("bedL", r(17.4, 11.5, 19.4, 12.4))
    z.furn("bedL", r(22.1, 11.3, 24.1, 12.2))
    W += [r(11.5, ys + 0.05, 13.0, ys + 0.35), r(13.9, ys + 0.05, 18.7, ys + 0.35), r(19.8, ys + 0.05, 21.6, ys + 0.35),
          r(22.8, ys + 0.05, 26.2, ys + 0.35), r(x1 - 0.35, 4.6, x1 - 0.05, 7.2), r(x1 - 0.35, 11.5, x1 - 0.05, 13.0),
          r(10.75, 4.3, 11.05, 6.0), r(11.6, 14.7, 12.8, 15.0), r(13.9, 14.7, 16.7, 15.0), r(17.8, 14.7, 19.6, 15.0),
          r(22.5, 14.7, 24.3, 15.0), r(9.5, 14.7, 10.6, 15.0)]
    A = [("Obývacia izba + jedáleň", [r(13.4, yf, 19.2, 8.1), r(13.4, 8.1, 18.1, 9.4), r(11.1, yf, 13.4, 6.674)], dict(lab=(16.3, 5.6))),
         ("Kuchyňa s ostrovom", r(13.4, 9.4, 17.2, 14.648), dict(lab=(15.0, 14.1))),
         ("Predsieň", r(11.1, 6.774, 13.4, 9.4), dict(lab=(12.2, 8.0))),
         ("WC", r(11.1, 9.5, 13.3, 11.0), dict(small=True, lab=(11.8, 10.5))),
         ("Komora", r(11.1, 11.1, 13.3, 14.648), dict(lab=(12.2, 13.0))),
         ("Práčovňa / technika", r(9.1, 10.424, 11.0, 14.648), dict(small=True, lab=(10.05, 12.4))),
         ("Chodba", r(18.2, 8.2, 24.7, 9.4), dict(small=True, lab=(21.5, 8.75))),
         ("Izba 3 / pracovňa", r(19.3, yf, 22.1, 8.1), dict(lab=(20.7, 6.6))),
         ("Spálňa", r(22.2, yf, xr, 8.1), dict(lab=(25.5, 5.6))),
         ("Šatník", r(24.8, 8.2, xr, 9.9), dict(small=True, lab=(25.8, 9.3))),
         ("Kúpeľňa + WC", r(24.8, 10.0, xr, 14.648), dict(small=True, lab=(25.9, 12.0))),
         ("Izba 1", r(17.3, 9.5, 20.0, 14.648), dict(lab=(18.6, 10.6))),
         ("Kúp. + WC", r(20.1, 9.5, 21.9, 12.2), dict(small=True, lab=(21.0, 10.8))),
         ("Šatník", r(20.1, 12.3, 21.9, 14.648), dict(small=True, lab=(21.0, 13.5))),
         ("Izba 2", r(22.0, 9.5, 24.7, 14.648), dict(lab=(23.4, 10.6)))]
    ta = [r(0.3, 0.3, 32.9, ys), r(0.3, ys, 5.7, 12.92), r(5.7, ys, 10.7, 6.574), r(x1, ys, 32.9, 12.92)]
    p.terr += [("Terasa – celá strecha patrí bytu", ta[0], "terr"), ("Terasa", ta[1], "terr"), ("", ta[2], "terr"), ("Terasa", ta[3], "terr")]
    F = [Flat("B4.01", "4", "5-izb.", z.rooms(A), f"terasa {area(ta):.0f}", "nový – jediný byt na 4.NP", head=(16.3, 4.6))]
    p.flats = F

    def ex(p, c):
        p.f_tub(c, r(2.2, 5.0, 4.6, 7.4))
        p.text(c, 3.4, 6.3, "vírivka", 4)
    p.extra.append(ex)
    p.dims += [("h", -1.5, [0, 33.2]), ("h", -0.8, [0, 10.7, x1, 33.2]), ("v", -0.9, [0, ys, 15.048])]
    return F


# =====================================================================
#  LISTY
# =====================================================================
LEG_OFF = [("fill", "struct", "Obvodové a nosné steny – bez zmeny oproti PD"),
           ("fill", "part", "Priečky podľa PD"),
           ("fill", "new", "Nové konštrukcie (výťahová šachta, nové priečky)"),
           ("dash", "split", "Deliaca rovina – tu sa byt neskôr rozdelí"),
           ("two", ("a1", "b1"), "Byt, ktorý sa bude deliť: každý má svoju farbu;"),
           ("two", ("a4", "b4"), "svetlý odtieň = časť, ktorá ostáva pôvodným bytom,"),
           ("two", ("a5", "b5"), "sýty odtieň = jednotka, ktorá sa odčlení"),
           ("fill", "n1", "Byt bez delenia"),
           ("fill", "common", "Spoločné priestory"), ("fill", "terr", "Balkón / lodžia / terasa")]
LEG_SPLIT = [("fill", "struct", "Obvodové a nosné steny – bez zmeny oproti PD"), ("fill", "part", "Priečky podľa PD"),
             ("fill", "new", "Nové konštrukcie (výťah, zamurované otvory)"),
             ("fill", "t1", "Jednotka 1-izbová"), ("fill", "t2", "Byt 2-izbový"),
             ("fill", "common", "Spoločné priestory"), ("fill", "terr", "Balkón / lodžia / terasa")]
LEG_4 = [("fill", "struct", "Atika strechy 3.NP"), ("fill", "new", "Nové konštrukcie – celé ustúpené podlažie"),
         ("fill", "t4", "Byt na 4.NP"), ("fill", "common", "Spoločné priestory"),
         ("fill", "terr", "Terasa bytu – celá strecha patrí bytom")]
COLS = [("Byt", 14, "l"), ("Typ", 22, "l"), ("Plocha", 18, "r"), ("Balkón / lodžia / terasa", 34, "l"), ("Pôvod · budúce delenie", 0, "l")]


def flat_rows(F):
    rows = [[f.id, f.tname, m2(f.a), f.ext, f.note] for f in F]
    rows.append(["Spolu", f"{len(F)} bytov" if len(F) != 1 else "1 jednotka", m2(sum(f.a for f in F)), "", ""])
    return rows


def sheet_plan(c, n, title, sheet, build, leg, note_lines, tab_title):
    p = Plan()
    F = build(p)
    frame(c, title, SUB, sheet, n, TOTAL)
    north(c)
    p.draw(c)
    legend(c, leg)
    table(c, 104, 66, COLS, flat_rows(F), title=tab_title, bold_last=True)
    notes(c, 294, 85, "POZNÁMKY", note_lines, width=110, size=5.4)
    c.setFont("F", 5)
    c.setFillColor(C["ink"])
    c.drawString(28 * MM, 270.5 * MM, "▲ strana k parkovisku / ul. Palárikova (hlavný vstup v 1.PP)        ▼ strana do záhrady        ◄ JZ štít        SV štít ►")
    c.showPage()
    return F


def section(c, x0, y0, s=5.0):
    """Schematický priečny rez cez výťah, 1:200."""
    def X(y):
        return (x0 + y * s) * MM

    def Z(z):
        return (y0 + z * s) * MM
    c.setLineWidth(0.5)
    c.setStrokeColor(C["ink"])
    lv = [(-2.8, 0.0, 6.376, 15.048, "1.PP", C["common"]), (0.0, 2.975, 0, 15.048, "1.NP", C["t3"]),
          (2.975, 5.95, 0, 15.048, "2.NP", C["t3"]), (5.95, 8.925, 0, 15.048, "3.NP", C["t2"]),
          (8.925, 11.9, 2.9, 15.048, "4.NP", C["t4"])]
    for z1, z2, a, b, nm, col in lv:
        c.setFillColor(col)
        c.rect(X(a), Z(z1), (b - a) * s * MM, (z2 - z1) * s * MM, fill=1, stroke=1)
        c.setFillColor(C["ink"])
        c.setFont("FB", 6)
        c.drawString(X(11.2), Z(z1 + 1.2), nm)
        c.setFont("F", 5)
        c.drawRightString(X(-0.6), Z(z1) - 1.5, f"{z1:+.3f}".replace(".", ",").replace("+0,000", "±0,000"))
        c.line(X(-0.5), Z(z1), X(0), Z(z1))
    c.drawRightString(X(-0.6), Z(11.9) - 1.5, "+11,900")
    c.drawRightString(X(-0.6), Z(12.45) - 1.5, "+12,45 atika")
    c.setFont("F", 4.6)
    c.drawString(X(15.3), Z(9.6), "atika v PD +10,575")
    c.setFillColor(HexColor("#fbd9b5"))
    c.setStrokeColor(C["new"])
    c.setLineWidth(0.9)
    c.rect(X(8.474), Z(-3.9), 1.75 * s * MM, (12.6 + 3.9) * s * MM, fill=1, stroke=1)
    c.setFillColor(C["new"])
    c.setFont("FB", 5)
    c.saveState()
    c.translate(X(9.55), Z(3.0))
    c.rotate(90)
    c.drawCentredString(0, 0, "VÝŤAH 1.PP – 4.NP (5 staníc)")
    c.restoreState()
    c.setStrokeColor(C["ink"])
    c.setLineWidth(0.5)
    c.line(X(0), Z(8.925), X(0), Z(10.0))
    c.line(X(2.9), Z(12.45), X(15.048), Z(12.45))
    c.line(X(2.9), Z(11.9), X(2.9), Z(12.45))
    c.line(X(15.048), Z(11.9), X(15.048), Z(12.45))
    c.setFont("F", 5)
    c.setFillColor(C["ink"])
    c.drawString(X(0.2), Z(9.3), "terasa")
    c.setStrokeColor(HexColor("#6b4f2a"))
    c.setLineWidth(1)
    c.line(X(-4), Z(-2.8), X(6.376), Z(-2.8))
    c.line(X(15.048), Z(-0.1), X(17.6), Z(0.1))
    c.drawString(X(0.3), Z(-2.8) + 3, "parkovisko")
    c.drawString(X(15.5), Z(0.5), "záhrada")
    c.drawString(X(0.3), Z(-1.6), "kryté parkovanie")


def sheet_summary(c, floors, f4, fpp):
    frame(c, "VARIANT C (rev. 3) · SÚHRN", SUB, "Súhrn, bilancia, porovnanie 4.NP", 1, TOTAL, scale="rez 1:200")
    allf = [f for F in floors for f in F]
    rows = []
    for i, F in enumerate(floors):
        typs = {}
        for f in F:
            typs[f.tname] = typs.get(f.tname, 0) + 1
        rows.append([f"{i + 1}.NP", str(len(F)), " + ".join(f"{v}× {kk}" for kk, v in typs.items()), m2(sum(f.a for f in F), 1), "9 (6× 1-izb. + 3× 2-izb.)"])
    rows.append(["4.NP", "2 (V3: 1)", "2× 4-izb. (V3: 1× 5-izb.)", " / ".join(k(sum(f.a for f in f4[v])) for v in (1, 2, 3)) + " m²", "2 (1)"])
    rows.append(["Spolu byty", "18", "", "", "29"])
    rows.append(["1.PP", "(+1)", "nebytový priestor – 1-izb.", m2(fpp[0].a, 1), "(+1)"])
    table(c, 14, 266, [("Podlažie", 22, "l"), ("Bytov", 17, "l"), ("Skladba (stav do povolenia)", 50, "l"), ("Plocha bytov", 34, "r"), ("Po rozdelení", 0, "l")],
          rows, title="BILANCIA – 18 BYTOV DO POVOLENIA, PRIPRAVENÉ NA 29 + 1", size=5.8, lead=4.5)

    # ---- porovnanie variantov 4.NP ----
    def ter(f):
        return f.ext.replace("terasa ", "") + " m²"

    def room(f, name):
        return k(sum(x.a for x in f.rooms if x.name == name))
    gs = {v: gross_4np(v) for v in (1, 2, 3)}
    A1, B1 = f4[1]
    A2, B2 = f4[2]
    S3 = f4[3][0]
    rows = [["Počet bytov na 4.NP", "2", "2", "1"],
            ["Hrubá plocha (limit 233,5 m²)", f"{k(gs[1])} m² · {k(gs[1] / ZAST * 100)} %", f"{k(gs[2])} m² · {k(gs[2] / ZAST * 100)} %", f"{k(gs[3])} m² · {k(gs[3] / ZAST * 100)} %"],
            ["B4.01 – plocha", f"{k(A1.a)} m² · 4-izb.", f"{k(A2.a)} m² · 4-izb.", f"{k(S3.a)} m² · 5-izb."],
            ["B4.01 – obývačka + kuchyňa", room(A1, "Obývacia izba + kuchyňa") + " m²", room(A2, "Obývacia izba + kuchyňa") + " m²", "57,6 m²"],
            ["B4.01 – chodby v byte", room(A1, "Chodba") + " m²", room(A2, "Chodba") + " m²", room(S3, "Chodba") + " m² + predsieň"],
            ["B4.01 – terasa", ter(A1) + " (aj pri schodisku)", ter(A2) + " (len pred izbami)", ter(S3) + " (celá strecha)"],
            ["B4.02 – plocha", f"{k(B1.a)} m² · 4-izb.", f"{k(B2.a)} m² · 4-izb.", "–"],
            ["B4.02 – obývačka + kuchyňa", room(B1, "Obývacia izba + kuchyňa") + " m²", room(B2, "Obývacia izba + kuchyňa") + " m²", "–"],
            ["B4.02 – terasa", ter(B1), ter(B2), "–"],
            ["Spálňa + šatník + vlastná kúpeľňa", "oba byty", "oba byty", "áno + 2. kúpeľňa, WC hostí"],
            ["Byty na 1.–3.NP (spolu 18)", "5 + 5 + 6", "5 + 5 + 6", "5 + 6 + 6"]]
    y2 = table(c, 14, 218, [("4.NP", 46, "l"), ("Variant 1 – chodba + terasa", 38, "l"), ("Variant 2 – bez chodby", 36, "l"), ("Variant 3 – jeden byt", 0, "l")],
               rows, title="POROVNANIE TROCH VARIANTOV 4.NP", size=5.4, lead=4.3)
    y2 = notes(c, 14, y2 - 3, "PRINCÍP VARIANTOV 4.NP", [
        "Všetky: zadná stena lícuje so záhradnou fasádou, celá strecha mimo bytov sú terasy bytov (žiadna spoločná plocha, žiadna FVE). Každý byt má spálňu so šatníkom a vlastnou kúpeľňou s WC + druhú kúpeľňu s WC pre izby.",
        "V1: vľavo krídlo izieb, popri schodisku už len presklená chodba 1,5 m a pred ňou terasa, vpravo výbežok s obývačkou a kuchyňou. B4.02 má prednú terasu 6 m hlbokú a celú pravú časť strechy.",
        "V2: obývačka B4.01 je hneď pri izbách pred schodiskom – byt nemá spojovaciu chodbu, ale terasu má len pred izbami. Obývačka B4.02 je vo výbežku v strede, izby vzadu a na konci.",
        "V3: jeden 5-izbový byt napravo od schodiska, vpredu terasa 3,1 m po celej dĺžke + celá ľavá aj pravá časť strechy. 180 m² limit 50 % nepustí – po odpočítaní schodiska s výťahom vychádza max. cca 172 m². Aby ostalo 18 bytov, 2.NP by malo 6 bytov ako 3.NP.",
    ], width=150, size=5.5)
    notes(c, 14, y2 - 2, "VÝŤAH", [
        "V trakte bytu B03 pri schodisku, dvere do spoločnej chodby – stanica na každom podlaží vrátane 1.PP, fasáda aj schodisko bez zmeny, B03 ostáva 2-izbový (−6 m²). Ostatné polohy (strana k parkovisku, koniec chodby, schodisková hala, vonkajšia šachta) sú horšie – viď predchádzajúca revízia.",
    ], width=150, size=5.5)
    # ---- zoznam bytov ----
    rows = [[f.id, f.tname, m2(f.a), f.ext, f.note] for f in allf]
    for f in f4[1]:
        rows.append([f.id, f.tname, f"{k(f.a, 2)} m²", f.ext, "variant 1 (V2: " + k([x for x in f4[2] if x.id == f.id][0].a) + " m²)"])
    rows.append([fpp[0].id, fpp[0].tname, m2(fpp[0].a), fpp[0].ext, fpp[0].note])
    table(c, 172, 266, [("Byt", 14, "l"), ("Typ", 21, "l"), ("Plocha", 19, "r"), ("Balkón / terasa m²", 34, "l"), ("Pôvod · budúce delenie", 0, "l")],
          rows, title="ZOZNAM BYTOV (stav do povolenia)", size=5.6, lead=4.25)
    # ---- pravý stĺpec ----
    yy = notes(c, 308, 266, "ČO SA OPROTI PD MENÍ", [
        "Fasády 1.–3.NP: žiadna zmena – okná, lodžie, balkóny podľa PD. Pribúda len ustúpené 4.NP.",
        "1.NP a 2.NP: byty B04 a B05 sú zväčšené o polovicu štítového bytu B06 → dva 3-izbové (84 a 83 m²). Tým ubudnú 2 byty a počet ostáva 18.",
        "Na pôdorysoch má každý deliteľný byt vlastnú farbu: svetlý odtieň ostáva pôvodným bytom, sýty odtieň je jednotka, ktorá sa odčlení.",
        "Rozdelenie = zamurovať jeden dverný otvor, otvoriť pripravený 2. vstup a doplniť kuchynskú linku na pripravené rozvody.",
        "1.PP: miestnosť Domovník ako 1-izbový byt, vstup len zvnútra z vestibulu; vonkajšie dvere v štíte z PD zrušené.",
    ], width=97, size=5.6)
    notes(c, 308, yy - 2, "NA OVERENIE S PROJEKTANTOM", [
        "Územný plán: definícia ustúpeného podlažia (50 % z ktorej plochy, či musí byť odstup od uličnej fasády) a max. výška – atika stúpne z +10,575 na cca +12,45.",
        "Stavebné povolenie: nadstavba, výťah a zmena skladby bytov = zmena stavby pred dokončením.",
        "Statika: steny 4.NP v osiach nosných stien 3.NP a nad stenou chodby; výbežok obývačky a predné steny ako stenové nosníky. Základy na +1 podlažie.",
        "PBS: 4 nadzemné podlažia – nové posúdenie únikovej cesty.",
        "Parkovanie: 18 bytov bez zmeny; pri delení na 29 jednotiek prepočet STN 73 6110.",
        "1.PP jednotka: po zrušení dverí v štíte ostáva len okno do krytého parkovania – overiť denné osvetlenie, prípadne v otvore dverí nechať pevné zasklenie.",
    ], width=97, size=5.6)
    c.setFont("FB", 6.5)
    c.setFillColor(C["ink"])
    c.drawString(172 * MM, 126 * MM, "SCHEMATICKÝ PRIEČNY REZ CEZ VÝŤAH · 1:200")
    section(c, 200, 38)
    c.setFont("F", 5)
    c.setFillColor(C["ink"])
    c.drawString(172 * MM, 14 * MM, "Plochy = podlahové plochy miestností zo štúdie, bez balkónov, lodžií a terás.")
    c.showPage()


def main():
    c = canvas.Canvas(OUT, pagesize=landscape(A3))
    c.setTitle("BD Palárikova – variant C rev. 3 (18 bytov, ustúpené 4.NP v 3 variantoch, výťah)")
    c.setAuthor("LEFA Solutions s.r.o.")
    floors = [typical(Plan(), fl, north=nm) for fl, nm in ((1, "merge"), (2, "merge"), (3, "b06"))]
    f4 = {v: plan_4np(Plan(), v) for v in (1, 2, 3)}
    fpp = plan_pp(Plan())
    for v in (1, 2, 3):
        assert gross_4np(v) <= ZAST / 2, (v, gross_4np(v))
    assert sum(len(F) for F in floors) + 2 == 18

    sheet_summary(c, floors, f4, fpp)
    sheet_plan(c, 2, "VARIANT C · PÔDORYS 1.PP (−2,800)", "Pôdorys 1.PP", plan_pp,
               [("fill", "struct", "Obvodové a nosné steny – bez zmeny oproti PD"),
                ("fill", "new", "Nové konštrukcie (výťah, priečky, zamurované dvere)"),
                ("fill", "nb", "Nebytový priestor rozkreslený ako 1-izbový byt"),
                ("fill", "common", "Spoločné priestory"), ("fill", "park", "Kryté parkovanie pod domom")],
               ["NP0.01 vznikne z miestnosti 1.01 Domovník: obytná izba s kuchynským kútom, kúpeľňa s WC, predsieň.",
                "Vstup je len zvnútra – z vestibulu pôvodnými dverami D32. Vonkajšie dvere v štíte (PD D31) sú zrušené a zamurované.",
                "Kuchynská linka pod pôvodným oknom k parkovaniu, posteľ čelom k stene v zadnej časti.",
                "Výťah má stanicu vo vestibule oproti hlavnému vstupu. Dvere do miestnosti 103 sú posunuté vedľa šachty.",
                "Domovník / upratovanie sa presúva do 108 Rezerva."], "JEDNOTKA – 1.PP")
    note_m = ["Do povolenia 5 bytov. Každý deliteľný byt má vlastnú farbu – svetlý odtieň ostáva bytom, sýty odtieň je jednotka, ktorá sa neskôr odčlení (so štítkom a plochou).",
              "B{0}.04 (modrý) a B{0}.05 (ružový) = byt B04 / B05 z PD + polovica štítového bytu B06, prepojené jedným dverným otvorom v nosnej stene.",
              "Rozdelenie: zamuruje sa prepojovací otvor na fialovej čiare, otvorí sa pripravený 2. vstup zo zádveria a doplní kuchynská linka.",
              "B{0}.01 (oranžový) a B{0}.02 (fialový) sa rovnako delia na 2× 1-izb.",
              "Po rozdelení: 9 jednotiek na podlaží (list 9). Okná, lodžie a balkóny bez zmeny oproti PD."]
    sheet_plan(c, 3, "VARIANT C · PÔDORYS 1.NP (±0,000)", "Pôdorys 1.NP", lambda p: typical(p, 1, north="merge"),
               LEG_OFF, [s.format(1) for s in note_m], "BYTY – 1.NP")
    sheet_plan(c, 4, "VARIANT C · PÔDORYS 2.NP (+2,975)", "Pôdorys 2.NP", lambda p: typical(p, 2, north="merge"),
               LEG_OFF, [s.format(2) for s in note_m], "BYTY – 2.NP")
    sheet_plan(c, 5, "VARIANT C · PÔDORYS 3.NP (+5,950)", "Pôdorys 3.NP", lambda p: typical(p, 3, north="b06"),
               LEG_OFF, ["Do povolenia 6 bytov – skladba ako v PD (3× 3-izb., 3× 2-izb.).",
                         "Deliteľné byty B3.01 (oranžový), B3.02 (fialový) a B3.06 (ružový): sýty odtieň = jednotka, ktorá sa odčlení → 2× 1-izb.",
                         "B3.03, B3.04 a B3.05 (zelené) sa nedelia. B3.05: druhá predsieň z PD je pripojená k izbe.",
                         "B3.03 je oproti PD menší o výťahovú šachtu, ostáva 2-izbový.",
                         "Okná, lodžie a balkóny bez zmeny oproti PD."], "BYTY – 3.NP")
    V4 = {1: ("VARIANT 1 – CHODBA PRI SCHODISKU + TERASA", [
              "B4.01: vľavo izba 1, izba 2 a spoločná kúpeľňa s WC, vzadu spálňa so šatníkom a vlastnou kúpeľňou. Popri schodisku je už len presklená chodba 1,5 m (WC a kúpeľňa sú presunuté doľava) a pred ňou terasa; vpravo výbežok s obývačkou a kuchyňou.",
              "B4.02: spálňa so šatníkom a vlastnou kúpeľňou, dve izby, druhá kúpeľňa s WC, obývačka s kuchyňou na konci s presklením do prednej terasy hlbokej 6 m.",
              "Celá strecha mimo bytov sú terasy: B4.01 pred izbami, pri schodisku a pred obývačkou; B4.02 celá pravá časť strechy."]),
          2: ("VARIANT 2 – BEZ CHODBY, OBÝVAČKY V STREDE", [
              "B4.01: obývačka s kuchyňou je hneď pri izbách pred schodiskom – žiadna spojovacia chodba (len 4,7 m² pri izbách). Cena: terasa len pred izbami a úzky pás pred obývačkou.",
              "B4.02: obývačka s kuchyňou vo výbežku v strede so širokým priechodom, spálňa so šatníkom a kúpeľňou vzadu, dve izby na konci, druhá kúpeľňa s WC.",
              "B4.02 má celú pravú časť strechy – prednú terasu 6 m hlbokú po celej dĺžke a bočnú."]),
          3: ("VARIANT 3 – JEDEN VEĽKÝ BYT", [
              "Jediný 5-izbový byt: obývačka s jedálňou a kuchyňa s ostrovom v ľavej časti, spálňa so šatníkom a kúpeľňou, tri izby, druhá kúpeľňa, WC hostí, komora a práčovňa.",
              "180 m² sa do limitu 50 % nezmestí: z 233,5 m² zoberie schodisko s výťahom a obvodové steny toľko, že čistá plocha vychádza cca 172 m².",
              "Terasa: 3,1 m hlboký pás vpredu po celej dĺžke domu + celá ľavá a pravá časť strechy.",
              "Aby ostalo 18 bytov, 2.NP by v tomto variante malo 6 bytov ako 3.NP (5 + 6 + 6 + 1)."])}
    for v in (1, 2, 3):
        nm, lines = V4[v]
        g = gross_4np(v)
        sheet_plan(c, 5 + v, f"VARIANT C · 4.NP (+8,925) · {nm}", f"Pôdorys 4.NP – variant {v}", lambda p, v=v: plan_4np(p, v), LEG_4,
                   [f"Hrubá plocha 4.NP {k(g)} m² = {k(g / ZAST * 100)} % zo zastavanej plochy {ZAST:.0f} m² (limit {k(ZAST / 2)} m²), vrátane schodiska a výťahu."] + lines
                   + ["Zadná stena lícuje so záhradnou fasádou. Žiadna spoločná plocha ani FVE na streche."],
                   f"BYTY – 4.NP · VARIANT {v}")
    sheet_plan(c, 9, "VARIANT C · TYPICKÉ PODLAŽIE PO ROZDELENÍ (1.–3.NP)", "Stav po rozdelení bytov",
               lambda p: typical(p, 0, south="split", b02="split", north="split", ids=[f"J{i}" for i in range(1, 10)]),
               LEG_SPLIT,
               ["Cieľový stav každého z 1.–3.NP po rozdelení: 9 jednotiek (6× 1-izb., 3× 2-izb.).",
                "Stavebne: zamurovanie prepojovacích otvorov, otvorenie pripravených vstupov, v J3 kúpeľňa namiesto chodby, kuchynské linky na pripravené rozvody.",
                "Zádveria na koncoch chodby sa stávajú spoločným priestorom pre dve jednotky.",
                "Spolu po rozdelení: 3 × 9 + 2 byty na 4.NP = 29 bytov + jednotka v 1.PP."],
               "JEDNOTKY – TYPICKÉ PODLAŽIE PO ROZDELENÍ")
    c.save()
    print("OK", OUT, "gross", [round(gross_4np(v), 1) for v in (1, 2, 3)],
          [[round(f.a, 1) for f in f4[v]] for v in (1, 2, 3)], [f.ext for v in (1, 2, 3) for f in f4[v]])


if __name__ == "__main__":
    main()
