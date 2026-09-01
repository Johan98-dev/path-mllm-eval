# -*- coding: utf-8 -*-
import os
import re

html_path = "reports/index.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Title
title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
print("Title:", title_match.group(1) if title_match else "No title")

# 2. KPI Cards
print("\n=== 1. KPI CARDS ===")
kpi_blocks = re.findall(r'<div class="kpi-card".*?<div class="kpi-label">(.*?)</div>\s*<div class="kpi-value">(.*?)</div>\s*<div class="kpi-sub">(.*?)</div>', content, re.DOTALL)
for l, v, s in kpi_blocks:
    print(f"  * {l.strip()}: {v.strip()} [{s.strip()}]")

# 3. Filter Buttons
print("\n=== 2. FILTER BUTTONS ===")
buttons = re.findall(r'<button class="filter-btn[^"]*"\s+onclick="filterCategory\(\'([^\']+)\',\s*this\)">([^<]+)</button>', content)
for cat, label in buttons:
    print(f"  * Filter: '{cat}' -> Label: '{label}'")

# 4. Table Rows
print("\n=== 3. TABLE ROWS ===")
row_pattern = re.compile(r'<tr class="dataset-row" data-category="([^"]+)" data-access="([^"]+)">\s*<td[^>]*>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>', re.DOTALL)

rows = row_pattern.findall(content)
print(f"Total rows matched: {len(rows)}")

cat_counts = {}
for idx, (cat, access, c_num, c_name, c_repo, c_task, c_rec, c_mod, c_stor, c_acc, c_rep) in enumerate(rows, 1):
    num_txt = re.sub(r'<[^>]+>', '', c_num).strip()
    name_txt = re.findall(r'<div[^>]*font-weight:\s*bold[^>]*>([^<]+)</div>', c_name)
    name_str = name_txt[0].strip() if name_txt else "Unknown"
    
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    badge_match = re.search(r'<span class="badge ([^"]+)"[^>]*>([^<]+)</span>', c_task)
    badge_cls = badge_match.group(1) if badge_match else "no-class"
    badge_txt = badge_match.group(2) if badge_match else "no-badge"
    
    task_match = re.search(r'<div[^>]*font-weight:\s*600[^>]*>([^<]+)</div>', c_task)
    task_str = task_match.group(1).strip() if task_match else ""
    
    rec_match = re.search(r'<div[^>]*font-weight:\s*bold[^>]*>([^<]+)</div>', c_rec)
    rec_str = rec_match.group(1).strip() if rec_match else ""
    
    link_match = re.search(r'href="([^"]+)"', c_rep)
    link_href = link_match.group(1) if link_match else "no-link"
    link_exists = os.path.exists(os.path.join("reports", link_href))
    
    print(f"\n[#{num_txt}] {name_str}")
    print(f"   Category: '{cat}' | Badge text: '{badge_txt}' | Badge class: 'badge {badge_cls}'")
    print(f"   Task: {task_str}")
    print(f"   Records: {rec_str}")
    print(f"   Report file: {link_href} (Exists on disk: {link_exists})")

print("\n=== 4. SUMMARY OF CATEGORIES IN ROWS ===")
for cat, cnt in cat_counts.items():
    print(f"  * '{cat}': {cnt} datasets")

# 5. Badge CSS Classes
print("\n=== 5. BADGE CSS DEFINITIONS ===")
badge_classes = re.findall(r'\.badge-([a-zA-Z0-9_-]+)\s*\{([^}]+)\}', content)
for b_name, b_rules in badge_classes:
    print(f"  .badge-{b_name}: {b_rules.strip()}")
