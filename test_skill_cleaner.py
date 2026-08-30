import pandas as pd
import re
import random

# Global sets to track kept and removed skills for the report
raw_skills_set = set()
kept_skills_set = set()
removed_skills_set = set()

def is_valid_skill(s):
    # Rule 1: Purely numeric or starts with digits and under 5 chars or no substantial alphabetic content
    if re.match(r'^\d+[a-z]*$', s):
        return False
        
    # Rule 2: Contains "#" hashtag symbol anywhere
    if '#' in s:
        return False
        
    # Rule 3: Starts with a bullet/list-style character
    if re.match(r'^[-.*]|^[0-9]+[.)]', s):
        return False
        
    # Rule 4: Full sentence (more than 6 words)
    if len(s.split()) > 6:
        return False
        
    # Rule 5: Explicit experience/duration language
    if re.search(r'(year|yrs?)\s+(of\s+)?experience|years?\s+in|yrs?\s+in|banking experience', s):
        return False
        
    # Rule 6: Common education-level patterns
    edu_patterns = {'10th', '12th', '10th pass', '12th pass', 'graduate', 'post graduate', 'undergraduate', '10+2'}
    if s in edu_patterns:
        return False
        
    # Additional edge cases from user examples
    if "english and tamil" in s or "verbal communication" in s or "written english" in s:
        # maybe handled by word count, but let's let generic rules catch it
        pass
        
    return True

def clean_skills(skill_str):
    if pd.isna(skill_str):
        return []
    skills = str(skill_str).lower().split(',')
    cleaned_skills = []
    for s in skills:
        s = s.strip()
        if not s: continue
        raw_skills_set.add(s)
        
        s = re.sub(r'\b(ms excel|microsoft excel)\b', 'excel', s)
        s = re.sub(r'\b(ms office|microsoft office)\b', 'office', s)
        s = re.sub(r'\b(machine learning)\b', 'ml', s)
        s = re.sub(r'\b(artificial intelligence)\b', 'ai', s)
        s = re.sub(r'\b(amazon web services)\b', 'aws', s)
        s = re.sub(r'\b(google cloud platform)\b', 'gcp', s)
        
        if len(s) > 1 and is_valid_skill(s):
            cleaned_skills.append(s)
            kept_skills_set.add(s)
        else:
            removed_skills_set.add(s)
            
    return cleaned_skills

# Test on data
naukri = pd.read_csv('data/combined_job_postings.csv')
naukri['skills_list'] = naukri['skills'].apply(clean_skills)

print(f"Original Unique Skills: {len(raw_skills_set)}")
print(f"Cleaned Unique Skills: {len(kept_skills_set)}")
print(f"Removed Unique Skills: {len(removed_skills_set)}")

print("\n--- 30 Random Kept Skills ---")
for s in random.sample(list(kept_skills_set), min(30, len(kept_skills_set))):
    print(s)
    
print("\n--- 20 Random Removed Skills ---")
for s in random.sample(list(removed_skills_set), min(20, len(removed_skills_set))):
    print(s)
