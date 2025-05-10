import json
import sys
from collections import defaultdict
import datetime

def verify_vehicle_ids(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        records = data if isinstance(data, list) else [data]
        
        invalid_ids = []
        
        for record in records:
            if 'VEHICLE_ID' not in record:
                print(f"Error: Record missing VEHICLE_ID field: {record}")
                return False
            
            vehicle_id = record['VEHICLE_ID']
            
            if not isinstance(vehicle_id, (int, float)):
                try:
                    vehicle_id = int(vehicle_id)
                except (ValueError, TypeError):
                    invalid_ids.append(f"Non-numeric ID: {vehicle_id}")
                    continue
            
            if vehicle_id < 2901 or vehicle_id > 99222:
                invalid_ids.append(vehicle_id)
        
        if invalid_ids:
            print(f"Error: Found {len(invalid_ids)} invalid vehicle IDs: {invalid_ids[:10]}")
            if len(invalid_ids) > 10:
                print(f"... and {len(invalid_ids) - 10} more.")
            return False
        else:
            print("Success: All vehicle IDs are positive and within the range of 2901 to 99222.")
            return True
            
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file {json_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return False

def verify_timestamp_format(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        records = data if isinstance(data, list) else [data]
        
        invalid_times = []
        
        for record in records:
            if 'timestamp' not in record:
                print(f"Error: Record missing timestamp field: {record}")
                return False
            
            timestamp = record['timestamp']
            
            # Check if time is in DD:MM:YYYY:HH:MM:SS format
            try:
                # Parse the time string
                time_parts = timestamp.split(':')
                if len(time_parts) == 6:  # Complete datetime format
                    day, month, year, hour, minute, second = map(int, time_parts)
                    
                    # Verify that time components are within valid ranges
                    if (hour < 0 or hour > 23 or 
                        minute < 0 or minute > 59 or 
                        second < 0 or second > 59):
                        invalid_times.append(timestamp)
                else:
                    # If not in expected format, consider it invalid
                    invalid_times.append(timestamp)
                    
            except (ValueError, AttributeError, TypeError):
                invalid_times.append(f"Invalid time format: {timestamp}")
                continue
        
        if invalid_times:
            print(f"Error: Found {len(invalid_times)} invalid timestamp values: {invalid_times[:10]}")
            if len(invalid_times) > 10:
                print(f"... and {len(invalid_times) - 10} more.")
            return False
        else:
            print("Success: All timestamp values are in valid DD:MM:YYYY:HH:MM:SS format.")
            return True
            
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file {json_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return False

def verify_coordinates_within_portland(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        records = data if isinstance(data, list) else [data]
        
        invalid_coordinates = []
        
        # Portland, Oregon boundaries (corrected)
        MIN_LATITUDE = 45.0
        MAX_LATITUDE = 46.0
        MIN_LONGITUDE = -123.0
        MAX_LONGITUDE = -122.0
        
        for record in records:
            if 'GPS_LATITUDE' not in record or 'GPS_LONGITUDE' not in record:
                print(f"Error: Record missing GPS coordinates: {record}")
                continue
            
            lat = record['GPS_LATITUDE']
            lon = record['GPS_LONGITUDE']
            
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
                try:
                    lat = float(lat)
                    lon = float(lon)
                except (ValueError, TypeError):
                    invalid_coordinates.append(f"Non-numeric coordinates: lat={lat}, lon={lon}")
                    continue
            
            # Check if coordinates are within Portland boundaries
            if (lat < MIN_LATITUDE or lat > MAX_LATITUDE or 
                lon < MIN_LONGITUDE or lon > MAX_LONGITUDE):
                invalid_coordinates.append(f"lat={lat}, lon={lon}")
        
        if invalid_coordinates:
            print(f"Error: Found {len(invalid_coordinates)} coordinates outside Portland area: {invalid_coordinates[:10]}")
            if len(invalid_coordinates) > 10:
                print(f"... and {len(invalid_coordinates) - 10} more.")
            return False
        else:
            print("Success: All GPS coordinates are within Portland, Oregon area (lat: 45-46°N, lon: 122-123°W).")
            return True
            
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file {json_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return False

def parse_timestamp(time_str):
    """
    Parse the timestamp string in DD:MM:YYYY:HH:MM:SS format into a datetime object.
    
    Args:
        time_str (str): Time string in DD:MM:YYYY:HH:MM:SS format
        
    Returns:
        datetime.datetime: The parsed datetime object
    """
    time_parts = time_str.split(':')
    if len(time_parts) == 6:
        day, month, year, hour, minute, second = map(int, time_parts)
        return datetime.datetime(year, month, day, hour, minute, second)
    raise ValueError(f"Invalid time format: {time_str}")

def verify_meters_increase_with_time(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        records = data if isinstance(data, list) else [data]
        
        # Group records by vehicle_id and date
        vehicle_records = defaultdict(list)
        for record in records:
            if ('VEHICLE_ID' not in record or 'OPD_DATE' not in record or 
                'timestamp' not in record or 'METERS' not in record):
                continue
                
            vehicle_id = record['VEHICLE_ID']
            opd_date = record['OPD_DATE']
            key = f"{vehicle_id}_{opd_date}"
            
            # Extract the relevant fields
            try:
                # Parse the timestamp in DD:MM:YYYY:HH:MM:SS format
                timestamp = parse_timestamp(record['timestamp'])
                meters = float(record['METERS'])
                vehicle_records[key].append((timestamp, meters))
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error parsing record: {e}")
                continue
        
        # Check if meters increase with time for each vehicle on each day
        anomalies = []
        
        for key, time_meter_pairs in vehicle_records.items():
            # Sort by timestamp to ensure chronological order
            time_meter_pairs.sort(key=lambda x: x[0])
            
            vehicle_id, opd_date = key.split('_', 1)
            
            for i in range(1, len(time_meter_pairs)):
                prev_time, prev_meters = time_meter_pairs[i-1]
                curr_time, curr_meters = time_meter_pairs[i]
                
                # If time increases but meters don't increase or decrease
                if curr_time > prev_time and curr_meters < prev_meters:
                    anomalies.append({
                        'vehicle_id': vehicle_id,
                        'opd_date': opd_date,
                        'prev_time': prev_time.strftime('%d:%m:%Y:%H:%M:%S'),
                        'prev_meters': prev_meters,
                        'curr_time': curr_time.strftime('%d:%m:%Y:%H:%M:%S'),
                        'curr_meters': curr_meters
                    })
        
        if anomalies:
            print(f"Error: Found {len(anomalies)} instances where meters decreased as time increased:")
            for i, anomaly in enumerate(anomalies[:10]):
                print(f"  {i+1}. Vehicle {anomaly['vehicle_id']} on {anomaly['opd_date']}: " +
                      f"At time {anomaly['prev_time']}: {anomaly['prev_meters']}m → " +
                      f"At time {anomaly['curr_time']}: {anomaly['curr_meters']}m")
            
            if len(anomalies) > 10:
                print(f"... and {len(anomalies) - 10} more anomalies.")
            return False
        else:
            print("Success: All vehicles' meters increase consistently with time.")
            return True
            
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file {json_file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        verify_vehicle_ids(json_file)
        verify_timestamp_format(json_file)
        verify_coordinates_within_portland(json_file)
        verify_meters_increase_with_time(json_file)
    else:
        print("Usage: python Chris_Assertions.py <path_to_json_file>")