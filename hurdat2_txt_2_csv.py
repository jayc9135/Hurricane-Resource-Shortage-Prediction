import pandas as pd
import csv

# File paths
input_file = "datasets/hurdat2-1851-2023-051124.txt"
output_file = "datasets/hurdat2.csv"

# Define column headers
header_col = ["storm_id", "storm_name", "num_of_obs"]
obs_col = ["date",
           "time",
           "record_identifier",
           "status_of_system",
           "latitude",
           "longitude",
           "maximum_sustained_wind_knots",
           "central_pressure_mb",
           "34_kt_ne_nm",
           "34_kt_se_nm",
           "34_kt_sw_nm",
           "34_kt_nw_nm",
           "50_kt_ne_nm",
           "50_kt_se_nm",
           "50_kt_sw_nm",
           "50_kt_nw_nm",
           "64_kt_ne_nm",
           "64_kt_se_nm",
           "64_kt_sw_nm",
           "64_kt_nw_nm",
           "radius_of_max_wind_nm"
           ]

headers = header_col + obs_col

# read the file
with open(input_file, "r") as f:
    f = csv.reader(f)
    storm_id = None
    storm_name = None
    num_of_obs = None
    data = []
    for line in f:
        line = [item.strip() for item in line]

        if len(line) == 4:
            storm_id = line[0].strip()
            storm_name = line[1].strip()
            num_of_obs = line[2].strip()
        elif len(line) == 21:
            row= [storm_id, storm_name, num_of_obs] + line
            data.append(row)


df = pd.DataFrame(data, columns=headers)
df.to_csv(output_file, index=False)
print("Done converting the file to CSV")

