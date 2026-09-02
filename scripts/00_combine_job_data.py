import pandas as pd
import numpy as np

def main():
    print("="*50)
    print("PHASE 1: COMBINE JOB DATA")
    print("="*50)
    
    # 1. Load Data
    try:
        df_old = pd.read_csv('data/naukri_com-job_sample.csv')
        print(f"Loaded old dataset: {len(df_old)} rows")
    except Exception as e:
        print(f"Error loading old dataset: {e}")
        return
        
    try:
        # Load the new excel file
        df_new = pd.read_excel('data/indian-job-market-dataset-2025.xlsx')
        print(f"Loaded new dataset: {len(df_new)} rows")
    except Exception as e:
        print(f"Error loading new dataset: {e}")
        return

    # 2. Map old dataset to common schema
    # Schema: job_title, location, skills, experience, min_salary, max_salary, source, industry
    old_mapped = pd.DataFrame({
        'job_title': df_old['jobtitle'] if 'jobtitle' in df_old.columns else np.nan,
        'location': df_old['joblocation_address'] if 'joblocation_address' in df_old.columns else np.nan,
        'skills': df_old['skills'] if 'skills' in df_old.columns else np.nan,
        'experience': df_old['experience'] if 'experience' in df_old.columns else np.nan,
        'min_salary': np.nan, # leave null as requested
        'max_salary': np.nan, # leave null as requested
        'source': 'naukri_2017',
        'industry': df_old['industry'] if 'industry' in df_old.columns else np.nan
    })
    
    # 3. Map new dataset to common schema
    new_mapped = pd.DataFrame({
        'job_title': df_new['title'] if 'title' in df_new.columns else np.nan,
        'location': df_new['location'] if 'location' in df_new.columns else np.nan,
        'skills': df_new['tagsAndSkills'] if 'tagsAndSkills' in df_new.columns else np.nan,
        'experience': df_new['experience'] if 'experience' in df_new.columns else np.nan,
        'min_salary': df_new['minimumSalary'] if 'minimumSalary' in df_new.columns else np.nan,
        'max_salary': df_new['maximumSalary'] if 'maximumSalary' in df_new.columns else np.nan,
        'source': 'naukri_2025',
        'industry': np.nan # new dataset doesn't have an explicit industry column
    })
    
    # Clean up any potential 'Not Disclosed' or string garbage in min_salary/max_salary
    new_mapped['min_salary'] = pd.to_numeric(new_mapped['min_salary'], errors='coerce')
    new_mapped['max_salary'] = pd.to_numeric(new_mapped['max_salary'], errors='coerce')
    
    # 4. Concatenate and Deduplicate
    combined = pd.concat([old_mapped, new_mapped], ignore_index=True)
    before_count = len(combined)
    
    # Remove exact duplicates across all columns
    combined = combined.drop_duplicates()
    after_count = len(combined)
    
    print(f"\nConcatenated Total Rows: {before_count}")
    print(f"Total Rows after dropping exact duplicates: {after_count}")
    print(f"Dropped {before_count - after_count} exact duplicate rows.")
    
    print("\nRows by Source:")
    print(combined['source'].value_counts())
    
    # 5. Calculate Salary Coverage
    salary_coverage = combined['min_salary'].notna() & combined['max_salary'].notna()
    coverage_pct = (salary_coverage.sum() / after_count) * 100
    
    print(f"\nSalary Data Coverage: {coverage_pct:.1f}% ({salary_coverage.sum()} rows have clean numeric min/max salaries)")
    
    # 6. Check Role Diversity
    print("\nRole Diversity Check (Top 10 job titles):")
    print(combined['job_title'].value_counts().head(10))
    
    # 7. Save to CSV
    combined.to_csv('data/combined_job_postings.csv', index=False)
    print("\nSaved combined dataset to data/combined_job_postings.csv")
    print("="*50)

if __name__ == "__main__":
    main()
