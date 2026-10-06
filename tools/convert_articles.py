#!/usr/bin/env python3
"""
Converts Astro MDX articles from rainfall-corp-website into Quarto .qmd files
with the exact 2-column layout and right-hand Featured sidebar matching
rainfallhealth.com/post/* (Screenshots 2-4).
Also generates media.qmd (Screenshot 1).
"""

import os
import re
import json
import glob
from datetime import datetime

SRC_DIR = "/Users/kylemcauliffe/code/rainfall-corp-website/src/content/blog"
DEST_DIR = "/Users/kylemcauliffe/stratus/articles"
MEDIA_DIR = "/Users/kylemcauliffe/stratus"

os.makedirs(DEST_DIR, exist_ok=True)

AUTHOR_AVATARS = {
    "Ahmed Qureshi": "/assets/authors/eddie-qureshi.png",
    'Ahmed "Eddie" Qureshi': "/assets/authors/eddie-qureshi.png",
    "Dr. David Shulkin": "/assets/authors/david-shulkin.png",
    "David Shulkin": "/assets/authors/david-shulkin.png",
    "Dr. Hemant Keny": "/assets/authors/hemant-keny.png",
    "Paul Hammer": "/assets/authors/paul-hammer.png",
    "Paul Uhrig": "/assets/authors/paul-uhrig.jpg",
    "Dr. Charlotte Yeh": "/assets/authors/charlotte-yeh.png",
    "Steve Ganyard": "/assets/authors/steve-ganyard.jpg",
    "Mark Adams": "/assets/authors/mark-adams.webp",
    "Dr. Steve Schutzer": "/assets/authors/steve-schutzer.jpg",
    "Dr. Scott Cooper": "/assets/authors/scott-cooper.png",
    "Dr. Sandra Scott": "/assets/authors/sandra-scott.jpg",
    "Cora Han": "/assets/authors/cora-han.png",
    "Cora Han, JD": "/assets/authors/cora-han.png",
    "Rainfall Health": "/assets/rainfall-logo.svg",
}

def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    
    fm_raw = parts[1]
    body = parts[2]
    meta = {}
    
    # Simple YAML key-value extractor
    current_key = None
    list_items = []
    in_list = False
    
    for line in fm_raw.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue
            
        m = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if m:
            if in_list and current_key:
                meta[current_key] = list_items
                in_list = False
                list_items = []
                
            key = m.group(1)
            val = m.group(2).strip()
            current_key = key
            
            if val.startswith("[") and val.endswith("]"):
                # single line list
                items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                meta[key] = items
            elif val.startswith("["):
                in_list = True
                list_items = []
                first_items = [x.strip().strip("'\"") for x in val[1:].split(",") if x.strip()]
                list_items.extend(first_items)
            elif not val:
                # possible multi-line list next
                in_list = True
                list_items = []
            else:
                meta[key] = val.strip("'\"")
        elif in_list:
            if "]" in line_clean:
                before = line_clean.split("]")[0]
                items = [x.strip().strip("'\",") for x in before.split(",") if x.strip().strip("'\",")]
                list_items.extend(items)
                meta[current_key] = list_items
                in_list = False
                list_items = []
            else:
                item = line_clean.lstrip("- ").strip("'\",")
                if item:
                    list_items.append(item)
                    
    if in_list and current_key:
        meta[current_key] = list_items

    return meta, body

def clean_body(body):
    # Remove import statements
    body = re.sub(r"^import\s+.*?;?\s*$", "", body, flags=re.MULTILINE)
    
    # Transistor embed
    def replace_transistor(m):
        m_id = re.search(r'episodeId=["\']([^"\']+)["\']', m.group(0))
        if m_id:
            ep = m_id.group(1)
            return f'<div class="my-4"><iframe width="100%" height="180" frameborder="no" scrolling="no" seamless src="https://share.transistor.fm/e/{ep}"></iframe></div>'
        return ""
    body = re.sub(r"<BlogTransistorEmbed[^>]*/>", replace_transistor, body)
    
    # YouTube embed
    def replace_youtube(m):
        m_id = re.search(r'id=["\']([^"\']+)["\']', m.group(0))
        if m_id:
            yt = m_id.group(1)
            return f'<div class="ratio ratio-16x9 my-4"><iframe src="https://www.youtube.com/embed/{yt}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width:100%; height:400px; border-radius:8px;"></iframe></div>'
        return ""
    body = re.sub(r"<YouTube[^>]*/>", replace_youtube, body)
    
    # BlogTldr
    body = re.sub(r"<BlogTldr>\s*", '<aside class="blog-tldr not-prose"><div class="blog-tldr__label">TL;DR</div><div class="blog-tldr__body">\n', body)
    body = re.sub(r"\s*</BlogTldr>", "\n</div></aside>", body)
    
    # BlogCallout
    def replace_callout(m):
        full = m.group(0)
        label_m = re.search(r'label=["\']([^"\']+)["\']', full)
        variant_m = re.search(r'variant=["\']([^"\']+)["\']', full)
        label = label_m.group(1) if label_m else ""
        variant = variant_m.group(1) if variant_m else "default"
        label_html = f'<div class="blog-callout__label">{label}</div>' if label else ""
        return f'<aside class="blog-callout blog-callout--{variant} not-prose">{label_html}<div class="blog-callout__body">'
    body = re.sub(r"<BlogCallout[^>]*>", replace_callout, body)
    body = re.sub(r"</BlogCallout>", "</div></aside>", body)
    
    # BlogPullQuote
    body = re.sub(r"<BlogPullQuote[^>]*>\s*", '<blockquote class="blog-pull-quote">\n', body)
    body = re.sub(r"\s*</BlogPullQuote>", "\n</blockquote>", body)

    # Normalize image paths
    body = re.sub(r"/images/blog/", "/assets/media/", body)
    body = re.sub(r"/images/about/blog-authors/", "/assets/authors/", body)
    body = re.sub(r"/images/about/leadership/", "/assets/authors/", body)
    
    return body

def format_date(d_str):
    if not d_str:
        return "September 2026"
    try:
        dt = datetime.fromisoformat(str(d_str).split("T")[0])
        return dt.strftime("%B %d, %Y")
    except Exception:
        return str(d_str)

def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*.mdx")))
    articles = []
    
    for f in files:
        slug = os.path.basename(f)[:-4]
        # Skip pure profile cards
        if slug.startswith("advisor-") or slug.startswith("founder-"):
            continue
            
        with open(f, "r", encoding="utf-8") as fp:
            content = fp.read()
            
        meta, raw_body = parse_frontmatter(content)
        cleaned_body = clean_body(raw_body)
        
        title = meta.get("title", slug.replace("-", " ").title())
        desc = meta.get("description", "")
        subtitle = meta.get("subtitle", "")
        author = meta.get("author", "Rainfall Health")
        raw_date = meta.get("publishDate", "2026-09-23")
        display_date = format_date(raw_date)
        raw_img = meta.get("image", "")
        img = raw_img.replace("/images/blog/", "/assets/media/") if raw_img else ""
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        ebook = meta.get("ebookDownload", "")
        blog_group = meta.get("blogGroup", "article")
        
        articles.append({
            "slug": slug,
            "title": title,
            "description": desc,
            "subtitle": subtitle,
            "author": author,
            "publishDate": raw_date,
            "displayDate": display_date,
            "image": img,
            "tags": tags,
            "ebook": ebook,
            "blogGroup": blog_group,
            "body": cleaned_body
        })

    # Sort articles by publishDate descending
    articles.sort(key=lambda x: str(x.get("publishDate", "")), reverse=True)
    
    # Save JSON index for website components
    with open(os.path.join(MEDIA_DIR, "assets", "articles-index.json"), "w", encoding="utf-8") as fp:
        json.dump([{k: v for k, v in a.items() if k != "body"} for a in articles], fp, indent=2)

    # 8 top featured items for sidebar
    featured_pool = [a for a in articles if a["image"]][:8]

    # Generate each article .qmd
    for art in articles:
        slug = art["slug"]
        title = art["title"]
        desc = art["description"]
        subtitle = art["subtitle"]
        author = art["author"]
        display_date = art["displayDate"]
        img = art["image"]
        tags = art["tags"]
        ebook = art["ebook"]
        body = art["body"]
        
        # Parse authors (split by &)
        import html
        author_names = [a.strip() for a in re.split(r"\s*&\s*", author) if a.strip()]
        author_chips = []
        for a_name in author_names:
            av = AUTHOR_AVATARS.get(a_name, "/assets/authors/eddie-qureshi.png")
            author_chips.append(f'<span class="author-chip"><img src="{av}" alt="{html.escape(a_name, quote=True)}" class="author-avatar"> <span>{a_name}</span></span>')
        authors_html = " ".join(author_chips)
        
        clean_tags = [t.strip("[]'\" ") for t in tags if t.strip("[]'\" ")]
        tags_html = " ".join([f'<span class="article-tag-pill">{t}</span>' for t in clean_tags])
        
        ebook_btn = ""
        if ebook:
            ebook_btn = f'''
            <a href="{ebook}" class="btn-download-ebook" target="_blank" rel="noopener noreferrer">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              <span>Download eBook</span>
            </a>
            '''

        # Featured sidebar items (excluding self)
        featured_items = [f for f in featured_pool if f["slug"] != slug][:6]
        sidebar_items_html = []
        for feat in featured_items:
            f_img = feat["image"] or "/assets/media/hip-fracture-home-scott-cooper-banner.jpg"
            sidebar_items_html.append(f'''
              <li>
                <a href="../articles/{feat["slug"]}.html" class="blog-featured__link">
                  <img src="{f_img}" alt="" class="blog-featured__thumb" loading="lazy">
                  <span class="blog-featured__title">{feat["title"]}</span>
                </a>
              </li>
            ''')
        featured_list_html = "\n".join(sidebar_items_html)

        hero_img_html = f'<img src="{img}" alt="{title}" class="article-hero-image">' if img else ""
        subtitle_html = f'<p class="article-subtitle" style="font-size:1.15rem; color:#475569; margin-bottom:1.5rem; line-height:1.6;">{subtitle}</p>' if subtitle else ""

        qmd_content = f'''---
title: {json.dumps(title)}
description: {json.dumps(desc)}
format:
  html:
    page-layout: full
    toc: false
---

```{{=html}}
<div class="blog-shell">
  <div class="blog-article-grid">
    <div class="blog-prose-column">
      <a href="../media.html" class="article-back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Back to Blogs &amp; Media
      </a>

      <header class="mb-8">
        <div class="article-tags">
          {tags_html}
        </div>
        <div class="article-kicker">Media</div>
        <h1 class="article-h1">{title}</h1>
        {subtitle_html}

        <div class="article-byline">
          <div class="byline-authors">
            {authors_html}
          </div>
          <span class="byline-dot">&middot;</span>
          <span class="byline-date">{display_date}</span>

          <div class="article-share-actions">
            <a href="https://www.linkedin.com/sharing/share-offsite/?url=" target="_blank" rel="noopener noreferrer" class="share-btn" aria-label="Share on LinkedIn">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
            </a>
            <a href="https://twitter.com/intent/tweet" target="_blank" rel="noopener noreferrer" class="share-btn" aria-label="Share on X">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            {ebook_btn}
          </div>
        </div>
      </header>

      {hero_img_html}

      <div class="article-body">
```

{body}

```{{=html}}
      </div>
    </div>

    <!-- Sticky Right Featured Sidebar (Screenshots 2-4) -->
    <aside class="blog-featured not-prose" aria-labelledby="blog-featured-heading">
      <h2 id="blog-featured-heading" class="blog-featured__heading">Featured</h2>
      <ul class="blog-featured__list">
        {featured_list_html}
      </ul>
    </aside>
  </div>
</div>
```
'''
        out_path = os.path.join(DEST_DIR, f"{slug}.qmd")
        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(qmd_content)
            
    print(f"Successfully converted {len(articles)} articles into {DEST_DIR}!")

    # Now generate media.qmd (Screenshot 1)
    cards_html = []
    for art in articles:
        bg = art["blogGroup"]
        group_type = "podcast" if "podcast" in bg.lower() or "podcast" in art["title"].lower() else ("report" if "report" in bg.lower() or "cfo" in art["slug"] or "ceo" in art["slug"] else "article")
        f_img = art["image"] or "/assets/media/hip-fracture-home-scott-cooper-banner.jpg"
        cards_html.append(f'''
        <div class="research-card" data-group="{group_type}">
          <a href="articles/{art["slug"]}.html" class="media-card">
            <div class="media-card__image-wrap">
              <img src="{f_img}" alt="{art["title"]}" class="media-card__image" loading="lazy">
            </div>
            <div class="media-card__content">
              <time class="media-card__date">{art["displayDate"]}</time>
              <h3 class="media-card__title">{art["title"]}</h3>
              <p class="media-card__description">{art["description"]}</p>
              <span class="media-card__readmore">
                Read more &rarr;
              </span>
            </div>
          </a>
        </div>
        ''')
        
    grid_content = "\n".join(cards_html)
    
    media_qmd = f'''---
title: "Media & Articles | Rainfall Health"
format:
  html:
    page-layout: full
    toc: false
---

```{{=html}}
<div class="page-container">
  <div class="media-header">
    <h1>Media</h1>
    <p>CMS TEAM eBooks, webinars, and research from Rainfall Health — plus the impact report.</p>
    
    <div class="filter-pills-bar" id="media-filters">
      <button type="button" class="research-filter-pill research-filter-pill--active" data-filter="all">All</button>
      <button type="button" class="research-filter-pill" data-filter="podcast">Podcast</button>
      <button type="button" class="research-filter-pill" data-filter="report">Report</button>
    </div>
  </div>

  <div class="media-cards-grid" id="media-grid">
    {grid_content}
  </div>

  <p id="media-empty" style="display:none; text-align:center; padding:3rem 0; color:#64748b;">
    No articles match this filter.
  </p>
</div>

<script>
  document.addEventListener('DOMContentLoaded', () => {{
    const filterBar = document.getElementById('media-filters');
    const grid = document.getElementById('media-grid');
    const empty = document.getElementById('media-empty');
    if (!filterBar || !grid) return;

    const buttons = filterBar.querySelectorAll('.research-filter-pill');
    const cards = grid.querySelectorAll('.research-card');

    buttons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        buttons.forEach(b => b.classList.remove('research-filter-pill--active'));
        btn.classList.add('research-filter-pill--active');

        const filter = btn.dataset.filter;
        let count = 0;
        cards.forEach(card => {{
          const group = card.dataset.group;
          const show = (filter === 'all' || group === filter);
          card.style.display = show ? 'block' : 'none';
          if (show) count++;
        }});

        if (empty) {{
          empty.style.display = (count === 0) ? 'block' : 'none';
        }}
      }});
    }});
  }});
</script>
```
'''
    with open(os.path.join(MEDIA_DIR, "media.qmd"), "w", encoding="utf-8") as fp:
        fp.write(media_qmd)
        
    print(f"Successfully generated media.qmd at {os.path.join(MEDIA_DIR, 'media.qmd')}!")

if __name__ == "__main__":
    main()
