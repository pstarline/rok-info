"""Static site builder for rokadviser.kr (GitHub Pages, serves /docs).
Usage: python3 tools/build.py
Posts: src/posts/YYYY-MM-DD-slug.md with front matter:
---
title: ...
description: ... (검색 결과에 보일 120자 내외 요약)
tags: 태그1, 태그2
category: 휴가·외출 | 입대 준비 | 보직·병과 | 급여·혜택 | 생활 꿀팁 | 전역 준비
---
본문 (Markdown). 이미지는 static/img/<slug>/1.jpg … 로 두고 본문에 ![설명](1.jpg) 처럼 파일명만 쓴다.
"""
import os, re, json, html, shutil, datetime
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, 'site.json'), encoding='utf-8'))
SITE, URL = CFG['name'], CFG['url'].rstrip('/')
OUT = os.path.join(ROOT, 'docs')
esc = lambda s: html.escape(s, quote=True)

def load_posts():
    posts = []
    d = os.path.join(ROOT, 'src', 'posts')
    for f in sorted(os.listdir(d)):
        if not f.endswith('.md'): continue
        raw = open(os.path.join(d, f), encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
        meta = dict(re.findall(r'^(\w+):\s*(.*)$', m.group(1), re.M))
        date, slug = f[:10], f[11:-3]
        body = m.group(2)
        body = re.sub(r'!\[([^\]]*)\]\(([^/)]+)\)', lambda x: f'![{x.group(1)}](/img/{slug}/{x.group(2)})', body)
        h = markdown.markdown(body, extensions=['tables', 'sane_lists'])
        h = h.replace('<img ', '<img loading="lazy" decoding="async" width="1080" height="1080" ')
        h = re.sub(r'<table>', '<div class="tbl"><table>', h).replace('</table>', '</table></div>')
        imgs = re.findall(r'/img/' + re.escape(slug) + r'/[^"\s)]+', h)
        text = re.sub(r'<[^>]+>', '', h)
        posts.append(dict(slug=slug, date=date, title=meta['title'], desc=meta.get('description', ''),
                          tags=[t.strip() for t in meta.get('tags', '').split(',') if t.strip()],
                          cat=meta.get('category', '군생활 정보'), html=h,
                          cover=imgs[0] if imgs else '', mins=max(1, round(len(re.sub(r'\s', '', text)) / 500))))
    return sorted(posts, key=lambda p: p['date'], reverse=True)

CSS = '''
:root{--bg:#f6f5f0;--paper:#ffffff;--ink:#1d2419;--mute:#5f6858;--line:#dfe0d6;--olive:#4b5d3a;--olive-ink:#ffffff;--sand:#c9a227;--link:#3c5a2a;
--f:"Noto Sans KR",-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;--d:"Black Han Sans","Noto Sans KR",sans-serif}
@media (prefers-color-scheme:dark){:root{--bg:#141712;--paper:#1c201a;--ink:#e8eae2;--mute:#a0a897;--line:#2e3329;--olive:#7d9a62;--olive-ink:#10140d;--sand:#e0bc4a;--link:#a9c98e;color-scheme:dark}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.8 var(--f);word-break:keep-all;overflow-wrap:anywhere}
a{color:var(--link)}
img{max-width:100%;height:auto}
.wrap{max-width:760px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
header.top{background:var(--olive);color:var(--olive-ink)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-block:14px}
.logo{color:inherit;text-decoration:none;font:400 24px var(--d);letter-spacing:.5px}
.logo small{font:500 12px var(--f);opacity:.85;margin-left:8px;letter-spacing:0}
nav{white-space:nowrap}
nav a{color:inherit;text-decoration:none;font-size:14px;font-weight:500;margin-left:14px;opacity:.9}
.hero{padding-block:36px 20px}
.hero h1{font:400 34px/1.3 var(--d);margin:0 0 8px;text-wrap:balance}
.hero p{margin:0;color:var(--mute)}
.list{display:grid;gap:14px;padding-block:8px 40px}
.card{display:grid;grid-template-columns:120px 1fr;gap:16px;background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:12px;text-decoration:none;color:inherit}
.card img{width:120px;height:120px;object-fit:cover;border-radius:8px;display:block}
.card h2{font-size:18px;line-height:1.45;margin:2px 0 6px;text-wrap:balance}
.card p{margin:0;font-size:14px;color:var(--mute);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.meta{font-size:13px;color:var(--mute);display:flex;gap:10px;flex-wrap:wrap}
.cat{color:var(--olive);font-weight:700}
article{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:28px max(18px,4vw);margin-block:24px 40px}
article h1{font:400 30px/1.35 var(--d);margin:8px 0 12px;text-wrap:balance}
article h2{font-size:23px;line-height:1.4;margin:44px 0 12px;padding-top:6px;border-top:3px solid var(--sand);display:inline-block}
article h3{font-size:19px;margin:28px 0 8px}
article p{margin:0 0 16px}
article ul,article ol{padding-left:22px;margin:0 0 18px}
article li{margin-bottom:6px}
article img{display:block;border-radius:10px;margin:22px auto;border:1px solid var(--line)}
article blockquote{margin:20px 0;padding:14px 18px;background:var(--bg);border-left:4px solid var(--olive);border-radius:0 8px 8px 0}
article blockquote p:last-child{margin:0}
.tbl{overflow-x:auto;margin:0 0 20px}
table{border-collapse:collapse;width:100%;font-size:15px;min-width:420px}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--bg)}
.tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:28px}
.tags span{font-size:13px;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:3px 12px;color:var(--mute)}
.ad{margin:24px 0;min-height:0}
footer{border-top:1px solid var(--line);color:var(--mute);font-size:13px}
footer .wrap{padding-block:24px 40px}
@media (max-width:520px){.logo small{display:none}.card{grid-template-columns:88px 1fr}.card img{width:88px;height:88px}.hero h1{font-size:28px}article h1{font-size:25px}}
'''

def page(title, desc, path, body, og_img='', jsonld=None, typ='website'):
    canon = URL + path
    ads = ''
    if CFG.get('adsense_client'):
        ads = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc(CFG["adsense_client"])}" crossorigin="anonymous"></script>'
    verify = ''.join(f'<meta name="{esc(k)}" content="{esc(v)}">' for k, v in CFG.get('verify', {}).items())
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''
    og = f'<meta property="og:image" content="{URL}{og_img}">' if og_img else ''
    full_title = title if title == SITE else f'{title} | {SITE}'
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(full_title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}"><link rel="alternate" type="application/rss+xml" title="{esc(SITE)}" href="{URL}/feed.xml">
<meta property="og:type" content="{typ}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:site_name" content="{esc(SITE)}"><meta property="og:locale" content="ko_KR">{og}
<meta name="twitter:card" content="summary_large_image">{verify}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>{CSS}</style>{ads}{ld}</head><body>
<header class="top"><div class="wrap"><a class="logo" href="/">{esc(CFG["logo"])}<small>{esc(CFG["tagline"])}</small></a>
<nav><a href="/">전체 글</a><a href="/about/">소개</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">© {datetime.date.today().year} {esc(SITE)} · 현역 운전병이 직접 정리하는 군생활 정보. 제도와 기준은 부대·시기에 따라 다를 수 있으니 소속 부대에 꼭 확인하세요.</div></footer>
</body></html>'''

def write(path, s):
    p = os.path.join(OUT, path.lstrip('/'))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def build():
    posts = load_posts()
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    if os.path.isdir(os.path.join(ROOT, 'static')):
        shutil.copytree(os.path.join(ROOT, 'static'), OUT, dirs_exist_ok=True)
    open(os.path.join(OUT, 'CNAME'), 'w').write(CFG['url'].split('//')[1].strip('/') + '\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    ad_slot = ''
    if CFG.get('adsense_client') and CFG.get('adsense_slot'):
        ad_slot = f'<div class="ad"><ins class="adsbygoogle" style="display:block" data-ad-client="{esc(CFG["adsense_client"])}" data-ad-slot="{esc(CFG["adsense_slot"])}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>'
    for p in posts:
        path = f'/posts/{p["slug"]}/'
        body = p['html']
        # 광고: 두 번째 소제목 앞에 1개
        if ad_slot:
            hs = [m.start() for m in re.finditer(r'<h2>', body)]
            if len(hs) >= 2: body = body[:hs[1]] + ad_slot + body[hs[1]:]
        art = f'''<article><div class="meta"><span class="cat">{esc(p["cat"])}</span><time datetime="{p["date"]}">{p["date"].replace("-", ".")}</time><span>{p["mins"]}분 읽기</span></div>
<h1>{esc(p["title"])}</h1>{body}
<div class="tags">{"".join(f"<span>#{esc(t)}</span>" for t in p["tags"])}</div></article>'''
        ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p['title'], "description": p['desc'],
              "datePublished": p['date'], "dateModified": p['date'], "inLanguage": "ko-KR",
              "author": {"@type": "Person", "name": CFG['author']}, "mainEntityOfPage": URL + path,
              **({"image": URL + p['cover']} if p['cover'] else {})}
        write(path + 'index.html', page(p['title'], p['desc'], path, art, p['cover'], ld, 'article'))
    cards = ''.join(f'''<a class="card" href="/posts/{p["slug"]}/">{f'<img src="{p["cover"]}" alt="" loading="lazy" width="120" height="120">' if p["cover"] else '<span></span>'}
<div><div class="meta"><span class="cat">{esc(p["cat"])}</span><span>{p["date"].replace("-", ".")}</span></div><h2>{esc(p["title"])}</h2><p>{esc(p["desc"])}</p></div></a>''' for p in posts)
    hero = f'<section class="hero"><h1>{esc(CFG["headline"])}</h1><p>{esc(CFG["description"])}</p></section>'
    write('/index.html', page(SITE, CFG['description'], '/', hero + f'<div class="list">{cards}</div>'))
    about = open(os.path.join(ROOT, 'src', 'about.md'), encoding='utf-8').read()
    write('/about/index.html', page('소개', CFG['description'], '/about/', f'<article><h1>소개</h1>{markdown.markdown(about)}</article>'))
    write('/404.html', page('페이지를 찾을 수 없어요', CFG['description'], '/404.html', '<article><h1>페이지를 찾을 수 없어요</h1><p><a href="/">처음으로 돌아가기</a></p></article>'))
    urls = [('/', posts[0]['date'] if posts else ''), ('/about/', '')] + [(f'/posts/{p["slug"]}/', p['date']) for p in posts]
    write('/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
          ''.join(f'<url><loc>{URL}{u}</loc>{f"<lastmod>{d}</lastmod>" if d else ""}</url>' for u, d in urls) + '</urlset>\n')
    write('/robots.txt', f'User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
    items = ''.join(f'<item><title>{esc(p["title"])}</title><link>{URL}/posts/{p["slug"]}/</link><guid>{URL}/posts/{p["slug"]}/</guid><pubDate>{datetime.datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900")}</pubDate><description>{esc(p["desc"])}</description></item>' for p in posts[:30])
    write('/feed.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{esc(SITE)}</title><link>{URL}/</link><description>{esc(CFG["description"])}</description><language>ko</language>{items}</channel></rss>\n')
    if CFG.get('adsense_pub'):
        write('/ads.txt', f'google.com, {CFG["adsense_pub"]}, DIRECT, f08c47fec0942fa0\n')
    print(f'built {len(posts)} posts -> docs/')

if __name__ == '__main__':
    build()
