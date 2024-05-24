import pandas as pd
import matplotlib.pyplot as plt
import re
import os
import argparse
import logging

# 检查字符串是否为有效时间格式 (HH:MM)
def is_time_format(s):
    return bool(re.match(r"^\d{2}:\d{2}$", s))

# 处理考勤数据并生成图表的函数
def process_attendance(input_file, output_file, plot_file):
    try:
        # 读取原始数据
        data = pd.read_excel(input_file, sheet_name='Sheet1')
    except Exception as e:
        logging.error(f"读取输入文件出错: {e}")
        return

    # 初始化一个空列表来存储处理后的记录
    processed_records = []

    # 获取包含日期和星期的表头行
    header_row = data.iloc[0]

    # 遍历每个人的数据（从第二行开始）
    for index, row in data.iterrows():
        if index == 0:
            continue  # 跳过表头行
        name = row['姓名']
        
        # 遍历每一天的考勤数据
        for col in range(6, len(row)):  # 遍历每一列
            if ' ' not in header_row[col]:
                continue  # 跳过不包含日期和星期信息的列
            
            date_info = header_row[col].split(' ')
            date = date_info[0]
            day_of_week = date_info[1]
            
            attendance_info = row[col]
            if not pd.isna(attendance_info):
                attendance_info_split = attendance_info.split(',')
                if len(attendance_info_split) == 2:
                    start_time = attendance_info_split[0].replace('正常(', '').replace(')', '')
                    end_time = attendance_info_split[1].replace('正常(', '').replace(')', '')
                    
                    # 将处理后的记录添加到列表中
                    processed_records.append([name, date, day_of_week, start_time, '12:00', '13:30', end_time])
                else:
                    # 对于不完整的记录，仍然添加日期和姓名，但时间为空
                    processed_records.append([name, date, day_of_week, None, '12:00', '13:30', None])

    # 从处理后的记录创建一个 DataFrame
    processed_df = pd.DataFrame(processed_records, columns=['姓名', '日期', '星期', '上班时间', '午休开始', '午休结束', '下班时间'])

    # 将无效的时间记录替换为 "-"
    processed_df['上班时间'] = processed_df['上班时间'].apply(lambda x: x if is_time_format(str(x)) else '-')
    processed_df['下班时间'] = processed_df['下班时间'].apply(lambda x: x if is_time_format(str(x)) else '-')

    try:
        # 将清理后的 DataFrame 保存为新的 Excel 文件
        processed_df.to_excel(output_file, index=False)
    except Exception as e:
        logging.error(f"写入输出文件出错: {e}")
        return

    # 为每个人的数据创建字典
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

    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 8))

    for name, data in attendance_dict.items():
        ax.plot(data['dates'], data['start_times'], marker='o', linestyle='-', label=f'{name} - 上班时间')
        ax.plot(data['dates'], data['end_times'], marker='x', linestyle='--', label=f'{name} - 下班时间')

    # 设置图表格式
    plt.xlabel('日期')
    plt.ylabel('时间')
    plt.title('每日考勤时间分布')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    try:
        # 保存图表为文件
        plt.savefig(plot_file)
        plt.show()
    except Exception as e:
        logging.error(f"保存图表文件出错: {e}")

# 主函数
def main():
    parser = argparse.ArgumentParser(description='处理考勤数据并生成图表。')
    parser.add_argument('--input', type=str, required=True, help='输入 Excel 文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出 Excel 文件路径')
    parser.add_argument('--plot', type=str, required=True, help='输出图表文件路径')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    if os.path.exists(args.input):
        process_attendance(args.input, args.output, args.plot)
        logging.info(f'处理后的数据已保存到 {args.output}')
        logging.info(f'图表已保存到 {args.plot}')
    else:
        logging.error(f'输入文件 {args.input} 不存在')

if __name__ == "__main__":
    main()
