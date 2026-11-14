# -*- coding: utf-8 -*-
"""BD Palárikova – variant C: 18 bytov (16 + 2 na ustúpenom 4.NP), výťah, byt v 1.PP.
Súradnice v metroch: x = pozdĺž domu (0 = JZ štít), y = 0 fasáda k parkovisku, y rastie do záhrady."""
import sys
from engine import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "BD_Palarikova_variant_C_18bytov_2026-11-14.pdf"
SUB = "18 bytov: 1.NP 5 + 2.NP 5 + 3.NP 6 + ustúpené 4.NP 2 · výťah 1.PP–4.NP · nebytový priestor (1-izb.) v 1.PP · fasáda 1.–3.NP bez zmeny"
TOTAL = 7
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

    def rooms(self, lst):
        out = []
        for name, rects, kw in lst:
            rects = rects if isinstance(rects, list) else [rects]
            kw = dict(kw)
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
        self.p.furn.append((kind, self.R(b)))

    def bath(self, sh=None, wc=None, bs=None, tub=None):
        if sh:
            self.furn("shower", sh)
        if wc:
            self.furn("wc", wc)
        if bs:
            self.furn("basin", bs)
        if tub:
            self.furn("bath", tub)


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
    # inštalačné šachty (PD)
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
        p.doors.append((r(7.8, 14.648, 8.9, 15.048), "l", 1))
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


def end_bay(p, mode, mirror=False):
    """Štítový byt (B01 juh / B06 sever). mode: off | split | merge. Vráti (rooms1, rooms2, zadv_rect)."""
    z = Zone(p, mirror)
    z.part(r(0.4, 4.9, 5.9, 5.0), r(2.2, 5.0, 2.3, 6.7), r(0.4, 6.7, 5.9, 6.8),
           r(2.9, 6.8, 3.0, 8.1), r(4.4, 6.8, 4.5, 8.1), r(0.4, 8.1, 3.0, 8.2), r(4.4, 8.1, 5.9, 8.2))
    z.door(r(5.9, 6.95, 6.1, 7.95), "t", -1)                      # vstup z chodby
    z.door(r(2.2, 5.45, 2.3, 6.25), "t", 1)                       # kúpeľňa 1
    z.door(r(2.9, 7.05, 3.0, 7.85), "t", 1)                       # kúpeľňa 2
    z.bath(sh=r(0.45, 5.05, 1.35, 5.95), wc=r(0.45, 6.1, 1.0, 6.5), bs=r(1.55, 5.05, 2.15, 5.5))
    z.bath(sh=r(1.2, 6.85, 2.1, 7.75), wc=r(0.45, 7.2, 1.0, 7.6), bs=r(2.25, 6.85, 2.85, 7.3))
    kup1 = ("Kúp.", r(0.4, 5.0, 2.2, 6.7), dict(small=True, lab=(1.75, 6.25)))
    kup2 = ("Kúp.", r(0.4, 6.8, 2.9, 8.1), dict(small=True, lab=(2.5, 7.7)))
    pred = ("Predsieň", r(2.3, 5.0, 5.9, 6.7), dict(lab=(4.1, 5.8)))
    zadv = z.R(r(4.5, 6.8, 5.9, 8.1))
    if mode == "off":
        z.part(r(3.2, 0.4, 3.3, 4.9))
        z.door(r(2.35, 4.9, 3.15, 5.0), "r", -1)
        z.door(r(3.5, 4.9, 4.3, 5.0), "l", -1)
        z.door(r(4.75, 6.7, 5.55, 6.8), None, 0)
        z.door(r(4.4, 7.05, 4.5, 7.85), None, 0)
        z.furn("bed", r(0.5, 1.3, 2.5, 2.9))
        z.furn("bed", r(4.9, 1.2, 5.8, 3.2))
        z.furn("kitchen", r(0.5, 8.25, 2.9, 8.85))
        z.furn("table", r(3.7, 9.9, 5.3, 10.7))
        z.furn("box", r(0.5, 10.0, 1.4, 12.2))
        r1 = z.rooms([("Izba", r(0.4, 0.4, 3.2, 4.9), dict(lab=(1.8, 3.7))),
                      ("Izba", r(3.3, 0.4, 5.9, 4.9), dict(lab=(4.2, 3.9))), kup1, pred,
                      ("Zádv.", r(4.5, 6.8, 5.9, 8.1), dict(small=True)), kup2,
                      ("Obývacia izba + KK", [r(0.4, 8.2, 5.9, 12.82), r(3.0, 6.8, 4.4, 8.2)], dict(lab=(2.4, 9.4)))])
        return r1, [], None
    # split / merge: dve samostatné jednotky + spoločné zádverie
    z.door(r(4.75, 6.7, 5.55, 6.8), "l", -1)                      # vstup jednotky 1
    z.door(r(4.4, 7.05, 4.5, 7.85), "t", -1)                      # vstup jednotky 2
    z.door(r(3.5, 4.9, 4.3, 5.0), "l", -1)
    if mode == "split":
        z.part(r(3.0, 8.1, 4.4, 8.2))
        z.door(r(3.3, 8.1, 4.1, 8.2), "l", 1)
        z.furn("kitchen", r(0.5, 4.3, 3.1, 4.9))
        z.furn("bed", r(0.5, 0.9, 2.5, 2.5))
        z.furn("table", r(3.9, 2.5, 5.1, 3.3))
        z.furn("kitchen", r(0.5, 8.25, 2.9, 8.85))
        z.furn("bed", r(3.8, 10.4, 5.8, 12.0))
        z.furn("table", r(1.0, 10.4, 2.2, 11.2))
        r1 = z.rooms([("Obytná izba + KK", r(0.4, 0.4, 5.9, 4.9), dict(lab=(3.6, 3.6))), kup1, pred])
        r2 = z.rooms([("Obytná izba + KK", r(0.4, 8.2, 5.9, 12.82), dict(lab=(3.0, 9.6))),
                      ("Pred.", r(3.0, 6.8, 4.4, 8.1), dict(small=True)), kup2])
    else:  # merge – jednotky sú izbami susedných bytov (B04 / B05)
        z.furn("bed", r(0.5, 1.2, 2.5, 2.8))
        z.furn("box", r(4.2, 0.5, 5.8, 1.1))
        z.furn("bed", r(0.5, 10.2, 2.5, 11.8))
        z.furn("box", r(0.5, 8.25, 2.9, 8.85))
        r1 = z.rooms([("Izba (spálňa + pracovňa)", r(0.4, 0.4, 5.9, 4.9), dict(lab=(3.4, 3.9))), kup1,
                      ("Predsieň / šatník", r(2.3, 5.0, 5.9, 6.7), dict(lab=(4.0, 5.8)))])
        r2 = z.rooms([("Izba (spálňa)", [r(0.4, 8.2, 5.9, 12.82), r(3.0, 6.8, 4.4, 8.2)], dict(lab=(3.4, 9.6))), kup2])
    return r1, r2, zadv


def typical(p, floor, south="off", b02="off", north="b06", ids=None):
    """Zostaví podlažie. Vráti zoznam bytov."""
    g = floor == 1
    structure_typ(p, ground=g)
    lift(p)
    p.extra.append(stairs)
    p.common.append(("Spoločná chodba", [r(6.1, 6.774, 26.9, 8.274)]))
    p.fills.append(([r(6.1, 8.274, 8.9, 14.648)], C["common"]))
    tn = "terasa" if g else "balkón"
    F = []
    n = [0]

    def fid(suffix=""):
        n[0] += 1
        return f"B{floor}.{n[0]:02d}" if ids is None else ids[n[0] - 1]

    z = Zone(p)
    # ---------- JUH (B01) ----------
    r1, r2, zadv = end_bay(p, south)
    if south == "off":
        F.append(Flat(fid(), "3", "3-izb.", r1, f"{tn} 10,4", "PD B01 · → 2× 1-izb.", head=(3.3, 11.8)))
        p.splits += [(0.4, 6.75, 4.45, 6.75), (4.45, 6.75, 4.45, 8.15), (4.45, 8.15, 5.9, 8.15)]
    else:
        F.append(Flat(fid(), "1", "1-izb.", r1, "–", "z B01", head=(4.3, 1.2)))
        f2 = Flat(fid(), "1", "1-izb.", r2, f"{tn} 10,4", "z B01", head=(3.0, 11.6))
        p.common.append(("Zádv.", [zadv]))
    # ---------- B02 ----------
    z.part(r(12.1, 4.6, 17.9, 4.7), r(15.5, 4.7, 15.6, 6.574))
    z.door(r(12.7, 6.574, 13.7, 6.774), "l", -1)
    z.door(r(12.9, 4.6, 13.8, 4.7), None, 0)
    z.door(r(15.5, 5.5, 15.6, 6.3), "t", -1)
    z.bath(sh=r(16.55, 4.75, 17.45, 5.65), bs=r(15.7, 4.75, 16.3, 5.2), wc=r(16.9, 5.95, 17.45, 6.35))
    z.furn("kitchen", r(14.9, 4.0, 17.8, 4.6))
    z.furn("table", r(12.7, 2.0, 14.3, 2.8))
    u3 = [("Obývacia izba + KK", r(12.1, 0.4, 17.9, 4.6), dict(lab=(15.6, 2.9))),
          ("Predsieň", r(12.1, 4.7, 15.5, 6.574), dict(lab=(14.3, 5.6))),
          ("Kúp.", r(15.6, 4.7, 17.5, 6.574), dict(small=True, lab=(16.2, 6.1)))]
    if b02 == "off":
        z.part(r(9.0, 1.4, 9.1, 6.574), r(9.1, 4.874, 11.9, 4.974))
        z.door(r(11.9, 5.25, 12.1, 6.15), None, 0)
        z.door(r(9.9, 4.874, 10.7, 4.974), "l", -1)
        z.door(r(9.0, 5.35, 9.1, 6.15), "t", -1)
        z.furn("bed", r(6.2, 2.6, 8.2, 4.2))
        z.furn("bed", r(9.2, 1.2, 11.2, 2.8))
        rooms = z.rooms([("Izba", r(6.1, 1.4, 9.0, 6.574), dict(lab=(7.55, 5.2))),
                         ("Izba", r(9.1, 0.4, 11.9, 4.874), dict(lab=(10.5, 3.7))),
                         ("Chodba", r(9.1, 4.974, 11.9, 6.574), dict(lab=(10.5, 5.6)))] + u3)
        F.append(Flat(fid(), "3", "3-izb.", rooms, "lodžia 2,4", "PD B02 · → 2× 1-izb.", head=(16.2, 1.3)))
        p.splits.append((12.0, 0.4, 12.0, 6.574))
        p.texts.append((10.5, 6.35, "príprava ZTI (kúpeľňa)", dict(size=3.6, col=C["split"])))
        p.texts.append((7.6, 6.42, "pripravený 2. vstup", dict(size=3.6, col=C["split"])))
    else:
        z.part(r(9.0, 4.874, 9.1, 6.574), r(9.1, 4.874, 11.9, 4.974))
        p.new.append(r(11.9, 5.25, 12.1, 6.15))
        z.door(r(7.3, 6.574, 8.3, 6.774), "l", -1)
        z.door(r(9.0, 5.35, 9.1, 6.15), "t", -1)
        z.bath(sh=r(10.95, 5.02, 11.85, 5.92), bs=r(9.9, 5.02, 10.5, 5.47), wc=r(11.3, 6.1, 11.85, 6.5))
        z.furn("kitchen", r(6.15, 2.6, 6.75, 5.2))
        z.furn("bed", r(9.8, 0.9, 11.8, 2.5))
        z.furn("table", r(7.4, 2.0, 8.6, 2.8))
        ra = z.rooms([("Obytná izba + KK", [r(6.1, 1.4, 9.0, 6.574), r(9.0, 0.4, 11.9, 4.874)], dict(lab=(8.4, 4.0))),
                      ("Kúp.", r(9.1, 4.974, 11.9, 6.574), dict(small=True, lab=(10.3, 6.1)))])
        F.append(Flat(fid(), "1", "1-izb.", ra, "lodžia 2,4", "z B02", head=(10.4, 3.2)))
        F.append(Flat(fid(), "1", "1-izb.", z.rooms(u3), "–", "z B02", head=(16.2, 1.3)))
    # ---------- B03 (pri výťahu) ----------
    z.part(r(12.1, 10.348, 17.9, 10.448), r(15.5, 8.474, 15.6, 10.348))
    z.door(r(12.7, 8.274, 13.7, 8.474), "l", 1)
    z.door(r(12.9, 10.348, 13.8, 10.448), None, 0)
    z.door(r(11.9, 8.85, 12.1, 9.65), "b", -1)
    z.door(r(15.5, 8.75, 15.6, 9.55), "t", -1)
    z.bath(sh=r(16.55, 9.4, 17.45, 10.3), bs=r(15.7, 9.85, 16.3, 10.3), wc=r(16.9, 8.6, 17.45, 9.0))
    z.furn("kitchen", r(14.9, 10.45, 17.8, 11.05))
    z.furn("table", r(12.7, 12.4, 14.3, 13.2))
    z.furn("bed", r(9.2, 11.4, 11.2, 13.0))
    rooms = z.rooms([("Obývacia izba + KK", r(12.1, 10.448, 17.9, 14.648), dict(lab=(15.4, 12.2))),
                     ("Predsieň", r(12.1, 8.474, 15.5, 10.348), dict(lab=(14.3, 9.5))),
                     ("Kúp.", r(15.6, 8.474, 17.5, 10.348), dict(small=True, lab=(16.2, 9.4))),
                     ("Izba", [r(9.1, 10.424, 11.9, 13.648), r(10.9, 8.474, 11.9, 10.424)], dict(lab=(10.5, 10.9)))])
    b03 = Flat("", "2", "2-izb.", rooms, f"{tn} 2,4 + 4,7", "PD B03 − výťah", head=(16.2, 13.6))
    # ---------- B04 ----------
    z.part(r(18.1, 4.6, 23.9, 4.7), r(20.4, 4.7, 20.5, 6.574))
    z.door(r(22.3, 6.574, 23.3, 6.774), "r", -1)
    z.door(r(22.2, 4.6, 23.1, 4.7), None, 0)
    z.door(r(20.4, 5.5, 20.5, 6.3), "t", 1)
    z.bath(sh=r(18.55, 4.75, 19.45, 5.65), bs=r(19.7, 4.75, 20.3, 5.2), wc=r(18.55, 5.95, 19.1, 6.35))
    z.furn("kitchen", r(18.2, 4.0, 21.1, 4.6))
    z.furn("table", r(21.7, 2.0, 23.3, 2.8))
    b04 = [("Obývacia izba + KK", r(18.1, 0.4, 23.9, 4.6), dict(lab=(20.4, 2.9))),
           ("Predsieň", r(20.5, 4.7, 23.9, 6.574), dict(lab=(21.7, 5.6))),
           ("Kúp.", r(18.5, 4.7, 20.4, 6.574), dict(small=True, lab=(19.8, 6.1)))]
    # ---------- B05 ----------
    z.part(r(18.1, 10.348, 23.9, 10.448), r(20.4, 8.474, 20.5, 10.348))
    z.door(r(22.3, 8.274, 23.3, 8.474), "r", 1)
    z.door(r(22.2, 10.348, 23.1, 10.448), None, 0)
    z.door(r(20.4, 8.75, 20.5, 9.55), "t", 1)
    z.door(r(23.9, 8.85, 24.1, 9.65), "b", 1)
    z.bath(sh=r(18.55, 9.4, 19.45, 10.3), bs=r(19.7, 9.85, 20.3, 10.3), wc=r(18.55, 8.6, 19.1, 9.0))
    z.furn("kitchen", r(18.2, 10.45, 21.1, 11.05))
    z.furn("table", r(21.7, 12.4, 23.3, 13.2))
    z.furn("bed", r(24.2, 12.0, 26.2, 13.6))
    b05 = [("Obývacia izba + KK", r(18.1, 10.448, 23.9, 14.648), dict(lab=(20.6, 12.2))),
           ("Predsieň", r(20.5, 8.474, 23.9, 10.348), dict(lab=(21.7, 9.5))),
           ("Kúp.", r(18.5, 8.474, 20.4, 10.348), dict(small=True, lab=(19.8, 9.4)))]
    # ---------- SEVER ----------
    if north == "merge":
        r1, r2, zadv = end_bay(p, "merge", mirror=True)
        z.part(r(24.1, 4.9, 26.9, 5.0), new=True)
        z.door(r(25.1, 4.9, 25.9, 5.0), "l", -1)
        z.door(r(23.9, 5.3, 24.1, 6.2), None, 0)
        z.door(r(26.9, 5.3, 27.1, 6.2), "t", 1)
        z.furn("bed", r(24.2, 1.6, 26.2, 3.2))
        z.furn("box", r(24.15, 5.95, 26.6, 6.5))
        ra = z.rooms(b04 + [("Izba", r(24.1, 1.4, 26.9, 4.9), dict(lab=(25.5, 3.9))),
                            ("Chodba / šatník", r(24.1, 5.0, 26.9, 6.574), dict(lab=(25.5, 5.5)))]) + r1
        z.part(r(24.1, 10.348, 26.9, 10.448))
        z.door(r(25.0, 10.348, 25.9, 10.448), "l", 1)
        z.door(r(26.9, 8.75, 27.1, 9.65), "t", 1)
        z.furn("box", r(24.15, 8.52, 26.2, 9.1))
        rb = z.rooms(b05 + [("Chodba / šatník", r(24.1, 8.474, 26.9, 10.348), dict(lab=(25.6, 9.7))),
                            ("Izba", r(24.1, 10.448, 26.9, 14.648), dict(lab=(25.5, 11.3)))]) + r2
        b03.id = fid()
        F.append(b03)
        F.append(Flat(fid(), "3", "3-izb.", ra, "lodžia 2,4", "B04 + ½ B06 → 2-izb. + 1-izb.", head=(19.9, 1.3)))
        F.append(Flat(fid(), "3", "3-izb.", rb, f"{tn} 4,7 + 2,2 + {'14,1' if g else '10,8'}",
                      "B05 + ½ B06 → 2-izb. + 1-izb.", head=(19.9, 13.6)))
        p.common.append(("Zádv.", [zadv]))
        p.splits += [(27.0, 0.4, 27.0, 6.574), (27.0, 8.474, 27.0, 12.82)]
        p.texts.append((28.75, 6.62, "2. vstup", dict(size=3.4, col=C["split"])))
        p.texts.append((28.3, 8.4, "2. vstup", dict(size=3.4, col=C["split"])))
    else:
        z.door(r(23.9, 5.25, 24.1, 6.15), "t", 1)
        z.furn("bed", r(24.2, 2.2, 26.2, 3.8))
        z.furn("box", r(26.25, 8.55, 26.85, 10.3))
        ra = z.rooms(b04 + [("Izba", r(24.1, 1.4, 26.9, 6.574), dict(lab=(25.5, 5.0)))])
        rb = z.rooms(b05 + [("Izba so šatníkom", r(24.1, 8.474, 26.9, 14.648), dict(lab=(25.4, 11.0)))])
        if south == "off":
            b03.id = fid()
            F.append(b03)
            F.append(Flat(fid(), "2", "2-izb.", ra, "lodžia 2,4", "PD B04", head=(19.9, 1.3)))
            F.append(Flat(fid(), "2", "2-izb.", rb, f"{tn} 4,7 + 2,2", "PD B05 · bez 2. predsiene", head=(19.9, 13.6)))
            r1, r2, zadv = end_bay(p, "off", mirror=True)
            F.append(Flat(fid(), "3", "3-izb.", r1, f"{tn} 10,8", "PD B06 · → 2× 1-izb.", head=(29.9, 11.8)))
            p.splits += [(32.8, 6.75, 28.75, 6.75), (28.75, 6.75, 28.75, 8.15), (28.75, 8.15, 27.1, 8.15)]
        else:  # všetko rozdelené
            b03.id = fid()
            F.append(b03)
            F.append(Flat(fid(), "2", "2-izb.", ra, "lodžia 2,4", "B04", head=(19.9, 1.3)))
            F.append(Flat(fid(), "2", "2-izb.", rb, f"{tn} 4,7 + 2,2", "B05", head=(19.9, 13.6)))
            r1, r2, zadv = end_bay(p, "split", mirror=True)
            F.append(Flat(fid(), "1", "1-izb.", r1, "–", "z B06", head=(29.0, 1.2)))
            F.append(Flat(fid(), "1", "1-izb.", r2, f"{tn} 10,8", "z B06", head=(30.2, 11.6)))
            p.common.append(("Zádv.", [zadv]))
    if south != "off":
        F.insert(1, f2)
        # prečíslovanie podľa poradia
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
    p.doors += [(r(6.95, 6.376, 8.05, 6.776), "l", 1),
                (r(0, 7.3, 0.4, 8.3), "t", 1),                      # presklené dvere v štíte (PD D31)
                (r(5.9, 6.95, 6.1, 7.95), "t", -1),                 # vstup do NP0.01 z vestibulu (PD D32)
                (r(11.9, 7.05, 12.1, 7.95), "t", 1),
                (r(7.65, 9.676, 8.5, 9.876), "l", 1),
                (r(11.0, 9.676, 11.85, 9.876), "r", 1),
                (r(14.3, 8.276, 15.2, 8.476), "l", 1), (r(20.3, 8.276, 21.2, 8.476), "l", 1),
                (r(25.0, 8.276, 25.9, 8.476), "l", 1), (r(26.9, 7.05, 27.1, 7.95), "t", 1)]
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
        p.text(c, 7.5, 5.5, "HLAVNÝ VSTUP", 5.5, bold=True)
        p.text(c, 7.5, 5.8, "z parkoviska −2,800", 4.4)
        p.line(c, 7.5, 5.9, 7.5, 6.3, C["ink"], 0.8)
        p.text(c, -1.2, 7.7, "terasa /", 4.2)
        p.text(c, -1.2, 7.95, "predzáhradka", 4.2)
    p.extra.append(st)
    # ---- nebytový priestor rozkreslený ako 1-izbový byt ----
    z = Zone(p)
    z.part(r(4.3, 6.776, 4.4, 8.3), r(4.4, 8.3, 5.9, 8.4), r(3.9, 8.4, 4.0, 10.5), r(3.9, 10.5, 5.9, 10.6), new=True)
    z.door(r(4.3, 7.1, 4.4, 7.9), "t", -1)
    z.door(r(3.9, 9.5, 4.0, 10.3), "b", -1)
    z.bath(sh=r(4.95, 8.45, 5.85, 9.35), wc=r(5.3, 9.9, 5.85, 10.3), bs=r(4.1, 8.45, 4.7, 8.9))
    z.furn("kitchen", r(0.5, 6.83, 3.6, 7.43))
    z.furn("table", r(1.0, 8.6, 2.2, 9.4))
    z.furn("bed", r(3.6, 10.9, 5.6, 12.5))
    z.furn("box", r(0.5, 10.6, 1.4, 12.6))
    rooms = z.rooms([("Obytná izba + KK", [r(0.4, 6.776, 4.3, 8.4), r(0.4, 8.4, 3.9, 10.6), r(0.4, 10.6, 5.9, 12.82)],
                      dict(lab=(2.5, 10.0))),
                     ("Pred.", r(4.4, 6.776, 5.9, 8.3), dict(small=True)),
                     ("Kúp.", r(4.0, 8.4, 5.9, 10.5), dict(small=True, lab=(4.6, 9.9)))])
    f = Flat("NP0.01", "nb", "nebyt. priestor (1-izb.)", rooms, "predzáhradka pri štíte", "PD 1.01 Domovník", head=(2.4, 11.6), count=False)
    f.tname = "1-izb. (nebyt.)"
    p.flats = [f]
    p.dims += [("h", -0.4, [0, 33.2]), ("v", -0.9, [6.376, 15.048])]
    return [f]


# =====================================================================
#  4.NP – ustúpené podlažie
# =====================================================================
X0, X1, YS, XM = 1.5, 19.9, 2.0, 14.45


def plan_4np(p):
    # strecha 3.NP = terasy
    p.terr += [("Terasa B4.01", r(0.3, 0.3, X0, 12.92), "terr"),
               ("Terasa B4.01", r(X0, 0.3, XM, YS), "terr"),
               ("Terasa B4.02", r(XM, 0.3, X1, YS), "terr"),
               ("Terasa B4.02", r(X1, 0.3, 26.0, 14.748), "terr"),
               ("Vegetačná strecha / FVE / technológie (VZT, TČ)", r(26.0, 0.3, 32.9, 12.92), "green"),
               ("", r(26.0, 12.92, 27.0, 14.748), "green")]
    # atika (obrys 3.NP)
    S = p.struct
    S += [r(0, 0, 33.2, 0.3), r(0, 0, 0.3, 13.22), r(32.9, 0, 33.2, 13.22), r(0, 12.92, X0, 13.22),
          r(27.0, 12.92, 33.2, 13.22), r(27.0, 12.92, 27.3, 15.048), r(X1, 14.748, 27.3, 15.048)]
    N = p.new
    N += [r(X0, YS, X1, YS + 0.4), r(X0, YS, X0 + 0.4, 13.22), r(X0, 12.82, 6.1, 13.22),
          r(5.7, 12.82, 6.1, 15.048), r(5.7, 14.648, X1, 15.048), r(X1 - 0.4, YS, X1, 15.048),
          r(5.9, 6.574, 6.1, 12.82), r(5.9, 6.574, 14.6, 6.774), r(14.3, YS + 0.4, 14.6, 6.774),
          r(8.9, 8.474, 9.1, 14.648), r(10.9, 6.774, 11.1, 10.424), r(9.1, 10.224, 11.1, 10.424)]
    lift(p)
    p.extra.append(stairs)
    p.common.append(("Chodba pred výťahom", [r(6.1, 6.774, 10.9, 8.274)]))
    p.fills.append(([r(6.1, 8.274, 8.9, 14.648)], C["common"]))
    z = Zone(p)
    # ---------------- B4.01 (ľavý, nárožie JZ) ----------------
    z.part(r(X0 + 0.4, 5.4, 5.9, 5.5), r(5.9, 2.4, 6.0, 5.5), r(4.6, 5.5, 4.7, 8.3), r(X0 + 0.4, 6.6, 4.6, 6.7),
           r(X0 + 0.4, 8.3, 5.9, 8.4), r(11.5, 2.4, 11.6, 6.574), new=True)
    z.door(r(5.9, 6.95, 6.1, 7.95), "t", -1)        # vstup
    z.door(r(4.8, 5.4, 5.6, 5.5), "r", -1)          # izba 1
    z.door(r(4.6, 5.6, 4.7, 6.4), "t", -1)          # WC
    z.door(r(4.6, 7.2, 4.7, 8.0), "t", -1)          # kúpeľňa
    z.door(r(4.9, 8.3, 5.7, 8.4), "r", 1)           # spálňa
    z.door(r(11.5, 5.5, 11.6, 6.3), "b", 1)         # izba 3
    p.windows += [r(2.5, YS + 0.05, 5.3, YS + 0.35), r(6.6, YS + 0.05, 11.2, YS + 0.35), r(12.0, YS + 0.05, 14.0, YS + 0.35),
                  r(X0 + 0.05, 2.9, X0 + 0.35, 4.9), r(X0 + 0.05, 7.1, X0 + 0.35, 7.9), r(X0 + 0.05, 9.2, X0 + 0.35, 11.8),
                  r(2.6, 12.87, 5.0, 13.17), r(6.5, 14.7, 8.5, 15.0)]
    z.bath(sh=r(1.95, 5.55, 2.95, 6.55), wc=r(3.9, 5.85, 4.5, 6.25), bs=r(3.15, 5.55, 3.75, 6.0))
    z.bath(tub=r(1.95, 7.55, 3.65, 8.25), wc=r(1.95, 6.8, 2.5, 7.2), bs=r(3.9, 6.75, 4.5, 7.2))
    z.furn("bed", r(2.0, 3.0, 4.0, 4.6))
    z.furn("bed", r(2.0, 9.7, 4.0, 11.5))
    z.furn("box", r(2.0, 12.15, 5.0, 12.75))
    z.furn("kitchen", r(6.6, 5.95, 10.2, 6.55))
    z.furn("table", r(6.5, 3.6, 8.1, 4.4))
    z.furn("box", r(10.5, 3.6, 11.4, 5.6))
    z.furn("bed", r(12.2, 3.0, 14.2, 4.6))
    L = z.rooms([("Obývacia izba + KK", r(6.0, 2.4, 11.5, 6.574), dict(lab=(8.6, 5.3))),
                 ("Izba 1", r(X0 + 0.4, 2.4, 5.9, 5.4), dict(lab=(4.9, 3.3))),
                 ("WC + sprcha", r(X0 + 0.4, 5.5, 4.6, 6.6), dict(small=True, lab=(3.5, 6.42))),
                 ("Predsieň", r(4.7, 5.5, 5.9, 8.3), dict(small=True, lab=(5.3, 6.9))),
                 ("Kúpeľňa", r(X0 + 0.4, 6.7, 4.6, 8.3), dict(small=True, lab=(3.15, 7.1))),
                 ("Spálňa", r(X0 + 0.4, 8.4, 5.9, 12.82), dict(lab=(4.8, 10.6))),
                 ("Izba 3", r(11.6, 2.4, 14.3, 6.574), dict(lab=(13.0, 5.5)))])
    p.doors.append((r(5.9, 5.55, 6.0, 6.5), None, 0, C["t4"]))
    # ---------------- B4.02 (pravý) ----------------
    z.part(r(12.5, 6.774, 12.6, 8.4), r(12.6, 8.4, 14.6, 8.5), r(14.5, 6.774, 14.6, 8.5), r(16.7, 8.4, X1 - 0.4, 8.5),
           r(11.1, 9.6, 16.7, 9.7), r(13.9, 9.7, 14.0, 14.648), r(16.7, 8.5, 16.8, 14.648),
           r(11.0, 10.424, 11.1, 14.648), new=True)
    z.door(r(10.9, 6.95, 11.1, 7.95), "t", 1)       # vstup
    z.door(r(13.2, 8.4, 14.0, 8.5), "l", -1)        # kúpeľňa 2
    z.door(r(12.0, 9.6, 12.8, 9.7), "l", 1)         # izba 1
    z.door(r(11.0, 11.0, 11.1, 11.8), "t", -1)      # kúpeľňa pri spálni
    z.door(r(14.9, 9.6, 15.7, 9.7), "l", 1)         # izba 2
    z.door(r(16.7, 8.6, 16.8, 9.4), "t", 1)         # izba 3
    p.windows += [r(15.4, YS + 0.05, 19.0, YS + 0.35), r(X1 - 0.35, 3.0, X1 - 0.05, 7.6), r(X1 - 0.35, 9.6, X1 - 0.05, 12.2),
                  r(9.5, 14.7, 10.6, 15.0), r(11.7, 14.7, 13.5, 15.0), r(14.5, 14.7, 16.3, 15.0), r(17.3, 14.7, 19.1, 15.0)]
    z.bath(sh=r(12.65, 6.82, 13.55, 7.72), wc=r(13.95, 6.85, 14.45, 7.25), bs=r(13.85, 7.75, 14.45, 8.2))
    z.bath(tub=r(9.15, 12.9, 9.95, 14.6), sh=r(10.05, 13.7, 10.95, 14.6), wc=r(9.15, 10.5, 9.7, 10.9), bs=r(9.15, 11.3, 9.6, 11.9))
    z.furn("kitchen", r(14.65, 2.9, 15.25, 6.3))
    z.furn("box", r(16.4, 4.2, 17.3, 5.8))         # ostrovček
    z.furn("table", r(17.2, 7.0, 19.0, 7.8))
    z.furn("box", r(18.5, 3.0, 19.4, 5.2))
    z.furn("bed", r(11.2, 11.8, 13.2, 13.6))
    z.furn("bed", r(14.1, 11.8, 16.1, 13.6))
    z.furn("bed", r(16.9, 10.6, 18.9, 12.4))
    Rr = z.rooms([("Obývacia izba + KK", r(14.6, 2.4, X1 - 0.4, 8.4), dict(lab=(17.3, 6.3))),
                  ("Predsieň", r(11.1, 6.774, 12.5, 8.5), dict(small=True, lab=(11.8, 7.6))),
                  ("Kúp.", r(12.6, 6.774, 14.5, 8.4), dict(small=True, lab=(13.3, 8.15))),
                  ("Chodba", r(11.1, 8.5, 16.7, 9.6), dict(small=True, lab=(13.9, 9.05))),
                  ("Spálňa", r(11.1, 9.7, 13.9, 14.648), dict(lab=(12.5, 10.9))),
                  ("Kúpeľňa", r(9.1, 10.424, 11.0, 14.648), dict(small=True, lab=(10.3, 12.5))),
                  ("Izba 2", r(14.0, 9.7, 16.7, 14.648), dict(lab=(15.4, 10.9))),
                  ("Izba 3", r(16.8, 8.5, X1 - 0.4, 14.648), dict(lab=(18.2, 9.6)))])
    p.doors.append((r(11.1, 8.4, 12.5, 8.5), None, 0, C["t4"]))
    p.doors.append((r(15.0, 8.4, 16.5, 8.5), None, 0, C["t4"]))
    tl = area([r(0.3, 0.3, X0, 12.92), r(X0, 0.3, XM, YS)])
    tr = area([r(XM, 0.3, X1, YS), r(X1, 0.3, 26.0, 14.748)])
    F = [Flat("B4.01", "4", "4-izb.", L, f"terasa {tl:.0f}", "nový", head=(9.6, 2.95)),
         Flat("B4.02", "4", "4-izb.", Rr, f"terasa {tr:.0f}", "nový · možnosť 5-izb.", head=(17.3, 3.5))]
    p.flats = F

    def ex(p, c):
        # deliace steny terás, vírivky, kóty ustúpenia
        p.line(c, XM, 0.3, XM, YS, C["ink"], 1.2)
        p.line(c, 26.0, 0.3, 26.0, 14.748, C["ink"], 1.2)
        p.f_tub(c, r(0.4, 0.4, 2.3, 1.95))
        p.text(c, 1.35, 1.25, "vírivka", 3.8)
        p.f_tub(c, r(21.0, 1.0, 23.2, 3.2))
        p.text(c, 22.1, 3.55, "vírivka", 4)
        p.line(c, 12.0, 0.0, 12.0, YS, C["dim"], 0.3)
        p.text(c, 12.05, 1.2, " ustúpenie 2 000", 4, col=C["dim"], align="l")
        p.line(c, 0, 10.0, X0, 10.0, C["dim"], 0.3)
        p.text(c, 0.8, 9.9, "1 500", 3.6, col=C["dim"])
        p.text(c, 29.4, 8.6, "(nepochôdzna – spoločná)", 4.2)
        p.text(c, 18.2, 12.9, "(deliteľná → 5-izb.)", 3.6, col=C["split"])
        p.line(c, 16.8, 11.5, X1 - 0.4, 11.5, C["split"], 0.6, [2, 2])
    p.extra.append(ex)
    p.dims += [("h", -1.5, [0, 33.2]), ("h", -0.8, [0, X0, X1, 33.2]), ("v", -0.9, [0, YS, 15.048])]
    return F


def gross_4np():
    return (5.85 - X0) * (13.22 - YS) + (X1 - 5.85) * (15.048 - YS)


# =====================================================================
#  LISTY
# =====================================================================
LEG_TYP = [("fill", "struct", "Obvodové a nosné steny – bez zmeny oproti PD"),
           ("fill", "part", "Priečky podľa PD"),
           ("fill", "new", "Nové konštrukcie (výťahová šachta, nové priečky)"),
           ("dash", "split", "Deliaca rovina – pripravené budúce rozdelenie bytu"),
           ("fill", "t2", "Byt 2-izbový"), ("fill", "t3", "Byt 3-izbový"), ("fill", "t1", "Byt / jednotka 1-izbová"),
           ("fill", "common", "Spoločné priestory"), ("fill", "terr", "Balkón / lodžia / terasa")]
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
    """Schematický priečny rez cez výťah, 1:200. x0,y0 v mm = poloha (y=0 fasáda parkovisko, ±0,000)."""
    def X(y):
        return (x0 + y * s) * MM

    def Z(z):
        return (y0 + z * s) * MM
    c.setLineWidth(0.5)
    c.setStrokeColor(C["ink"])
    lv = [(-2.8, 0.0, 6.376, 15.048, "1.PP", C["common"]), (0.0, 2.975, 0, 15.048, "1.NP", C["t3"]),
          (2.975, 5.95, 0, 15.048, "2.NP", C["t3"]), (5.95, 8.925, 0, 15.048, "3.NP", C["t2"]),
          (8.925, 11.9, YS, 15.048, "4.NP", C["t4"])]
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
    # výťah
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
    # terasa, atika, terén
    c.setStrokeColor(C["ink"])
    c.setLineWidth(0.5)
    c.line(X(0), Z(8.925), X(0), Z(10.0))
    c.line(X(0), Z(12.45), X(15.048), Z(12.45))
    c.line(X(YS), Z(11.9), X(YS), Z(12.45))
    c.line(X(15.048), Z(11.9), X(15.048), Z(12.45))
    c.setFont("F", 5)
    c.setFillColor(C["ink"])
    c.drawString(X(0.1), Z(9.3), "terasa")
    c.setStrokeColor(HexColor("#6b4f2a"))
    c.setLineWidth(1)
    c.line(X(-4), Z(-2.8), X(6.376), Z(-2.8))
    c.line(X(15.048), Z(-0.1), X(19), Z(0.2))
    c.setFont("F", 5)
    c.drawString(X(0.3), Z(-2.8) + 3, "parkovisko")
    c.drawString(X(15.5), Z(0.5), "záhrada")
    c.drawString(X(0.3), Z(-1.6), "kryté parkovanie")


def sheet_summary(c, floors, f4, fpp, split):
    frame(c, "VARIANT C · SÚHRN", SUB, "Variant C – súhrn, bilancia, výťah", 1, TOTAL, scale="rez 1:200")
    allf = [f for F in floors for f in F] + f4
    # ---- bilancia ----
    y = 266
    rows = []
    for i, F in enumerate(floors):
        typs = {}
        for f in F:
            typs[f.tname] = typs.get(f.tname, 0) + 1
        rows.append([f"{i + 1}.NP", str(len(F)), " + ".join(f"{v}× {k}" for k, v in typs.items()), m2(sum(f.a for f in F), 1), "9 (6× 1-izb. + 3× 2-izb.)"])
    rows.append(["4.NP", "2", "2× 4-izb.", m2(sum(f.a for f in f4), 1), "2"])
    rows.append(["Spolu byty", str(len(allf)), "", m2(sum(f.a for f in allf), 1), "29"])
    rows.append(["1.PP", "(+1)", "nebytový priestor – 1-izb.", m2(fpp[0].a, 1), "(+1)"])
    table(c, 14, y, [("Podlažie", 22, "l"), ("Bytov", 13, "l"), ("Skladba (stav do povolenia)", 52, "l"), ("Plocha bytov", 26, "r"), ("Po rozdelení", 0, "l")],
          rows, title="BILANCIA – 18 BYTOV DO POVOLENIA, PRIPRAVENÉ NA 29 + 1", size=5.8, lead=4.5)
    g = gross_4np()
    y2 = 266 - 5 - 9 * 4.5 - 4
    y2 = notes(c, 14, y2, "USTÚPENÉ 4.NP", [
        f"Zastavaná plocha domu podľa PD {ZAST:.0f} m² → limit 50 % = {k(ZAST / 2)} m². Navrhnutá hrubá plocha 4.NP vrátane schodiska a výťahu: {k(g)} m² ({k(g / ZAST * 100)} %).",
        f"Hmota lícuje so záhradnou fasádou, od fasády k parkovisku je ustúpená o 2,0 m, od JZ štítu o 1,5 m, od SV štítu o {k(33.2 - X1)} m.",
        f"B4.01 – 4-izb. {k(f4[0].a)} m² (nárožie k parkovisku a JZ), B4.02 – 4-izb. {k(f4[1].a)} m² (dá sa predeliť na 5-izb.). Väčšie byty limit 50 % nepustí – z 233 m² zoberie jadro 35 m² a obvodové steny.",
        "Vstupy do oboch bytov sú z chodby priamo pred výťahom; schodisko z PD už na strechu vedie, len sa upraví posledné rameno.",
    ], width=150, size=5.6)
    y2 = notes(c, 14, y2 - 2, "VÝŤAH – POSÚDENÉ POLOHY", [
        "A) V trakte bytu B03 pri schodisku, dvere do spoločnej chodby (ZVOLENÉ). Jediná poloha, ktorá má stanicu na každom podlaží vrátane 1.PP v závetrí vestibulu, nemení fasádu ani schodisko. B03 zostáva 2-izbový (−6 m², izba 10,8 m²).",
        "B) Lodžia / izba za lodžiou na strane k parkovisku: v 1.PP je pod touto polovicou domu otvorené kryté parkovanie – šachta by stála pred hlavným vstupom a menila by fasádu. Nevhodné.",
        "C) Koniec chodby v štítovom byte B01: neberie obytnú miestnosť, ale šachta (1,6 m) je širšia ako chodba (1,5 m) a odreže vstup do štítového bytu. Nevhodné.",
        "D) V schodiskovej hale po prestavbe schodiska na dvojramenné: byty by nestratili nič, ale zanikne zadný bezbariérový vstup zo záhrady (±0,000), mení sa okno schodiska na fasáde a priechod popri šachte vychádza len 1,1 m. Rezerva na rokovanie so statikom/PBS.",
        "E) Vonkajšia šachta v nike záhradnej fasády: zastaví na medzipodestách (o pol podlažia vyššie/nižšie) a mení fasádu. Nevhodné.",
    ], width=150, size=5.6)
    # ---- zoznam bytov ----
    rows = [[f.id, f.tname, m2(f.a), f.ext, f.note] for f in allf]
    rows.append(["Spolu", "18 bytov", m2(sum(f.a for f in allf)), "", ""])
    rows.append([fpp[0].id, fpp[0].tname, m2(fpp[0].a), fpp[0].ext, fpp[0].note])
    table(c, 172, 266, [("Byt", 14, "l"), ("Typ", 21, "l"), ("Plocha", 19, "r"), ("Balkón / terasa m²", 34, "l"), ("Pôvod · budúce delenie", 0, "l")],
          rows, title="ZOZNAM BYTOV (stav do povolenia)", size=5.6, lead=4.25)
    # ---- pravý stĺpec ----
    yy = notes(c, 308, 266, "ČO SA OPROTI PD MENÍ", [
        "Fasády 1.–3.NP: žiadna zmena – okná, lodžie, balkóny aj hmotové členenie podľa PD. Pribúda len ustúpené 4.NP.",
        "1.NP a 2.NP: byty B04 a B05 sú zväčšené o polovicu štítového bytu B06 → dva 3-izbové (84 a 83 m²) namiesto 2+2+3. Tým ubudnú 2 byty a celkový počet ostáva 18.",
        "Každý 3-izbový byt má dve kúpeľne a druhý vstup zo spoločného zádveria, takže rozdelenie na 2-izb. + 1-izb. (resp. 2× 1-izb.) = zamurovať jeden dverný otvor a doplniť kuchynskú linku na pripravené rozvody.",
        "1.PP: miestnosť 1.01 Domovník rozkreslená ako 1-izbový byt s kuchyňou a kúpeľňou, vstup z vestibulu pôvodnými dverami; vedená ako nebytový priestor.",
    ], width=97, size=5.6)
    yy = notes(c, 308, yy - 2, "VYLEPŠENIA DISPOZÍCIÍ", [
        "B01/B06: predsieň 8,8 m² + samostatné WC nahradené dvomi kúpeľňami, predsieňou 6,1 m² a zádverím 1,8 m²; obývačka väčšia o 2 m².",
        "B05: hluchá druhá predsieň 5,25 m² pripojená k izbe (izba 17,3 m² so šatníkom).",
        "B02: chodba 4,5 m² má pripravené ZTI – pri delení je z nej kúpeľňa a jednotka pri lodžii nemá žiadnu chodbu.",
        "Výťahová šachta je pri izbe B03 – navrhnúť akustickú predstenu.",
    ], width=97, size=5.6)
    yy = notes(c, 308, yy - 2, "NA OVERENIE S PROJEKTANTOM", [
        "Územný plán: definícia ustúpeného podlažia (50 % z ktorej plochy) a max. výška – atika stúpne z +10,575 na cca +12,45.",
        "Stavebné povolenie: nadstavba, výťah a zmena skladby bytov = zmena stavby pred dokončením.",
        "Statika: steny 4.NP stoja prevažne na nosných stenách 3.NP (osi x = 5,9 / 8,9 / 14,3 a pozdĺžna stena chodby); predná stena 4.NP ako stenový nosník. Základy na +1 podlažie.",
        "PBS: 4 nadzemné podlažia, výška nad 9 m – nové posúdenie únikovej cesty a schodiska.",
        "Parkovanie: 18 bytov bez zmeny; pri delení na 29 jednotiek prepočet STN 73 6110.",
        "1.PP jednotka: denné osvetlenie (okno do krytého parkovania + presklené dvere v štíte).",
    ], width=97, size=5.6)
    # ---- rez ----
    c.setFont("FB", 6.5)
    c.setFillColor(C["ink"])
    c.drawString(14 * MM, 108 * MM, "SCHEMATICKÝ PRIEČNY REZ CEZ VÝŤAH · 1:200")
    section(c, 45, 36)
    c.setFont("F", 5)
    c.setFillColor(C["ink"])
    c.drawString(172 * MM, 14 * MM, "Plochy = podlahové plochy miestností zo štúdie, bez balkónov, lodžií a terás.")
    c.showPage()


def main():
    c = canvas.Canvas(OUT, pagesize=landscape(A3))
    c.setTitle("BD Palárikova – variant C (18 bytov, ustúpené 4.NP, výťah)")
    c.setAuthor("LEFA Solutions s.r.o.")
    # predbežný výpočet pre súhrn
    floors = []
    for fl, north_mode in ((1, "merge"), (2, "merge"), (3, "b06")):
        floors.append(typical(Plan(), fl, north=north_mode))
    f4 = plan_4np(Plan())
    fpp = plan_pp(Plan())
    sp = typical(Plan(), 0, south="split", b02="split", north="split", ids=[f"J{i}" for i in range(1, 10)])
    assert gross_4np() <= ZAST / 2, gross_4np()
    assert sum(len(F) for F in floors) + len(f4) == 18

    sheet_summary(c, floors, f4, fpp, sp)
    sheet_plan(c, 2, "VARIANT C · PÔDORYS 1.PP (−2,800)", "Pôdorys 1.PP", plan_pp,
               [("fill", "struct", "Obvodové a nosné steny – bez zmeny oproti PD"),
                ("fill", "new", "Nové konštrukcie (výťahová šachta, priečky bytu)"),
                ("fill", "nb", "Nebytový priestor rozkreslený ako 1-izbový byt"),
                ("fill", "common", "Spoločné priestory"), ("fill", "park", "Kryté parkovanie pod domom")],
               ["NP0.01 vznikne z miestnosti 1.01 Domovník: obytná izba s kuchynským kútom, kúpeľňa s WC, predsieň. Vstup z vestibulu pôvodnými dverami D32.",
                "Kuchynská linka je pod pôvodným oknom k parkovaniu, spanie v zadnej časti; presklené dvere v štíte (PD D31) vedú na predzáhradku.",
                "Výťah má stanicu vo vestibule hneď oproti hlavnému vstupu. Dvere do miestnosti 103 sú posunuté vedľa šachty.",
                "Domovník / upratovanie sa presúva do 108 Rezerva."], "JEDNOTKA – 1.PP")
    note_m = ["Do povolenia 5 bytov. B{0}.04 a B{0}.05 = byt B04/B05 z PD + polovica štítového bytu B06, prepojené jedným dverným otvorom v nosnej stene.",
              "Fialová čiara = miesto budúceho rozdelenia: zamuruje sa prepojovací otvor, otvorí sa pripravený 2. vstup zo zádveria a doplní kuchynská linka.",
              "B{0}.01 a B{0}.02 (3-izb.) sú pripravené na rozdelenie na 2× 1-izb. rovnakým spôsobom.",
              "Okná, lodžie a balkóny bez zmeny oproti PD."]
    sheet_plan(c, 3, "VARIANT C · PÔDORYS 1.NP (±0,000)", "Pôdorys 1.NP", lambda p: typical(p, 1, north="merge"),
               LEG_TYP, [s.format(1) for s in note_m] + ["Zadný vstup zo záhrady ostáva – bezbariérová trasa k výťahu."], "BYTY – 1.NP")
    sheet_plan(c, 4, "VARIANT C · PÔDORYS 2.NP (+2,975)", "Pôdorys 2.NP", lambda p: typical(p, 2, north="merge"),
               LEG_TYP, [s.format(2) for s in note_m], "BYTY – 2.NP")
    sheet_plan(c, 5, "VARIANT C · PÔDORYS 3.NP (+5,950)", "Pôdorys 3.NP", lambda p: typical(p, 3, north="b06"),
               LEG_TYP, ["Do povolenia 6 bytov – skladba ako v PD (3× 3-izb., 3× 2-izb.).",
                         "3-izbové byty B3.01, B3.02 a B3.06 sú pripravené na rozdelenie na 2× 1-izb. (fialová čiara).",
                         "B3.05: hluchá druhá predsieň z PD je pripojená k izbe (17,3 m² so šatníkom).",
                         "B3.03 je oproti PD menší o výťahovú šachtu, ostáva 2-izbový.",
                         "Okná, lodžie a balkóny bez zmeny oproti PD."], "BYTY – 3.NP")
    g = gross_4np()
    sheet_plan(c, 6, "VARIANT C · PÔDORYS 4.NP – USTÚPENÉ PODLAŽIE (+8,925)", "Pôdorys 4.NP", plan_4np,
               [("fill", "struct", "Atika strechy 3.NP"), ("fill", "new", "Nové konštrukcie – celé ustúpené podlažie"),
                ("fill", "t4", "Byt 4-izbový"), ("fill", "common", "Spoločné priestory"),
                ("fill", "terr", "Terasa bytu"), ("fill", "green", "Vegetačná strecha / FVE / technológie")],
               [f"Hrubá plocha 4.NP {k(g)} m² = {k(g / ZAST * 100)} % zo zastavanej plochy {ZAST:.0f} m² (limit 50 % = {k(ZAST / 2)} m²), vrátane schodiska a výťahu.",
                "Zadná stena lícuje so záhradnou fasádou; terasy sú vpredu (k parkovisku) a na oboch bokoch.",
                "B4.01: obývačka s kuchyňou a izby do prednej terasy, spálňa a kúpeľňa s oknom na JZ; chodby len 3,4 m².",
                "B4.02: nárožná obývačka 30 m² (terasa spredu aj zboku), tri izby do záhrady, 2 kúpeľne. Izba 3 sa dá predeliť → 5-izb.",
                "Terasa B4.02 je zámerne ukončená pri x = 26 m; zvyšok strechy je spoločný (FVE, VZT, vegetačná strecha). Hranica sa dá posunúť."],
               "BYTY – 4.NP")
    sheet_plan(c, 7, "VARIANT C · TYPICKÉ PODLAŽIE PO ROZDELENÍ (1.–3.NP)", "Stav po rozdelení bytov",
               lambda p: typical(p, 0, south="split", b02="split", north="split", ids=[f"J{i}" for i in range(1, 10)]),
               [x for x in LEG_TYP if x[1] not in ("split", "t3")],
               ["Cieľový stav každého z 1.–3.NP po rozdelení: 9 jednotiek (6× 1-izb., 3× 2-izb.).",
                "Stavebne: zamurovanie 4 prepojovacích otvorov, otvorenie pripravených vstupov, v J3 kúpeľňa namiesto chodby, 4 kuchynské linky na pripravené rozvody.",
                "Zádveria na koncoch chodby sa stávajú spoločným priestorom pre dve jednotky.",
                "Spolu po rozdelení: 3 × 9 + 2 byty na 4.NP = 29 bytov + jednotka v 1.PP."],
               "JEDNOTKY – TYPICKÉ PODLAŽIE PO ROZDELENÍ")
    c.save()
    print("OK", OUT, "4.NP gross", round(g, 1), "flats", [round(f.a, 1) for F in floors for f in F], [round(f.a, 1) for f in f4], round(fpp[0].a, 1))


if __name__ == "__main__":
    main()
