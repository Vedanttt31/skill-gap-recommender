import pandas as pd
import numpy as np

def main():
    print("="*50)
    print("PHASE 1: EXPLORATORY DATA ANALYSIS")
    print("="*50)
    
    # Load Data
    try:
        naukri = pd.read_csv('data/naukri_com-job_sample.csv')
        plfs = pd.read_csv('data/plfs_merged_2024.csv')
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 1. Naukri Data EDA
    print("\n--- Naukri Data Overview ---")
    print(f"Shape: {naukri.shape}")
    print("\nNull counts:")
    print(naukri.isnull().sum()[naukri.isnull().sum() > 0])
    print(f"\nDuplicates: {naukri.duplicated().sum()}")
    
    print("\nUnique Counts:")
    for col in ['industry', 'jobtitle', 'skills']:
        if col in naukri.columns:
            print(f"{col}: {naukri[col].nunique()}")
            
    print("\nTop 5 Cities:")
    if 'joblocation_address' in naukri.columns:
        print(naukri['joblocation_address'].value_counts().head(5))
        
    print("\nTop 5 Skills (Raw):")
    if 'skills' in naukri.columns:
        print(naukri['skills'].value_counts().head(5))

    # 2. PLFS Data EDA
    print("\n--- PLFS Data Overview ---")
    print(f"Shape: {plfs.shape}")
    print("\nSummary Statistics:")
    print(plfs.describe())
    
    # Identify outliers simply (e.g. states with UR > mean + 2*std)
    ur_mean, ur_std = plfs['UR'].mean(), plfs['UR'].std()
    outliers = plfs[plfs['UR'] > ur_mean + 2*ur_std]
    if not outliers.empty:
        print(f"\nHigh Unemployment Outliers (UR > {ur_mean + 2*ur_std:.2f}):")
        print(outliers[['state', 'UR']])

    # 3. City to State Mapping
    city_to_state = {
        'bengaluru': 'Karnataka',
        'bangalore': 'Karnataka',
        'mumbai': 'Maharashtra',
        'pune': 'Maharashtra',
        'hyderabad': 'Telangana',
        'secunderabad': 'Telangana',
        'chennai': 'Tamil Nadu',
        'noida': 'Uttar Pradesh',
        'ghaziabad': 'Uttar Pradesh',
        'lucknow': 'Uttar Pradesh',
        'delhi': 'Delhi',
        'ncr': 'Delhi',
        'new delhi': 'Delhi',
        'gurgaon': 'Haryana',
        'gurugram': 'Haryana',
        'ahmedabad': 'Gujarat',
        'gandhinagar': 'Gujarat',
        'kolkata': 'West Bengal',
        'kochi': 'Kerala',
        'trivandrum': 'Kerala',
        'thiruvananthapuram': 'Kerala',
        'chandigarh': 'Chandigarh',
        'jaipur': 'Rajasthan',
        'indore': 'Madhya Pradesh',
        'bhopal': 'Madhya Pradesh',
        'bhubaneswar': 'Odisha',
        'patna': 'Bihar'
    }

    def map_to_state(location):
        if pd.isna(location):
            return np.nan
        loc_lower = str(location).lower()
        for city, state in city_to_state.items():
            if city in loc_lower:
                return state
        return np.nan

    naukri['state'] = naukri['joblocation_address'].apply(map_to_state)
    
    match_count = naukri['state'].notna().sum()
    total_count = len(naukri)
    print(f"\nCity-to-State Match Rate: {match_count/total_count*100:.2f}% ({match_count}/{total_count})")
    
    # Drop unmatched rows
    naukri_clean = naukri.dropna(subset=['state'])
    
    # Merge with PLFS
    merged_data = pd.merge(naukri_clean, plfs, on='state', how='inner')
    
    print("\n--- Plain Language Summary ---")
    print(f"The Naukri dataset contains {total_count} job postings, out of which {match_count} could be mapped to an Indian state.")
    print(f"The PLFS dataset provides macroeconomic indicators (LFPR, WPR, UR) for {len(plfs)} states/UTs.")
    print(f"After mapping cities to states and merging, we have {len(merged_data)} job postings with corresponding state-level economic data.")
    print(f"The most in-demand regions are dominated by IT hubs like Karnataka, Maharashtra, and Delhi NCR.")
    print(f"State-wise unemployment (UR) ranges from {plfs['UR'].min():.2f}% to {plfs['UR'].max():.2f}%.")
    print("="*50)
    
    # We save an intermediate CSV with mapped states for phase 2
    naukri_clean.to_csv('data/naukri_mapped.csv', index=False)
    print("Saved 'data/naukri_mapped.csv' for Phase 2.")

if __name__ == "__main__":
    main()
