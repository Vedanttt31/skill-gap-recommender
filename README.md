# Skill Gap Recommender 🎯

An AI-powered skill recommendation engine that analyzes real-time job market data to help you target the most valuable skills for your career.

Live Streamlit App: [Coming Soon - Placeholder URL]

## Project Overview

This tool combines job posting data across India to extract the exact skills employers are looking for right now. It features:
- A personalized skill recommendation engine powered by PyTorch
- Interactive skill roadmaps with estimated learning time and employability uplift
- Real-time job market dashboard
- Downloadable custom PDF reports

## Folder Structure

```
skill-gap-recommender/
├── data/                        # Processed datasets (raw datasets excluded)
├── models/                      # Trained ML models & embeddings
├── scripts/                     # Core data pipeline and model training scripts
│   ├── 00_combine_job_data.py   
│   ├── 01_eda.py                
│   ├── 02_feature_engineering.py
│   ├── 02b_skill_normalization.py
│   ├── 03_model_clustering.py   
│   ├── 04_model_recommender.py  
│   └── 05_model_predictive.py   
├── streamlit_app.py             # Main Streamlit web application
├── requirements.txt             # Python dependencies
├── .gitignore
├── .streamlit/
│   └── config.toml              # Streamlit theme configuration
└── README.md
```

## How to Run the Application Locally

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Regenerating Raw Data

To keep the repository lightweight for Streamlit Community Cloud (and under GitHub's 100MB file limit), the massive raw source files were intentionally excluded from this repo. The app runs perfectly on the processed `data/naukri_features.csv` dataset.

If you want to re-run the entire pipeline from scratch, you will need to add the following raw datasets to the `data/` folder:
- `indian-job-market-dataset-2025.xlsx` (~30MB)
- `naukri_com-job_sample.csv` (~50MB)

Then run the pipeline scripts sequentially:
1. `python scripts/00_combine_job_data.py` (Produces `combined_job_postings.csv`)
2. `python scripts/01_eda.py`
3. `python scripts/02_feature_engineering.py` (Produces `naukri_mapped.csv` and `naukri_features.csv`)
4. `python scripts/02b_skill_normalization.py`
5. `python scripts/03_model_clustering.py`
6. `python scripts/04_model_recommender.py`
7. `python scripts/05_model_predictive.py`

Excluded files (added to `.gitignore`):
- `data/indian-job-market-dataset-2025.xlsx`
- `data/naukri_com-job_sample.csv`
- `data/combined_job_postings.csv`
- `data/naukri_mapped.csv`
