import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import time
from datetime import datetime


def convert_to_unix_timestamp(timestamp_str):
    try:
        # Try to parse the input as a Unix timestamp (integer or float)
        timestamp = float(timestamp_str)
        return int(timestamp)
    except ValueError:
        # Try to parse the input as a datetime string
        for fmt in ['%m/%d/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ', '%d/%m/%Y %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return int(dt.timestamp())
            except ValueError:
                pass
        raise ValueError(f"No matching format found for timestamp {timestamp_str}")


def run_app():
    st.header("Sensor Data Analysis Report Dashboard")

    # Define API parameters
    url = "http://gapp.agverse.in/api/v1/get-telemetry-data"
    start_id = 1
    id_interval = 100000
    # Define time interval parameters
    interval_seconds = 3
    previous_id = None

    # Create empty containers to display results
    containers = {
        'Total Number of Records': [st.subheader("1. Total Number of Records"), st.empty()],
        'Unique Mac IDS': [st.subheader("2. Unique Mac IDS"), st.empty()],
        'Sensor ID and Its Count': [st.subheader("3. Sensor ID and Its Count"), st.empty()],
        'Summary Statistics of Sensor ID': [st.subheader("4. Summary Statistics of Sensor ID"), st.empty()]
    }

    # Create empty DataFrame to store data
    all_data = pd.DataFrame()

    while True:
        try:
            # Update start and end IDs based on time interval
            if previous_id is None:
                previous_id = start_id
                end_id = previous_id + id_interval
            else:
                start_id = previous_id
                previous_id = end_id
                end_id = previous_id + id_interval

            # Fetch data from API
            params = {"id": f"{start_id}/{start_id + id_interval - 1}"}
            url_encoded_params = urllib.parse.urlencode(params)
            url_with_params = f"{url}?{url_encoded_params}"
            url_auth = urllib.request.Request(url_with_params,
                                              headers={"username": "gapp-apis", "password": "4Score&7yrsAgo"})
            response = urllib.request.urlopen(url_auth)
            data = response.read()
            values = json.loads(data)
            telemetry_data = values.get("result", [])
            df = pd.DataFrame(telemetry_data)

            if not df.empty:
                # Convert timestamps to Unix timestamps
                df['timestamp_unix'] = df['timestamp'].apply(convert_to_unix_timestamp)

                # Calculate time difference
                df['time_difference (s)'] = df['timestamp_unix'].diff()

                all_data = all_data.append(df)
                all_data = all_data.drop_duplicates()

                # Display total number of records
                num_records = all_data.shape[0]
                containers['Total Number of Records'][1].write(f"Total number of records: **{num_records}**")

                # Display unique mac ids
                unique_sensor_ids = all_data['mac_id'].str.upper()
                unique_sensor_ids = unique_sensor_ids.str.replace('[^A-F0-9:]+', '', regex=True)
                unique_sensor_ids = unique_sensor_ids[unique_sensor_ids.str.contains(':')].value_counts()
                unique_sensor_ids = unique_sensor_ids[(unique_sensor_ids != 1)]
                containers['Unique Mac IDS'][1].write(
                    f"Total number of unique Mac IDs (excluding those with count of 1 and 2): {len(unique_sensor_ids)}")

                # Display unique Sensor IDs and their counts
                sensor_counts = all_data['mac_id'].str.upper().value_counts()
                sensor_counts_df = pd.DataFrame({'mac_id': sensor_counts.index, 'Count': sensor_counts.values})
                sensor_counts_df = sensor_counts_df[sensor_counts_df['Count'] > 1] # Exclude mac_id with count of 1
                sensor_counts_df['mac_id'] = sensor_counts_df['mac_id'].str.upper().str.replace('[^A-F0-9:]+', '',
                                                                                                regex=True)
                sensor_counts_df = sensor_counts_df[sensor_counts_df['mac_id'].str.contains(':')]
                sensor_counts_df = sensor_counts_df.drop_duplicates()
                if not sensor_counts_df.empty:
                    containers['Sensor ID and Its Count'][1].write(sensor_counts_df)
                else:
                    containers['Sensor ID and Its Count'][1].write("No Sensor ID with count > 2 found.")

                # Calculate summary statistics of sensor IDs
                # sensor_stats = df.groupby('mac_id')['time_difference (s)'].agg(['mean', 'max', 'min']).reset_index()
                sensor_stats = all_data.groupby(all_data['mac_id'].str.upper())['time_difference (s)']\
                    .agg(['mean', 'max', 'min']).reset_index()
                sensor_stats.rename(
                    columns={'mean': 'Mean Interval', 'max': 'Maximum Interval', 'min': 'Minimum Interval'},
                    inplace=True)
                sensor_stats['Maximum Interval'] = sensor_stats['Maximum Interval'].fillna(0).astype(int)
                sensor_stats['Minimum Interval'] = sensor_stats['Minimum Interval'].fillna(0).astype(int)
                sensor_stats['Mean Interval'] = sensor_stats['Mean Interval'].apply(lambda x: '{:.2f}'.format(x))
                sensor_stats = sensor_stats[
                    sensor_stats['mac_id'].isin(sensor_counts_df['mac_id'])]  # Exclude mac_id with count of 2
                sensor_stats['mac_id'] = sensor_stats['mac_id'].str.upper().str.replace('[^A-F0-9:]+', '', regex=True)
                sensor_stats = sensor_stats[sensor_stats['mac_id'].str.contains(':')]
                if not sensor_stats.empty:
                    containers['Summary Statistics of Sensor ID'][1].write(sensor_stats)
                else:
                    containers['Summary Statistics of Sensor ID'][1].write("No Sensor ID with count > 2 found.")
            # Sleep for 1 second before checking for new CSV files again
            time.sleep(interval_seconds)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            break


if __name__ == '__main__':
    run_app()
