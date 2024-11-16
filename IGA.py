# IGA.py の print メッセージは「マゼンタ」で表示される
from PIL import Image
from typing import List
import random
from GPT import create_base_gene_prompts_from_GPT

class Gene:
    def __init__(self, init_image: Image.Image, image_strengs: float, seed: int, steps: int, prompt_length: int, cfg_scale: float, prompt: List[str], evaluation_score: int, init_image_name: str):
        self.init_image = init_image
        self.image_strings = image_strengs
        self.seed = seed
        self.steps = steps
        self.prompt_length = prompt_length
        self.cfg_scale = cfg_scale
        self.prompt = prompt
        self.evaluation_score = evaluation_score
        self.init_image_name = init_image_name # プログラム上必要になったため追加、IGA処理とは関係しない
    
    def __str__(self):
        return f"init_image={self.init_image}, image_strings={self.image_strings}, seed={self.seed}, steps={self.steps}, prompt_length={self.prompt_length}, cfg_scale={self.cfg_scale}, prompt={self.prompt}"
    
# 初期の8個の遺伝子の構築
def create_base_genes(input_text, input_image):
    print("\033[95m初期の8個の遺伝子を作成します\033[0m")
    genes = []
    length_list = [random.randint(10, 15) for _ in range(8)]
    prompt_list = create_base_gene_prompts_from_GPT(length_list, input_text)
    
    for i in range(8):
        # image_strings は 0.1 から 0.4 の間でランダムに生成
        image_strings = round(random.uniform(0.1, 0.4), 2)
        # seed は 0 から 10000 の間でランダムに生成
        seed = random.randint(0, 10000)
        # steps は 50 から 100 の間でランダムに生成
        steps = random.randint(50, 100)
        # prompt_length は 10 から 15 の間でランダムに生成
        prompt_length = length_list[i]
        # cfg_scale は 6.0 から 12.0 の間でランダムに生成
        cfg_scale = round(random.uniform(6.0, 12.0), 1)
        
        gene = Gene(input_image, image_strings, seed, steps, prompt_length, cfg_scale, prompt_list[i], 0, "")
        genes.append(gene)

    print(f"\033[95m初期の8個の遺伝子を作成しました\033[0m")
    return genes

# ループ時の次世代の遺伝子の構築
def create_next_generation_genes(genes):
    genes.init_image_name = "first_pick"
    return genes