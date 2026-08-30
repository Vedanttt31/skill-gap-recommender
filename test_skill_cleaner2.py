import pandas as pd
import re
import random
from collections import defaultdict

raw_skills_set = set()
kept_skills_set = set()
removed_skills_set = set()

def is_valid_skill(s):
    # Rule 1: Age patterns
    if re.search(r'\d+\+?\s*(yrs?|years?)?\s*age\b', s) or re.search(r'\bage\s*\d+', s):
        return False
        
    # Rule 2: Salary patterns
    if re.search(r'\d+.*(lpa|lacs|lakh|ctc|per annum|p\.a\.|₹|rs\.?|rupees)', s):
        return False
        
    # Rule 3: Shift / Availability
    if re.search(r'\b(24/7|24x7|night shift|day shift|rotational shift|work from home|wfh)\b', s):
        return False
        
    # Rule 4: Experience / Duration
    if re.search(r'\d+[\-\s]?\d*\s*(yrs?|years?)\s*(of\s*)?.*experience', s):
        return False
    # Catch any 'years experience' variants anywhere
    if re.search(r'(year|yrs?)\s+(of\s+)?experience|years?\s+in|yrs?\s+in|banking experience', s):
        return False
        
    # Rule 6: Purely numeric codes with no real words
    # Remove digit-only strings (already handled by len(s)>1 if it's a single digit, but e.g. "1040")
    if re.match(r'^\d+$', s):
        return False
    # Remove things like "45001& 50001" or "1040s"
    if re.match(r'^[\d\s&]+$', s):
        return False
    if re.match(r'^(1040s?|1065|1099.*)$', s):
        return False
        
    # Rule 8: Vague generic terms
    vague_terms = {'agreement', 'agreement for sale', 'required', 'preferred', 'must have', 'mandatory'}
    if s in vague_terms:
        return False
        
    # Previous rules
    if '#' in s:
        return False
    if re.match(r'^[-.*]|^[0-9]+[.)]', s):
        return False
    if len(s.split()) > 6:
        return False
    edu_patterns = {'10th', '12th', '10th pass', '12th pass', 'graduate', 'post graduate', 'undergraduate', '10+2'}
    if s in edu_patterns:
        return False
        
    return True

def clean_skill_string(s):
    s = s.strip()
    # Rule 5: Trailing punctuation / requirement words
    s = re.sub(r'(preferred|required|must have|mandatory)\.?$', '', s).strip()
    s = s.rstrip('.')
    return s.strip()

def process_skills(df):
    cleaned_all = []
    canonical_map = defaultdict(list)
    
    # 1. First pass filtering and normalization mapping
    for skill_str in df['skills'].dropna():
        skills = str(skill_str).lower().split(',')
        for s in skills:
            s = clean_skill_string(s)
            if not s: continue
            raw_skills_set.add(s)
            
            s = re.sub(r'\b(ms excel|microsoft excel)\b', 'excel', s)
            s = re.sub(r'\b(ms office|microsoft office)\b', 'office', s)
            s = re.sub(r'\b(machine learning)\b', 'ml', s)
            s = re.sub(r'\b(artificial intelligence)\b', 'ai', s)
            s = re.sub(r'\b(amazon web services)\b', 'aws', s)
            s = re.sub(r'\b(google cloud platform)\b', 'gcp', s)
            
            if len(s) > 1 and is_valid_skill(s):
                # Canonical key: strip all non-alphanumeric except spaces
                key = re.sub(r'[^a-z0-9\s]', '', s)
                # compress spaces
                key = re.sub(r'\s+', ' ', key).strip()
                canonical_map[key].append(s)
                
    # Determine best phrasing for each key
    best_phrasing = {}
    for key, variants in canonical_map.items():
        if not key: continue
        # Most frequent variant wins
        counts = pd.Series(variants).value_counts()
        best_phrasing[key] = counts.index[0]
        
    # 2. Second pass to apply mapping
    def apply_clean(skill_str):
        if pd.isna(skill_str): return []
        skills = str(skill_str).lower().split(',')
        res = []
        for s in skills:
            s = clean_skill_string(s)
            if not s: continue
            s = re.sub(r'\b(ms excel|microsoft excel)\b', 'excel', s)
            s = re.sub(r'\b(ms office|microsoft office)\b', 'office', s)
            s = re.sub(r'\b(machine learning)\b', 'ml', s)
            s = re.sub(r'\b(artificial intelligence)\b', 'ai', s)
            s = re.sub(r'\b(amazon web services)\b', 'aws', s)
            s = re.sub(r'\b(google cloud platform)\b', 'gcp', s)
            if len(s) > 1 and is_valid_skill(s):
                key = re.sub(r'[^a-z0-9\s]', '', s)
                key = re.sub(r'\s+', ' ', key).strip()
                if key in best_phrasing:
                    mapped = best_phrasing[key]
                    res.append(mapped)
                    kept_skills_set.add(mapped)
            else:
                removed_skills_set.add(s)
        return res
        
    df['skills_list'] = df['skills'].apply(apply_clean)
    return df

naukri = pd.read_csv('data/combined_job_postings.csv')
naukri = process_skills(naukri)

print(f"Original Unique Skills: {len(raw_skills_set)}")
print(f"Cleaned Unique Skills: {len(kept_skills_set)}")
print(f"Removed Unique Skills (Invalid): {len(removed_skills_set)}")
print(f"Merged Variants (Near-Duplicates Removed): {len([s for s in raw_skills_set if s not in removed_skills_set and s not in kept_skills_set])}")

print("\n--- Testing Specific Bad Examples ---")
bad_examples = ["27+ age", "25 lpa.", "24/7", "24x7", "2 years experience", "2-3 yrs of hfm experience", "agreement", "agreement for sale"]
for bad in bad_examples:
    bad_clean = clean_skill_string(bad)
    print(f"'{bad}' -> Valid? {is_valid_skill(bad_clean)}")

print("\n--- Testing Valid Technical Skills with Numbers ---")
valid_examples = ["5 axis", "4g lte", "5g new radio", "2/4 wheeler", "power bi", "office 365", "2d & 3d animation"]
for good in valid_examples:
    good_clean = clean_skill_string(good)
    print(f"'{good}' -> Valid? {is_valid_skill(good_clean)}")

print("\n--- 30 Random Kept Skills ---")
for s in random.sample(list(kept_skills_set), min(30, len(kept_skills_set))):
    print(s)

print("\n--- 30 Random Removed Skills ---")
for s in random.sample(list(removed_skills_set), min(30, len(removed_skills_set))):
    print(s)
