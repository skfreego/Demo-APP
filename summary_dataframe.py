import os
import csv
import time
import statistics
import pandas as pd
import streamlit as st


def process_csv_files(input_folder, previous_data=None):
    # Initialize the total row count, sensor count, and dictionaries to store sensor time intervals
    total_rows = 0
    sensor_counts = {}
    sensor_avg_times = {}
    sensor_max_times = {}
    sensor_min_times = {}
    unique_sensor_ids = set()
    # Initialize a list to store the file names that have already been processed
    processed_files = []

    if previous_data is not None:
        # Initialize the dictionaries with the previous data
        sensor_counts = previous_data['sensor_counts']
        sensor_avg_times = previous_data['sensor_avg_times']
        sensor_max_times = previous_data['sensor_max_times']
        sensor_min_times = previous_data['sensor_min_times']
        total_rows = previous_data['total_rows']
        unique_sensor_ids = previous_data['unique_sensor_ids']
        processed_files = previous_data['processed_files']

    while True:
        # Get a list of CSV files in the input folder that have not been processed before
        csv_files = [filename for filename in os.listdir(input_folder) if filename.endswith('.csv')
                     and filename not in processed_files]

        if not csv_files:
            print('There are no CSV files in the input folder.')
            time.sleep(5)
            continue

        # Process each CSV file
        for csv_file in csv_files:
            # Open the CSV file for reading
            with open(os.path.join(input_folder, csv_file), 'r') as csvfile:
                reader = csv.reader(csvfile)
                # Skip the header row
                header_row = next(reader, None)
                if header_row is None:
                    print(f'The file {csv_file} is empty or contains only a header row.')
                    continue

                # Count the number of rows and sensor IDs in the file
                for row in reader:
                    sensor_id = row[1]
                    total_rows += 1
                    if sensor_id == '' or sensor_id == '00':
                        continue  # Skip rows with empty or "00" sensor ID
                    if sensor_id in sensor_counts:
                        sensor_counts[sensor_id] += 1
                    else:
                        sensor_counts[sensor_id] = 1
                        unique_sensor_ids.add(sensor_id)

                    if row[3] == '':
                        print(f'Time interval value is empty in file {csv_file}, row {total_rows}.')
                        continue

                    try:
                        time_interval = float(row[3])
                    except ValueError:
                        print(f'Invalid time interval value in file {csv_file}, row {total_rows}: {row[3]}')
                        continue

                    if sensor_id in sensor_avg_times:
                        sensor_avg_times[sensor_id].append(time_interval)
                        sensor_max_times[sensor_id] = max(sensor_max_times[sensor_id], time_interval)
                        sensor_min_times[sensor_id] = min(sensor_min_times[sensor_id], time_interval)
                    else:
                        sensor_avg_times[sensor_id] = [time_interval]
                        sensor_max_times[sensor_id] = time_interval
                        sensor_min_times[sensor_id] = time_interval

            # Add the processed file name to the list
            processed_files.append(csv_file)

        # Construct a pandas dataframe from the collected data
        data = {
            'Sensor ID': [':'.join([s_id.upper().zfill(2) for s_id in sensor_id.split(':')])
                          for sensor_id in sensor_avg_times.keys() if sensor_id != '' and sensor_id != '00'],
            'Count': [sensor_counts[sensor_id] for sensor_id in sensor_avg_times.keys()
                      if sensor_id != '' and sensor_id != '00'],
            'Average Interval': [round(statistics.mean(sensor_avg_times[sensor_id]), 2)
                                 for sensor_id in sensor_avg_times.keys()
                                 if sensor_id != '' and sensor_id != '00'],
            'Maximum Interval': [int(round(sensor_max_times[sensor_id]))
                                 for sensor_id in sensor_max_times.keys() if sensor_id != '' and sensor_id != '00'],
            'Minimum Interval': [int(round(sensor_min_times[sensor_id]))
                                 for sensor_id in sensor_min_times.keys()
                                 if sensor_id != '' and sensor_id != '00']
        }
        df = pd.DataFrame(data)

        # Sort the dataframe by sensor ID
        df.sort_values(by=['Sensor ID'], inplace=True)
        st.write('Total records:', total_rows, '\n')
        st.write('Unique Sensor IDs:', len(unique_sensor_ids), '\n')

        # Print the sensor ID and count
        count_sensors_df = pd.DataFrame({
            'Sensor ID': [':'.join([s_id.upper().zfill(2) for s_id in sensor_id.split(':')]) for sensor_id in
                          sorted(sensor_avg_times.keys()) if sensor_id not in ['', '00']],
            'Count': [sensor_counts[sensor_id] for sensor_id in sensor_avg_times.keys()
                      if sensor_id != '' and sensor_id != '00']
            })

        # Print the Summary statistics
        summary_stats_df = pd.DataFrame({
            'Sensor ID': [':'.join([s_id.upper().zfill(2) for s_id in sensor_id.split(':')]) for sensor_id in
                          sorted(sensor_avg_times.keys()) if sensor_id not in ['', '00']],
            'Average Interval': [round(statistics.mean(sensor_avg_times[sensor_id]), 2)
                                 for sensor_id in sensor_avg_times.keys()
                                 if sensor_id != '' and sensor_id != '00'],
            'Maximum Interval': [int(round(sensor_max_times[sensor_id]))
                                 for sensor_id in sorted(sensor_max_times.keys())
                                 if sensor_id not in ['', '00']],
            'Minimum Interval': [int(round(sensor_min_times[sensor_id]))
                                 for sensor_id in sorted(sensor_min_times.keys())
                                 if sensor_id not in ['', '00']]
            })

        # Format the average interval values as strings with 2 decimal places
        summary_stats_df['Average Interval'] = summary_stats_df['Average Interval'].apply(lambda x: "{:.2f}".format(x))


        # Display as table
        st.write(count_sensors_df)
        st.write(summary_stats_df)


# Wait for 5 seconds before checking for new files again
time.sleep(5)

def streamlit_app():
    st.title('Sensor Data Dashboard')
    st.write('')
    output_text = st.empty()
    while True:
        output_text.text(process_csv_files('.'))
        time.sleep(5)


# Run the Streamlit app
streamlit_app()

