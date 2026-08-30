import pandas as pd
import numpy as np
import re
import random

# Load data
df = pd.read_csv('data/naukri_com-job_sample.csv')
payrate = df['payrate']

total_rows = len(payrate)
non_null = payrate.notnull().sum()
pct_missing = (total_rows - non_null) / total_rows * 100

print(f"Total Rows: {total_rows}")
print(f"Non-null Rows: {non_null}")
print(f"Missing %: {pct_missing:.2f}%")

# Unique formats and examples
unique_vals = payrate.dropna().unique()
print(f"\nNumber of unique raw values: {len(unique_vals)}")
print("\nRandom 25 distinct examples:")
random.seed(42)
examples = random.sample(list(unique_vals), min(25, len(unique_vals)))
for ex in examples:
    print(f" - {ex}")

# Categorizing patterns
patterns = {
    'Not Disclosed / Blank': 0,
    'Range in Numbers (e.g. 1,00,000 - 2,00,000)': 0,
    'Range in Lacs (e.g. 3-5 Lacs)': 0,
    'Rupee Symbol / INR prefix': 0,
    'Negotiable / Best in Industry': 0,
    'Other Text / Unknown': 0
}

def categorize(val):
    if pd.isna(val) or 'not disclosed' in str(val).lower() or str(val).strip() == '':
        return 'Not Disclosed / Blank'
    
    val_lower = str(val).lower()
    
    if 'negotiable' in val_lower or 'best' in val_lower or 'industry standard' in val_lower or 'commensurate' in val_lower:
        return 'Negotiable / Best in Industry'
        
    if 'inr' in val_lower or '₹' in val_lower or 'rs' in val_lower:
        return 'Rupee Symbol / INR prefix'
        
    if 'lacs' in val_lower or 'lakh' in val_lower:
        return 'Range in Lacs (e.g. 3-5 Lacs)'
        
    # Check for basic number range format (e.g., 100000 - 200000)
    if re.search(r'\d+[\s,]*[a-zA-Z\s]*\-\s*\d+', val_lower):
        return 'Range in Numbers (e.g. 1,00,000 - 2,00,000)'
        
    return 'Other Text / Unknown'

cats = payrate.apply(categorize).value_counts()
print("\nFormat Patterns Breakdown:")
for cat, count in cats.items():
    print(f" - {cat}: {count} ({count/total_rows*100:.2f}%)")

# Attempt to parse
def parse_salary(val):
    if pd.isna(val) or 'not disclosed' in str(val).lower():
        return np.nan, np.nan
        
    val = str(val).lower()
    
    # Extract all numbers (handling commas)
    val_clean = val.replace(',', '')
    nums = re.findall(r'[\d\.]+', val_clean)
    
    if len(nums) == 0:
        return np.nan, np.nan
        
    try:
        nums = [float(n) for n in nums]
    except:
        return np.nan, np.nan
        
    # Convert lacs to actual numbers
    if 'lac' in val or 'lakh' in val or 'pa' in val:
        # Sometimes it says 3,00,000 PA but already actual numbers
        # If nums are small (e.g. < 100), assume they are in Lakhs
        nums = [n * 100000 if n < 100 else n for n in nums]
        
    if len(nums) == 1:
        return nums[0], nums[0]
    elif len(nums) >= 2:
        return min(nums[:2]), max(nums[:2])
    
    return np.nan, np.nan

df['parsed_min'], df['parsed_max'] = zip(*payrate.apply(parse_salary))

parsed_count = df['parsed_min'].notnull().sum()
print(f"\nSuccessfully parsed rows: {parsed_count} ({parsed_count/total_rows*100:.2f}%)")
print(f"Unparseable / Dropped rows: {total_rows - parsed_count} ({(total_rows - parsed_count)/total_rows*100:.2f}%)")

print("\nExamples of unparseable raw values (that are not 'Not Disclosed'):")
unparseable = df[df['parsed_min'].isnull() & df['payrate'].notnull()]
unp_sample = unparseable[~unparseable['payrate'].str.lower().str.contains('not disclosed')]['payrate'].head(10).tolist()
for u in unp_sample:
    print(f" - {u}")

print("\nSanity Check on Parsed Data (Max Salary column):")
print(df['parsed_max'].describe(percentiles=[.05, .25, .5, .75, .95]).apply(lambda x: format(x, 'f')))

print("\nPotential Outliers (parsed_max < 10,000):")
print(df[df['parsed_max'] < 10000][['payrate', 'parsed_min', 'parsed_max']].head(5))

print("\nPotential Outliers (parsed_max > 1,00,00,000 (1 Crore)):")
print(df[df['parsed_max'] > 10000000][['payrate', 'parsed_min', 'parsed_max']].head(5))

