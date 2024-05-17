import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter, ImageOps
import os

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理器")
        self.root.geometry("800x600")

        # 初始化变量
        self.image = None
        self.image_path = None
        self.preview_image = None

        # 创建GUI元素
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.load_button = tk.Button(self.control_frame, text="加载图片", command=self.load_image)
        self.load_button.pack(pady=5)

        self.save_button = tk.Button(self.control_frame, text="保存图片", command=self.save_image)
        self.save_button.pack(pady=5)

        self.compression_frame = tk.LabelFrame(self.control_frame, text="压缩图片")
        self.compression_frame.pack(fill=tk.X, padx=5, pady=5)

        self.size_entry = tk.Entry(self.compression_frame)
        self.size_entry.pack(side=tk.LEFT, padx=5)
        self.size_entry.insert(0, "100")  # 默认100KB以下

        self.compress_button = tk.Button(self.compression_frame, text="压缩", command=self.compress_image)
        self.compress_button.pack(side=tk.LEFT, padx=5)

        self.effects_frame = tk.LabelFrame(self.control_frame, text="图像处理")
        self.effects_frame.pack(fill=tk.X, padx=5, pady=5)

        self.bw_button = tk.Button(self.effects_frame, text="黑白化", command=self.black_and_white)
        self.bw_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.gaussian_blur_button = tk.Button(self.effects_frame, text="高斯模糊", command=self.gaussian_blur)
        self.gaussian_blur_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.crop_frame = tk.LabelFrame(self.control_frame, text="裁切图片")
        self.crop_frame.pack(fill=tk.X, padx=5, pady=5)

        self.crop_x_entry = tk.Entry(self.crop_frame)
        self.crop_x_entry.pack(side=tk.LEFT, padx=5)
        self.crop_x_entry.insert(0, "0")

        self.crop_y_entry = tk.Entry(self.crop_frame)
        self.crop_y_entry.pack(side=tk.LEFT, padx=5)
        self.crop_y_entry.insert(0, "0")

        self.crop_width_entry = tk.Entry(self.crop_frame)
        self.crop_width_entry.pack(side=tk.LEFT, padx=5)
        self.crop_width_entry.insert(0, "100")

        self.crop_height_entry = tk.Entry(self.crop_frame)
        self.crop_height_entry.pack(side=tk.LEFT, padx=5)
        self.crop_height_entry.insert(0, "100")

        self.crop_button = tk.Button(self.crop_frame, text="裁切", command=self.crop_image)
        self.crop_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.resize_frame = tk.LabelFrame(self.control_frame, text="改变尺寸")
        self.resize_frame.pack(fill=tk.X, padx=5, pady=5)

        self.width_entry = tk.Entry(self.resize_frame)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        self.width_entry.insert(0, "800")

        self.height_entry = tk.Entry(self.resize_frame)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        self.height_entry.insert(0, "600")

        self.aspect_var = tk.BooleanVar()
        self.aspect_var.set(True)
        self.aspect_check = tk.Checkbutton(self.resize_frame, text="锁定纵横比", variable=self.aspect_var)
        self.aspect_check.pack(side=tk.LEFT, padx=5)

        self.resize_button = tk.Button(self.resize_frame, text="改变尺寸", command=self.resize_image)
        self.resize_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.format_frame = tk.LabelFrame(self.control_frame, text="转换格式")
        self.format_frame.pack(fill=tk.X, padx=5, pady=5)

        self.format_var = tk.StringVar()
        self.format_combobox = ttk.Combobox(self.format_frame, textvariable=self.format_var)
        self.format_combobox['values'] = ('JPEG', 'PNG', 'BMP', 'GIF')
        self.format_combobox.current(0)
        self.format_combobox.pack(side=tk.LEFT, padx=5)

        self.convert_button = tk.Button(self.format_frame, text="转换", command=self.convert_format)
        self.convert_button.pack(side=tk.LEFT, padx=5, pady=5)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if self.image_path:
            self.image = Image.open(self.image_path)
            self.display_image(self.image)

    def save_image(self):
        if self.preview_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"),
                                                                ("BMP files", "*.bmp"), ("GIF files", "*.gif")])
            if save_path:
                self.preview_image.save(save_path)
                messagebox.showinfo("保存图片", "图片已保存成功！")

    def display_image(self, image):
        self.preview_image = image
        img = ImageTk.PhotoImage(image.resize((400, 400), Image.LANCZOS))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def compress_image(self):
        if self.image:
            max_size_kb = int(self.size_entry.get())
            max_size_bytes = max_size_kb * 1024
            quality = 95

            while True:
                with open("temp.jpg", "wb") as temp_file:
                    self.image.save(temp_file, format="JPEG", quality=quality)
                if os.path.getsize("temp.jpg") <= max_size_bytes or quality <= 10:
                    break
                quality -= 5

            compressed_image = Image.open("temp.jpg")
            self.display_image(compressed_image)
            os.remove("temp.jpg")

    def black_and_white(self):
        if self.image:
            bw_image = self.image.convert("L")
            self.display_image(bw_image)

    def gaussian_blur(self):
        if self.image:
            blurred_image = self.image.filter(ImageFilter.GaussianBlur(5))
            self.display_image(blurred_image)

    def crop_image(self):
        if self.image:
            x = int(self.crop_x_entry.get())
            y = int(self.crop_y_entry.get())
            width = int(self.crop_width_entry.get())
            height = int(self.crop_height_entry.get())
            cropped_image = self.image.crop((x, y, x + width, y + height))
            self.display_image(cropped_image)

    def resize_image(self):
        if self.image:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            if self.aspect_var.get():
                self.image.thumbnail((width, height))
                resized_image = self.image
            else:
                resized_image = self.image.resize((width, height))
            self.display_image(resized_image)

    def convert_format(self):
        if self.image:
            format_ = self.format_var.get()
            converted_image = self.image
            self.display_image(converted_image)
            save_path = filedialog.asksaveasfilename(defaultextension=f".{format_.lower()}",
                                                     filetypes=[(f"{format_} files", f"*.{format_.lower()}")])
            if save_path:
                converted_image.save(save_path)
                messagebox.showinfo("转换格式", f"图片已转换为{format_}格式并保存成功！")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
