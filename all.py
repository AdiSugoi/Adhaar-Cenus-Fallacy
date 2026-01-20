import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

sns.set_style("whitegrid")
demo_files = glob.glob("/home/adisugoi/Documents/Projects/adhaar/api_data_aadhar_demographic/*.csv")       
enroll_files = glob.glob("/home/adisugoi/Documents/Projects/adhaar/api_data_aadhar_enrolment/*.csv")   
bio_files = glob.glob("/home/adisugoi/Documents/Projects/adhaar/api_data_aadhar_biometric/*.csv")         

def read_combine(files):
    if not files:
        raise ValueError("No CSV files found! Check your file paths.")
    df_list = []
    for f in files:
        df = pd.read_csv(f, parse_dates=['date'], dayfirst=True)
        df.columns = df.columns.str.strip()  # remove leading/trailing spaces
        df_list.append(df)
    df_combined = pd.concat(df_list, ignore_index=True)
    return df_combined

df_demo = read_combine(demo_files)
df_enroll = read_combine(enroll_files)
df_bio = read_combine(bio_files)

# Standardize column names


# Demo
df_demo.rename(columns={
    'demo_age_5_17': 'demo_age_5_17',
    'demo_age_17_': 'demo_age_17_'
}, inplace=True)

# Enroll
df_enroll.rename(columns={
    'age_0_5': 'age_0_5',
    'age_5_17': 'age_5_17',
    'age_18_greater': 'age_18_greater'
}, inplace=True)

# Biometric
df_bio.rename(columns={
    'bio_age_5_17': 'bio_age_5_17',
    'bio_age_17_': 'bio_age_17_'
}, inplace=True)

# Aggregate by State + District + Pincode


def aggregate_dataset(df, value_cols, agg_name):
    # Ensure all required columns exist
    for col in value_cols:
        if col not in df.columns:
            df[col] = 0
    df_agg = df.groupby(['state','district','pincode'])[value_cols].sum().reset_index()
    
    # Prevent double prefix
    new_cols = []
    for col in value_cols:
        if not col.startswith(agg_name + "_"):
            new_cols.append(f"{agg_name}_{col}")
        else:
            new_cols.append(col)
    df_agg.columns = ['state','district','pincode'] + new_cols
    return df_agg

df_demo_agg = aggregate_dataset(df_demo, ['demo_age_5_17','demo_age_17_'], 'demo')
df_enroll_agg = aggregate_dataset(df_enroll, ['age_0_5','age_5_17','age_18_greater'], 'enroll')
df_bio_agg = aggregate_dataset(df_bio, ['bio_age_5_17','bio_age_17_'], 'bio')

# Merge datasets

df_all = df_demo_agg.merge(df_enroll_agg, on=['state','district','pincode'], how='outer') \
                    .merge(df_bio_agg, on=['state','district','pincode'], how='outer')

# Fill missing values with 0
df_all.fillna(0, inplace=True)

# Rename aggregated columns for clarity
df_all.rename(columns={
    'demo_demo_age_5_17': 'demo_age_5_17',
    'demo_demo_age_17_': 'demo_age_17_',
    'bio_bio_age_5_17': 'bio_age_5_17',
    'bio_bio_age_17_': 'bio_age_17_'
}, inplace=True)


# Calculate ratios

df_all['enroll_ratio_5_17'] = df_all['enroll_age_5_17'] / df_all['demo_age_5_17'].replace(0,1)
df_all['enroll_ratio_17_plus'] = df_all['enroll_age_18_greater'] / df_all['demo_age_17_'].replace(0,1)

df_all['bio_ratio_5_17'] = df_all['bio_age_5_17'] / df_all['demo_age_5_17'].replace(0,1)
df_all['bio_ratio_17_plus'] = df_all['bio_age_17_'] / df_all['demo_age_17_'].replace(0,1)

# Identify anomalies / hotspots

low_enroll_5_17 = df_all[df_all['enroll_ratio_5_17'] < 0.2].sort_values('enroll_ratio_5_17')
low_enroll_17_plus = df_all[df_all['enroll_ratio_17_plus'] < 0.2].sort_values('enroll_ratio_17_plus')

high_bio_5_17 = df_all[df_all['bio_ratio_5_17'] > 0.8].sort_values('bio_ratio_5_17', ascending=False)
high_bio_17_plus = df_all[df_all['bio_ratio_17_plus'] > 0.8].sort_values('bio_ratio_17_plus', ascending=False)


# Top 20 districts by enrollment ratio 
plt.figure(figsize=(12,6))
sns.barplot(
    data=df_all.sort_values('enroll_ratio_5_17', ascending=False).head(20),
    x='district', y='enroll_ratio_5_17', hue='state'
)
plt.xticks(rotation=45, ha='right')
plt.title('Top 20 Districts by Enrollment Ratio')
plt.ylabel('Enrollment Ratio')
plt.xlabel('District')
plt.legend(title='State')
plt.tight_layout()
plt.show()

# Population vs enrollment scatter (5-17)
plt.figure(figsize=(8,6))
plt.scatter(df_all['demo_age_5_17'], df_all['enroll_age_5_17'], alpha=0.6)
plt.title('Enrollment vs Population (Age 5-17)')
plt.xlabel('Population Age 5-17')
plt.ylabel('Enrolled Age 5-17')
plt.grid(True)
plt.tight_layout()
plt.show()

# Top 10 districts stacked bar by age-group enrollment
df_all_plot = df_all[['district','enroll_age_0_5','enroll_age_5_17','enroll_age_18_greater']].sort_values('enroll_age_5_17', ascending=False).head(10)
df_all_plot.set_index('district')[['enroll_age_0_5','enroll_age_5_17','enroll_age_18_greater']].plot(kind='bar', stacked=True, figsize=(12,6))
plt.title('Top 10 Districts Enrollment by Age Group')
plt.ylabel('Number of Enrollments')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

## save results
output_folder = "analysis_results"
os.makedirs(output_folder, exist_ok=True)

low_enroll_5_17.to_csv(os.path.join(output_folder, "low_enroll_5_17.csv"), index=False)
high_bio_17_plus.to_csv(os.path.join(output_folder, "high_bio_17_plus.csv"), index=False)
df_all.to_csv(os.path.join(output_folder, "aadhaar_analysis_summary.csv"), index=False)

print("Analysis complete. Summary and anomaly files saved in 'analysis_results' folder.")
# Create a Priority Score (0 to 100)
# This weights Enrollment Gaps and Update Demand
df_all['priority_score'] = (
    (df_all['enroll_ratio_5_17'] * 0.4) + 
    (df_all['bio_ratio_17_plus'] * 0.6)
).rank(pct=True) * 100

# Identify Top 5 "Intervention Districts"
intervention_list = df_all.sort_values('priority_score', ascending=False).head(5)
print("Districts requiring immediate resource deployment:")
print(intervention_list[['state', 'district', 'priority_score']])

plt.figure(figsize=(10, 8))
corr = df_all[['demo_age_5_17', 'enroll_age_5_17', 'bio_age_5_17', 'enroll_ratio_5_17']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Analysis of Aadhaar Lifecycle Metrics')
plt.show()