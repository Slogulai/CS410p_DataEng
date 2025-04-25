import csv
from datetime import datetime
import os
import numpy as np
from scipy.stats import normaltest, skew, kurtosis, shapiro
import matplotlib
matplotlib.use('macosx') 
import matplotlib.pyplot as plt

# This script reads the employee data from the CSV file to allow me to do multiple validations
def read_csv(csv_path):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Create the absolute file path by joining the script directory with the csv filename
    absolute_csv_path = os.path.join(script_dir, csv_path)
    
    print(f"Looking for CSV at: {absolute_csv_path}")
    
    try:
        with open(absolute_csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found at '{absolute_csv_path}'")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in script directory: {os.listdir(script_dir)}")
        raise

##################################

# Validate that the first name exists and is not empty
def validate_first_names(rows):
    violation_count = 0
    for row in rows:
        first_name = row.get('name', '').strip().split()[0] if row.get('name', '').strip() else ''
        if not first_name:
            violation_count += 1
    return violation_count

##################################

# Validate that the hire date is not empty and is after 2015
def validate_hire_dates(rows):
    violation_count = 0
    for row in rows:
        hire_date = row.get('hire_date', '').strip()
        if hire_date:
            dt = datetime.strptime(hire_date, "%Y-%m-%d")
            if dt.year < 2015:
                violation_count += 1
        else:
            violation_count += 1  
    return violation_count

##################################

def check_birth_before_hire(rows):
    errors = []
    for i, row in enumerate(rows, 1):
        birth_date = row.get('birth_date', '').strip()
        hire_date = row.get('hire_date', '').strip()
        if not birth_date:
            errors.append(f"Record {i} missing birth_date")
            continue
        if not hire_date:
            errors.append(f"Record {i} missing hire_date")
            continue
        bd = datetime.strptime(birth_date, "%Y-%m-%d")
        hd = datetime.strptime(hire_date, "%Y-%m-%d")
        if bd >= hd:
            errors.append(f"Record {i} error: birth_date ({birth_date}) is not before hire_date ({hire_date})")
    return errors

##################################

# Validate that the manager exists by checking if the employee ID is present in the dataset
def validate_manager_exists(rows):
    employee_ids = {row.get('eid', '').strip() for row in rows if row.get('eid', '').strip()}
    violation_count = 0
    for row in rows:
        manager_id = row.get('reports_to', '').strip()
        # A violation occurs if the reports_to field is empty or
        # if the manager id is not present in the set of employee ids.
        if not manager_id or manager_id not in employee_ids:
            violation_count += 1
    return violation_count

##################################

# Count the number of violations where a city has more than one employee
def count_city_violations(rows):
    city_employee_count = {}
    for row in rows:
        city = row.get('city', '').strip()
        if city:
            city_employee_count[city] = city_employee_count.get(city, 0) + 1

    violation_count = 0
    for city, count in city_employee_count.items():
        if count > 1:
            violation_count += 1

    return violation_count

# Validate city data quality. I wrote this function since I wasnt sure if the data was clean and wanted to 
# make sure that I knew the data I was working with was valid to answer question 6
def validate_city_data_quality(rows):
    results = {
        'total_records': len(rows),
        'records_with_cities': 0,
        'unique_cities': set(),
        'empty_cities': 0,
        'cities_with_multiple_employees': {},
        'is_valid': True,
        'validation_message': ""
    }
    
    # Count records with valid cities
    for row in rows:
        city = row.get('city', '').strip()
        if city:
            results['records_with_cities'] += 1
            results['unique_cities'].add(city)
        else:
            results['empty_cities'] += 1
    
    # Count employees per city
    city_employee_count = {}
    for row in rows:
        city = row.get('city', '').strip()
        if city:
            city_employee_count[city] = city_employee_count.get(city, 0) + 1
    
    # Find cities with multiple employees
    for city, count in city_employee_count.items():
        if count > 1:
            results['cities_with_multiple_employees'][city] = count
    
    # Check if data is valid for analysis
    if results['empty_cities'] > results['total_records'] * 0.1:  # If more than 10% missing cities
        results['is_valid'] = False
        results['validation_message'] += "Too many records with missing city data. "
    
    if len(results['unique_cities']) < 2:  # Need at least some variety in cities
        results['is_valid'] = False
        results['validation_message'] += "Not enough variety in city data. "
        
    if not results['cities_with_multiple_employees']:
        results['validation_message'] += "No cities with multiple employees found. "
    
    # Add summary statistics
    results['percentage_with_cities'] = (results['records_with_cities'] / results['total_records']) * 100 if results['total_records'] > 0 else 0
    results['unique_city_count'] = len(results['unique_cities'])
    results['cities_with_multiple_count'] = len(results['cities_with_multiple_employees'])
    
    if not results['validation_message']:
        results['validation_message'] = "City data appears valid for analysis."
    
    return results

##################################

def validate_salary_distribution_dagostino(rows):
    # Extract salaries from the rows
    salaries = [float(row.get('salary', 0)) for row in rows if row.get('salary')]
    
    # Perform D'Agostino & Pearson's test
    stat_dagostino, p_value = normaltest(salaries)
    
    # Define significance level (alpha)
    alpha = 0.05
    
    # If p-value > alpha, we cannot reject the null hypothesis that the data is normally distributed
    return {
        "p_value": p_value,
        "statistic": stat_dagostino,
        "is_normal": p_value > alpha
    }

def generate_salary_histogram(rows):
    salaries = [float(row.get('salary', 0)) for row in rows if row.get('salary')]
    
    # Find the max salary correctly
    max_salary = max(salaries) if salaries else 0
    
    # Printing some basic statistics to understand the distribution
    unique_salaries = set(salaries)
    print(f"Number of employees: {len(salaries)}")
    print(f"Number of unique salary values: {len(unique_salaries)}")
    print(f"Salary range: ${min(salaries):,.0f} - ${max_salary:,.0f}")
    print(f"Most common salary values: {sorted([(salary, salaries.count(salary)) for salary in unique_salaries], key=lambda x: x[1], reverse=True)[:5]}")
    
    # Create a more informative histogram
    plt.figure(figsize=(10, 6))
    
    # Use appropriate binning for the histogram
    counts, bins, patches = plt.hist(salaries, bins='auto', color='blue', edgecolor='black', alpha=0.7)
    
    # Add value labels on top of the bars
    for count, bin_edge in zip(counts, bins[:-1]):
        if count > 0:  # Only show labels for bars with values
            plt.text(bin_edge + (bins[1] - bins[0])/2, count, 
                     f'{int(count)}', 
                     ha='center', va='bottom')
    
    # Set x-axis range - limit to just above the highest salary
    plt.xlim(0, max_salary + 10000)
    
    # Add labels and title
    plt.xlabel('Salary ($)', fontsize=12)
    plt.ylabel('Frequency (Number of Employees)', fontsize=12)
    plt.title('Salary Distribution Histogram', fontsize=14)
    
    # Format x-axis to show whole dollar amounts
    from matplotlib.ticker import FuncFormatter
    def currency_formatter(x, pos):
        return f"${int(x):,}"
    
    plt.gca().xaxis.set_major_formatter(FuncFormatter(currency_formatter))
    
    # Add a grid for better readability
    plt.grid(axis='y', alpha=0.3)
    
    # Save the plot to a file
    output_file = "salary_histogram.png"
    salaries_histogram_path = os.path.join(os.getcwd(), output_file)
    plt.savefig(salaries_histogram_path, bbox_inches='tight')
    plt.close()  
    print(f"Histogram saved to {salaries_histogram_path}")

##################################

if __name__ == '__main__':
    csv_file_path = 'employees.csv'  
    rows = read_csv(csv_file_path)
    print()

    # Validate first names
    count = validate_first_names(rows)
    print(f"Number of records with missing first name: {count}")
    print()

    # Validate hire dates
    hire_violation = validate_hire_dates(rows)
    print(f"Number of records with hire date earlier than 2015: {hire_violation}")
    print()
    
    # Validate birth dates
    breakdown = check_birth_before_hire(rows)
    count = 0
    for record in breakdown:
        count+=1
    print(f"Number of records with birth date before hire date: {count}")
    print()
    
    # Validate manager data
    mgr_violation = validate_manager_exists(rows)
    print(f"Number of records with an invalid manager: {mgr_violation}")
    print()
    
    # Validate city data for multiple employees
    city_count = count_city_violations(rows)
    print(f"Number of cities with more than one employee: {city_count}")
    print()
    
    # Validate city data quality
    city_validation = validate_city_data_quality(rows)
    print("\nCity Data Validation:")
    print(f"Total records: {city_validation['total_records']}")
    print(f"Records with cities: {city_validation['records_with_cities']} ({city_validation['percentage_with_cities']:.1f}%)")
    print(f"Unique cities: {city_validation['unique_city_count']}")
    print(f"Records with empty cities: {city_validation['empty_cities']}")
    print(f"Cities with multiple employees: {city_validation['cities_with_multiple_count']}")
    print(f"Is data valid for analysis? {city_validation['is_valid']}")
    print(f"Validation message: {city_validation['validation_message']}")
    
    # Validate salary distribution using D'Agostino test
    dagostino_test = validate_salary_distribution_dagostino(rows)
    print("\nSalary Distribution Analysis (D'Agostino test):")
    print(f"D'Agostino statistic: {dagostino_test['statistic']:.2f}")
    print(f"p-value: {dagostino_test['p_value']:.2f}")
    print(f"Normally distributed: {'Yes' if dagostino_test['is_normal'] else 'No'}")
    print()
    
    print("Generating salary histogram and adding context to data...")
    generate_salary_histogram(rows)
