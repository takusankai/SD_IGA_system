# UI.py の print メッセージは「黄色」で表示される
import os
import threading
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv(dotenv_path='settings.env')
if not os.path.exists('settings.env'): print('\033[93msettings.env の読み込みに失敗した為、デフォルト値を使用します\033[0m')
# 環境変数の取得(読み込めなければデフォルト値を使用)
WINDOW_SIZE_HEIGHT = int(os.getenv("WINDOW_SIZE_HEIGHT", 1300))
WINDOW_SIZE_WIDTH = int(os.getenv("WINDOW_SIZE_WIDTH", 1300))
FONT_SIZE = int(os.getenv("FONT_SIZE", 16))

# 全UI要素を初期化し、メインイベントループを開始する
def setup_ui():
    global window, input_field, start_igaloop_button, init_image_label, upload_button

    # tkメインウィンドウを作成
    window = tk.Tk()
    window.geometry(f"{WINDOW_SIZE_HEIGHT}x{WINDOW_SIZE_WIDTH}")

    # 入力フィールドを作成
    input_field = tk.Text(window, font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (70/1000)), height=4, wrap=tk.WORD)
    # 生成システム開始ボタンを作成
    start_igaloop_button = tk.Button(window, text="生成システムを開始", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=show_generate_UI)
    # 初期画像ラベルを作成
    init_image_label = tk.Label(window, text="ここに画像が表示されます", font=("Arial", FONT_SIZE), bd=1, relief="solid")
    # 画像アップロードボタンを作成
    upload_button = tk.Button(window, text="画像をアップロード", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=upload_image)

    # 初期画面を表示（中断復帰の際は、ここをshow_generate_UI()に変更する）
    show_init_UI()
    # メインイベントループを開始
    window.mainloop()

# 初期UIを表示
def show_init_UI():

    # 要素の配置
    input_field.pack(pady=10)
    start_igaloop_button.pack(pady=10)
    init_image_label.pack(pady=10)
    upload_button.pack(pady=10)

# 生成中UIを表示
def show_generate_UI():
    clear_ui()

# 評価UIを表示
def show_evaluation_UI():
    clear_ui()

def clear_ui():
    for widget in window.winfo_children():
        widget.destroy()

def upload_image():
    global init_image, init_image_path
    init_image_path = filedialog.askopenfilename(
        initialdir=r"C:\Users\吉岡拓真\Downloads\develop\SD_IGA_system\sample_images",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
    )
    
    if init_image_path:
        init_image = Image.open(init_image_path)
        init_image = init_image.resize((int(WINDOW_SIZE_HEIGHT * (250/1000)), int(WINDOW_SIZE_WIDTH * (250/1000))))
        init_image = ImageTk.PhotoImage(init_image)
        init_image_label.config(image=init_image)
        
if __name__ == "__main__":
    setup_ui()