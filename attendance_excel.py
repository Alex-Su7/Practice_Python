import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# Function to check if a string is a valid time (HH:MM format)
def is_time_format(s):
    return bool(re.match(r"^\d{2}:\d{2}$", s))

# Function to process attendance data and generate plot
def process_attendance(input_file, output_file, plot_file):
    # Load the original data
    data = pd.read_excel(input_file, sheet_name='Sheet1')

    # Initialize an empty list to hold the processed records
    processed_records = []

    # Get the header row with dates and days of the week
    header_row = data.iloc[0]

    # Iterate over each person (starting from the second row)
    for index, row in data.iterrows():
        if index == 0:
            continue  # Skip the header row
        name = row['姓名']
        
        # Iterate over each day's attendance data
        for col in range(6, len(row)):  # Iterate over each column
            if ' ' not in header_row[col]:
                continue  # Skip columns that do not contain date and day info
            
            date_info = header_row[col].split(' ')
            date = date_info[0]
            day_of_week = date_info[1]
            
            attendance_info = row[col]
            if not pd.isna(attendance_info):
                attendance_info_split = attendance_info.split(',')
                if len(attendance_info_split) == 2:
                    start_time = attendance_info_split[0].replace('正常(', '').replace(')', '')
                    end_time = attendance_info_split[1].replace('正常(', '').replace(')', '')
                    
                    # Append the processed record to the list
                    processed_records.append([name, date, day_of_week, start_time, '12:00', '13:30', end_time])
                else:
                    # For incomplete records, still add the date and name but with missing times
                    processed_records.append([name, date, day_of_week, None, '12:00', '13:30', None])

    # Create a DataFrame from the processed records
    processed_df = pd.DataFrame(processed_records, columns=['姓名', '日期', '星期', '上班时间', '午休开始', '午休结束', '下班时间'])

    # Replace invalid time records with "-"
    processed_df['上班时间'] = processed_df['上班时间'].apply(lambda x: x if is_time_format(str(x)) else '-')
    processed_df['下班时间'] = processed_df['下班时间'].apply(lambda x: x if is_time_format(str(x)) else '-')

    # Save the cleaned DataFrame to a new Excel file
    processed_df.to_excel(output_file, index=False)

    # Plot the data for each person
    attendance_dict = {}

    for index, row in processed_df.iterrows():
        name = row['姓名']
        date = row['日期']
        start_time = row['上班时间']
        end_time = row['下班时间']
        
        if name not in attendance_dict:
            attendance_dict[name] = {'dates': [], 'start_times': [], 'end_times': []}
        
        attendance_dict[name]['dates'].append(date)
        attendance_dict[name]['start_times'].append(start_time)
        attendance_dict[name]['end_times'].append(end_time)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    for name, data in attendance_dict.items():
        ax.plot(data['dates'], data['start_times'], marker='o', linestyle='-', label=f'{name} - Start Time')
        ax.plot(data['dates'], data['end_times'], marker='x', linestyle='--', label=f'{name} - End Time')

    # Formatting the plot
    plt.xlabel('Date')
    plt.ylabel('Time')
    plt.title('Daily Attendance Time Distribution')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(plot_file)
    plt.show()

# Main function
def main():
    input_file = '月度汇总_20240501_20240522.xlsx'  # Input Excel file path
    output_file = 'cleaned_attendance.xlsx'  # Output Excel file path
    plot_file = 'daily_attendance_time_distribution.png'  # Output plot file path

    if os.path.exists(input_file):
        process_attendance(input_file, output_file, plot_file)
        print(f'Processed data saved to {output_file}')
        print(f'Plot saved to {plot_file}')
    else:
        print(f'Input file {input_file} does not exist')

if __name__ == "__main__":
    main()
