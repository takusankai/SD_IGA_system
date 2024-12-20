# CSV.py の print メッセージは「黄色」で表示される
import csv
import os
from PIL import Image
from GENE import Gene

# ファイル新規作成のための、新規ファイル名を取得
def get_new_file_name(prefix):
    if not os.path.exists("projects"):
        os.makedirs("projects")
    
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith(f"{prefix}_")]
    project_numbers.sort()
    if project_numbers:
        last_project_number = project_numbers[-1]
    else:
        last_project_number = 0
        print(f"\033[93mprojectsディレクトリ内に画像が存在しないため、{prefix}_1.csvとして保存します。\033[0m")
    return f"{prefix}_" + str(last_project_number + 1) + ".csv"

# ファイル読み出し書き込みのための、最新ファイル名を取得
def get_last_file_name(prefix):  
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith(f"{prefix}_")]
    project_numbers.sort()
    return f"{prefix}_" + str(project_numbers[-1]) + ".csv"

def init_project_csv(genes, image_paths):
    print("\033[93m新規プロジェクトを作成し、遺伝子情報と生成画像情報を保存します\033[0m")  
    project_name = get_new_file_name("project")

    # project_name で新規プロジェクトcsvを作成し、情報を保存する
    # id, generation, evaluation_score, this_image_path, image_strengs, seed, steps, prompt_length, cfg_scale, weight_1, weight_2, ..., weight_50
    # idは1から8までの連番、世代は1、評価点数は0、this_image_pathは空
    header = ["id", "generation", "evaluation_score", "this_image_path", "image_strengs", "seed", "steps", "prompt_length", "cfg_scale"] + [f"weight_{i+1}" for i in range(50)]
    with open(os.path.join("projects", project_name), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i, gene in enumerate(genes):
            writer.writerow([i+1, 1, 0, image_paths[i], gene.image_strengs, gene.seed, gene.steps, gene.prompt_length, gene.cfg_scale, *gene.weight_list])

def init_favorite_csv():
    print("\033[93mお気に入り情報を保存するためのcsvを初期化します\033[0m")
    favorite_name = get_new_file_name("favorite")

    # favorite_name で新規お気に入りcsvを作成し、情報を保存する
    # id, generation, favorite_image_path
    # idは1から8までの連番、世代は1、お気に入りはFalse
    with open(os.path.join("projects", favorite_name), "w", newline='') as f:
        # ヘッダーのみのcsvを作成し初期化
        writer = csv.writer(f)
        writer.writerow(["id", "generation", "favorite_image_path"])

def init_dictionary_csv(prompt_dictionaly):
    print("\033[93mprompt_dictionaly を新規辞書として保存します\033[0m")
    dictionary_name = get_new_file_name("dictionary")

    # dictionary_name で新規辞書csvを作成し、情報を保存する
    # prompt_dictionaly の50個の要素を1行目にまとめて保存する
    with open(os.path.join("projects", dictionary_name), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(prompt_dictionaly)

def save_evaluation_scores(evaluation_scores):
    project_name = get_last_file_name("project")

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

def save_favorite_images(is_favorite_images, generation):
    # project_n.csv を開き、最終行-7から最終行までの8行のデータを取得し、this_generation_image_paths に保存
    project_name = get_last_file_name("project")
    this_generation_image_paths = []

    with open(os.path.join("projects", project_name), "r", newline='') as f:
        reader = csv.reader(f)
        next(reader)
        lines = list(reader)
        last_line = len(lines) - 1
        for line in lines[last_line-7:]:
            this_generation_image_paths.append(line[3])

    # favorite_n.csv を開き、is_favorite_images が True であるものに限定して、favorite_n.csv に generation と favorite_image_path を保存
    # ID は favorite_n.csv の最終行の ID + 1 とする
    favorite_files = os.listdir("projects")
    favorite_numbers = [int(f.split("_")[-1].split(".")[0]) for f in favorite_files if f.startswith("favorite_")]
    favorite_numbers.sort()
    favorite_name = "favorite_" + str(favorite_numbers[-1]) + ".csv"
    with open(os.path.join("projects", favorite_name), "a", newline='') as f:
        writer = csv.writer(f)
        for i, is_favorite in enumerate(is_favorite_images):
            if is_favorite:
                writer.writerow([len(favorite_numbers) * 8 + i + 1, generation, this_generation_image_paths[i]])
    
    # favorite_images ディレクトリにお気に入り画像を保存
    for i, is_favorite in enumerate(is_favorite_images):
        if is_favorite:
            image = Image.open(this_generation_image_paths[i])
            # ファイル名は this_generation_image_path の末尾であるファイル名と一致させる
            image.save(os.path.join("favorite_images", os.path.basename(this_generation_image_paths[i])))
    
def save_genes_and_images(next_genes, image_paths, generation):
    project_name = get_last_file_name("project")

    with open(os.path.join("projects", project_name), "a", newline='') as f:
        writer = csv.writer(f)
        for i, gene in enumerate(next_genes):
            writer.writerow([generation * 8 - 7 + i, generation, 0, image_paths[i], gene.image_strengs, gene.seed, gene.steps, gene.prompt_length, gene.cfg_scale, *gene.weight_list])

def get_last_generation_genes():
    # csv から前世代の遺伝子情報を取得
    project_name = get_last_file_name("project")
    last_generation_genes = []

    # csvを開き、最終行-7から最終行までの8行の遺伝子情報（評価とthis_image_pathも含む）を取得
    with open(os.path.join("projects", project_name), "r", newline='') as f:
        reader = csv.reader(f)
        next(reader) # ヘッダーをスキップ
        lines = list(reader)
        last_line = len(lines) - 1
        # 最終行-7から最終行までの8行のデータを、Gene クラスに変換してリストに追加
        for line in lines[last_line-7:]:
            # weight_list は第9要素以降の文字列を int のリストに変換
            weight_list = [int(w) for w in line[9:]]
            gene = Gene(
                image_strengs=float(line[4]),
                seed=int(line[5]),
                steps=int(line[6]),
                prompt_length=int(line[7]),
                cfg_scale=float(line[8]),
                weight_list=weight_list,
                this_image_path=os.path.normpath(line[3]),
                evaluation_score=int(line[2]) if line[2] else 12345 # 12345はエラー検証用の記録されないはずの値
            )
            last_generation_genes.append(gene)

    return last_generation_genes