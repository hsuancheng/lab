"""Clean the scraped news entries and append recent items documented in sources/cv.tex."""
import json
import re

PATH = 'src/content/news.json'
news = json.load(open(PATH, encoding='utf-8'))

url_re = re.compile(r'\(?\s*(https?://[^\s)]+)\s*\)?')
fixed = 0
for item in news:
    title, summary = item['title'].strip(), item['summary'].strip()

    # The scraper truncated titles at ~60 chars; the summary holds the full text.
    if title.endswith(('...', '…')) and summary.startswith(title.rstrip('.… ')[:20]):
        title = summary
        fixed += 1

    # Pull any URL out of the display text and into the link field.
    for field in (title, summary):
        m = url_re.search(field)
        if m and not item.get('link'):
            item['link'] = m.group(1)
    title = url_re.sub('', title).strip().rstrip('(（ ').strip()
    summary = url_re.sub('', summary).strip().rstrip('(（ ').strip()

    # 37 of 49 entries repeat the title verbatim as the summary.
    item['title'] = title
    item['summary'] = '' if summary == title else summary

print(f'un-truncated {fixed} titles')

# Recent items, each traceable to a dated line in sources/cv.tex.
recent = [
    ("2026-08-01",
     "Hsuan-Cheng Huang joins National Taiwan University as Professor in the Department of "
     "Computer Science and Information Engineering."),
    ("2025-11-08",
     "Best Poster Awards at the 2025 Multiomics and Precision Medicine Joint Conference, Taipei "
     "(Guan-Ting Chen, Ching-Ya Lin, and H.-S. Yang)."),
    ("2025-08-01",
     "New NSTC project begins: “Spatially-Informed Single-Cell Network Biology — A Multimodal "
     "Computational Framework for Drug Discovery and Cell Fate Engineering” (2025/8–2028/7)."),
    ("2025-05-02",
     "Best Poster Award at the 2025 International Symposium on Evolutionary Genomics and "
     "Bioinformatics (ISEGB2025), Tainan (H.-M. Tseng)."),
    ("2025-03-22",
     "Best Poster Award at the 39th Joint Annual Conference of Biomedical Sciences, Taipei (P.-Y. Chen)."),
    ("2024-11-09",
     "Best Poster Awards at the 2024 Multiomics and Precision Medicine Joint Conference, Taipei "
     "(Kuan-Yi Hsieh, C.-M. Chang, and P.-Y. Chen)."),
    ("2024-03-28",
     "Hsuan-Cheng Huang chaired the 2024 SMBE Regional Meeting in Taiwan: Evolutionary Genomics "
     "& Bioinformatics, Taipei."),
    ("2023-06-29",
     "Best Poster Award at the International Symposium on Evolutionary Genomics and Bioinformatics "
     "2023, chaired by Hsuan-Cheng Huang (Bing-Shiun Tsai)."),
]

existing = {(x['date'], x['title']) for x in news}
added = 0
for date, title in recent:
    if (date, title) not in existing:
        news.append({"date": date, "title": title, "summary": "", "link": ""})
        added += 1

news.sort(key=lambda x: x['date'], reverse=True)
with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(news, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'added {added} recent items; total {len(news)}; newest {news[0]["date"]}')
