# UI.py の print メッセージは「黄色」で表示される
import os
import threading
import queue
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv
from IGA import Gene, create_base_genes
from SD import ImageGenerator

# .envファイルの読み込み
load_dotenv(dotenv_path='settings.env')
if not os.path.exists('settings.env'):
    print('\033[93msettings.env の読み込みに失敗した為、UI 設定はデフォルト値を使用します\033[0m')
# 環境変数の取得(読み込めなければデフォルト値を使用)
WINDOW_SIZE_HEIGHT = int(os.getenv("WINDOW_SIZE_HEIGHT", 1300))
WINDOW_SIZE_WIDTH = int(os.getenv("WINDOW_SIZE_WIDTH", 1300))
FONT_SIZE = int(os.getenv("FONT_SIZE", 16))

# 全UI要素を初期化し、メインイベントループを開始する
def setup_ui():
    global window, input_field, start_iga_loop_button, first_image_label, upload_button, input_text_label, explain_text_label, gene_data_frame, gene_data_label, generation_step_label, remaining_time_label, generated_image_frame, generated_image_label, slider, slider_value_label, next_generation_button, result_queue
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
    # 生成画像表示フレームと8個の生成画像表示ラベルを作成
    generated_image_frame = tk.Frame(window)
    generated_image_label = [tk.Label(generated_image_frame, text=f"生成画像{i+1}", font=("Arial", FONT_SIZE), wraplength=int(WINDOW_SIZE_WIDTH * (200/1000))) for i in range(8)]
    # スライダーと文字表示枠を作成
    slider = [tk.Scale(generated_image_frame, from_=0, to=100, orient=tk.HORIZONTAL) for _ in range(8)]
    slider_value_label = [tk.Label(generated_image_frame, text="0", font=("Arial", FONT_SIZE)) for _ in range(8)]
    # 次の世代へ進むボタンを作成
    next_generation_button = tk.Button(window, text="次の世代へ進む", font=("Arial", FONT_SIZE), width=int(WINDOW_SIZE_WIDTH * (40/1000)), height=2, command=iga_loop)

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
    explain_text_label.config(text="以下に表示される遺伝子情報を元に、画像生成を行っています。")
    gene_data_frame.pack(pady=10)
    for i in range(8):
        gene_data_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=10)
    generation_step_label.pack(pady=10)
    remaining_time_label.pack(pady=10)

# 評価UIを表示
def show_evaluation_UI():
    # 要素の配置
    clear_ui()
    input_text_label.pack(pady=10)
    explain_text_label.pack(pady=10)
    explain_text_label.config(text="以下の画像評価点数により、要素が引き継がれる確率が決まります。")
    generated_image_frame.pack(pady=10)
    for i in range(8):
        generated_image_label[i].grid(row=(i//4), column=(i%4), padx=20, pady=20)
        slider[i].grid(row=(i//4)+2, column=(i%4), padx=20, pady=20)
        slider_value_label[i].grid(row=(i//4)+3, column=(i%4), padx=20, pady=20)
        slider[i].config(command=lambda val, idx=i: slider_value_label[idx].config(text=val))
    next_generation_button.pack(pady=10)

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

# 初期UIから1週目の生成システムを開始する
def start_iga_loop():
    global first_image_path
    # まず入力文章と画像を取得
    input_text = input_field.get("1.0", "end-1c")
    input_image = Image.open(first_image_path).convert("RGB")

    # 生成中UIを表示
    show_generate_UI()
    input_text_label.config(text=f"目標: {input_text}")
    generation_step_label.config(text="現在の世代数: 0")
    remaining_time_label.config(text="想定時間: 15秒")

    # 8つの初期遺伝子を作成し、表示する
    genes = create_base_genes(input_text, input_image)
    for i, gene in enumerate(genes):
        gene_data_label[i].config(text=str(gene))
        print(f"\033[93m遺伝子{i+1}の情報: {gene}\033[0m")

    threading.Thread(target=start_iga_loop_generate_thread, args=(genes,)).start()

def start_iga_loop_generate_thread(genes):
    # 作成した遺伝子を元に画像生成を実行し、表示する
    base_generator = ImageGenerator()
    base_images = base_generator.generate_images(genes)

    # csv に遺伝子情報と生成画像情報を新規プロジェクトとして保存
    image_names = base_generator.image_names
    init_project_csv(genes, image_names)

    # 評価UIを呼び出し、生成画像を表示する
    show_evaluation_UI()
    for i, image in enumerate(base_images):
        image = ImageTk.PhotoImage(image)
        generated_image_label[i].config(image=image)
        generated_image_label[i].image = image

def init_project_csv(genes, image_names):
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
    # id, generation, evaluation_score, this_image_name, init_image_name, image_strings, seed, prompt_length, cfg_scale, prompt
    # idは1から8までの連番、評価はこの段階では何も保存しない、世代は1である、init_image_nameはfirst_image_pathを加工して末尾を切り出す
    init_image_name = first_image_path.split("/")[-1]
    with open(os.path.join("projects", project_name), "w") as f:
        f.write("id,generation,evaluation_score,this_image_name,init_image_name,image_strings,seed,prompt_length,cfg_scale,prompt\n")
        for i, gene in enumerate(genes):
            f.write(f"{i+1},1,,{image_names[i]},{init_image_name},{gene.image_strings},{gene.seed},{gene.prompt_length},{gene.cfg_scale},{gene.prompt}\n")
       
def iga_loop():
    # まず評価点数を取得し、csvに保存

    # 生成中UIを表示

    # 前世代の遺伝子情報を取得し、次世代の遺伝子を生成

    # 遺伝子情報を元に画像生成を実行し、表示する

    # csv に遺伝子情報と生成画像情報を保存

    # 評価UIを呼び出し、生成画像を表示する
    
    pass

if __name__ == "__main__":
    setup_ui()