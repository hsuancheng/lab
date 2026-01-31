import re
import json
import io

def parse_latex_publications(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find \item \mypub{Title}{Authors}{Journal}
    # Handling nested braces is tricky with regex, so we might need a somewhat greedy approach or balanced brace parsing.
    # Given the structure, we can try to find `\item` and then the macro.
    
    # Let's try to split by \item and then parse each block.
    # The file starts with \begin{enumerate} and ends with \end{enumerate} for the list.
    
    start_idx = content.find(r'\begin{enumerate}')
    end_idx = content.find(r'\end{enumerate}')
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find enumerate block")
        return []

    items_block = content[start_idx:end_idx]
    # Split by \item, but ignore the first empty part
    raw_items = re.split(r'\\item', items_block)[1:]
    
    publications = []
    
    for raw_item in raw_items:
        # cleanup newlines
        raw_item = raw_item.strip()
        
        # We look for the pattern: \macro {Title} {Authors} {Journal}
        # Macros are \mypub, \mybpub, \newpub, \pub
        
        # Simple stack-based brace parser to extract 3 arguments
        args = []
        depth = 0
        current_arg = []
        in_arg = False
        arg_count = 0
        
        # Find start of first brace
        scan_idx = 0
        
        # Skip macro name
        macro_match = re.match(r'\s*\\[a-zA-Z]+\s*', raw_item)
        if macro_match:
            scan_idx = macro_match.end()
        else:
            # Maybe just braces directly?
            pass
            
        while scan_idx < len(raw_item) and arg_count < 3:
            char = raw_item[scan_idx]
            
            if char == '{':
                if depth == 0:
                    in_arg = True
                else:
                    current_arg.append(char)
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    in_arg = False
                    args.append("".join(current_arg).strip())
                    current_arg = []
                    arg_count += 1
                else:
                    current_arg.append(char)
            elif in_arg:
                current_arg.append(char)
            
            scan_idx += 1
            
        if len(args) < 3:
            print(f"Skipping malformed item: {raw_item[:50]}...")
            continue
            
        title_tex = args[0]
        authors_tex = args[1]
        journal_tex = args[2]
        
        # Extract extra info like IF and DOI from the rest of the string
        rest_of_item = raw_item[scan_idx:]
        
        # Parse Title
        title = clean_tex(title_tex)
        
        # Parse Authors
        authors = clean_tex(authors_tex)
        
        # Parse Journal and Year
        journal_info = clean_tex(journal_tex)
        year = 0
        # Try to find year in (YYYY) or bold YYYY or just YYYY
        year_match = re.search(r'\((\d{4})\)', journal_info)
        if year_match:
            year = int(year_match.group(1))
        else:
            # Fallback check in rest_of_item if extracted from journal string failed
             year_match = re.search(r'\((\d{4})\)', rest_of_item)
             if year_match:
                 year = int(year_match.group(1))

        # Check for accepted papers (year = current year or 0, maybe denote as "In Press")
        if "accepted" in journal_info.lower() or "in press" in journal_info.lower():
            if year == 0:
                year = 2025 # Assumption for "accepted" current papers based on context
        
        # Parse DOI from comments or text
        # Look for doi: ... in the rest_of_item
        doi = ""
        doi_match = re.search(r'doi:\s*(\S+)', rest_of_item, re.IGNORECASE)
        if doi_match:
            doi = doi_match.group(1).rstrip('}') # occasional cleanup
            
        # Parse Impact Factor
        note = ""
        if_match = re.search(r'IF:\s*([\d\.]+)', rest_of_item)
        if if_match:
            note = f"IF: {if_match.group(1)}"
            
        publications.append({
            "year": year,
            "title": title,
            "authors": authors,
            "venue": journal_info,
            "doi": doi,
            "note": note
        })
        
    return publications

def clean_tex(text):
    # Remove tex commands
    text = re.sub(r'\\bf\s+', '', text)
    text = re.sub(r'\\it\s+', '', text)
    text = re.sub(r'\\textsl', '', text)
    text = re.sub(r'[\{\}]', '', text) # Remove braces
    text = re.sub(r'\$\^(\*|\d+)\$', '', text) # Remove math superscripts like $^*$
    text = re.sub(r'\^(\*|\d+)', '', text) # Remove superscripts
    text = re.sub(r'\\', '', text) # Remove backslashes
    text = re.sub(r'\s+', ' ', text) # Normalize spaces
    return text.strip()

if __name__ == "__main__":
    latex_file = 'pub-260130.tex'
    json_output = 'src/content/publications.json'
    
    pubs = parse_latex_publications(latex_file)
    
    # Sort by year desc
    pubs.sort(key=lambda x: x['year'], reverse=True)
    
    print(f"Parsed {len(pubs)} publications.")
    
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(pubs, f, indent=2, ensure_ascii=False)
