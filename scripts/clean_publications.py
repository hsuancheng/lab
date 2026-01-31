import json

json_path = 'src/content/publications.json'

with open(json_path, 'r') as f:
    pubs = json.load(f)

print(f"Original count: {len(pubs)}")

# 1. Update the specific paper
target_title_frag = "Transcriptional dynamics of CD8+ T-cell exhaustion"
updated_count = 0
for p in pubs:
    if target_title_frag.lower() in p['title'].lower():
        if p['year'] != 2025:
            print(f"Updating year for: {p['title']}")
            p['year'] = 2025
            updated_count += 1

if updated_count == 0:
    print("WARNING: Target paper not found or already 2025.")

# 2. Remove year 0
clean_pubs = [p for p in pubs if p['year'] != 0]

# Sort again just in case
clean_pubs.sort(key=lambda x: x['year'], reverse=True)

print(f"Final count: {len(clean_pubs)}")
print(f"Removed {len(pubs) - len(clean_pubs)} year-0 items.")

with open(json_path, 'w') as f:
    json.dump(clean_pubs, f, indent=2, ensure_ascii=False)
