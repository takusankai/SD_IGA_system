# UI.py の print メッセージは「黄色」\033[93m で表示される
import os
import threading
import queue
import time
import csv
import ast
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv
from IGA_modules.IGA_module_2 import create_base_genes, create_next_generation_genes # ここを書き換える形で IGA のモジュールを変更する
from GENE import Gene
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
# 結果を格納するキューを作成
result_queue = queue.Queue()
# 現在の生成ステップ数を保持
generation = 1
# ループ終了世代数を設定
end_loop_generation = 10

# 全UI要素を初期化し、メインイベントループを開始する
def setup_ui():
    global window, input_field, start_iga_loop_button, first_image_label, upload_button, input_text_label, explain_text_label, gene_data_frame, gene_data_label, generation_step_label, remaining_time_label, generated_image_frame, generated_image_label, slider, next_generation_button, result_queue, generation, end_message_label, exit_button
    window = tk.Tk()
    window.geometry(f"{WINDOW_SIZE_HEIGHT}x{WINDOW_SIZE_WIDTH}")

    # 入力フィールドを作成
    input_field = tk.Text(window, font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (70/1000)), height=4, wrap=tk.WORD)
    input_field.insert("1.0", "自然豊かで子供向けの遊具が充実した、落ち着く景色でありかつ子供たちが楽しめる公園の情景")
    # 生成システム開始ボタンを作成
    start_iga_loop_button = tk.Button(window, text="生成システムを開始", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=first_iga_loop)
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
    # 生成画像表示フレームと8個の生成画像表示ラベルを作成
    generated_image_frame = tk.Frame(window)
    generated_image_label = [tk.Label(generated_image_frame, text=f"生成画像{i+1}", font=("Arial", FONT_SIZE), wraplength=int(WINDOW_SIZE_WIDTH * (200/1000))) for i in range(8)]
    # スライダーを作成
    slider = [tk.Scale(generated_image_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=250) for _ in range(8)]
    # 次の世代へ進むボタンを作成
    next_generation_button = tk.Button(window, text="次の世代へ進む", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=iga_loop)
    # 終了メッセージラベルとシステム終了ボタンを作成
    end_message_label = tk.Label(window, text="", font=("Arial", FONT_SIZE))
    exit_button = tk.Button(window, text="システムを終了する", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=window.quit)

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
    explain_text_label.config(text="以下の遺伝子情報を元に、画像生成を行っています。")
    gene_data_frame.pack(pady=10)
    for i in range(8):
        gene_data_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=10) # 2行4列に配置
    generation_step_label.pack(pady=10)
    remaining_time_label.pack(pady=10)

# 評価UIを表示
def show_evaluation_UI(end_flag=False):
    clear_ui()
    input_text_label.pack(pady=10)
    explain_text_label.pack(pady=10)
    explain_text_label.config(text="以下の画像評価点数により、要素が引き継がれる確率が決まります。")
    generated_image_frame.pack(pady=10)
    for i in range(8):
        generated_image_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=20)
        slider[i].set(0)
        slider[i].grid(row=(i//4)+2, column=(i%4), padx=20, pady=20)
    
    if end_flag:
        explain_text_label.config(text="評価終了")
        end_message_label.config(text="end_loop_generation世代の生成が終了しました。お疲れさまでした！")
        end_message_label.pack(pady=10)
        exit_button.pack(pady=10)
    else:
        next_generation_button.pack(pady=10)

def clear_ui():
    for widget in window.winfo_children():
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

# 初期UIから1週目の生成システムを開始する
def first_iga_loop():
    # まず入力文章を取得
    input_text = input_field.get("1.0", "end-1c")

    # 生成中UIを表示
    show_generate_UI()
    input_text_label.config(text=f"目標: {input_text}")
    generation_step_label.config(text=f"生成している世代は {generation} 世代目です")
    remaining_time_label.config(text="およその残り時間: 50秒")

    # 8つの初期遺伝子を作成し、表示する
    genes = create_base_genes(input_text, first_image_path)
    for i, gene in enumerate(genes):
        gene_data_label[i].config(text=str(gene))
        print(f"\033[93m遺伝子{i+1}の情報: {gene}\033[0m")

    # カウントダウンタイマースレッドを開始
    threading.Thread(target=update_remaining_time, args=(50,)).start()
    # 画像生成スレッドを開始
    threading.Thread(target=first_iga_loop_generate_thread, args=(genes,)).start()

# 1週目の生成システムの画像生成スレッド
def first_iga_loop_generate_thread(genes):
    # 作成した遺伝子を元に画像生成を実行し、表示する
    base_generator = ImageGenerator()
    base_images, image_paths = base_generator.generate_images(genes)

    # csv に遺伝子情報と生成画像情報を新規プロジェクトとして保存
    init_project_csv(genes, image_paths)

    # 評価UIを呼び出し、生成画像を表示する
    show_evaluation_UI()
    for i, image in enumerate(base_images):
        image = ImageTk.PhotoImage(image)
        generated_image_label[i].config(image=image)
        generated_image_label[i].image = image

def init_project_csv(genes, image_paths):
    print("\033[93m新規プロジェクトを作成し、遺伝子情報と生成画像情報を保存します\033[0m")
    if not os.path.exists("projects"):
        os.makedirs("projects")
        
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith("project_")]
    project_numbers.sort()

    if project_numbers:
        last_project_number = project_numbers[-1]
    else:
        last_project_number = 0
        print("\033[93mprojectsディレクトリ内に画像が存在しないため、project_1.jpgとして保存します。\033[0m")   
    project_name = "project_" + str(last_project_number + 1) + ".csv"

    # project_name で新規プロジェクトcsvを作成し、情報を保存する
    # id, generation, evaluation_score, this_image_path, init_image_path, image_strengs, seed, steps, prompt_length, cfg_scale, prompt
    # idは1から8までの連番、世代は1、評価点数は0、this_image_pathは空
    with open(os.path.join("projects", project_name), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "generation", "evaluation_score", "this_image_path", "init_image_path", "image_strengs", "seed", "steps", "prompt_length", "cfg_scale", "prompt"])
        for i, gene in enumerate(genes):
            writer.writerow([i+1, 1, 0, image_paths[i], str(os.path.normpath(first_image_path)), gene.image_strengs, gene.seed, gene.steps, gene.prompt_length, gene.cfg_scale, gene.prompt])

# 2週目以降の生成システムを開始する
def iga_loop():
    global generation
    generation += 1
    print(f"\033[93m{generation} 世代目の生成システムを開始します\033[0m")

    # まず評価点数を取得
    evaluation_scores = [slider[i].get() for i in range(8)]
    print(f"\033[93m評価点数: {evaluation_scores}\033[0m")

    # csv に評価点数を保存
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith("project_")]
    project_numbers.sort()
    project_name = "project_" + str(project_numbers[-1]) + ".csv"
    # csvを開き、最終行-7から最終行までの8行に評価点数を保存する
    with open(os.path.join("projects", project_name), "r+", newline='') as f:
        lines = f.readlines()
        last_line = len(lines) - 1
        for i in range(8):
            line = lines[last_line-7+i].strip().split(",")
            line[2] = str(evaluation_scores[i])  # 評価スコアを文字列に変換
            lines[last_line-7+i] = ",".join(line) + "\n"
        f.seek(0)
        f.writelines(lines)
        f.truncate()

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
        print(f"\033[93m遺伝子{i+1}の情報: {gene}\033[0m")

    # カウントダウンタイマースレッドを開始
    threading.Thread(target=update_remaining_time, args=(50,)).start()
    # 画像生成スレッドを開始
    threading.Thread(target=iga_loop_generate_thread, args=(next_genes,)).start()

# 2週目以降の生成システムの画像生成スレッド
def iga_loop_generate_thread(next_genes):
    # 遺伝子情報を元に画像生成を実行し、表示する
    next_generator = ImageGenerator()
    next_images, image_paths = next_generator.generate_images(next_genes)

    # csv に遺伝子情報と生成画像情報を保存
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith("project_")]
    project_numbers.sort()
    project_name = "project_" + str(project_numbers[-1]) + ".csv"

    with open(os.path.join("projects", project_name), "a", newline='') as f:
        writer = csv.writer(f)
        for i, gene in enumerate(next_genes):
            writer.writerow([generation * 8 - 7 + i, generation, 0, image_paths[i], gene.init_image_path, gene.image_strengs, gene.seed, gene.steps, gene.prompt_length, gene.cfg_scale, gene.prompt])

    # 評価UIを呼び出し、生成画像を表示する
    show_evaluation_UI(end_flag=(generation >= end_loop_generation)) # end_loop_generation世代で終了処理に移行
    for i, image in enumerate(next_images):
        image = ImageTk.PhotoImage(image)
        generated_image_label[i].config(image=image)
        generated_image_label[i].image = image

def get_last_generation_genes():
    # csv から前世代の遺伝子情報を取得
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith("project_")]
    project_numbers.sort()
    project_name = "project_" + str(project_numbers[-1]) + ".csv"
    last_generation_genes = []
    # csvを開き、最終行-7から最終行までの8行の遺伝子情報（評価とthis_image_pathも含む）を取得
    with open(os.path.join("projects", project_name), "r", newline='') as f:
        reader = csv.reader(f)
        next(reader) # ヘッダーをスキップ
        lines = list(reader)
        last_line = len(lines) - 1
        # 最終行-7から最終行までの8行のデータを、Gene クラスに変換してリストに追加
        for line in lines[last_line-7:]: 
            gene = Gene(
                init_image_path=os.path.normpath(line[4]),
                image_strengs=float(line[5]),
                seed=int(line[6]),
                steps=int(line[7]),
                prompt_length=int(line[8]),
                cfg_scale=float(line[9]),
                prompt=ast.literal_eval(line[10]), # 文字列をリストに変換
                this_image_path=os.path.normpath(line[3]),
                evaluation_score=int(line[2]) if line[2] else 1111 # エラー検証用の記録されないはずの値
            )
            last_generation_genes.append(gene)

    return last_generation_genes

if __name__ == "__main__":
    setup_ui()