with open("02_feature_engineering.py", "r") as f:
    content = f.read()

import re

# We will replace `is_valid_skill` and `clean_skills`
old_logic = re.search(r'def is_valid_skill\(s\):.*?return cleaned_skills', content, re.DOTALL).group(0)

new_logic = """
from collections import defaultdict

def is_valid_skill(s):
    # Age patterns
    if re.search(r'\d+\+?\s*(yrs?|years?)?\s*age\b', s) or re.search(r'\bage\s*\d+', s):
        return False
    # Salary patterns
    if re.search(r'\d+.*(lpa|lacs|lakh|ctc|per annum|p\.a\.|₹|rs\.?|rupees)', s):
        return False
    # Shift / Availability
    if re.search(r'\b(24/7|24x7|night shift|day shift|rotational shift|work from home|wfh)\b', s):
        return False
    # Experience / Duration
    if re.search(r'\d+[\-\s]?\d*\s*(yrs?|years?)\s*(of\s*)?.*experience', s):
        return False
    if re.search(r'(year|yrs?)\s+(of\s+)?experience|years?\s+in|yrs?\s+in|banking experience', s):
        return False
    # Purely numeric codes
    if re.match(r'^\d+$', s):
        return False
    if re.match(r'^[\d\s&]+$', s):
        return False
    if re.match(r'^(1040s?|1065|1099.*)$', s):
        return False
    # Vague generic terms
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
    s = re.sub(r'(preferred|required|must have|mandatory)\.?$', '', s).strip()
    s = s.rstrip('.')
    return s.strip()

# We need to process the dataframe directly to build the canonical map
def process_skills(df):
    canonical_map = defaultdict(list)
    
    # 1. First pass filtering and normalization mapping
    for skill_str in df['skills'].dropna():
        skills = str(skill_str).lower().split(',')
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
                canonical_map[key].append(s)
                
    best_phrasing = {}
    for key, variants in canonical_map.items():
        if not key: continue
        counts = pd.Series(variants).value_counts()
        best_phrasing[key] = counts.index[0]
        
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
                    res.append(best_phrasing[key])
        return list(set(res)) # return unique
        
    df['skills_list'] = df['skills'].apply(apply_clean)
    return df

# We override the main function call to use process_skills
"""

content = content.replace(old_logic, new_logic.strip())

# We also need to remove df['skills_list'] = df['skills'].apply(clean_skills) in main()
content = content.replace("naukri['skills_list'] = naukri['skills'].apply(clean_skills)", "naukri = process_skills(naukri)")

with open("02_feature_engineering.py", "w") as f:
    f.write(content)
