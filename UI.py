# UI.py の print メッセージは「黄色」で表示される
import os
import threading
import time
import csv
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv
from IGA_modules.IGA_module_4 import create_base_genes, create_next_generation_genes # ここを書き換える形で IGA のモジュールを変更する
from CSV import * # CSV.py の全ての関数をインポート
from SD import ImageGenerator

# .envファイルの読み込み
load_dotenv(dotenv_path='settings.env')
if not os.path.exists('settings.env'):
    print('\033[93msettings.env の読み込みに失敗した為、UI 設定はデフォルト値を使用します\033[0m')
# 環境変数の取得(読み込めなければデフォルト値を使用)
WINDOW_SIZE_HEIGHT = int(os.getenv("WINDOW_SIZE_HEIGHT", 1300))
WINDOW_SIZE_WIDTH = int(os.getenv("WINDOW_SIZE_WIDTH", 1300))
FONT_SIZE = int(os.getenv("FONT_SIZE", 16))

# グローバル変数の宣言
# 現在の生成ステップ数を保持
generation = 1
# 初期画像のパスを保持
first_image_path = ""
# 評価UIにて、お気に入りの状態を保持するリスト
favorite_states = [False] * 8
# 評価UIにて、遺伝子情報の表示/非表示の状態を保持する変数
show_gene_status = False

# 全UI要素を初期化し、メインイベントループを開始する
def setup_ui():
    global window, canvas, scrollbar, scrollable_frame, input_field, start_iga_loop_button, first_image_label, upload_button, input_text_label, explain_text_label, gene_data_frame, gene_data_label, generation_step_label, remaining_time_label, generated_image_frame, generated_image_label, sliders, favorite_buttons, before_star_image, after_star_image, next_generation_button, end_loop_button, show_gene_switch, favorite_images_frame, end_message_label, exit_button
    window = tk.Tk()
    window.geometry(f"{WINDOW_SIZE_HEIGHT}x{WINDOW_SIZE_WIDTH}")

    # キャンバスとスクロールバーを作成
    canvas = tk.Canvas(window)
    scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((60, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # スクロールバーとキャンバスを配置
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 入力フィールドを作成
    input_field = tk.Text(scrollable_frame, font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (70/1000)), height=4, wrap=tk.WORD)
    input_field.insert("1.0", "滑り台、揺れる動物の遊具、ブランコなど、多くの遊具が設置された子供向けの公園")
    # 生成システム開始ボタンを作成
    start_iga_loop_button = tk.Button(scrollable_frame, text="生成システムを開始", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=first_iga_loop)
    # 初期画像ラベルを作成
    first_image_label = tk.Label(scrollable_frame, text="ここに画像が表示されます", font=("Arial", FONT_SIZE), bd=1, relief="solid")
    # 画像アップロードボタンを作成
    upload_button = tk.Button(scrollable_frame, text="画像をアップロード", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=upload_image)
    # 入力文章表示ラベルを作成
    input_text_label = tk.Label(scrollable_frame, text="", font=("Arial", FONT_SIZE))
    # 説明文章表示ラベルを作成
    explain_text_label = tk.Label(scrollable_frame, text="", font=("Arial", FONT_SIZE))
    # 遺伝子情報表示フレームと8個の遺伝子情報表示ラベルを作成
    gene_data_frame = tk.Frame(scrollable_frame)
    gene_data_label = [tk.Label(gene_data_frame, text=f"遺伝子{i+1}", font=("Arial", FONT_SIZE), wraplength=int(WINDOW_SIZE_WIDTH * (200/1000))) for i in range(8)]
    # 現在世代数表示ラベルを作成
    generation_step_label = tk.Label(scrollable_frame, text="", font=("Arial", FONT_SIZE))
    # 想定残り時間表示ラベルを作成
    remaining_time_label = tk.Label(scrollable_frame, text="", font=("Arial", FONT_SIZE))
    # 生成画像表示フレームと8個の生成画像表示ラベルを作成
    generated_image_frame = tk.Frame(scrollable_frame)
    generated_image_label = [tk.Label(generated_image_frame, text=f"生成画像{i+1}", font=("Arial", FONT_SIZE), wraplength=int(WINDOW_SIZE_WIDTH * (200/1000))) for i in range(8)]
    # スライダーを作成
    sliders = [tk.Scale(generated_image_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=250) for _ in range(8)]
    for slider in sliders:
        slider.set(50) # 初期値を50に設定
    # お気に入りボタンを作成
    favorite_buttons = [tk.Button(generated_image_frame, command=lambda i=i: toggle_favorite(i)) for i in range(8)]
    # 星マークの画像を読み込む
    before_star_image = ImageTk.PhotoImage(Image.open("before_star_image.png").resize((30, 30)))
    after_star_image = ImageTk.PhotoImage(Image.open("after_star_image.png").resize((30, 30)))
    for button in favorite_buttons:
        button.config(image=before_star_image)
        button.image_before = before_star_image
        button.image_after = after_star_image
    # 次の世代へ進むボタンを作成
    next_generation_button = tk.Button(scrollable_frame, text="次の世代へ進む", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=iga_loop)
    # この世代で終了するボタンを作成
    end_loop_button = tk.Button(scrollable_frame, text="この世代で終了する", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=iga_loop_end)
    # 評価UIに遺伝情報を表示する/しない選択スイッチを作成
    show_gene_switch = tk.Button(scrollable_frame, text="遺伝子情報を表示する", font=("Arial", int(FONT_SIZE / 2)), width=int(WINDOW_SIZE_WIDTH * (20/1000)), height=1, command=toggle_show_gene_status)
    # お気に入り画像全一覧表示フレームを作成
    favorite_images_frame = tk.Frame(scrollable_frame)
    # 終了メッセージラベルとシステム終了ボタンを作成
    end_message_label = tk.Label(scrollable_frame, text="", font=("Arial", FONT_SIZE))
    exit_button = tk.Button(scrollable_frame, text="システムを終了する", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=window.quit)

    # 初期画面を表示（中断復帰の際は、ここをshow_generate_UI()に変更する）
    show_init_UI()
    # メインイベントループを開始
    scrollable_frame.mainloop()

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
    explain_text_label.config(text="以下の遺伝子情報を元に、画像生成を行っています。")
    gene_data_frame.pack(pady=10)
    for i in range(8):
        gene_data_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=10) # 2行4列に配置
        gene_data_label[i].config(font=("Arial", FONT_SIZE)) # フォントサイズを標準にする
    generation_step_label.pack(pady=10)
    remaining_time_label.pack(pady=10)

# 評価UIを表示
def show_evaluation_UI(redraw=False):
    clear_ui()
    input_text_label.pack(pady=10)
    explain_text_label.pack(pady=10)
    explain_text_label.config(text="以下の画像評価点数により、要素が引き継がれる確率が決まります。")
    generated_image_frame.pack(pady=10)
    for i in range(8):
        generated_image_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=20)
        if not redraw: sliders[i].set(50) # 表示/非表示の切り替え時はスライダーの値をリセットしない
        sliders[i].grid(row=(i//4)+2, column=(i%4), padx=5, pady=20, sticky="w")
        favorite_states[i] = False
        favorite_buttons[i].config(image=favorite_buttons[i].image_before)
        favorite_buttons[i].grid(row=(i//4)+2, column=(i%4), padx=0, pady=20, sticky="e")
    # 遺伝子情報の表示/非表示スイッチを表示
    show_gene_switch.pack(pady=10)
    # 表示状態に応じて遺伝子情報を表示
    if show_gene_status:
        gene_data_frame.pack(pady=10)
        for i in range(8):
            gene_data_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=10) # 2行4列に配置
            gene_data_label[i].config(font=("Arial", int(FONT_SIZE / 1.5))) # フォントサイズを縮小する
    next_generation_button.pack(pady=10)
    end_loop_button.pack(pady=10)

# 終了UIを表示
def show_finish_UI():
    clear_ui()
    input_text_label.pack(pady=10)
    end_message_label.pack(pady=10)
    end_message_label.config(text=f"{generation} 世代目でシステムを終了します。お疲れ様でした。")
    explain_text_label.pack(pady=10)
    explain_text_label.config(text="評価終了です。以下の画像がお気に入り画像として保存されました。")
    favorite_images_frame.pack(pady=10)
    # 最新の favorite_n.csv を読み込み、全てのお気に入り画像のパスを取得し、その数だけ favorite_images_frame の内にラベルを作成して表示する
    favorite_files = os.listdir("projects")
    favorite_numbers = [int(f.split("_")[-1].split(".")[0]) for f in favorite_files if f.startswith("favorite_")]
    favorite_numbers.sort()
    favorite_name = "favorite_" + str(favorite_numbers[-1]) + ".csv"
    with open(os.path.join("projects", favorite_name), "r", newline='') as f:
        reader = csv.reader(f)
        next(reader)
        lines = list(reader)
        for i, line in enumerate(lines):
            favorite_image_path = line[2]
            print(f"\033[93mお気に入り画像{i+1}のパス: {favorite_image_path}\033[0m")
            favorite_image = Image.open(favorite_image_path)
            favorite_image = favorite_image.resize((int(WINDOW_SIZE_HEIGHT * (200/1000)), int(WINDOW_SIZE_WIDTH * (200/1000))))
            favorite_image = ImageTk.PhotoImage(favorite_image)
            favorite_image_label = tk.Label(favorite_images_frame, image=favorite_image)
            favorite_image_label.image = favorite_image
            favorite_image_label.grid(row=(i//4), column=(i%4), padx=20, pady=20)
    exit_button.pack(pady=10)

def clear_ui():
    for widget in scrollable_frame.winfo_children():
        widget.pack_forget()

def upload_image():
    global first_image_path
    first_image_path = filedialog.askopenfilename(
        initialdir="D:\downloads\develop\SD_IGA_system\sample_images",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png")]
    )
    
    if first_image_path:
        first_image = Image.open(first_image_path)
        first_image = first_image.resize((int(WINDOW_SIZE_HEIGHT * (700/1000)), int(WINDOW_SIZE_WIDTH * (700/1000))))
        first_image = ImageTk.PhotoImage(first_image)
        first_image_label.config(image=first_image)
        first_image_label.image = first_image

def update_remaining_time(seconds):
    for remaining in range(seconds, -1, -1):
        remaining_time_label.config(text=f"およその残り時間: {remaining}秒")
        time.sleep(1)

def toggle_favorite(i):
    favorite_states[i] = not favorite_states[i]
    if favorite_states[i]:
        favorite_buttons[i].config(image=favorite_buttons[i].image_after)
    else:
        favorite_buttons[i].config(image=favorite_buttons[i].image_before)

def toggle_show_gene_status():
    global show_gene_status
    show_gene_status = not show_gene_status
    print(f"\033[93m遺伝子情報の表示状態: {show_gene_status}\033[0m")
    if show_gene_status:
        show_gene_switch.config(text="遺伝子情報を非表示にする")
    else:
        show_gene_switch.config(text="遺伝子情報を表示する")
    show_evaluation_UI(redraw=True)

# 初期UIから1週目の生成システムを開始する
def first_iga_loop():
    # まず入力文章を取得
    input_text = input_field.get("1.0", "end-1c")

    # 生成中UIを表示
    show_generate_UI()
    input_text_label.config(text=f"目標: {input_text}")
    generation_step_label.config(text=f"生成している世代は {generation} 世代目です")
    remaining_time_label.config(text="およその残り時間: 50秒")

    # 8つの初期遺伝子とプロンプト辞書を作成し、表示する
    genes, prompt_dictionaly = create_base_genes(input_text)

    # csv に prompt_dictionaly を新規辞書として保存
    init_dictionary_csv(prompt_dictionaly)
        
    for i, gene in enumerate(genes):
        gene_data_label[i].config(text=str(gene))
        print(f"\033[93m遺伝子{i+1}の情報:\n{gene}\033[0m")

    # カウントダウンタイマースレッドを開始
    threading.Thread(target=update_remaining_time, args=(50,)).start()
    # 画像生成スレッドを開始
    threading.Thread(target=first_iga_loop_generate_thread, args=(genes,)).start()

# 1週目の生成システムの画像生成スレッド
def first_iga_loop_generate_thread(genes):
    # 作成した遺伝子を元に画像生成を実行し、表示する
    base_generator = ImageGenerator()
    # first_image_path が存在する/しないで分岐
    if first_image_path:
        base_images, this_image_paths = base_generator.i2i_generate_images(genes, first_image_path)
    else:
        base_images, this_image_paths = base_generator.t2i_generate_images(genes)

    # csv に遺伝子情報と生成画像情報を新規プロジェクトとして保存
    init_project_csv(genes, this_image_paths)
    # csv にお気に入り情報を保存できるように初期化
    init_favorite_csv()

    # 評価UIを呼び出し、生成画像を表示する
    show_evaluation_UI()
    for i, image in enumerate(base_images):
        image = ImageTk.PhotoImage(image)
        generated_image_label[i].config(image=image)
        generated_image_label[i].image = image

# 2週目以降の生成システムを開始する
def iga_loop():
    global generation
    generation += 1
    print(f"\033[93m{generation} 世代目の生成システムを開始します\033[0m")

    # 評価点数とお気に入り情報を保存
    save_user_evaluations()

    # 生成中UIを表示
    input_text = input_text_label.cget("text")
    show_generate_UI()
    input_text_label.config(text=f"{input_text}")
    generation_step_label.config(text=f"生成している世代は {generation} 世代目です")
    remaining_time_label.config(text="およその残り時間: 50秒")

    # 前世代の遺伝子情報を取得し、次世代の遺伝子を生成
    before_genes = get_last_generation_genes()
    next_genes = create_next_generation_genes(before_genes)

    # 生成した遺伝子情報を表示
    for i, gene in enumerate(next_genes):
        gene_data_label[i].config(text=str(gene))
        print(f"\033[93m遺伝子{i+1}の情報:\n{gene}\033[0m")

    # カウントダウンタイマースレッドを開始
    threading.Thread(target=update_remaining_time, args=(50,)).start()
    # 画像生成スレッドを開始
    threading.Thread(target=iga_loop_generate_thread, args=(next_genes,)).start()

# 2週目以降の生成システムの画像生成スレッド
def iga_loop_generate_thread(next_genes):
    # 遺伝子情報を元に画像生成を実行し、表示する
    next_generator = ImageGenerator()

    # first_image_path が存在する/しないで分岐
    if first_image_path:
        next_images, this_image_paths = next_generator.i2i_generate_images(next_genes, first_image_path)
    else:
        next_images, this_image_paths = next_generator.t2i_generate_images(next_genes)

    # csv に遺伝子情報と生成画像情報を保存
    save_genes_and_images(next_genes, this_image_paths, generation)
    
    # 評価UIを呼び出し、生成画像を表示する
    show_evaluation_UI()
    for i, image in enumerate(next_images):
        image = ImageTk.PhotoImage(image)
        generated_image_label[i].config(image=image)
        generated_image_label[i].image = image

def iga_loop_end():
    # 評価点数とお気に入り情報を保存
    save_user_evaluations()

    # 終了UIを表示
    input_text = input_text_label.cget("text")
    show_finish_UI()
    input_text_label.config(text=f"{input_text}")

def save_user_evaluations():
    # まず評価点数を取得
    evaluation_scores = [sliders[i].get() for i in range(8)]
    print(f"\033[93m評価点数: {evaluation_scores}\033[0m")
    # csv に評価点数を保存
    save_evaluation_scores(evaluation_scores)

    # 続いてお気に入りの画像を取得
    is_favorite_images = [favorite_states[i] for i in range(8)]
    print(f"\033[93mお気に入りの画像: {is_favorite_images}\033[0m")
    # csv にお気に入り情報を保存
    save_favorite_images(is_favorite_images, generation)

if __name__ == "__main__":
    setup_ui()