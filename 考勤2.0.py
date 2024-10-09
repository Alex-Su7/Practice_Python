import pandas as pd
import re
import logging
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog
from tkinter import messagebox
import threading

# 检查字符串是否为有效时间格式 (HH:MM)
def is_time_format(s):
    try:
        return bool(re.match(r"^\d{2}:\d{2}$", s))
    except:
        return False

# 解析考勤信息的函数
def parse_attendance_info(attendance_info):
    # 初始化
    start_time = ''
    end_time = ''
    start_status = ''
    end_status = ''

    if pd.isna(attendance_info) or attendance_info.strip() == '':
        return start_status, start_time, end_status, end_time

    # 分割多条记录
    records = attendance_info.split(';')
    for record in records:
        # 分割上班和下班信息
        parts = record.split(',')
        if len(parts) >= 2:
            # 处理上班信息
            start_match = re.match(r'(\w+)\((.*?)\)', parts[0].strip())
            if start_match:
                start_status = start_match.group(1)
                start_time = start_match.group(2)
            else:
                start_status = parts[0].strip()
                start_time = ''
            # 处理下班信息
            end_match = re.match(r'(\w+)\((.*?)\)', parts[1].strip())
            if end_match:
                end_status = end_match.group(1)
                end_time = end_match.group(2)
            else:
                end_status = parts[1].strip()
                end_time = ''
            break  # 只处理第一条记录
        elif len(parts) == 1:
            # 处理只有上班或下班信息的情况
            match = re.match(r'(\w+)\((.*?)\)', parts[0].strip())
            if match:
                start_status = match.group(1)
                start_time = match.group(2)
            else:
                start_status = parts[0].strip()
                start_time = ''
            end_status = start_status
            end_time = start_time
            break
        else:
            continue

    return start_status, start_time, end_status, end_time

# 处理考勤数据的函数
def process_attendance(input_file, output_file, lunch_start='12:00', lunch_end='13:30'):
    try:
        # 读取 Excel 文件，使用第二行作为列名
        data = pd.read_excel(input_file, header=1)
    except Exception as e:
        logging.error(f"读取输入文件出错: {e}")
        messagebox.showerror("错误", f"读取输入文件出错: {e}")
        return

    # 重命名第一列为 '姓名'（如果未命名）
    if data.columns[0] != '姓名':
        data.rename(columns={data.columns[0]: '姓名'}, inplace=True)

    if '姓名' not in data.columns:
        logging.error("输入文件缺少必要的列：姓名")
        messagebox.showerror("错误", "输入文件缺少必要的列：姓名")
        return

    # 获取考勤数据列的起始索引
    try:
        start_col_index = data.columns.tolist().index('迟到时长(小时)') + 1
    except ValueError:
        logging.error("无法找到'迟到时长(小时)'列")
        messagebox.showerror("错误", "无法找到'迟到时长(小时)'列")
        return

    # 获取考勤日期列
    attendance_columns = data.columns[start_col_index:]

    # 初始化一个空列表来存储处理后的记录
    processed_records = []

    # 遍历每个人的数据
    for index, row in data.iterrows():
        name = row['姓名']
        # 遍历考勤日期列
        for col in attendance_columns:
            # 列名示例：'2024-09-01 星期日'
            date_info = str(col).split(' ')
            if len(date_info) >= 2:
                date = date_info[0]
                day_of_week = date_info[1]
            else:
                date = date_info[0]
                day_of_week = ''
            
            attendance_info = row[col]
            start_status, start_time, end_status, end_time = parse_attendance_info(attendance_info)

            # 根据解析结果，确定上班时间和下班时间
            if start_status in ['休息', '请假']:
                actual_start_time = start_status
            elif start_status == '正常':
                actual_start_time = start_time if is_time_format(start_time) else '-'
            elif start_status in ['外出', '外勤']:
                actual_start_time = start_status
            else:
                actual_start_time = '-'

            if end_status in ['休息', '请假']:
                actual_end_time = end_status
            elif end_status == '正常':
                actual_end_time = end_time if is_time_format(end_time) else '-'
            elif end_status in ['外出', '外勤']:
                actual_end_time = end_status
            else:
                actual_end_time = '-'

            # 将处理后的记录添加到列表中
            processed_records.append([
                name,
                date,
                day_of_week,
                actual_start_time,
                lunch_start,
                lunch_end,
                actual_end_time
            ])

    # 从处理后的记录创建一个 DataFrame
    processed_df = pd.DataFrame(processed_records, columns=['姓名', '日期', '星期', '上班时间', '午休开始', '午休结束', '下班时间'])

    try:
        # 将清理后的 DataFrame 保存为新的 Excel 文件
        processed_df.to_excel(output_file, index=False)
        messagebox.showinfo("成功", "数据处理完成！")
    except Exception as e:
        logging.error(f"写入输出文件出错: {e}")
        messagebox.showerror("错误", f"写入输出文件出错: {e}")
        return

# GUI 应用
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("考勤数据处理")

        self.input_file = StringVar()
        self.output_file = StringVar()
        self.lunch_start = StringVar(value='12:00')
        self.lunch_end = StringVar(value='13:30')

        Label(root, text="输入文件路径").grid(row=0, column=0)
        Entry(root, textvariable=self.input_file, width=40).grid(row=0, column=1)
        Button(root, text="浏览", command=self.browse_input_file).grid(row=0, column=2)

        Label(root, text="输出文件路径").grid(row=1, column=0)
        Entry(root, textvariable=self.output_file, width=40).grid(row=1, column=1)
        Button(root, text="浏览", command=self.browse_output_file).grid(row=1, column=2)

        Label(root, text="午休开始时间").grid(row=2, column=0)
        Entry(root, textvariable=self.lunch_start, width=40).grid(row=2, column=1)

        Label(root, text="午休结束时间").grid(row=3, column=0)
        Entry(root, textvariable=self.lunch_end, width=40).grid(row=3, column=1)

        Button(root, text="处理数据", command=self.process_and_generate).grid(row=4, column=0, columnspan=3)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel文件", "*.xlsx")])
        if file_path:
            self.input_file.set(file_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel文件", "*.xlsx")])
        if file_path:
            self.output_file.set(file_path)

    def process_and_generate(self):
        if not self.input_file.get():
            messagebox.showwarning("警告", "请选择输入文件！")
            return
        if not self.output_file.get():
            messagebox.showwarning("警告", "请选择输出文件！")
            return

        threading.Thread(target=self.run_processing).start()

    def run_processing(self):
        process_attendance(
            self.input_file.get(),
            self.output_file.get(),
            self.lunch_start.get(),
            self.lunch_end.get()
        )

# 主函数
def main():
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    
    root = Tk()
    app = AttendanceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
