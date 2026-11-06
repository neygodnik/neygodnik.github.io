"""Импорт постов из выгрузки канала t.me/s/neygodnik в _data/posts.json.

Запуск: python3 _tools/import_tg.py <posts_raw.json> <папка_с_картинками>
Сырые данные: {номер: {"html", "photos", "video", "date"}}, картинки: N-k.jpg.
Уже существующие записи в posts.json не перезаписываются (правки сохраняются).
"""
import html as H
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, '_data', 'posts.json')
IMG = os.path.join(ROOT, 'img', 'posts')

TAG_RUBRIC = {
    'НовыйМир': 'novyy-mir', 'ПарниВсейЗемли': 'parni-vsey-zemli',
    'БиблиотекаТоварища': 'biblioteka-tovarishcha', 'ЮрФак': 'yurfak',
    'Кентавризация': 'kentavrizatsiya', 'Забугор': 'zabugor',
}
SKIP = {1, 2, 3, 4, 22}

TR = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
              ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
               'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'y', '', 'e', 'yu', 'ya']))


def slugify(s):
    s = s.lower().replace('i', 'i')
    out = ''.join(TR.get(c, c) for c in s)
    out = re.sub(r'[^a-z0-9]+', '-', out).strip('-')
    return out[:70].rstrip('-') or 'post'


def clean(raw):
    h = re.sub(r'^<div[^>]*>', '', raw.strip())
    h = re.sub(r'</div>\s*$', '', h)
    h = re.sub(r'<i class="emoji"[^>]*><b>(.*?)</b></i>', r'\1', h)
    tags = [H.unescape(t) for t in re.findall(r'<a href="\?q=[^"]*">#([^<]+)</a>', h)]
    h = re.sub(r'<a href="\?q=[^"]*">#[^<]+</a>', '', h)
    h = re.sub(r'\s*onclick="[^"]*"', '', h)
    h = re.sub(r'<a href="https://t\.me/neygodnik/(\d+)"[^>]*>', r'<a href="tg:\1">', h)
    h = re.sub(r'<b>', '<strong>', h).replace('</b>', '</strong>')
    h = re.sub(r'<br\s*/?>', '\n', h)
    parts = [p.strip() for p in re.split(r'\n\s*\n', h) if p.strip()]
    first = parts[0].split('\n')[0]
    title = H.unescape(re.sub(r'<[^>]+>', '', first)).strip().rstrip('.').strip()
    rest_first = '\n'.join(parts[0].split('\n')[1:]).strip()
    body = ([rest_first] if rest_first else []) + parts[1:]
    body = [p for p in body if re.sub(r'<[^>]+>|\s', '', p)]
    paras = ['<p>' + p.replace('\n', '<br>') + '</p>' for p in body]
    return title, '\n'.join(paras), tags


def main(raw_path, img_dir):
    raw = json.load(open(raw_path))
    posts = json.load(open(DATA)) if os.path.exists(DATA) else []
    have = {p['id'] for p in posts}
    slugs = {p['slug'] for p in posts}
    os.makedirs(IMG, exist_ok=True)
    for n in sorted(raw, key=int):
        num = int(n)
        if num in SKIP or num in have:
            continue
        v = raw[n]
        if len(re.sub(r'<[^>]+>', '', v['html'])) < 300:
            continue
        title, body, tags = clean(v['html'])
        rubric = 'put' if num <= 196 else next((TAG_RUBRIC[t] for t in tags if t in TAG_RUBRIC), 'zabugor')
        slug = slugify(title)
        while slug in slugs:
            slug += '-2'
        slugs.add(slug)
        photos = []
        for k in range(1, len(v['photos']) + 1):
            src = os.path.join(img_dir, f'{num}-{k}.jpg')
            if not os.path.exists(src):
                continue
            im = Image.open(src).convert('RGB')
            if im.width > 1200:
                im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
            name = f'{num}-{k}.jpg'
            im.save(os.path.join(IMG, name), quality=82, optimize=True, progressive=True)
            photos.append({'src': f'/img/posts/{name}', 'w': im.width, 'h': im.height})
        posts.append({'id': num, 'date': v['date'], 'title': title, 'slug': slug, 'rubric': rubric,
                      'tags': tags, 'html': body, 'photos': photos, 'video': v['video'] > 0})
    posts.sort(key=lambda p: p['id'])
    json.dump(posts, open(DATA, 'w'), ensure_ascii=False, indent=1)
    print(len(posts), 'постов в', DATA)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
