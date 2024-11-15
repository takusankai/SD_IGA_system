# UI.py の print メッセージは「黄色」で表示される
import os
import threading
import queue
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv
from IGA import Gene, create_base_genes

# .envファイルの読み込み
load_dotenv(dotenv_path='settings.env')
if not os.path.exists('settings.env'): print('\033[93msettings.env の読み込みに失敗した為、デフォルト値を使用します\033[0m')
# 環境変数の取得(読み込めなければデフォルト値を使用)
WINDOW_SIZE_HEIGHT = int(os.getenv("WINDOW_SIZE_HEIGHT", 1300))
WINDOW_SIZE_WIDTH = int(os.getenv("WINDOW_SIZE_WIDTH", 1300))
FONT_SIZE = int(os.getenv("FONT_SIZE", 16))

# 全UI要素を初期化し、メインイベントループを開始する
def setup_ui():
    global window, input_field, start_iga_loop_button, first_image_label, upload_button, input_text_label, explain_text_label, gene_data_frame, gene_data_label, generation_step_label, remaining_time_label, result_queue

    # tkメインウィンドウを作成
    window = tk.Tk()
    window.geometry(f"{WINDOW_SIZE_HEIGHT}x{WINDOW_SIZE_WIDTH}")

    # 入力フィールドを作成
    input_field = tk.Text(window, font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (70/1000)), height=4, wrap=tk.WORD)
    # 生成システム開始ボタンを作成
    start_iga_loop_button = tk.Button(window, text="生成システムを開始", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=start_iga_loop)
    # 初期画像ラベルを作成
    first_image_label = tk.Label(window, text="ここに画像が表示されます", font=("Arial", FONT_SIZE), bd=1, relief="solid")
    # 画像アップロードボタンを作成
    upload_button = tk.Button(window, text="画像をアップロード", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=upload_image)
    # 入力文章表示ラベルを作成
    input_text_label = tk.Label(window, text="", font=("Arial", FONT_SIZE))
    # 説明文章表示ラベルを作成
    explain_text_label = tk.Label(window, text="", font=("Arial", FONT_SIZE))
    # 遺伝子情報表示フレームと8個の遺伝子情報表示ラベルを作成
    gene_data_frame = tk.Frame(window)
    gene_data_label = [tk.Label(gene_data_frame, text=f"遺伝子{i+1}", font=("Arial", FONT_SIZE), wraplength=int(WINDOW_SIZE_WIDTH * (200/1000))) for i in range(8)]
    # 現在世代数表示ラベルを作成
    generation_step_label = tk.Label(window, text="", font=("Arial", FONT_SIZE))
    # 想定残り時間表示ラベルを作成
    remaining_time_label = tk.Label(window, text="", font=("Arial", FONT_SIZE))

    # 結果を格納するキューを作成
    result_queue = queue.Queue()

    # 初期画面を表示（中断復帰の際は、ここをshow_generate_UI()に変更する）
    show_init_UI()
    # メインイベントループを開始
    window.mainloop()

# 初期UIを表示
def show_init_UI():
    # 要素の配置
    input_field.pack(pady=10)
    start_iga_loop_button.pack(pady=10)
    first_image_label.pack(pady=10)
    upload_button.pack(pady=10)

# 生成中UIを表示
def show_generate_UI():
    # 要素の配置
    clear_ui()
    input_text_label.pack(pady=10)
    explain_text_label.pack(pady=10)
    gene_data_frame.pack(pady=10)
    for i in range(8):
        gene_data_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=10) # 2行4列に配置
    generation_step_label.pack(pady=10)
    remaining_time_label.pack(pady=10)

# 評価UIを表示
def show_evaluation_UI():
    clear_ui()

# 初期UIから生成システムを開始する
def start_iga_loop():
    # まず入力文章と画像を取得
    input_text = input_field.get("1.0", "end-1c")
    input_image = first_image_label.cget("image")

    # 生成中UIを表示
    show_generate_UI()
    input_text_label.config(text=f"目標: {input_text}")

    # 別スレッドで遺伝子を作成する
    gene_thread = threading.Thread(target=create_genes, args=(input_text, input_image, result_queue))
    gene_thread.start()

    # スレッドの終了を待つ
    window.after(100, lambda: check_thread(gene_thread))

    # queueの中身を取得
    genes = result_queue.get_nowait()
    print(genes)
    
def check_thread(thread):
    if thread.is_alive():
        window.after(100, lambda: check_thread(thread))
    else:
        genes = result_queue.get()
        for i, gene in enumerate(genes):
            gene_data_label[i].config(text=str(gene))
        print("遺伝子の作成が完了しました")

def create_genes(input_text, input_image, result_queue):
    # 8つの遺伝子を作成する
    genes = create_base_genes(input_text, input_image)

    # 結果をキューに入れる
    result_queue.put(genes)

def clear_ui():
    for widget in window.winfo_children():
        widget.pack_forget()
        widget

def upload_image():
    global first_image, first_image_path
    first_image_path = filedialog.askopenfilename(
        initialdir="D:\downloads\develop\SD_IGA_system\sample_images",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
    )
    
    if first_image_path:
        first_image = Image.open(first_image_path)
        first_image = first_image.resize((int(WINDOW_SIZE_HEIGHT * (500/1000)), int(WINDOW_SIZE_WIDTH * (500/1000))))
        first_image = ImageTk.PhotoImage(first_image)
        first_image_label.config(image=first_image)
        first_image_label.image = first_image  # 参照を保持するために必要

if __name__ == "__main__":
    setup_ui()