import sys
import os
# We will import streamlit_app and call get_roadmap_content and generate_pdf_report
try:
    import streamlit_app as app
except Exception as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

print("App imported successfully.")
