# Aadhaar Census Fallacy Analysis

## Project Overview

This project analyzes Aadhaar enrolment and biometric update data to evaluate how Aadhaar service demand deviates from population-based assumptions (the "Census Fallacy"). By combining demographic, enrolment, and biometric datasets provided by UIDAI, the analysis identifies high-demand service hubs, under-utilized infrastructure, and priority districts for intervention. The project implements a **Demand–Saturate–Predict (DSP) Framework** to generate actionable insights for resource allocation.

---

## Datasets

- **National datasets**  
  Located in `api_data_aadhar_demographic/`, `api_data_aadhar_enrolment/`, `api_data_aadhar_biometric/`.  
  These contain Aadhaar data for all states and districts in India.

- **Coimbatore datasets**  
  Located in `coimbatore_datasets/`. Contains demographic, enrolment, and biometric data specific to Coimbatore. Used only by `coimbatore.py`.

---

## Scripts

- **all.py**  
  Processes all national datasets to perform full-scale analysis and generate priority intervention scores for every state and district.

- **district.py**  
  Processes district-level(only coimbatore) datasets only. Useful for focused, single-district analysis.

---

## Usage Instructions

1. Ensure datasets are in the correct directories as outlined above.
2. Install Python dependencies:
```bash
pip install pandas matplotlib seaborn
```
## Run the Scripts

```bash
python all.py          # Used National Mock-synthetic Data
python district.py     # District-level analysis
```

## Output

CSV summaries: Enrolment ratios, biometric ratios, priority scores.
Visualizations: Scatter plots, bar charts, and heatmaps highlighting high-priority intervention zones.    
Project_Report.pdf: Full documentation of methodology, analysis, and insights.
