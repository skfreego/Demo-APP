# Demo-App
This script processes CSV files in a specified input folder and generates summary statistics for each sensor ID. It uses the Pandas library to create a DataFrame to hold the collected data and then uses Streamlit to display the data as tables.

The script first initializes variables to keep track of the total number of rows, unique sensor IDs, and dictionaries to store the count and time intervals for each sensor ID. It then enters an infinite loop that checks for new CSV files in the input folder. If there are no new files, the script sleeps for 15 seconds before checking again. If new files are found, the script processes each file by iterating through its rows and counting the number of rows and sensor IDs. It skips rows with empty or "00" sensor IDs and records the time interval for each sensor ID.

After processing all files, the script constructs a DataFrame from the collected data and displays the total number of records and unique sensor IDs. It also displays two tables: one showing the sensor IDs and their counts and another showing the summary statistics for each sensor ID (average, maximum, and minimum time intervals).

The script uses several built-in functions and libraries, including os for file management, csv for reading CSV files, time for sleeping, statistics for computing summary statistics, and pandas and streamlit for creating and displaying data frames.

Overall, the script is well-organized and easy to understand. However, it could benefit from additional error handling to handle cases where files are locked or cannot be read due to file permissions, and it could also benefit from more descriptive error messages.

# Sensor Data Dashboard
### cloud link:-https://skfreego-demo-app-summary-dataframe-3yhusz.streamlit.app/
