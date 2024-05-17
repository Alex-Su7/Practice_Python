import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# 用于保存原始文件名和路径的文件
backup_file = "file_backup.txt"

def save_original_names(directory):
    with open(backup_file, "w") as f:
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)):
                f.write(f"{filename}\n")
    messagebox.showinfo("备份完成", "文件名备份已保存")

def add_suffix(directory, suffix):
    save_original_names(directory)
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            base, ext = os.path.splitext(filename)
            new_name = base + suffix + ext
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
    messagebox.showinfo("完成", f"已在所有文件名末尾添加后缀：{suffix}")

def add_current_time(directory):
    save_original_names(directory)
    current_time = datetime.datetime.now().strftime("_%Y%m%d%H%M%S")
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            base, ext = os.path.splitext(filename)
            new_name = base + current_time + ext
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
    messagebox.showinfo("完成", "已在所有文件名末尾添加当前时间")

def add_prefix(directory, prefix):
    save_original_names(directory)
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            new_name = prefix + filename
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
    messagebox.showinfo("完成", f"已在所有文件名前添加前缀：{prefix}")

def undo_changes(directory):
    if not os.path.exists(backup_file):
        messagebox.showwarning("警告", "没有备份文件，无法撤回")
        return
    
    with open(backup_file, "r") as f:
        original_names = f.read().splitlines()
    
    for original_name in original_names:
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)):
                base, ext = os.path.splitext(filename)
                if original_name.startswith(base.split('_')[0]):  # Match with the original name base
                    os.rename(os.path.join(directory, filename), os.path.join(directory, original_name))
                    break
    messagebox.showinfo("完成", "已撤回所有文件名修改")

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        entry_directory.delete(0, tk.END)
        entry_directory.insert(0, directory)

def execute_action():
    directory = entry_directory.get()
    if not directory:
        messagebox.showwarning("警告", "请先选择文件夹路径")
        return
    
    if var.get() == 1:
        suffix = entry_suffix.get()
        if not suffix:
            messagebox.showwarning("警告", "请先输入后缀")
            return
        add_suffix(directory, suffix)
    elif var.get() == 2:
        add_current_time(directory)
    elif var.get() == 3:
        prefix = entry_prefix.get()
        if not prefix:
            messagebox.showwarning("警告", "请先输入前缀")
            return
        add_prefix(directory, prefix)
    elif var.get() == 4:
        undo_changes(directory)
    else:
        messagebox.showwarning("警告", "请选择操作类型")

def update_clock():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clock_label.config(text=now)
    root.after(1000, update_clock)

# 创建主窗口
root = tk.Tk()
root.title("批量修改文件名")

# 文件夹选择框
tk.Label(root, text="文件夹路径:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
entry_directory = tk.Entry(root, width=50)
entry_directory.grid(row=0, column=1, padx=10, pady=5)
btn_browse = tk.Button(root, text="浏览", command=select_directory)
btn_browse.grid(row=0, column=2, padx=10, pady=5)

# 操作类型选择
var = tk.IntVar()
tk.Label(root, text="选择操作类型:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
tk.Radiobutton(root, text="添加后缀", variable=var, value=1).grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
tk.Radiobutton(root, text="添加当前时间", variable=var, value=2).grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
tk.Radiobutton(root, text="添加前缀", variable=var, value=3).grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
tk.Radiobutton(root, text="撤回", variable=var, value=4).grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

# 输入框
entry_suffix = tk.Entry(root, width=20)
entry_prefix = tk.Entry(root, width=20)
tk.Label(root, text="后缀:").grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
entry_suffix.grid(row=1, column=3, padx=10, pady=5)
tk.Label(root, text="前缀:").grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)
entry_prefix.grid(row=3, column=3, padx=10, pady=5)

# 执行按钮
btn_execute = tk.Button(root, text="执行", command=execute_action)
btn_execute.grid(row=5, column=1, padx=10, pady=10, columnspan=2)

# 时钟模块
clock_label = tk.Label(root, font=('times', 20, 'bold'))
clock_label.grid(row=6, column=0, columnspan=4, pady=10)
update_clock()

# 运行主循环
root.mainloop()
