import requests
from datetime import datetime, timedelta  
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json  
import os  
import shutil  

from urllib.request import urlopen

bus_ids = [ 2901,2914,2922,2938,3009,3010,3016,3018,3019,3021,3023,3031,3032,3033,3034,3038,3042,3045,3102,3104,
            3108,3112,3113,3117,3123,3124,3125,3127,3130,3134,3139,3140,3143,3145,3153,3157,3160,3163,3202,3203,
            3206,3209,3210,3220,3224,3225,3229,3233,3234,3240,3241,3242,3243,3245,3246,3248,3249,3251,3257,3261,
            3262,3264,3268,3305,3314,3321,3404,3409,3410,3415,3416,3419,3501,3502,3504,3505,3506,3507,3509,3511,
            3513,3514,3516,3519,3523,3524,3533,3535,3537,3542,3543,3544,3545,3546,3547,3553,3559,3566,3567,3569,
            3572,3576,3602,3606,3608,3610,3620,3622,3625,3630,3634,3640,3644,3648,3702,3707,3715,3716,3719,3721,
            3724,3725,3727,3731,3732,3734,3737,3745,3747,3748,3750,3802,3805,3907,3913,3917,3918,3919,3920,3921,
            3930,3931,3932,3935,3936,3938,3941,3942,3943,3949,3957,3960,3961,3964,4002,4004,4005,4007,4012,4013,
            4014,4017,4019,4026,4031,4034,4035,4037,4038,4039,4041,4042,4049,4051,4057,4058,4060,4062,4064,4071,
            4201,4202,4204,4207,4216,4218,4227,4231,4234,4235,4237,4302,4513,4516,4519,4520,4521,4531,99222]

today = datetime.today()
date_str = today.strftime("%Y%m%d")
output_dir = date_str
if os.path.exists(output_dir):
    shutil.rmtree(output_dir) 
os.makedirs(output_dir, exist_ok=True)

count = 0
for bus_id in bus_ids:
    url = f"https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id={bus_id}"
    try:
        response = urlopen(url)
        if response.getcode() != 200:
            error_message = f"Error: Received status code {response.getcode()} for bus {bus_id}"
            print(error_message)
            error_folder = f"{date_str}_Error"
            os.makedirs(error_folder, exist_ok=True)
            error_file_path = os.path.join(error_folder, f"BUS{bus_id}_{date_str}_error.txt")
            with open(error_file_path, 'w') as ef:
                ef.write(error_message)
            continue
        content = response.read().decode('utf-8').strip()
        file_path = os.path.join(output_dir, f"BUS{bus_id}_{date_str}.json")
        with open(file_path, 'w') as f:
            f.write(content)
        count += 1
    except Exception as e:
        error_message = f"Error fetching data for bus {bus_id}: {e}"
        print(error_message)
        error_folder = f"{date_str}_Error"
        os.makedirs(error_folder, exist_ok=True)
        error_file_path = os.path.join(error_folder, f"BUS{bus_id}_{date_str}_error.txt")
        with open(error_file_path, 'w') as ef:
            ef.write(error_message)
print(f"Total files saved: {count}")

"""
try:
    html = urlopen(vehicle_id)
    if html.getcode() != 200:
        print("Error: Received status code", html.getcode())
        exit(1)
    content = html.read().decode('utf-8').strip()
    try:
        # First try parsing the entire content as JSON.
        parsed = json.loads(content)
        if isinstance(parsed, list):
            df = pd.DataFrame(parsed)
        elif isinstance(parsed, dict):
            df = pd.DataFrame([parsed])
        else:
            print("Unexpected JSON structure.")
            exit(1)
    except json.JSONDecodeError:
        # Fallback: treat content as multiple newline-separated JSON objects.
        json_objects = [json.loads(line) for line in content.splitlines() if line.strip()]
        df = pd.DataFrame(json_objects)
except Exception as e:
    print("Error fetching URL:", e)
    exit(1)

if 'ACT_TIME' in df.columns:
    df['ACT_TIME'] = df['ACT_TIME'].apply(lambda s: str(timedelta(seconds=s)))

print(df)
"""