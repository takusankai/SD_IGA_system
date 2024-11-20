# IGA.py の print メッセージは「マゼンタ」で表示される
import os
import csv
from PIL import Image
from typing import List
import random
from GENE import Gene
from GPT import create_base_gene_prompts_from_GPT
from IGA_modules.IGA_module_2 import interactive_Genetic_algorithm # ここを書き換える形で IGA のモジュールを変更する
    
# 初期の8個の遺伝子の構築
def create_base_genes(input_text, input_image):
    print("\033[95m初期の8個の遺伝子を作成します\033[0m")
    genes = []
    length_list = [random.randint(10, 15) for _ in range(8)]
    prompt_list = create_base_gene_prompts_from_GPT(length_list, input_text)
    
    for i in range(8):
        # image_strengs は 0.1 から 0.4 の間でランダムに生成
        image_strengs = round(random.uniform(0.1, 0.4), 2)
        # seed は 0 から 10000 の間でランダムに生成
        seed = random.randint(0, 10000)
        # steps は 50 から 100 の間でランダムに生成
        steps = random.randint(50, 100)
        # prompt_length は 10 から 15 の間でランダムに生成
        prompt_length = length_list[i]
        # cfg_scale は 6.0 から 12.0 の間でランダムに生成
        cfg_scale = round(random.uniform(6.0, 12.0), 1)
        
        gene = Gene(input_image, image_strengs, seed, steps, prompt_length, cfg_scale, prompt_list[i], 0, "")
        genes.append(gene)

    print(f"\033[95m初期の8個の遺伝子を作成しました\033[0m")
    return genes

# ループ時の次世代の遺伝子の構築
def create_next_generation_genes(genes):
    # csvファイルから最新8件の this_image_name を取得し、PIL.Image.Image に変換して渡す
    project_files = os.listdir("projects")
    project_numbers = [int(f.split("_")[-1].split(".")[0]) for f in project_files if f.startswith("project_")]
    project_numbers.sort()
    project_name = "project_" + str(project_numbers[-1]) + ".csv"
    this_images = []
    with open(os.path.join("projects", project_name), "r", newline='') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        lines = list(reader)
        last_line = len(lines) - 1
        # 最終行-7から最終行までの8行の this_image_name を取得
        for line in lines[last_line-7:]:
            this_image_name = line[3]
            this_image = Image.open(os.path.join("generated_images", this_image_name))
            this_images.append(this_image)

    new_genes = interactive_Genetic_algorithm(genes, this_images)
    return new_genes