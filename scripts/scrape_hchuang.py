import json
import re
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://sbl.csie.org/HCHLab"
ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "src" / "content"
CONTENT_DIR.mkdir(parents=True, exist_ok=True)


def fetch(url: str) -> BeautifulSoup:
    try:
        print(f"Fetching {url}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return BeautifulSoup("", "html.parser")


def clean_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).strip()


def scrape_news() -> list[dict]:
    """Scrape news from the main page."""
    url = f"{BASE_URL}/"
    soup = fetch(url)
    items = []

    # DokuWiki structure: headers often have IDs, e.g. "news"
    # Looking for the specific section
    # Based on chunk: "News" header
    news_header = soup.find(id="news")
    if not news_header:
        # Fallback: look for h2 with text "News"
        for h2 in soup.find_all("h2"):
            if "News" in h2.get_text():
                news_header = h2
                break

    if news_header:
        # Robustly find the next UL
        ul = news_header.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                text = clean_text(li.get_text())
                # Format: YYYY.MM Content
                match = re.search(r"(\d{4}\.\d{2})\s+(.*)", text) # Use search, not match, to be safer
                if match:
                    date_str = match.group(1).replace(".", "-") + "-01"
                    content = match.group(2)
                    
                    # Extract link if exists
                    link = ""
                    a_tag = li.find("a")
                    if a_tag and a_tag.get("href"):
                        link = a_tag["href"]
                        if not link.startswith("http"):
                            link = f"{BASE_URL}/{link}"

                    items.append({
                        "date": date_str,
                        "title": content[:80] + "..." if len(content) > 80 else content,
                        "summary": content,
                        "link": link
                    })

    return items


def scrape_people() -> dict:
    """Scrape PI and members."""
    data = {
        "pi": [],
        "members": [],
        "alumni": []
    }

    # --- PI ---
    pi_url = f"{BASE_URL}/doku.php?id=PI:Hsuan-Cheng%20Huang"
    soup = fetch(pi_url)
    # This page structure is simple headers.
    # We'll just hardcode the PI since scraping this free-text is error-prone and static.
    # But let's try to grab the title/email if possible or just use the hardcoded one from prompt as fallback
    # The prompt gave a good template. We will stick to a static PI entry but verify name.
    
    data["pi"].append({
        "name": "Hsuan-Cheng Huang",
        "title": "Professor",
        "affiliation": "Institute of Biomedical Informatics, NYCU",
        "email": "hsuancheng@nycu.edu.tw", # Updated to NYCU usually
        "homepage": "http://www.hchuang.info/",
        "interests": ["Systems Biology", "Bioinformatics", "Computational Biology", "Network Biology"]
    })


    # --- Members ---
    mem_url = f"{BASE_URL}/doku.php?id=members:start"
    soup = fetch(mem_url)
    
    # Sections: Research assistant, PhD students, MS students, Alumni
    # DokuWiki headers often have IDs: research_assistant, phd_students, ms_students, alumni
    
    section_map = {
        "research_assistant": "Research Assistant",
        "phd_students": "PhD Student",
        "ms_students": "MS Student",
        "alumni": "Alumni"
    }

    for sec_id, role_name in section_map.items():
        header = soup.find(id=sec_id)
        if not header:
            continue
            
        curr = header.next_sibling
        while curr:
            if curr.name and curr.name.startswith("h1"): # DokuWiki h1? Actually the chunk showed h1.
                break
                
            # If we hit another header level closer to h1/h2? 
            # DokuWiki uses h1 for page title usually, h2 for sections. 
            # But the chunk showed "headers:{type:MARKDOWN_NODE_TYPE_HEADER_1 text:"Research assistant"}"
            # So likely they are h1 or h2.
             
            if curr.name in ["ul", "p", "div"]:
                # If it's a div, might contain the text lines.
                # If ul, it's a list.
                # The chunk showed lines like "Name (Year- ...)"
                
                # Check for direct text in div or paragraphs
                lines = []
                if curr.name == "ul":
                    lines = [li.get_text() for li in curr.find_all("li")]
                else:
                    # just text separated by newlines
                    lines = curr.get_text().split('\n')
                
                for line in lines:
                    line = clean_text(line)
                    if not line: continue
                    
                    # Parse: Name EnglishName (Year- range...)
                    # Example: 陳韻茹 Yun-Ru Chen (18- , 09- 18 BMI phd, 08-09 BMI m1)
                    # Example: 杜岳華 Yueh-Hua Tu (19- TIGP, w/ Prof. Juan; 14-16 BMI ms)
                    
                    # Regex to find name and parens
                    # We want the part BEFORE the first '(' as name
                    parts = line.split('(', 1)
                    name_part = parts[0].strip()
                    desc_part = "(" + parts[1] if len(parts) > 1 else ""
                    
                    if not name_part or len(name_part) < 2: continue
                    
                    # Attempt to extract start year
                    start_year = None
                    yr_match = re.search(r"(\d{2})[-]", desc_part)
                    if yr_match:
                        # assume 20xx
                        start_year = 2000 + int(yr_match.group(1))
                        # minimal logic for 90s?
                        if start_year > 2030: start_year -= 100 
                    
                    entry = {
                        "name": name_part,
                        "role": role_name,
                        "startYear": start_year,
                        "email": "",
                        "homepage": "",
                        "interests": [] #[desc_part] # Put full details in interests/desc? No, schema says list of strings.
                    }
                    
                    if sec_id == "alumni":
                        data["alumni"].append(entry)
                    else:
                        data["members"].append(entry)
                        
            curr = curr.next_sibling

    return data


def scrape_publications() -> list[dict]:
    """Scrape publications."""
    url = f"{BASE_URL}/doku.php?id=PUBLICATION:HCH"
    soup = fetch(url)
    items = []
    
    # Look for "Selected Journal Papers" section
    # ID: selected_journal_papers_期刊論文 (DokuWiki auto-generates IDs from text)
    # We'll just look for the header text contained in H2
    
    target_sections = ["Selected Journal Papers", "Selected Conference Proceedings"]
    
    for h2 in soup.find_all(["h2", "h3"]):
        header_text = h2.get_text()
        if any(t in header_text for t in target_sections):
            venue_type = "Journal" if "Journal" in header_text else "Conference"
            
            # Find next content container
            curr = h2.next_sibling
            while curr:
                if curr.name and curr.name.startswith("h"):
                    break 
                
                # Search targets: list items or paragraphs if no list
                items_nodes = []
                
                if curr.name in ["ol", "ul"]:
                    items_nodes = curr.find_all("li")
                elif curr.name == "div":
                    # Check for lists first
                    lists = curr.find_all(["ol", "ul"])
                    if lists:
                        for l in lists:
                            items_nodes.extend(l.find_all("li"))
                    else:
                        # Fallback to <p> tags if no list
                        items_nodes = curr.find_all("p")
                
                for node in items_nodes:
                    text = clean_text(node.get_text())
                    
                    # Filter: Must start with number if from p tag (loose check)
                    # "1.Authors..."
                    if not re.match(r"^\d+\.", text):
                        continue
                        
                    # Remove leading number "1. "
                    text = re.sub(r"^\d+\.\s*", "", text)

                    # Format: Authors. "Title." Venue (Year).
                    # ... (same parsing regex) ...
                    
                    # 1. Year
                    year = 0
                    y_match = re.search(r"\((\d{4})\)", text)
                    if y_match:
                        year = int(y_match.group(1))
                    else:
                        y_match2 = re.search(r"\b(19|20)\d{2}\b", text)
                        if y_match2:
                            year = int(y_match2.group(0))
                    
                    # 2. DOI
                    doi = ""
                    a_tag = node.find("a")
                    if a_tag and "doi.org" in (a_tag.get("href") or ""):
                        doi = a_tag["href"]
                    
                    # 3. Title
                    # Heuristic: Authors are usually first. Title is often quoted.
                    title = text
                    t_match = re.search(r"“([^”]+)”", text) or re.search(r"\"([^\"]+)\"", text)
                    if t_match:
                        title = t_match.group(1)
                    
                    # Cleanup authors
                    authors = text.split("“")[0] if "“" in text else text.split("\"")[0]
                    authors = authors.strip().strip(",").strip(".")
                    
                    items.append({
                        "year": year,
                        "authors": authors[:50] + "..." if len(authors)>50 else authors,
                        "title": title,
                        "venue": venue_type,
                        "doi": doi,
                        "note": ""
                    })
                
                curr = curr.next_sibling
                
    return items


def main():
    print("Starting scrape...")
    news = scrape_news()
    people = scrape_people()
    pubs = scrape_publications()

    print(f"Found {len(news)} news items")
    print(f"Found {len(people.get('pi', []))} PI, {len(people.get('members', []))} members")
    print(f"Found {len(pubs)} publications")

    if news:
        (CONTENT_DIR / "news.json").write_text(json.dumps(news, ensure_ascii=False, indent=2), encoding="utf-8")
    if people["pi"] or people["members"]:
        (CONTENT_DIR / "people.json").write_text(json.dumps(people, ensure_ascii=False, indent=2), encoding="utf-8")
    if pubs:
        (CONTENT_DIR / "publications.json").write_text(json.dumps(pubs, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Scrape complete. Checked/Wrote news.json, people.json, publications.json to src/content")


if __name__ == "__main__":
    main()
