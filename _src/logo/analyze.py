# -*- coding: utf-8 -*-
"""تحليل شعار اليابس (logo.jpg 1667x1667 على أبيض): طبقتا الذهبي والأسود، ومكونات كل منطقة،
وهيكل حروف الاسم (Zhang-Suen) لتأليف خطوط القلم يدويا عليه.

    python analyze.py      ⇒ cov_gold.npy · cov_dark.npy · comps.json · name_ids.png · name_skel.png · kufic_ids.png
"""
import json
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
GOLD = np.array([184, 162, 104], float)
DARK = np.array([29, 29, 29], float)
WHITE = np.array([255, 255, 255], float)

def imread(f):
    return cv2.imdecode(np.fromfile(str(f), np.uint8), cv2.IMREAD_COLOR)


def imwrite(f, img):
    cv2.imencode(Path(f).suffix, img)[1].tofile(str(f))   # cv2.imwrite لا يقبل مسارا عربيا


rgb = cv2.cvtColor(imread(HERE / "logo.jpg"), cv2.COLOR_BGR2RGB).astype(float)
H, W = rgb.shape[:2]

# تغطية كل لون: إسقاط البكسل على الخط بين الأبيض ولونه، مع التمييز بالتشبع
sat = rgb.max(-1) - rgb.min(-1)
lum = rgb @ np.array([0.299, 0.587, 0.114])
cov_dark = np.clip((255 - lum) / (255 - 29), 0, 1) * (sat < 45)
tg = np.clip(((WHITE - rgb) @ (WHITE - GOLD)) / ((WHITE - GOLD) @ (WHITE - GOLD)), 0, 1)
cov_gold = tg * (sat >= 30) * (lum > 95)
np.save(HERE / "cov_dark.npy", cov_dark.astype(np.float32))
np.save(HERE / "cov_gold.npy", cov_gold.astype(np.float32))

dark, gold = cov_dark > 0.5, cov_gold > 0.5
REG = {"pillar_gold": (gold, 0, 930), "kufic": (dark, 100, 800), "name": (dark, 950, 1300),
       "latin": (dark, 1320, 1460), "tag": (gold, 1470, 1667)}
out = {"size": [W, H]}
for key, (m, y0, y1) in REG.items():
    sub = np.zeros_like(m)
    sub[y0:y1] = m[y0:y1]
    n, lab, st, ce = cv2.connectedComponentsWithStats(sub.astype(np.uint8), 8)
    cs = [dict(i=i, x=int(st[i][0]), y=int(st[i][1]), w=int(st[i][2]), h=int(st[i][3]), a=int(st[i][4]),
               cx=round(float(ce[i][0]), 1), cy=round(float(ce[i][1]), 1)) for i in range(1, n) if st[i][4] >= 20]
    out[key] = sorted(cs, key=lambda c: -(c["x"] + c["w"]))
    if key in ("name", "kufic"):
        vis = cv2.cvtColor(np.where(sub, 60, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        for c in out[key]:
            col = (0, 0, 255) if c["a"] >= 2500 else (0, 160, 0)
            cv2.rectangle(vis, (c["x"], c["y"]), (c["x"] + c["w"], c["y"] + c["h"]), col, 1)
            cv2.putText(vis, str(c["i"]), (c["x"], max(12, c["y"] - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, col, 1)
        imwrite(HERE / f"{key}_ids.png", vis[y0:y1])
json.dump(out, open(HERE / "comps.json", "w", encoding="utf-8"), indent=1)


# ---- هيكل حروف الاسم ----
def zhang_suen(img):
    img = img.astype(np.uint8).copy()
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            p = np.pad(img, 1)
            P2, P3, P4 = p[:-2, 1:-1], p[:-2, 2:], p[1:-1, 2:]
            P5, P6, P7 = p[2:, 2:], p[2:, 1:-1], p[2:, :-2]
            P8, P9 = p[1:-1, :-2], p[:-2, :-2]
            nb = [P2, P3, P4, P5, P6, P7, P8, P9]
            B = sum(x.astype(int) for x in nb)
            seq = nb + [P2]
            A = sum(((seq[k] == 0) & (seq[k + 1] == 1)).astype(int) for k in range(8))
            if step == 0:
                c = (P2 * P4 * P6 == 0) & (P4 * P6 * P8 == 0)
            else:
                c = (P2 * P4 * P8 == 0) & (P2 * P6 * P8 == 0)
            rm = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if rm.any():
                img[rm] = 0
                changed = True
    return img


y0, y1 = 950, 1300
big = np.zeros((y1 - y0, W), np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(dark[y0:y1].astype(np.uint8), 8)
for i in range(1, n):
    if st[i][4] >= 2500:                                   # الحروف لا الزخارف
        big[lab == i] = 1
sk = zhang_suen(big)
np.save(HERE / "skel_name.npy", sk)
dist = cv2.distanceTransform(big, cv2.DIST_L2, 5)
np.save(HERE / "dist_name.npy", dist.astype(np.float32))
vis = cv2.cvtColor(np.where(big, 200, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
vis[sk > 0] = (0, 0, 255)
for x in range(0, W, 50):                                  # شبكة كل ٥٠ بكسلا لقراءة الإحداثيات
    cv2.line(vis, (x, 0), (x, y1 - y0), (230, 200, 160) if x % 100 else (200, 150, 90), 1)
    if x % 100 == 0:
        cv2.putText(vis, str(x), (x + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 90, 30), 1)
for y in range(0, y1 - y0, 50):
    cv2.line(vis, (0, y), (W, y), (230, 200, 160), 1)
    cv2.putText(vis, str(y + y0), (2, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 90, 30), 1)
imwrite(HERE / "name_skel.png", vis)
print({k: len(v) for k, v in out.items() if isinstance(v, list)})
print("letters:", [(c["i"], c["x"], c["w"], c["a"]) for c in out["name"] if c["a"] >= 2500])
