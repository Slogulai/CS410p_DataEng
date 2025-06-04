import pandas as pd
import datetime
from bs4 import BeautifulSoup, SoupStrainer
import time
import re
import scipy.stats as stats

# Initialize lists to store the data
trip_ids = []
vehicle_numbers = []
arrive_times = []
location_ids = []
ons_list = []
offs_list = []

# Use a chunk-based approach for faster processing
print("Processing HTML data using chunk-based parsing...")

# Process the HTML file in chunks to reduce memory usage

start_time = time.time()

# Only parse tr elements to improve speed
parse_only = SoupStrainer('tr')

# Process the file in chunks
row_count = 0
chunk_size = 32768  # 32 KB chunks
first_chunk = True  # Flag to identify the first chunk to skip header

with open('trimet_stopevents_2022-12-07.html', 'r', encoding='utf-8') as file:
    # Read the file in chunks and process each chunk
    buffer = ""
    
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        
        # Add chunk to buffer
        buffer += chunk
        
        # Find complete rows in the buffer
        tr_start_indices = [m.start() for m in re.finditer(r'<tr', buffer)]
        tr_end_indices = [m.start() + 5 for m in re.finditer(r'</tr>', buffer)]
        
        # Process complete rows
        for i in range(min(len(tr_start_indices), len(tr_end_indices))):
            if tr_start_indices[i] < tr_end_indices[i]:
                row_html = buffer[tr_start_indices[i]:tr_end_indices[i]]
                
                # Skip first row (header) only on the first chunk
                if first_chunk and i == 0:
                    first_chunk = False
                    continue
                    
                # Parse the individual row
                row_soup = BeautifulSoup(row_html, 'html.parser', parse_only=parse_only)
                cols = row_soup.find_all('td')
                  # Based on the actual table structure you provided:
                # vehicle_number, leave_time, train, route_number, direction, service_key, trip_number, stop_time,
                # arrive_time, dwell, location_id, door, lift, ons, offs, ...
                
                if len(cols) >= 15:  # We need at least up to the 'offs' column (index 14)
                    row_count += 1
                    
                    # Correct column mapping
                    vehicle_num = cols[0].text.strip()
                    trip_id = cols[6].text.strip()  # trip_number is in col 6
                    arrive_time = cols[8].text.strip()  # arrive_time is in col 8
                    location_id = cols[10].text.strip()  # location_id is in col 10
                    
                    # Add to our lists
                    vehicle_numbers.append(vehicle_num)
                    trip_ids.append(trip_id)
                    arrive_times.append(arrive_time)
                    location_ids.append(location_id)
                    
                    # Handle non-numeric values in ons and offs columns (cols 13 and 14)
                    try:
                        ons_value = float(cols[13].text.strip()) if cols[13].text.strip() else 0
                    except ValueError:
                        ons_value = 0  # Default to 0 if value can't be converted to float
                    
                    try:
                        offs_value = float(cols[14].text.strip()) if cols[14].text.strip() else 0
                    except ValueError:
                        offs_value = 0  # Default to 0 if value can't be converted to float
                        
                    ons_list.append(ons_value)
                    offs_list.append(offs_value)
                    
        # Keep only the portion of buffer that might contain incomplete rows
        if tr_end_indices:
            buffer = buffer[tr_end_indices[-1]:]

end_time = time.time()
print(f"\nProcessing complete. Total: {row_count} rows in {end_time-start_time:.2f} seconds ({row_count/(end_time-start_time):.2f} rows/sec)")
print(f"Processed {len(trip_ids)} rows of data\n")

# Convert arrive_time (seconds since midnight) to datetime
# Create a function to convert seconds since midnight to a datetime object
def seconds_to_time(seconds):
    if not seconds or not str(seconds).isdigit():
        return None
    base_date = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time())
    return base_date + datetime.timedelta(seconds=int(seconds))
# Convert arrive_times to tstamp
start_time = time.time()
tstamps = []
for i, time_val in enumerate(arrive_times):
    tstamps.append(seconds_to_time(time_val))

# Create the DataFrame
stops_df = pd.DataFrame({
    'trip_id': trip_ids,
    'vehicle_number': vehicle_numbers,
    'tstamp': tstamps,
    'location_id': location_ids,
    'ons': ons_list,
    'offs': offs_list
})

# Display the first few rows
print(stops_df.head())

print("\n--- Transform the Data ---")
# Find the number of unique vehicle_ids
unique_vehicles = stops_df['vehicle_number'].nunique()
print(f"\nNumber of unique vehicle_numbers: {unique_vehicles}")
# Find and print the number of unique location_ids
unique_locations = stops_df['location_id'].nunique()
print(f"\nNumber of unique location_ids: {unique_locations}")
# Find and print the minimum and maximum timestamps
# Filter out None values first to avoid comparison errors
valid_timestamps = stops_df['tstamp'].dropna()
if not valid_timestamps.empty:
    min_timestamp = valid_timestamps.min()
    max_timestamp = valid_timestamps.max()
    print(f"\nTimestamp range:")
    print(f"Minimum timestamp: {min_timestamp}")
    print(f"Maximum timestamp: {max_timestamp}")
else:
    print("\nNo valid timestamps found in the data.")
# Count and analyze boarding events
boarding_events = stops_df[stops_df['ons'] >= 1]
print(f"\nNumber of stop events with at least one passenger boarding: {len(boarding_events)} ({len(boarding_events)/len(stops_df)*100:.2f}% of total)")

# Data validation slide
print("\n--- Validate the Data for location_id 6913 ---")
# Data validation for location ID 6913

loc_6913_df = stops_df[stops_df['location_id'] == '6913']
print(f"\nTotal stops made at location '6913': {len(loc_6913_df)}")
analysis_df = loc_6913_df
loc_id = '6913'
unique_buses = analysis_df['vehicle_number'].nunique()
# 2. How many different buses stopped at this location?
print(f"Number of different buses that stopped at location {loc_id}: {unique_buses}")
# 3. For what percentage of stops did at least one passenger board?
boarding_events = analysis_df[analysis_df['ons'] >= 1]
boarding_percentage = (len(boarding_events) / len(analysis_df) * 100)
print(f"Stops with at least one boarding at location {loc_id}: {len(boarding_events)} ({boarding_percentage:.2f}% of stops at this location)")

# Vehicle 4062 validation
print("\n--- Validate the Data for vehicle_id 4062 ---")
vehicle_4062_df = stops_df[stops_df['vehicle_number'] == '4062']
# 1. How many stops made by this vehicle?
stops_by_4062 = len(vehicle_4062_df)
print(f"Total stops made by vehicle 4062: {stops_by_4062}")
# 2. How many total passengers boarded this vehicle?
total_boarding = vehicle_4062_df['ons'].sum()
print(f"Total passengers who boarded vehicle 4062: {total_boarding:.0f}")
# 3. How many passengers deboarded this vehicle?
total_deboarding = vehicle_4062_df['offs'].sum()
print(f"Total passengers who deboarded vehicle 4062: {total_deboarding:.0f}")
# 4. For what percentage of this vehicle's stop events did at least one passenger board?
boarding_events_4062 = vehicle_4062_df[vehicle_4062_df['ons'] >= 1]
if stops_by_4062 > 0:
    boarding_percentage_4062 = (len(boarding_events_4062) / stops_by_4062) * 100
    print(f"Stops with at least one boarding for vehicle 4062: {len(boarding_events_4062)} ({boarding_percentage_4062:.2f}% of stops by this vehicle)")
else:
    print("No data found for vehicle 4062.")

print("\n--- Detect Bias in Boarding Data using Binomial Test ---")

system_stops_total = len(stops_df)
system_stops_with_boardings = len(stops_df[stops_df['ons'] >= 1])
system_boarding_proportion = system_stops_with_boardings / system_stops_total
print(f"System-wide baseline: {system_stops_with_boardings} out of {system_stops_total} stops had boardings ({system_boarding_proportion:.4f} or {system_boarding_proportion*100:.2f}%)")
unique_vehicle_numbers = stops_df['vehicle_number'].unique()
print(f"Analyzing {len(unique_vehicle_numbers)} unique vehicles for bias...")
alpha = 0.05

biased_vehicles = []
p_values = []
proportions = []
stop_counts = []

# Loop through each vehicle and perform the binomial test
for vehicle in unique_vehicle_numbers:
    vehicle_df = stops_df[stops_df['vehicle_number'] == vehicle]
    
    vehicle_stops_total = len(vehicle_df)
    vehicle_stops_with_boardings = len(vehicle_df[vehicle_df['ons'] >= 1])
    
    if vehicle_stops_total < 10:  # Minimum threshold for meaningful statistical analysis
        continue
    
    vehicle_boarding_proportion = vehicle_stops_with_boardings / vehicle_stops_total
    result = stats.binomtest(vehicle_stops_with_boardings, vehicle_stops_total, 
                           system_boarding_proportion, alternative='two-sided')
    p_value = result.pvalue
    
    if p_value < alpha:
        biased_vehicles.append(vehicle)
        p_values.append(p_value)
        proportions.append(vehicle_boarding_proportion)
        stop_counts.append(vehicle_stops_total)

print(f"\nFound {len(biased_vehicles)} vehicles with statistically significant bias in boarding data (p < {alpha})")
if biased_vehicles:
    print("\nVehicles with biased boarding data (p < 5%):")
    print("Vehicle ID | Stops | Boarding % | p-value")
    print("-" * 50)
    
    # Sort by p-value (most significant first)
    sorted_indices = sorted(range(len(p_values)), key=lambda i: p_values[i])
    
    for idx in sorted_indices:
        vehicle = biased_vehicles[idx]
        p_val = p_values[idx]
        prop = proportions[idx]
        stops = stop_counts[idx]
        print(f"{vehicle:10} | {stops:5} | {prop*100:8.2f}% | {p_val:.8f}")


