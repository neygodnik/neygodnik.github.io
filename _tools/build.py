"""Сборка сайта neygodnik.ru из _data/ в корень репозитория.

Запуск из корня репозитория: python3 _tools/build.py
Источники: _data/posts.json (посты), _data/library.md (каталог «Библиотеки Товарища»).
"""
import html as H
import json
import os
import re
import shutil
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://neygodnik.ru'
TG = 'https://t.me/neygodnik'
IG = 'https://instagram.com/neygodnik_blog'
MSK = timezone(timedelta(hours=3))
FONTS = ('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700'
         '&family=PT+Serif:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap')

RUBRICS = {
    'put': ('Путь', 'От деревни Бобровка в Оренбургских степях до Москвы: история по местам и периодам.', 'old'),
    'novyy-mir': ('Новый Мiр', 'Товарищество, казаки, история, на которую можно опереться.', 'new'),
    'parni-vsey-zemli': ('Парни всей земли', 'Крипторынок без глянца: казино, дно, контейнер, боты.', 'new'),
    'biblioteka-tovarishcha': ('Библиотека Товарища', 'Что читал Сталин и что из этого стоит прочитать нам.', 'new'),
    'yurfak': ('ЮрФак', 'Как заставить систему работать: письма, жалобы, ответы.', 'new'),
    'kentavrizatsiya': ('Кентавризация', 'Как я работаю с ИИ-товарищами и что из этого выходит.', 'new'),
    'zabugor': ('Забугор', 'Города и дороги: как живут у них и вокруг чего строится мир.', 'new'),
}
SERIES = [{'name': 'Казаки', 'ids': [232, 250, 265]}]

esc = H.escape


def plural(n, one, few, many):
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:
        return one
    if 2 <= n10 <= 4 and not 12 <= n100 <= 14:
        return few
    return many


def dt(p):
    return datetime.fromisoformat(p['date']).astimezone(MSK)


def dmy(p):
    return dt(p).strftime('%d.%m.%Y')


def url(p):
    return f"/{p['rubric']}/{p['slug']}/"


def plain(h):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()


def excerpt(p, n=160):
    t = plain(p['html'])
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(' ', 1)[0].rstrip(',.:;—-')
    return cut + '…'


def minutes(p):
    return max(1, round(len(plain(p['html'])) / 1100))


def write(path, text):
    full = os.path.join(ROOT, path.lstrip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)


def head(title, descr, path, image=None, jsonld=None, og_type='website'):
    img = SITE + (image or '/img/og-default.jpg')
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>\n'
                 for j in (jsonld or []))
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(descr)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Неугодник">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(descr)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Неугодник" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/style.css">
{ld}<meta name="google-site-verification" content="Ge22rWv9ot2AqjruS_Ar4eLL4gflaGz3V5b_134BOAM">
<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){{
        m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=114119306', 'ym');

    ym(114119306, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
</script>
<!-- /Yandex.Metrika counter -->
</head>
<body>
<noscript><div><img src="https://mc.yandex.ru/watch/114119306" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<a class="skip" href="#main">К содержанию</a>
'''


def header(cur=None):
    links = ''.join(
        f'<a href="/{k}/"{" aria-current=\"page\"" if k == cur else ""}>{esc(v[0])}</a>' for k, v in RUBRICS.items())
    return f'''<header class="site-head"><div class="wrap">
<a class="logo" href="/"><b>НЕУГОДНИК</b><span>блог о пути, товариществе и книгах</span></a>
<nav class="nav" aria-label="Разделы">{links}</nav>
<a class="btn" href="{TG}">Присоединиться</a>
</div></header>
<main id="main">
'''


FOOT = f'''</main>
<footer class="site-foot"><div class="wrap">
<span>© 2026 Неугодник · Аслан</span>
<nav aria-label="Соцсети"><a href="{TG}">Телеграм</a><a href="{IG}">Инстаграм</a><a href="/feed.xml">RSS</a></nav>
</div></footer>
</body>
</html>
'''


def crumbs_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u}
                                for i, (n, u) in enumerate(items)]}


def link_body(h, by_id):
    def tg(m):
        n = int(m.group(1))
        return f'<a href="{url(by_id[n])}">' if n in by_id else f'<a href="{TG}/{n}">'
    h = re.sub(r'<a href="tg:(\d+)">', tg, h)
    h = re.sub(r'<a href="(https?://(?!neygodnik\.ru)[^"]+)"[^>]*>',
               r'<a href="\1" target="_blank" rel="noopener">', h)
    return h


def pos(ph):
    """Точка кадрирования для обрезки под карточку: вертикальные кадры держим ближе к верху,
    чтобы не резать головы и заголовки слайдов. Можно задать вручную полем "pos" у фото."""
    if ph.get('pos'):
        return f' style="object-position:{ph["pos"]}"'
    if ph['h'] > ph['w'] * 1.05:
        return ' style="object-position:50% 30%"'
    return ''


def card(p, cls='card'):
    img = (f'<img src="{p["photos"][0]["src"]}" alt="" loading="lazy" width="{p["photos"][0]["w"]}" '
           f'height="{p["photos"][0]["h"]}"{pos(p["photos"][0])}>' if p['photos'] else f'<div class="ph">{esc(p["title"])}</div>')
    return (f'<a class="{cls}" href="{url(p)}">{img}<span class="meta">{dmy(p)} · {esc(RUBRICS[p["rubric"]][0])}</span>'
            f'<span class="h3">{esc(p["title"])}</span><p>{esc(excerpt(p, 140))}</p></a>')


def build_post(p, posts, by_id):
    rname = RUBRICS[p['rubric']][0]
    same = [q for q in posts if q['rubric'] == p['rubric']]
    i = same.index(p)
    prev_p = same[i - 1] if i > 0 else None
    next_p = same[i + 1] if i + 1 < len(same) else None
    descr = excerpt(p)
    photo = p['photos'][0] if p['photos'] else None
    ld = [{'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'],
           'description': descr, 'datePublished': dt(p).isoformat(), 'inLanguage': 'ru',
           'author': {'@type': 'Person', 'name': 'Аслан', 'url': SITE + '/'},
           'publisher': {'@type': 'Organization', 'name': 'Неугодник', 'url': SITE + '/'},
           'mainEntityOfPage': SITE + url(p), **({'image': SITE + photo['src']} if photo else {})},
          crumbs_ld([('Главная', '/'), (rname, f'/{p["rubric"]}/'), (p['title'], url(p))])]
    out = [head(f'{p["title"]} · Неугодник', descr, url(p), photo['src'] if photo else None, ld, 'article'),
           header(p['rubric'])]
    out.append(f'''<article>
<div class="narrow">
<nav class="crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span aria-hidden="true">/</span><a href="/{p["rubric"]}/">{esc(rname)}</a></nav>
<header class="post-head">
<p class="kicker">{esc(rname)}</p>
<h1 class="h1">{esc(p["title"])}</h1>
<p class="meta"><time datetime="{dt(p).isoformat()}">{dmy(p)}</time> · {minutes(p)} {plural(minutes(p), "минута", "минуты", "минут")} чтения · Аслан</p>
</header>
</div>''')
    if photo:
        out.append(f'<figure class="post-hero"><img src="{photo["src"]}" alt="{esc(p["title"])}" '
                   f'width="{photo["w"]}" height="{photo["h"]}"></figure>')
    out.append(f'<div class="narrow body">{link_body(p["html"], by_id)}')
    if len(p['photos']) > 1:
        out.append('<div class="gallery">' + ''.join(
            f'<a href="{ph["src"]}"><img src="{ph["src"]}" alt="{esc(p["title"])}, фото {k + 2}" loading="lazy" '
            f'width="{ph["w"]}" height="{ph["h"]}"{pos(ph)}></a>' for k, ph in enumerate(p['photos'][1:])) + '</div>')
    if p.get('video'):
        out.append(f'<p class="note">В этом посте есть видео: <a href="{TG}/{p["id"]}">смотреть в Телеграме</a>.</p>')
    tags = ''.join(f'<a href="/{p["rubric"]}/">#{esc(t)}</a>' for t in p.get('tags', []))
    out.append(f'<p class="tags">{tags}<a href="{TG}/{p["id"]}">Обсудить в Телеграме</a></p>')
    for s in SERIES:
        if p['id'] in s['ids']:
            items = ''
            for k, sid in enumerate(s['ids']):
                q = by_id[sid]
                if sid == p['id']:
                    items += f'<li class="cur"><b>{k + 1}</b><strong>{esc(q["title"])}</strong><span class="meta">вы здесь</span></li>'
                else:
                    items += f'<li><b>{k + 1}</b><a href="{url(q)}">{esc(q["title"])}</a></li>'
            out.append(f'<section class="series" aria-label="Серия"><h2 class="h3">Серия «{esc(s["name"])}»</h2><ol>{items}</ol></section>')
    pn = ''
    if prev_p:
        pn += f'<a href="{url(prev_p)}" rel="prev"><span>Предыдущая запись</span><b>{esc(prev_p["title"])}</b></a>'
    if next_p:
        pn += f'<a href="{url(next_p)}" rel="next"><span>Следующая запись</span><b>{esc(next_p["title"])}</b></a>'
    if pn:
        out.append(f'<nav class="pn" aria-label="Соседние записи">{pn}</nav>')
    out.append('</div></article>')
    out.append(f'''<section class="cta"><div class="narrow">
<h2 class="h2">Обсудим в Телеграме</h2>
<p>Новые записи выходят там раньше всего, три раза в неделю. Там же можно написать мне.</p>
<a class="btn btn-light" href="{TG}">Открыть канал</a>
</div></section>''')
    rel = [q for q in reversed(same) if q is not p][:3]
    if rel:
        out.append('<section class="wrap pad"><h2 class="sec-title">Читать дальше</h2><div class="cards" style="margin-top:24px">'
                   + ''.join(card(q) for q in rel) + '</div></section>')
    out.append(FOOT)
    write(url(p) + 'index.html', '\n'.join(out))


def build_rubric(k, posts):
    name, descr, order = RUBRICS[k]
    items = [p for p in posts if p['rubric'] == k]
    if order == 'new':
        items = list(reversed(items))
    lis = ''.join(f'<li><a href="{url(p)}"><b>{esc(p["title"])}</b><span class="meta">{dmy(p)}</span>'
                  f'<p>{esc(excerpt(p, 200))}</p></a></li>' for p in items)
    extra = ''
    if k == 'biblioteka-tovarishcha':
        extra = ('<p style="margin:0"><a class="btn" href="/biblioteka-tovarishcha/katalog/">'
                 'Каталог: 392 книги с пометками Сталина</a></p>')
    ld = [crumbs_ld([('Главная', '/'), (name, f'/{k}/')])]
    page = [head(f'{name} · Неугодник', descr, f'/{k}/', items[0]['photos'][0]['src'] if items and items[0]['photos'] else None, ld),
            header(k),
            f'''<div class="wrap pad" style="display:flex;flex-direction:column;gap:18px">
<nav class="crumbs" style="margin:0" aria-label="Хлебные крошки"><a href="/">Главная</a></nav>
<h1 class="h1">{esc(name)}</h1>
<p style="margin:0;font-size:21px;color:var(--text);max-width:720px">{esc(descr)}</p>
<p class="meta">{len(items)} {plural(len(items), "запись", "записи", "записей")}{" · читать по порядку, с самого начала" if order == "old" else ""}</p>
{extra}
<ul class="list">{lis}</ul>
</div>''', FOOT]
    write(f'/{k}/index.html', '\n'.join(page))


def build_index(posts):
    latest = list(reversed(posts))
    feat, fresh = latest[0], latest[1:4]
    counts = {k: sum(1 for p in posts if p['rubric'] == k) for k in RUBRICS}
    fimg = feat['photos'][0] if feat['photos'] else None
    rub = ''.join(
        f'<a href="/{k}/"><b>{esc(v[0])}</b><span>{esc(v[1])}</span><span class="meta">{counts[k]} '
        f'{plural(counts[k], "запись", "записи", "записей")}</span></a>' for k, v in RUBRICS.items())
    ld = [{'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Неугодник', 'url': SITE + '/',
           'inLanguage': 'ru', 'author': {'@type': 'Person', 'name': 'Аслан'}}]
    descr = ('Личный блог Аслана: путь из деревни в Оренбургских степях до Москвы, товарищество, казаки, '
             'библиотека Сталина и крипторынок без глянца.')
    page = [head('Неугодник: блог о пути, товариществе и книгах', descr, '/', fimg['src'] if fimg else None, ld),
            header(),
            f'''<section class="wrap hero">
<div class="hero-text">
<p class="kicker">Меня зовут Аслан</p>
<h1 class="h1">Из деревни в Оренбургских степях до Москвы</h1>
<p class="lead">Всю жизнь работал в тени: политтехнолог, чужие победы, ни одной личной страницы. Здесь мои истории по местам и периодам. Вперемешку стыд, смех и то, во что я верю.</p>
<div class="row"><a class="btn btn-line" href="{url(posts[0])}">Читать с начала</a><a href="#novyy-mir" style="text-decoration:underline;font-family:var(--ui);font-weight:600;font-size:15px;padding:12px 6px">Что такое Новый Мiр</a></div>
</div>
<a class="feature" href="{url(feat)}">{f'<img src="{fimg["src"]}" alt="" width="{fimg["w"]}" height="{fimg["h"]}"{pos(fimg)}>' if fimg else ''}
<div><span class="meta">{dmy(feat)} · {esc(RUBRICS[feat["rubric"]][0])}</span><span class="h3">{esc(feat["title"])}</span><p>{esc(excerpt(feat, 170))}</p></div></a>
</section>
<section class="wrap" style="padding-bottom:56px" aria-labelledby="fresh">
<div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;border-top:1px solid var(--ink);padding-top:16px;margin-bottom:24px">
<h2 id="fresh" class="h3" style="font-size:28px">Свежее</h2></div>
<div class="cards">{''.join(card(p) for p in fresh)}</div>
</section>
<section class="band" aria-labelledby="lib"><div class="wrap">
<div style="flex:2 1 480px;min-width:0;display:flex;flex-direction:column;gap:16px">
<p class="kicker">Библиотека Товарища</p>
<h2 id="lib" class="h2">392 книги с пометками Сталина</h2>
<p style="margin:0;font-size:19px;max-width:640px">Опись 3 фонда 558 РГАСПИ, разложенная так, как Сталин сам просил разложить свою библиотеку в записке 1925 года: не по авторам, а по вопросам.</p>
</div>
<div style="flex:1 1 260px;display:flex;flex-direction:column;gap:16px;align-items:flex-start">
<div class="stats"><div><b>392</b><span>книги</span></div><div><b>32</b><span>рубрики</span></div><div><b>12</b><span>авторов отдельно</span></div></div>
<a class="btn btn-light" href="/biblioteka-tovarishcha/katalog/">Открыть каталог</a>
</div></div></section>
<section class="wrap pad" aria-labelledby="rubrics">
<h2 id="rubrics" class="sec-title" style="margin-bottom:24px">Рубрики</h2>
<div class="grid-rub">{rub}</div>
</section>
<section id="novyy-mir" class="nm" aria-labelledby="nm"><div class="wrap">
<div class="col">
<p class="kicker">Новый Мiр</p>
<h2 id="nm" class="h2">Мир, где созидание ценится теми, для кого оно создаётся</h2>
<p>Я вырос в деревне, где на моих глазах умер совхоз-миллионник. Не потому, что люди разучились работать: работать они умели лучше всех. А потому, что систему, в которой их труд имел смысл, разобрали на металлолом.</p>
<p>Много лет ищу ответ на простой вопрос: как жить правильно? И нашёл одно общее во всём, что цепляло: нормально жить можно только вместе, на честных условиях. Не в красивых словах, а в конкретных делах.</p>
<a class="btn" style="align-self:flex-start" href="{TG}">Присоединиться в Телеграме</a>
</div>
<div class="col">
<h3 class="h3" style="font-size:22px"><a href="/put/kodeks-tovarishchestva/">Кодекс товарищества</a></h3>
<ol class="codex">
<li><b>1</b><span>Между товарищами секретов нет, если это не гостайна.</span></li>
<li><b>2</b><span>Товарищи всегда говорят правду, без недомолвок и умалчиваний. Честность - главное правило.</span></li>
<li><b>3</b><span>Главный принцип товарищества - безупречность во всех действиях (сделать всё, что можешь, + 20%).</span></li>
<li><b>4</b><span>Сам погибай, но товарища выручай. Интересы товарища выше своих собственных.</span></li>
</ol>
</div>
</div></section>''', FOOT]
    write('/index.html', '\n'.join(page))


def build_library():
    md = open(os.path.join(ROOT, '_data', 'library.md'), encoding='utf-8').read()
    secs = re.split(r'^## ', md, flags=re.M)
    note = re.search(r'«Мой совет.*?»', md, re.S).group(0)
    main_secs = [s for s in secs[1:] if re.match(r'(I|II|III|IV)\. ', s)]
    from import_tg import slugify  # noqa: E402
    authors, grid, blocks = [], [], []
    total_books = 0
    for s in main_secs:
        stitle = s.split('\n', 1)[0].strip()
        blocks.append(f'<h2 class="sec-title" style="margin-top:56px">{esc(stitle)}</h2>')
        for r in re.split(r'^### ', s, flags=re.M)[1:]:
            lines = r.split('\n')
            m = re.match(r'(.*?)\s*\((\d+)\)\s*$', lines[0].strip())
            rname, cnt = (m.group(1), int(m.group(2))) if m else (lines[0].strip(), 0)
            total_books += cnt
            rid = slugify(rname)
            items, descr = [], []
            for ln in lines[1:]:
                if ln.startswith('- '):
                    t = ln[2:].strip()
                    mm = re.match(r'(.*?)\s*\((оп\. 3, д\. \d+)\)\s*$', t)
                    items.append(f'<li>{esc(mm.group(1))}<span>{esc(mm.group(2))}</span></li>' if mm
                                 else f'<li>{esc(t)}</li>')
                elif ln.strip():
                    descr.append(ln.strip())
            d = ''.join(f'<p class="descr">{esc(x)}</p>' for x in descr)
            body = f'<ul>{"".join(items)}</ul>' if items else '<p class="empty">Пока пусто: книг с пометками по этой рубрике в описи нет. Пополняем.</p>'
            blocks.append(f'<section class="rub" id="{rid}"><h3>{esc(rname)} <span>{cnt}</span></h3>{d}{body}</section>')
            if stitle.startswith('I.'):
                authors.append(f'<a href="#{rid}">{esc(rname)} <b>{cnt}</b></a>')
            elif stitle.startswith('II.'):
                mk = re.match(r'(\S+\))\s*(.*)', rname)
                k, nm = (mk.group(1), mk.group(2)) if mk else ('', rname)
                grid.append(f'<a href="#{rid}"{" class=\"empty\"" if cnt == 0 else ""}><span><i>{esc(k)}</i>{esc(nm)}</span>'
                            f'<b>{cnt if cnt else "пусто"}</b></a>')
    title = 'Библиотека Сталина: 392 книги с его пометками, каталог · Неугодник'
    descr = ('Каталог книг из библиотеки И. В. Сталина с его пометками (РГАСПИ, ф. 558, оп. 3), разложенный по '
             'рубрикам его собственной записки 1925 года: философия, политэкономия, военное дело, беллетристика и другие.')
    path = '/biblioteka-tovarishcha/katalog/'
    ld = [crumbs_ld([('Главная', '/'), ('Библиотека Товарища', '/biblioteka-tovarishcha/'), ('Каталог', path)]),
          {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Библиотека Товарища: каталог',
           'description': descr, 'url': SITE + path, 'inLanguage': 'ru'}]
    page = [head(title, descr, path, None, ld), header('biblioteka-tovarishcha'),
            f'''<div class="wrap">
<nav class="crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span aria-hidden="true">/</span><a href="/biblioteka-tovarishcha/">Библиотека Товарища</a></nav>
<section style="display:flex;flex-wrap:wrap;gap:48px;padding-bottom:32px">
<div style="flex:3 1 520px;min-width:0;display:flex;flex-direction:column;gap:18px">
<p class="kicker">Каталог · #БиблиотекаТоварища</p>
<h1 class="h1">Библиотека Товарища</h1>
<p style="margin:0;font-size:21px;color:var(--text)">{total_books} книг из библиотеки И. В. Сталина, в которых остались его пометки. Основа: опись 3 фонда 558 РГАСПИ, «Книги из библиотеки И. В. Сталина с его пометками. 1866-1952». Разложены так, как он сам просил разложить свою библиотеку в 1925 году.</p>
<p class="meta">Раскладка по рубрикам сделана по названиям книг и местами спорна. Перекладываем, когда находим основания. «оп. 3, д. N» означает номер дела в описи.</p>
</div>
<blockquote class="lib-quote"><span class="kicker">Записка помощнику, 1925</span><q>{esc(note)}</q><span class="meta" style="color:#BDBDBD">И. В. Сталин, записка И. П. Товстухе</span></blockquote>
</section>
<h2 class="sec-title">Отдельно: двенадцать авторов</h2>
<p class="meta" style="margin:6px 0 18px">Пункт 2 записки.</p>
<div class="chips">{"".join(authors)}</div>
<h2 class="sec-title" style="margin-top:40px">По вопросам</h2>
<p class="meta" style="margin:6px 0 18px">Пункт 1 записки. Пустые рубрики тоже показываем: их мы пополняем.</p>
<div class="rgrid">{"".join(grid)}</div>
{"".join(blocks)}
<p class="meta" style="margin:48px 0">Источник: <a href="https://rgaspi-558.dlibrary.org/ru/nodes/28327-opis-3-knigi-iz-biblioteki-i-v-stalina-s-ego-pometkami-1866-locale-nil-1952" target="_blank" rel="noopener" style="text-decoration:underline">РГАСПИ, ф. 558, оп. 3</a>. Текст записки по публикации <a href="https://1001.ru/articles/post/chto-chital-stalin-29522" target="_blank" rel="noopener" style="text-decoration:underline">1001.ru</a>.</p>
</div>''', FOOT]
    write(path + 'index.html', '\n'.join(page))


def build_misc(posts):
    pages = ['/', '/biblioteka-tovarishcha/katalog/'] + [f'/{k}/' for k in RUBRICS] + [url(p) for p in posts]
    lastmod = {url(p): dt(p).date().isoformat() for p in posts}
    today = datetime.now(MSK).date().isoformat()
    sm = ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{lastmod.get(u, today)}</lastmod></url>\n' for u in pages)
    write('/sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    write('/robots.txt', f'User-agent: *\nAllow: /\nDisallow: /_data/\nDisallow: /_tools/\n\nSitemap: {SITE}/sitemap.xml\nHost: neygodnik.ru\n')
    write('/CNAME', 'neygodnik.ru\n')
    items = ''
    for p in list(reversed(posts))[:20]:
        items += (f'<item><title>{esc(p["title"])}</title><link>{SITE}{url(p)}</link><guid>{SITE}{url(p)}</guid>'
                  f'<pubDate>{dt(p).strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>'
                  f'<description>{esc(excerpt(p, 300))}</description></item>\n')
    write('/feed.xml', f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Неугодник</title><link>{SITE}/</link>
<description>Личный блог Аслана о пути, товариществе и книгах</description><language>ru</language>
{items}</channel></rss>
''')
    write('/favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#B3261E"/>'
          '<text x="32" y="47" font-family="Arial Narrow,Arial,sans-serif" font-weight="700" font-size="44" '
          'text-anchor="middle" fill="#F4F4F2">Н</text></svg>\n')
    write('/404.html', head('Страница не найдена · Неугодник', 'Такой страницы нет.', '/404.html') + header() +
          '<div class="wrap pad" style="display:flex;flex-direction:column;gap:18px"><h1 class="h1">Такой страницы нет</h1>'
          '<p style="margin:0">Возможно, адрес изменился. Начните с <a href="/" style="text-decoration:underline">главной</a>.</p></div>' + FOOT)


def main():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    posts = sorted(json.load(open(os.path.join(ROOT, '_data', 'posts.json'), encoding='utf-8')), key=lambda p: p['id'])
    by_id = {p['id']: p for p in posts}
    for k in RUBRICS:
        d = os.path.join(ROOT, k)
        if os.path.isdir(d):
            shutil.rmtree(d)
    for p in posts:
        build_post(p, posts, by_id)
    for k in RUBRICS:
        build_rubric(k, posts)
    build_library()
    build_index(posts)
    build_misc(posts)
    print('собрано:', len(posts), 'постов')


if __name__ == '__main__':
    main()
