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
DT Project/
├── 00_combine_job_data.py       # Combines raw data into single job dataset
├── 01_eda.py                    # Exploratory data analysis
├── 02_feature_engineering.py    # Builds the finalized feature dataset
├── 02b_skill_normalization.py   # Normalizes hyper-specific skills
├── 03_model_clustering.py       # ML clustering for jobs/skills
├── 04_model_recommender.py      # Base recommendation logic
├── 05_model_predictive.py       # Trains PyTorch MLP model
├── streamlit_app.py             # Main Streamlit web application
├── requirements.txt             # Python dependencies
├── data/                        # Processed datasets (raw datasets excluded)
└── models/                      # Trained models & embeddings
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
1. `python 00_combine_job_data.py` (Produces `combined_job_postings.csv`)
2. `python 01_eda.py`
3. `python 02_feature_engineering.py` (Produces `naukri_mapped.csv` and `naukri_features.csv`)
4. `python 02b_skill_normalization.py`
5. `python 03_model_clustering.py`
6. `python 04_model_recommender.py`
7. `python 05_model_predictive.py`

Excluded files (added to `.gitignore`):
- `data/indian-job-market-dataset-2025.xlsx`
- `data/naukri_com-job_sample.csv`
- `data/combined_job_postings.csv`
- `data/naukri_mapped.csv`
