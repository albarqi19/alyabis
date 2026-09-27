# -*- coding: utf-8 -*-
"""شعار اليابس متجها ⇒ ../parts.json   (شغل analyze.py أولا)

الإحداثيات = بكسل المصدر × 0.5 (viewBox 0 0 833.5 833.5).
  bars[0..3]     أشرطة العمود الذهبية: التاج العلوي (0 الأعلى، 1)، ثم القاعدة (2، 3 الأدنى)
  cols[0..1]     العمودان الذهبيان الجانبيان
  stones[]       أحجار الكتلة الكوفية السوداء بترتيب البناء (من الأسفل إلى الأعلى): {d, cy}
  letters[0..4]  قطع الاسم «عبدالله بن عبدالرحمن اليابس» (السوداء الكبيرة)، مرتبة من اليمين
  strokes[i]     خطوط القلم لكل قطعة، مولدة من الهيكل: [{d, w, len, sx, sy, vert}] مرتبة للكتابة
  orn[]          زخارف الاسم ونقاطه: {d, cx, cy, letter}
  latin          الاسم الإنجليزي (أسود) · tag_ar / tag_en سطرا الوصف الذهبيان عربيا وإنجليزيا
"""
import json
from pathlib import Path

import cv2
import numpy as np
import potrace

HERE = Path(__file__).resolve().parent
SC = 0.5
dark = np.load(HERE / "cov_dark.npy") > 0.5
gold = np.load(HERE / "cov_gold.npy") > 0.5
H, W = dark.shape


def fmt(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def trace(mask, ox=0, oy=0):
    if not mask.any():
        return ""
    plist = potrace.Bitmap(~mask).trace(turdsize=4, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                                        alphamax=1.0, opticurve=True, opttolerance=0.3)
    f = lambda p: f"{fmt((p.x + ox) * SC)} {fmt((p.y + oy) * SC)}"
    out = []
    for c in plist:
        s = [f"M{f(c.start_point)}"]
        for seg in c.segments:
            s.append(f"L{f(seg.c)}L{f(seg.end_point)}" if seg.is_corner
                     else f"C{f(seg.c1)} {f(seg.c2)} {f(seg.end_point)}")
        s.append("Z")
        out.append("".join(s))
    return "".join(out)


def comps(mask, y0=0, y1=None, x0=0, x1=None, amin=20):
    sub = np.zeros_like(mask)
    sub[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    n, lab, st, ce = cv2.connectedComponentsWithStats(sub.astype(np.uint8), 8)
    cs = [dict(i=i, x=int(st[i][0]), y=int(st[i][1]), w=int(st[i][2]), h=int(st[i][3]), a=int(st[i][4]),
               cx=float(ce[i][0]), cy=float(ce[i][1])) for i in range(1, n) if st[i][4] >= amin]
    return lab, cs


def trace_comp(lab, c, pad=3):
    x0, y0 = max(0, c["x"] - pad), max(0, c["y"] - pad)
    x1, y1 = min(W, c["x"] + c["w"] + pad), min(H, c["y"] + c["h"] + pad)
    return trace(lab[y0:y1, x0:x1] == c["i"], x0, y0)


def trace_box(mask, x0, y0, x1, y1):
    m = np.zeros_like(mask)
    m[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    return trace(m[y0:y1, x0:x1], x0, y0)


out = {"viewBox": [0, 0, round(W * SC, 2), round(H * SC, 2)], "scale": SC}

# ---------------------------------------------------------------- العمود
labG, csG = comps(gold, 0, 930)
bars = sorted([c for c in csG if c["w"] > 300 and c["h"] < 80], key=lambda c: c["y"])
cols = sorted([c for c in csG if c["h"] > 400], key=lambda c: -c["x"])
assert len(bars) == 4 and len(cols) == 2, ([(c["w"], c["h"]) for c in csG])
out["bars"] = [trace_comp(labG, c) for c in bars]
out["cols"] = [trace_comp(labG, c) for c in cols]
out["pillar_box"] = [round(min(c["x"] for c in bars) * SC, 1), round(bars[0]["y"] * SC, 1),
                     round(max(c["x"] + c["w"] for c in bars) * SC, 1), round((bars[3]["y"] + bars[3]["h"]) * SC, 1)]

labK, csK = comps(dark, 100, 800)
out["stones"] = [{"d": trace_comp(labK, c), "cy": round(c["cy"] * SC, 1), "cx": round(c["cx"] * SC, 1)}
                 for c in sorted(csK, key=lambda c: -(c["y"] + c["h"]))]

# ---------------------------------------------------------------- الاسم
NY0, NY1 = 950, 1300
labN, csN = comps(dark, NY0, NY1)
letters = sorted([c for c in csN if c["a"] >= 2500], key=lambda c: -(c["x"] + c["w"]))
orns = [c for c in csN if c["a"] < 2500]
out["letters"] = [trace_comp(labN, c) for c in letters]
letter_of = {c["i"]: k for k, c in enumerate(letters)}

dists = [cv2.distanceTransform((labN != L["i"]).astype(np.uint8), cv2.DIST_L2, 5) for L in letters]


def owner(c):
    x, y = int(round(c["cx"])), int(round(c["cy"]))
    return int(np.argmin([d[y, x] for d in dists]))


out["orn"] = [{"d": trace_comp(labN, c), "cx": round(c["cx"] * SC, 1), "cy": round(c["cy"] * SC, 1), "letter": owner(c)}
              for c in sorted(orns, key=lambda c: -c["cx"])]

# ---- خطوط القلم من الهيكل: فروع بين العقد، وتقليم الزوائد، ودمج ما يمر بعقدة درجتها ٢ ----
sk = np.zeros((H, W), np.uint8)
sk[NY0:NY1] = np.load(HERE / "skel_name.npy")
body = np.zeros((H, W), np.uint8)
for c in letters:
    body[labN == c["i"]] = 1
dist = cv2.distanceTransform(body, cv2.DIST_L2, 5)
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
pts = set(zip(*np.nonzero(sk)))


def nbrs(p):
    return [(p[0] + dy, p[1] + dx) for dy, dx in N8 if (p[0] + dy, p[1] + dx) in pts]


deg = {p: len(nbrs(p)) for p in pts}
nodes = {p for p, d in deg.items() if d != 2}
# عناقيد العقد المتجاورة عقدة واحدة
cluster, cid = {}, 0
for p in nodes:
    if p in cluster:
        continue
    stack = [p]
    cluster[p] = cid
    while stack:
        q = stack.pop()
        for r in nbrs(q):
            if r in nodes and r not in cluster:
                cluster[r] = cid
                stack.append(r)
    cid += 1

edges, seen = [], set()
for p in nodes:
    for q in nbrs(p):
        if q in nodes or (p, q) in seen:
            continue
        path, prev, cur = [p], p, q
        while cur not in nodes:
            path.append(cur)
            nxt = [r for r in nbrs(cur) if r != prev and r not in path[-3:]]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
        path.append(cur)
        seen.add((path[-2], path[-1]) if len(path) > 1 else (p, q))
        seen.add((p, q))
        a, b = cluster.get(path[0]), cluster.get(path[-1])
        edges.append({"a": a, "b": b, "pts": path})
# الحلقات بلا عقد (مثل رأس الميم)
used = {pp for e in edges for pp in e["pts"]}
left = pts - used - nodes
while left:
    s = left.pop()
    loop, cur, prev = [s], s, None
    while True:
        nxt = [r for r in nbrs(cur) if r != prev and r in left]
        if not nxt:
            break
        prev, cur = cur, nxt[0]
        left.discard(cur)
        loop.append(cur)
    if len(loop) > 8:
        edges.append({"a": None, "b": None, "pts": loop + [loop[0]]})

# إزالة المكرر: كل فرع يرصد من طرفيه، ومن بكسلات مختلفة في العقدة الواحدة ⇒ المفتاح بكسلاته الداخلية
uniq, keys = [], set()
for e in edges:
    inner = [q for q in e["pts"] if q not in nodes]
    k = frozenset(inner) if inner else frozenset([("n", e["a"]), ("n", e["b"])])
    if k and k not in keys:
        keys.add(k)
        uniq.append(e)
edges = [e for e in uniq if not (e["a"] is not None and e["a"] == e["b"] and len(e["pts"]) < 12)]
print("edges after dedup:", len(edges), "lengths:", sorted(len(e["pts"]) for e in edges)[:30])


def ends_deg(es):
    d = {}
    for e in es:
        for n in (e["a"], e["b"]):
            if n is not None:
                d[n] = d.get(n, 0) + 1
    return d


for _ in range(3):                                          # تقليم الزوائد القصيرة
    d = ends_deg(edges)
    edges = [e for e in edges if not (len(e["pts"]) < 16 and (d.get(e["a"], 0) == 1 or d.get(e["b"], 0) == 1))]

changed = True                                               # دمج عبر العقد ذات الدرجة ٢
while changed:
    changed = False
    d = ends_deg(edges)
    for n, k in d.items():
        if k != 2:
            continue
        pair = [e for e in edges if n in (e["a"], e["b"])]
        if len(pair) != 2 or pair[0] is pair[1]:
            continue
        e1, e2 = pair
        p1 = e1["pts"] if e1["b"] == n else e1["pts"][::-1]
        p2 = e2["pts"] if e2["a"] == n else e2["pts"][::-1]
        na = e1["a"] if e1["b"] == n else e1["b"]
        nb = e2["b"] if e2["a"] == n else e2["a"]
        edges = [e for e in edges if e is not e1 and e is not e2] + [{"a": na, "b": nb, "pts": p1 + p2}]
        changed = True
        break


def simplify(p, eps=1.4):
    arr = np.array([[x, y] for y, x in p], np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(arr, eps, False).reshape(-1, 2)


strokes = [[] for _ in letters]
for e in edges:
    P = e["pts"]
    ys, xs = np.array([p[0] for p in P]), np.array([p[1] for p in P])
    vert = (ys.max() - ys.min()) > 1.6 * (xs.max() - xs.min())
    if vert:                                                 # الألف واللام تكتب من الأعلى
        if P[0][0] > P[-1][0]:
            P = P[::-1]
    elif P[0][1] < P[-1][1]:                                 # غيرها من اليمين إلى اليسار
        P = P[::-1]
    poly = simplify(P)
    if len(poly) < 2:
        continue
    dvals = np.array([dist[y, x] for y, x in P])
    w = float(2 * np.percentile(dvals, 92) + 5)
    L = float(np.sum(np.hypot(*np.diff(poly, axis=0).T)))
    mid = P[len(P) // 2]
    k = letter_of.get(int(labN[mid[0], mid[1]]))
    if k is None:
        continue
    strokes[k].append({"poly": poly, "w": w, "len": L, "sx": float(poly[0][0]), "sy": float(poly[0][1]), "vert": bool(vert)})

# ---- الأطراف الحرة تمد حتى رأس الحرف (الهيكل يقف قبل الرأس بنصف العرض) ----
free = {p for p, d in deg.items() if d == 1}


def extend(poly, at_start, w):
    a, b = (poly[0], poly[min(3, len(poly) - 1)]) if at_start else (poly[-1], poly[max(-4, -len(poly))])
    v = a.astype(float) - b.astype(float)
    n = np.hypot(*v)
    if n < 1e-6:
        return poly
    tip = a + v / n * min(0.9 * w, 24)
    return np.vstack([tip[None], poly]) if at_start else np.vstack([poly, tip[None]])


for ss in strokes:
    for st in ss:
        P0, P1 = st["poly"][0], st["poly"][-1]
        near = lambda q: any((int(q[1]) + dy, int(q[0]) + dx) in free for dy in (-2, -1, 0, 1, 2) for dx in (-2, -1, 0, 1, 2))
        if near(P0):
            st["poly"] = extend(st["poly"], True, st["w"])
        if near(P1):
            st["poly"] = extend(st["poly"], False, st["w"])
        st["sx"], st["sy"] = float(st["poly"][0][0]), float(st["poly"][0][1])
        st["len"] = float(np.sum(np.hypot(*np.diff(st["poly"], axis=0).T)))


def raster(ss_all):
    cv = np.zeros((H, W), np.uint8)
    for ss in ss_all:
        for st in ss:
            cv2.polylines(cv, [np.round(st["poly"]).astype(np.int32).reshape(-1, 1, 2)], False, 1, thickness=max(1, int(round(st["w"]))))
    return cv


# ---- ما بقي مكشوفا: نقرة قصيرة من جسم أقرب خط إلى أبعد نقطة في الفجوة ----
miss0 = (body > 0) & (raster(strokes) == 0)
n, lab, st_, ce = cv2.connectedComponentsWithStats(miss0.astype(np.uint8), 8)
for i in range(1, n):
    if st_[i][4] < 5:
        continue
    ys, xs = np.nonzero(lab == i)
    cxy = np.array([ce[i][0], ce[i][1]])
    best = None
    for k, ss in enumerate(strokes):
        for j, stv in enumerate(ss):
            d = np.hypot(*(stv["poly"] - cxy).T)
            m = int(np.argmin(d))
            if best is None or d[m] < best[0]:
                best = (d[m], k, j, stv["poly"][m])
    if best is None or best[0] > 60:
        continue
    _, k, j, base = best
    far = np.argmax(np.hypot(xs - base[0], ys - base[1]))
    tip = np.array([xs[far], ys[far]], float)
    local = float(max(dist[y, x] for y, x in zip(ys, xs)))
    strokes[k].append({"poly": np.vstack([base, tip]), "w": 2 * local + 6, "len": float(np.hypot(*(tip - base))),
                       "sx": float(base[0]), "sy": float(base[1]), "vert": False, "flick": True})

# ترتيب الكتابة داخل القطعة: بموضع البداية من اليمين
for k in range(len(strokes)):
    strokes[k].sort(key=lambda s: -s["sx"])

# ---- فحص التغطية: كل بكسل من الحروف تحت قناعه ----
cover = np.zeros((H, W), np.uint8)
for k, ss in enumerate(strokes):
    for s in ss:
        cv2.polylines(cover, [np.round(s["poly"]).astype(np.int32).reshape(-1, 1, 2)], False, 1, thickness=max(1, int(round(s["w"]))))
miss = (body > 0) & (cover == 0)
print("strokes per letter:", [len(s) for s in strokes], "· uncovered px:", int(miss.sum()), f"({miss.sum() / body.sum():.2%})")
vis = cv2.cvtColor(np.where(body, 150, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
vis[miss] = (0, 0, 255)
for ss in strokes:
    for n, s in enumerate(ss):
        cv2.polylines(vis, [np.round(s["poly"]).astype(np.int32).reshape(-1, 1, 2)], False, (255, 120, 0), 1)
        cv2.circle(vis, (int(s["sx"]), int(s["sy"])), 3, (0, 170, 0), -1)
cv2.imencode(".png", vis[NY0:NY1])[1].tofile(str(HERE / "strokes_check.png"))

out["strokes"] = [[{"d": "M" + " L".join(f"{fmt(x * SC)} {fmt(y * SC)}" for x, y in s["poly"]),
                    "w": round(s["w"] * SC, 1), "len": round(s["len"] * SC, 1), "sx": round(s["sx"] * SC, 1),
                    "sy": round(s["sy"] * SC, 1), "vert": s["vert"]} for s in ss] for ss in strokes]

# ---------------------------------------------------------------- السطور تحت الاسم
out["latin"] = trace_box(dark, 0, 1320, W, 1460)
out["tag_ar"] = trace_box(gold, 860, 1470, W, H)
out["tag_en"] = trace_box(gold, 0, 1470, 860, H)
out["name_box"] = [0, round(NY0 * SC, 1), round(W * SC, 1), round(NY1 * SC, 1)]
(HERE.parent / "parts.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print("parts.json", round((HERE.parent / "parts.json").stat().st_size / 1024), "K ·", len(out["stones"]), "stones ·",
      len(out["orn"]), "orn")
