# -*- coding: utf-8 -*-
"""يبني موقع الدكتور عبدالله اليابس للمحاماة والاستشارات القانونية من _src إلى جذر website.

- layout.html الإطار، وpages/*.html الصفحات، وcontent/site.json النصوص (من موقعهم الحالي بلا إضافة).
- parts.json الشعار متجها (logo/analyze.py ثم logo/vectorize.py). الافتتاحية: يبنى العمود
  (القاعدة، فالعمودان، فأحجار الكتلة الكوفية من الأسفل، فالتاج)، ثم يكتب القلم الاسم من اليمين،
  ثم ينتقل العمود والاسم معا إلى الترويسة مع التمرير.
- يزال التشكيل من كل المخرجات. PREVIEW: المعاينة محجوبة عن محركات البحث.

التشغيل من جذر website:  python _src/build.py
"""
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import quote

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
V = "1"
PREVIEW = True
DOMAIN = "https://alyabislaw.com"
PREVIEW_ORIGIN = "https://alyabis.sites.alraedlaw.com"
ORIGIN = PREVIEW_ORIGIN if PREVIEW else DOMAIN

S = json.loads((SRC / "content" / "site.json").read_text(encoding="utf-8"))
P = json.loads((SRC / "parts.json").read_text(encoding="utf-8"))
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
TASHKEEL = re.compile("[ً-ْٰـ]")
GOLD, INK = "#b8a268", "#1d1d1d"
ar = lambda n: str(n).translate(AR)
vb = lambda b: " ".join(str(round(v, 2)) for v in b)
SPRITE = f"/assets/img/sprite.svg?v={V}"


def wa(text):
    return f"https://wa.me/{S['whatsapp']}?text={quote(text)}"


def bbox_of(paths):
    xs, ys = [], []
    for d in paths:
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
        xs += nums[0::2]
        ys += nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def box(paths, pad=2):
    x0, y0, x1, y1 = bbox_of(paths)
    return (round(x0 - pad, 1), round(y0 - pad, 1), round(x1 - x0 + 2 * pad, 1), round(y1 - y0 + 2 * pad, 1))


PILLAR = P["bars"] + P["cols"] + [s["d"] for s in P["stones"]]
NAMEP = P["letters"] + [o["d"] for o in P["orn"]]
PILLAR_BOX = box(PILLAR)
NAME_BOX = box(NAMEP)
LOGO_BOX = box(PILLAR + NAMEP + [P["latin"], P["tag_ar"], P["tag_en"]], 4)

ICONS = {
    # الخدمات
    "i-cases": ("0 0 48 48", ["M24 7v34", "M12 41h24", "M9 15h30", "M13 15l-6 12h12z", "M35 15l-6 12h12z", "M21 7h6"]),
    "i-bankruptcy": ("0 0 48 48", ["M8 38h32", "M12 38V22", "M20 38V16", "M28 38V26", "M36 38V30", "M10 12l10 6 8-6 10 8"]),
    "i-arbitration": ("0 0 48 48", ["M24 8v32", "M6 24h12", "M13 19l5 5-5 5", "M42 24H30", "M35 19l-5 5 5 5", "M18 40h12"]),
    "i-companies": ("0 0 48 48", ["M6 41h36", "M10 41V11h16v30", "M26 19h12v22", "M15 17h6", "M15 24h6", "M15 31h6", "M31 26h2", "M31 33h2"]),
    "i-trustees": ("0 0 48 48", ["M16 20a6 6 0 1 0 0-.1", "M32 20a6 6 0 1 0 0-.1", "M6 40c1-7 5-11 10-11s9 4 10 11", "M22 40c1-7 5-11 10-11s9 4 10 11"]),
    "i-consulting": ("0 0 48 48", ["M7 9h34v24H23l-9 7v-7H7z", "M14 18h20", "M14 24h13"]),
    # واجهة
    "i-arrow": ("0 0 24 24", ["M19 12H5", "M11 6l-6 6 6 6"]),
    "i-up": ("0 0 24 24", ["M12 19V5", "M6 11l6-6 6 6"]),
    "i-wa": ("0 0 24 24", ["M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z",
                           "M9 7.8c-.5 0-1 .6-1 1.3 0 2.5 2.8 5.6 5.6 5.6.8 0 1.3-.5 1.3-1l-1.5-1-1 .8c-1-.5-2-1.5-2.5-2.5l.8-1-1-1.5z"]),
    "i-phone": ("0 0 24 24", ["M6.6 3.5h3l1.5 4-2 1.3a11 11 0 0 0 6.1 6.1l1.3-2 4 1.5v3a2 2 0 0 1-2.2 2A17 17 0 0 1 4.6 5.7a2 2 0 0 1 2-2.2z"]),
    "i-mail": ("0 0 24 24", ["M3.5 6h17v12h-17z", "M4 7l8 6 8-6"]),
    "i-pin": ("0 0 24 24", ["M12 21s-7-6.2-7-11.5a7 7 0 1 1 14 0C19 14.8 12 21 12 21z", "M12 12.2a2.6 2.6 0 1 0 0-5.2 2.6 2.6 0 0 0 0 5.2z"]),
    "i-door": ("0 0 24 24", ["M14 3h5v18h-5", "M10 17l5-5-5-5", "M15 12H4"]),
    "i-clock": ("0 0 24 24", ["M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z", "M12 7v5l3 2"]),
    "i-shield": ("0 0 24 24", ["M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6z", "M8.5 12l2.5 2.5 4.5-5"]),
}


def build_sprite():
    G = f'style="fill:var(--lg,{GOLD})"'
    K = f'style="fill:var(--lk,{INK})"'
    part = lambda pid, d, st: f'<path id="{pid}" d="{d}" fill-rule="evenodd" pathLength="1" {st}/>'
    defs = [part(f"b{i}", d, G) for i, d in enumerate(P["bars"])]
    defs += [part(f"c{i}", d, G) for i, d in enumerate(P["cols"])]
    defs += [part(f"s{i}", s["d"], K) for i, s in enumerate(P["stones"])]
    defs += [part(f"l{i}", d, K) for i, d in enumerate(P["letters"])]
    defs.append('<g id="orn">' + "".join(f'<path d="{o["d"]}" fill-rule="evenodd" pathLength="1" {K}/>' for o in P["orn"]) + "</g>")
    defs += [part("latin", P["latin"], K), part("tagar", P["tag_ar"], G), part("tagen", P["tag_en"], G)]
    uses = lambda ids: "".join(f'<use href="#{i}"/>' for i in ids)
    pil = [f"b{i}" for i in range(4)] + ["c0", "c1"] + [f"s{i}" for i in range(len(P["stones"]))]
    nam = [f"l{i}" for i in range(len(P["letters"]))] + ["orn"]
    syms = [f'<symbol id="pillar" viewBox="{vb(PILLAR_BOX)}">{uses(pil)}</symbol>',
            f'<symbol id="name" viewBox="{vb(NAME_BOX)}">{uses(nam)}</symbol>',
            f'<symbol id="logo" viewBox="{vb(LOGO_BOX)}">{uses(pil + nam + ["latin", "tagar", "tagen"])}</symbol>']
    for iid, (bx, paths) in ICONS.items():
        body = "".join(f'<path d="{d}" pathLength="1"/>' for d in paths)
        syms.append(f'<symbol id="{iid}" viewBox="{bx}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">{body}</symbol>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg"><defs>{"".join(defs)}</defs>{"".join(syms)}</svg>'
    (OUT / "assets" / "img" / "sprite.svg").write_text(svg, encoding="utf-8")
    return len(svg)


def ico(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="{ICONS[name][0]}" aria-hidden="true" focusable="false"><use href="{SPRITE}#{name}"/></svg>'


def fly_pillar():
    """العمود للبناء: كل شريط وعمود وحجر عنصر مستقل."""
    b = "".join(f'<path class="yp-bar" data-i="{i}" d="{d}" fill-rule="evenodd"/>' for i, d in enumerate(P["bars"]))
    c = "".join(f'<path class="yp-col" data-i="{i}" d="{d}" fill-rule="evenodd"/>' for i, d in enumerate(P["cols"]))
    s = "".join(f'<path class="yp-stone" data-i="{i}" d="{st["d"]}" fill-rule="evenodd"/>' for i, st in enumerate(P["stones"]))
    return f'<svg class="yp" viewBox="{vb(PILLAR_BOX)}" focusable="false" aria-hidden="true">{b}{c}{s}</svg>'


def fly_name():
    """الاسم للكتابة: قناع لكل قطعة فيه خطوط القلم، وتوقيت كل خط بموضع بدايته من اليمين."""
    x0, x1 = NAME_BOX[0], NAME_BOX[0] + NAME_BOX[2]
    masks, letters = [], []
    for i, strokes in enumerate(P["strokes"]):
        paths = "".join(
            f'<path class="wm" data-t="{round((x1 - s["sx"]) / (x1 - x0), 3)}" data-len="{s["len"]}" d="{s["d"]}" fill="none" '
            f'stroke="#fff" stroke-width="{s["w"]}" stroke-linecap="round" stroke-linejoin="round"/>' for s in strokes)
        masks.append(f'<mask id="wm{i}" maskUnits="userSpaceOnUse" x="-20" y="440" width="880" height="230">{paths}</mask>')
        letters.append(f'<path class="yn-l" d="{P["letters"][i]}" fill-rule="evenodd" mask="url(#wm{i})"/>')
    orn = "".join(f'<path class="yn-o" data-t="{round((x1 - o["cx"]) / (x1 - x0), 3)}" d="{o["d"]}" fill-rule="evenodd"/>' for o in P["orn"])
    return (f'<svg class="yn" viewBox="{vb(NAME_BOX)}" focusable="false" aria-hidden="true"><defs>{"".join(masks)}</defs>'
            f'{"".join(letters)}{orn}</svg>')


def slot_style(b):
    lx, ly, lw, lh = LOGO_BOX
    x, y, w, h = b
    return f"left:{(x - lx) / lw * 100:.3f}%;top:{(y - ly) / lh * 100:.3f}%;width:{w / lw * 100:.3f}%;height:{h / lh * 100:.3f}%"


def hero_lines():
    """السطور تحت الاسم في البطل (تثبت مكانها، وتتلاشى عند انتقال الشعار)."""
    return (f'<svg class="hero__under" viewBox="{vb(LOGO_BOX)}" focusable="false" aria-hidden="true">'
            f'<path class="yu yu-latin" d="{P["latin"]}" fill-rule="evenodd"/><path class="yu yu-ar" d="{P["tag_ar"]}" fill-rule="evenodd"/>'
            f'<path class="yu yu-en" d="{P["tag_en"]}" fill-rule="evenodd"/></svg>')


def lockup(cls):
    """الشعار الأفقي كما في ترويستهم: العمود يمينا والاسم يسارا."""
    pw, ph = PILLAR_BOX[2], PILLAR_BOX[3]
    nw, nh = NAME_BOX[2], NAME_BOX[3]
    s = ph * 0.9 / nh                       # الاسم بتسعة أعشار ارتفاع العمود
    gap = pw * 0.28
    W = nw * s + gap + pw
    return (f'<svg class="{cls}" viewBox="0 0 {round(W, 1)} {round(ph, 1)}" aria-hidden="true" focusable="false">'
            f'<use href="{SPRITE}#name" x="0" y="{round(ph * 0.08, 1)}" width="{round(nw * s, 1)}" height="{round(nh * s, 1)}"/>'
            f'<use href="{SPRITE}#pillar" x="{round(nw * s + gap, 1)}" y="0" width="{round(pw, 1)}" height="{round(ph, 1)}"/></svg>')


# ---------------------------------------------------------------- القطع المشتركة
NAV = [("home", "/", "الرئيسية"), ("about", "/about-us/", "من نحن"), ("services", "/services/", "الخدمات"),
       ("clients", "/#clients", "عملاؤنا"), ("contact", "/contact/", "تواصل معنا")]


def nav_html(key):
    return "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if k == key else ""}>{t}</a></li>' for k, h, t in NAV)


def menu_html(key):
    return "".join(f'<li style="--i:{i}"><a href="{h}"{" aria-current=\"page\"" if k == key else ""}><i>{ar(i)}</i>{t}</a></li>'
                   for i, (k, h, t) in enumerate(NAV, 1))


def colonnade(link=True):
    """الخدمات أعمدة متجاورة: تاج وقاعدة ذهبيان، وفي الجسم رقم الركيزة وعنوانها."""
    out = []
    for i, s in enumerate(S["services"], 1):
        href = f'/services/#{s["key"]}'
        tag = "a" if link else "article"
        attr = f' href="{href}"' if link else f' id="{s["key"]}"'
        out.append(f"""<{tag} class="col"{attr}>
            <span class="col__cap" aria-hidden="true"><i></i><i></i></span>
            <span class="col__body">
              <span class="col__n" aria-hidden="true">{ar(i)}</span>
              {ico('i-' + s['key'], 'col__ico draw')}
              <span class="col__t">{s['title']}</span>
              <span class="col__sub">{s['sub']}</span>
            </span>
            <span class="col__base" aria-hidden="true"><i></i><i></i></span>
          </{tag}>""")
    return "\n          ".join(out)


def service_rows():
    out = []
    for i, s in enumerate(S["services"], 1):
        msg = f"السلام عليكم، أرغب في الاستفسار عن خدمة: {s['title']}."
        out.append(f"""<article class="srow" id="{s['key']}">
            <div class="srow__side"><span class="srow__n">{ar(i)}</span>{ico('i-' + s['key'], 'srow__ico draw')}</div>
            <div class="srow__main">
              <p class="srow__sub" data-rise>{s['sub']}</p>
              <h2 class="srow__t" data-words>{s['title']}</h2>
              <p class="srow__d" data-rise>{s['desc']}</p>
              <a class="link-arrow" href="{wa(msg)}" target="_blank" rel="noopener" data-rise><span>اسأل عن هذه الخدمة</span>{ico('i-wa')}</a>
            </div>
          </article>""")
    return "\n        ".join(out)


def clients_html():
    return "".join(f'<li class="cl"><img src="/assets/img/clients/{c["file"]}.webp" alt="{escape(c["name"])}" loading="lazy" width="200" height="140"></li>'
                   for c in S["clients"])


def credentials():
    return "".join(f'<li class="stone"><span>{c}</span></li>' for c in S["credentials"])


def contact_block():
    return f"""<ul class="cinfo">
          <li><span class="cinfo__i">{ico('i-wa')}</span><span><small>واتساب والجوال</small><a href="{wa(S['whatsapp_text'])}" target="_blank" rel="noopener" dir="ltr">{S['mobile']}</a></span></li>
          <li><span class="cinfo__i">{ico('i-phone')}</span><span><small>الهاتف</small><a href="tel:{S['phone_intl']}" dir="ltr">{S['phone']}</a></span></li>
          <li><span class="cinfo__i">{ico('i-mail')}</span><span><small>البريد الإلكتروني</small><a href="mailto:{S['email']}" dir="ltr">{S['email']}</a></span></li>
          <li><span class="cinfo__i">{ico('i-pin')}</span><span><small>العنوان</small><a href="{S['map']}" target="_blank" rel="noopener">{S['address']}</a></span></li>
          <li><span class="cinfo__i">{ico('i-door')}</span><span><small>بوابة العملاء وفريق العمل</small><a href="{S['portal']}">الدخول إلى حسابك</a></span></li>
        </ul>"""


def composer():
    types = "".join(f'<option value="{t}">{t}</option>' for t in S["case_types"])
    times = "".join(f'<label><input type="radio" name="time" value="{t}"><span>{t}</span></label>' for t in S["times"])
    return f"""<form class="wa" id="wa-form" action="https://wa.me/{S['whatsapp']}" method="get" target="_blank">
          <div class="wa__head">{ico('i-wa')}<span><b>طلب استشارة عبر واتساب</b><small>تصل رسالتك إلى المكتب مباشرة</small></span></div>
          <div class="field"><input id="wa-name" name="name" placeholder=" " autocomplete="name" required><label for="wa-name">الاسم الكامل</label></div>
          <div class="field field--select"><select id="wa-type" name="type" required><option value="" selected disabled>اختر نوع الخدمة</option>{types}</select><label for="wa-type">نوع الخدمة</label></div>
          <fieldset class="pick"><legend>وقت التواصل المفضل</legend><div class="pick__opts">{times}</div></fieldset>
          <div class="field field--area"><textarea id="wa-msg" name="msg" rows="3" placeholder=" " required></textarea><label for="wa-msg">تفاصيل القضية أو الاستفسار</label></div>
          <div class="wa__preview" aria-hidden="true"><span class="wa__bubble" id="wa-bubble">{S['whatsapp_text']}</span></div>
          <input type="hidden" name="text" id="wa-text" value="{escape(S['whatsapp_text'])}">
          <p class="wa__note">{ico('i-shield')}<span>{S['consult_note']}</span></p>
          <button class="btn btn--ink" type="submit">{ico('i-wa')}<span>إرسال عبر واتساب</span></button>
        </form>"""


def cta(title, line):
    return f"""<section class="cta">
      <div class="wrap cta__in">
        <p class="eyebrow" data-rise>تواصل معنا</p>
        <h2 class="h2 cta__t" data-words>{title}</h2>
        <p class="lead" data-rise>{line}</p>
        <div class="cta__actions" data-rise>
          <a class="btn btn--ink" href="{wa(S['whatsapp_text'])}" target="_blank" rel="noopener">{ico('i-wa')}<span>ابدأ المحادثة الآن</span></a>
          <a class="btn btn--line" href="/contact/"><span>احجز استشارتك</span>{ico('i-arrow')}</a>
        </div>
      </div>
    </section>"""


def page_hero(title, crumb, lead=""):
    lead_html = f'<p class="phero__lead" data-rise>{lead}</p>' if lead else ""
    return f"""<section class="phero">
      <div class="phero__grid" aria-hidden="true"></div>
      <svg class="phero__pillar" viewBox="{vb((0, 0, PILLAR_BOX[2], PILLAR_BOX[3]))}" aria-hidden="true" focusable="false"><use href="{SPRITE}#pillar"/></svg>
      <div class="wrap phero__in">
        <nav class="crumbs" aria-label="مسار الصفحة" data-rise><a href="/">الرئيسية</a><span aria-hidden="true">/</span>{crumb}</nav>
        <h1 class="phero__t" data-words>{title}</h1>
        {lead_html}
      </div>
    </section>"""


def jsonld():
    return json.dumps({
        "@context": "https://schema.org", "@type": "LegalService", "@id": f"{DOMAIN}/#organization",
        "name": S["name"], "alternateName": S["display"], "url": f"{DOMAIN}/", "logo": f"{DOMAIN}/assets/img/icon-512.png",
        "image": f"{DOMAIN}/assets/img/og-image.jpg", "telephone": S["phone_intl"], "email": S["email"],
        "address": {"@type": "PostalAddress", "streetAddress": "حي العليا، برج السلام، مكتب 109", "addressLocality": "الخبر",
                    "addressRegion": "المنطقة الشرقية", "addressCountry": "SA"},
        "identifier": [{"@type": "PropertyValue", "name": "رقم الترخيص", "value": S["license"]},
                       {"@type": "PropertyValue", "name": "الرقم الموحد للمنشأة", "value": S["unified"]}],
        "founder": {"@type": "Person", "name": S["leader_name"]}, "areaServed": "SA",
    }, ensure_ascii=False)


def page(key, title, desc, canon, main, fly=""):
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    rep = {
        "TITLE": title, "DESC": desc, "CANON": f"{DOMAIN}{canon}", "OG_URL": f"{ORIGIN}{canon}",
        "OG_IMAGE": f"{ORIGIN}/assets/img/og-image.jpg",
        "ROBOTS": '<meta name="robots" content="noindex, nofollow">' if PREVIEW else "",
        "PAGE": key, "NAV": nav_html(key), "MENU": menu_html(key), "MAIN": main, "FLY": fly, "V": V, "SPRITE": SPRITE,
        "PILLAR_VB": vb((0, 0, PILLAR_BOX[2], PILLAR_BOX[3])), "NAME_VB": vb((0, 0, NAME_BOX[2], NAME_BOX[3])),
        "LOCKUP_FTR": lockup("ftr__lockup"), "JSONLD": jsonld(),
        "WA": wa(S["whatsapp_text"]), "MOBILE": S["mobile"], "MOBILE_INTL": S["mobile_intl"], "PHONE": S["phone"],
        "PHONE_INTL": S["phone_intl"], "EMAIL": S["email"], "ADDRESS": S["address"], "PORTAL": S["portal"],
        "NAME": S["name"], "SHORT": S["short"], "DISPLAY": S["display"], "LICENSE": ar(S["license"]),
        "ICO_WA": ico("i-wa"), "ICO_UP": ico("i-up"), "ICO_DOOR": ico("i-door"),
    }
    for k, v in rep.items():
        layout = layout.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", layout)
    assert not left, (key, left)
    return TASHKEEL.sub("", layout)


def fill(tpl, **kw):
    html = (SRC / "pages" / tpl).read_text(encoding="utf-8")
    for k, v in kw.items():
        html = html.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", html)
    assert not left, (tpl, left)
    return html


def write(rel, html):
    f = OUT / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding="utf-8")
    return len(html.encode("utf-8"))


def main():
    sizes = {"sprite.svg": build_sprite()}
    common = dict(ICO_WA=ico("i-wa"), ICO_ARROW=ico("i-arrow"), WA=wa(S["whatsapp_text"]), SPRITE=SPRITE,
                  NAME=S["name"], DISPLAY=S["display"], STATEMENT=S["statement"], SUB=S["sub"], YEARS=S["years"],
                  ABOUT_TITLE=S["about_title"], ABOUT1=S["about"][0], ABOUT2=S["about"][1], PARTNER=S["partner"],
                  LEADER_NAME=S["leader_name"], LEADER_ROLE=S["leader_role"], LEADER_BIO=S["leader_bio"],
                  CREDENTIALS=credentials(), SERVICES_TITLE=S["services_title"], SERVICES_INTRO=S["services_intro"],
                  COLONNADE=colonnade(), BK_TITLE=S["bk_title"], BK_TEXT=S["bk_text"], CLIENTS_TITLE=S["clients_title"],
                  CLIENTS=clients_html(), CONSULT_TITLE=S["consult_title"], CONSULT_LINE=S["consult_line"],
                  CONTACT=contact_block(), COMPOSER=composer(), PILLAR_VB=vb((0, 0, PILLAR_BOX[2], PILLAR_BOX[3])))

    home = fill("home.html", **common, LOGO_VB=vb((0, 0, LOGO_BOX[2], LOGO_BOX[3])), HERO_UNDER=hero_lines(),
                LOGO_AR=f"{LOGO_BOX[2]} / {LOGO_BOX[3]}",
                SLOT_PILLAR=slot_style(PILLAR_BOX), SLOT_NAME=slot_style(NAME_BOX))
    fly = (f'<div class="fly fly--pillar" aria-hidden="true">{fly_pillar()}</div>'
           f'<div class="fly fly--name" aria-hidden="true">{fly_name()}</div>')
    sizes["index.html"] = write("index.html", page(
        "home", f"{S['display']} | الخبر",
        "الدكتور عبدالله اليابس للمحاماة والاستشارات القانونية في الخبر: القضايا، والإفلاس، والتحكيم، وخدمات الشركات، والاستشارات الشرعية والقانونية.",
        "/", home, fly))

    sizes["about-us/index.html"] = write("about-us/index.html", page(
        "about", f"من نحن | {S['short']}", "نبذة عن شركة الدكتور عبدالله بن عبدالرحمن اليابس للمحاماة والاستشارات القانونية وقائد فريقها.",
        "/about-us/", page_hero("من نحن", '<span aria-current="page">من نحن</span>', S["about_title"])
        + fill("about.html", **common, CTA=cta("نسعد بخدمتك", S["consult_line"]))))

    sizes["services/index.html"] = write("services/index.html", page(
        "services", f"الخدمات | {S['short']}", "خدمات الدكتور عبدالله اليابس للمحاماة: القضايا، والإفلاس، والتحكيم، والشركات، والشراكة مع أمناء الإفلاس، والاستشارات الشرعية والقانونية.",
        "/services/", page_hero(S["services_title"], '<span aria-current="page">الخدمات</span>', S["services_intro"])
        + fill("services.html", **common, SERVICE_ROWS=service_rows(), CTA=cta("أي هذه الخدمات تحتاج؟", S["consult_line"]))))

    sizes["contact/index.html"] = write("contact/index.html", page(
        "contact", f"تواصل معنا | {S['short']}", "احجز استشارتك مع الدكتور عبدالله اليابس للمحاماة في الخبر: واتساب، والهاتف، والبريد الإلكتروني.",
        "/contact/", page_hero(S["consult_title"], '<span aria-current="page">تواصل معنا</span>', S["consult_line"])
        + fill("contact.html", **common)))

    sizes["404.html"] = write("404.html", page("404", f"الصفحة غير موجودة | {S['short']}", "الصفحة غير موجودة.", "/404",
                                               fill("404.html", **common)))
    urls = ["/", "/about-us/", "/services/", "/contact/"]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{DOMAIN}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", "User-agent: *\nDisallow: /\n" if PREVIEW else f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(" · ".join(f"{k} {v // 1024}K" for k, v in sizes.items()))
    print("boxes: pillar", PILLAR_BOX, "name", NAME_BOX, "logo", LOGO_BOX)


if __name__ == "__main__":
    main()
