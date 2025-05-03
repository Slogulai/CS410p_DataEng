import pandas as pd
from datetime import datetime, timedelta

def create_timestamp(row):
    base_date = datetime.strptime(row['OPD_DATE'], '%d%b%Y:%H:%M:%S')
    
    time_delta = timedelta(seconds=int(row['ACT_TIME']))
    
    return base_date + time_delta

def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, usecols=[
        "EVENT_NO_TRIP",
        "EVENT_NO_STOP",
        "OPD_DATE",
        "VEHICLE_ID",
        "METERS",
        "ACT_TIME",
        "GPS_LONGITUDE",
        "GPS_LATITUDE"
    ])
    
    df['TIMESTAMP'] = df.apply(create_timestamp, axis=1)
    
    df = df.sort_values('TIMESTAMP')
    
    df['dTIME'] = df['TIMESTAMP'].diff().dt.total_seconds()  # Time difference in seconds
    df['dMETERS'] = df['METERS'].diff()  # Distance difference in meters
    
    # Calculate speed in km/h: (meters / 1000) / (seconds / 3600)
    df['SPEED'] = df.apply(lambda x: 
                          (x['dMETERS'] / 1000) / (x['dTIME'] / 3600) 
                          if pd.notna(x['dTIME']) and x['dTIME'] > 0 
                          else 0, axis=1)
    
    df = df.drop(['dTIME', 'dMETERS'], axis=1)
    
    df = df.drop("EVENT_NO_STOP", axis=1)
    df = df.drop("OPD_DATE", axis=1)
    df = df.drop("ACT_TIME", axis=1)
    #df = df.drop("GPS_SATELLITES", axis=1)
    #df = df.drop("GPS_HDOP", axis=1)
    
    return df

if __name__ == "__main__":
    file_path = "bc_trip259172515_230215.csv"
    data = load_data(file_path)
    print("\n", data.head())
    print(f"\nNumber of breadcrumbs: {len(data)}")
    
    print("\nSpeed statistics (km/h):")
    print(data['SPEED'].describe())
