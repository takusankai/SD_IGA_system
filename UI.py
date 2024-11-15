# UI.py の print メッセージは「黄色」で表示される
import os
import threading
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv(dotenv_path='local_settings.env')
# 環境変数の取得(読み込めなければデフォルト値を使用)
WINDOW_SIZE_HEIGHT = int(os.getenv("WINDOW_SIZE_HEIGHT", 1300))
WINDOW_SIZE_WIDTH = int(os.getenv("WINDOW_SIZE_WIDTH", 1300))
FONT_SIZE = int(os.getenv("FONT_SIZE", 16))

# 全UI要素を初期化し、メインイベントループを開始する
def setup_ui():
    global window, input_field, button

    # tkメインウィンドウを作成
    window = tk.Tk()
    window.geometry(f"{WINDOW_SIZE_HEIGHT}x{WINDOW_SIZE_WIDTH}")

    # 入力フィールドと決定ボタンを作成
    input_field = tk.Text(window, font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (10/100)), height=5, wrap=tk.WORD)
    button = tk.Button(window, text="生成", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (5/100)), height=2, command=show_generate_UI)

    # 初期画面を表示
    show_init_UI()
    
    # メインイベントループを開始
    window.mainloop()

def show_init_UI():
    global input_field, button

    # 入力フィールドと決定ボタンを配置
    input_field.pack()
    button.pack()

def show_generate_UI():
    global input_field, button

    # 入力フィールドと決定ボタンを削除
    input_field.pack_forget()
    button.pack_forget()

if __name__ == "__main__":
    setup_ui()