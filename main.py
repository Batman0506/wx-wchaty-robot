import subprocess
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import threading
import os
import time

class App:
    def __init__(self, master):
        self.master = master
        master.title("npm run start GUI")

        # 创建 "登录二维码：" 标签
        self.qr_label = tk.Label(master, text="微信扫码:")
        self.qr_label.pack(side=tk.LEFT, pady=5)

        # 创建图像显示框
        self.image_label = tk.Label(master)
        self.image_label.pack(side=tk.LEFT, pady=5)

        # 创建启动按钮
        self.start_button = tk.Button(master, text="启动", command=self.start_npm)
        self.start_button.pack(side=tk.LEFT, pady=10, padx=10)

        # 创建文本框，用于显示输出
        self.output_text = scrolledtext.ScrolledText(master, width=80, height=25)  # 调整 width 和 height 来适应需要的大小
        self.output_text.pack(pady=10)

        # 保存上一次图像的修改时间
        self.last_modified_time = None

        # 是否启动按钮被点击标志
        self.start_button_clicked = False

        # 在单独的线程中定时检测 qrcode.png 是否有更新
        threading.Thread(target=self.check_qrcode_update, daemon=True).start()

        # 初始信息
        self.output_text.insert(tk.END, "微信转发机器人，目前主要功能是微信小号扫码登录，可以转发小号所在的所有群的信息。把小号充当机器人。闲时自己开发，可能有意想不到的bug。\n流程：\n1.点击启动，输出框显示QR code saved to qrcode.png之后（重点！！一定要等到他显示，不然扫的就是过期的码！！）\n2.微信扫码。\n3.测试是否可以\n")

    def start_npm(self):
        # 在单独的线程中执行 npm run start 命令
        threading.Thread(target=self.execute_npm).start()
        # 启动按钮被点击
        self.start_button_clicked = True

    def execute_npm(self):
        try:
            # 启动 npm run start 命令，使用二进制模式
            process = subprocess.Popen('npm run start', shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=False)

            # 逐行读取输出并在主线程更新 GUI
            for line in process.stdout:
                # 解码使用 utf-8
                decoded_line = line.decode('utf-8', errors='replace')

                # 将字符串拆分为适当长度的行
                lines = [decoded_line[i:i+80] for i in range(0, len(decoded_line), 80)]

                # 在主线程更新 GUI
                for l in lines:
                    self.master.after(0, lambda: self.update_output(l))

                    # 如果按钮已经点击且检测到 "QR code saved to qrcode.png" 就显示图像
                    if self.start_button_clicked and "QR code saved to qrcode.png" in l:
                        self.master.after(0, self.show_image)
                        self.update_output(f"可以开始扫码啦！\n")

            # 等待命令执行完成
            process.wait()

            # 在主线程更新 GUI，显示命令结束后的输出
            remaining_output = process.stdout.read().decode('utf-8', errors='replace')
            self.master.after(0, lambda: self.update_output(remaining_output))
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，在主线程更新 GUI 显示错误信息
            self.master.after(0, lambda: self.update_output(f"命令执行失败，返回码：{e.returncode}\n{e.output.decode('utf-8', errors='replace')}"))

    def update_output(self, text):
        # 在文本框中追加输出
        self.output_text.insert(tk.END, text)

    def check_qrcode_update(self):
        while True:
            if self.start_button_clicked:
                # 检查 qrcode.png 的修改时间
                modified_time = os.path.getmtime('qrcode.png')

                # 如果修改时间有变化，更新图像
                if modified_time != self.last_modified_time:
                    self.last_modified_time = modified_time
                    self.master.after(0, self.show_image)

            # 每隔一段时间检查一次
            time.sleep(1)

    def show_image(self):
        # 获取图像的绝对路径
        image_path = os.path.abspath('qrcode.png')

        # 显示图像到输出框
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

# 创建主窗口
root = tk.Tk()
app = App(root)

# 运行主循环
root.mainloop()
