import pandas as pd
import os
from us_state_abbrev import abbrev_to_us_state
import seaborn as sns
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
census_file_path = os.path.join(current_dir, 'acs2017_county_data.csv')
cases_file_path = os.path.join(current_dir, 'covid_confirmed_usafacts.csv')
deaths_file_path = os.path.join(current_dir, 'covid_deaths_usafacts.csv')

census_df = pd.read_csv(census_file_path)
cases_df = pd.read_csv(cases_file_path)
deaths_df = pd.read_csv(deaths_file_path)

# Remove the extra space at the end of county names in cases_df and deaths_df
cases_df['County Name'] = cases_df['County Name'].str.rstrip()
deaths_df['County Name'] = deaths_df['County Name'].str.rstrip()

def convert_state_abbrev_to_full(state_abbrev):
    if state_abbrev in abbrev_to_us_state:
        return abbrev_to_us_state[state_abbrev]
    return state_abbrev 

# Apply the conversion to the State column in both DataFrames
print("Converting state abbreviations to full state names...")
cases_df['State'] = cases_df['State'].apply(convert_state_abbrev_to_full)
deaths_df['State'] = deaths_df['State'].apply(convert_state_abbrev_to_full)

print("State conversion complete.")
print(f"Unique states in cases_df: {cases_df['State'].nunique()}")
print(f"Unique states in deaths_df: {deaths_df['State'].nunique()}")

# Remove "Statewide Unallocated" entries from both datasets
cases_df = cases_df[cases_df['County Name'] != 'Statewide Unallocated']
deaths_df = deaths_df[deaths_df['County Name'] != 'Statewide Unallocated']

print(f"Removed 'Statewide Unallocated' entries from cases_df and deaths_df")
print(f"cases_df shape after removal: {cases_df.shape}")
print(f"deaths_df shape after removal: {deaths_df.shape}")

# Trim census_df to only include the specified columns
census_columns = ['County', 'State', 'TotalPop', 'IncomePerCap', 'Poverty', 'Unemployment']
census_df = census_df[census_columns]

# Find the latest date column in cases_df and deaths_df
latest_cases_date = max([col for col in cases_df.columns if col.startswith('20')], default=None)
latest_deaths_date = max([col for col in deaths_df.columns if col.startswith('20')], default=None)

# Rename the date columns to 'Cases' and 'Deaths' respectively
cases_df = cases_df[['County Name', 'State', latest_cases_date]]
cases_df = cases_df.rename(columns={latest_cases_date: 'Cases'})
deaths_df = deaths_df[['County Name', 'State', latest_deaths_date]]
deaths_df = deaths_df.rename(columns={latest_deaths_date: 'Deaths'})

# Create a "key" column in each DataFrame by concatenating county and state
census_df['key'] = census_df['County'] + '_' + census_df['State']
cases_df['key'] = cases_df['County Name'] + '_' + cases_df['State']
deaths_df['key'] = deaths_df['County Name'] + '_' + deaths_df['State']

# Set the "key" column as the index for each DataFrame
census_df.set_index('key', inplace=True)
cases_df.set_index('key', inplace=True)
deaths_df.set_index('key', inplace=True)

# Ensure index is string type to prevent .str accessor errors
cases_df.index = cases_df.index.astype(str)
deaths_df.index = deaths_df.index.astype(str)
census_df.index = census_df.index.astype(str)

# Display information about the DataFrames with new indices
print("\nCensus DataFrame with 'key' index:")
print(f"Shape: {census_df.shape}")
print("First few rows:")
print(census_df.head())

print("\nCases DataFrame with 'key' index:")
print(f"Shape: {cases_df.shape}")
print("First few rows:")
print(cases_df.head(3))
print(cases_df.columns.values.tolist())

print("\nDeaths DataFrame with 'key' index:")
print(f"Shape: {deaths_df.shape}")
print("First few rows:")
print(deaths_df.head(3))
print(deaths_df.columns.values.tolist())

covid_df = cases_df.join(deaths_df, how='outer', lsuffix='_cases', rsuffix='_deaths')
join_df = covid_df.join(census_df, how='inner', lsuffix='_covid', rsuffix='_census')

cases_col = 'Cases'  
deaths_col = 'Deaths'  
pop_col = 'TotalPop'  

# Check if the expected column names exist, otherwise find them with suffixes
if cases_col not in join_df.columns:
    cases_col = next((col for col in join_df.columns if col.startswith('Cases_')), None)
if deaths_col not in join_df.columns:
    deaths_col = next((col for col in join_df.columns if col.startswith('Deaths_')), None)
if pop_col not in join_df.columns:
    pop_col = next((col for col in join_df.columns if col.startswith('TotalPop')), None)

# Add new columns for per capita calculations using the correct column names
join_df['CasesPerCap'] = join_df[cases_col] / join_df[pop_col] * 100000  
join_df['DeathsPerCap'] = join_df[deaths_col] / join_df[pop_col] * 100000  

# Displaying information about the joined DataFrame
print("\nJoined DataFrame Info:")
print(f"Shape: {join_df.shape}")
print(f"Columns: {join_df.columns.tolist()}")
print("\nFirst few rows of the joined DataFrame:")
print(join_df.head())

print("\nConstructing correlation matrix for numeric columns...")
numeric_columns = join_df.select_dtypes(include=['number']).columns
correlation_matrix = join_df[numeric_columns].corr()

print("\nCorrelation Matrix:")
print(correlation_matrix)

# Create a larger figure with more white space around the plot
plt.figure(figsize=(12, 10))  
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidth=0.5)
plt.title('Correlation Matrix Heatmap', fontsize=16, pad=20)  # Add padding to the title

# Adjust layout to ensure all elements are visible
plt.tight_layout(pad=3.0)  

# Save the figure with high resolution before showing it
plt.savefig(os.path.join(current_dir, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
plt.show()

print("\nFormatted Correlation Matrix (rounded to 2 decimal places):")
pd.set_option('display.precision', 2)  
print(correlation_matrix.round(2))

print("\n" + "="*50)
print("SEARCHING FOR 'WASHINGTON COUNTY' IN DATASETS")
print("="*50)

# Search for Washington County in the datasets (with fixed string index)
washington_cases = cases_df[cases_df.index.str.startswith('Washington County_')]
print(f"\nFound {len(washington_cases)} entries for 'Washington County' in COVID cases data:")

washington_deaths = deaths_df[deaths_df.index.str.startswith('Washington County_')]
print(f"Found {len(washington_deaths)} entries for 'Washington County' in COVID deaths data:")

total_washington_counties = len(washington_cases) + len(washington_deaths)
print(f"\nTotal matches for 'Washington County' across all datasets: {total_washington_counties}\n")

