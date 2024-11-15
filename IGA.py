# IGA.py の print メッセージは「マゼンタ」で表示される
from PIL import Image
from typing import List
import random
from GPT import create_base_gene_prompts_from_GPT

class Gene:
    def __init__(self, init_image: Image.Image, image_strengs: float, seed: int, prompt_length: int, cfg_scale: float, prompt: List[str]):
        self.init_image = init_image
        self.image_strings = image_strengs
        self.seed = seed
        self.prompt_length = prompt_length
        self.cfg_scale = cfg_scale
        self.prompt = prompt
    
    def __str__(self):
        return f"init_image={self.init_image}, image_strings={self.image_strings}, seed={self.seed}, prompt_length={self.prompt_length}, cfg_scale={self.cfg_scale}, prompts={self.prompt}"
    
# 初期の8個の遺伝子の構築
def create_base_genes(input_text, input_image):
    print("\033[95m初期の8個の遺伝子を作成します\033[0m")
    genes = []
    length_list = [random.randint(10, 15) for _ in range(8)]
    prompt_list = create_base_gene_prompts_from_GPT(length_list, input_text)
    
    for i in range(8):
        # image_strings は 0.1 から 0.9 の間でランダムに生成
        image_strings = round(random.uniform(0.1, 0.9), 2)
        # seed は 0 から 100000 の間でランダムに生成
        seed = random.randint(0, 100000)
        # prompt_length は 10 から 15 の間でランダムに生成
        prompt_length = length_list[i]
        # cfg_scale は 6.0 から 12.0 の間でランダムに生成
        cfg_scale = round(random.uniform(6.0, 12.0), 2)
        
        gene = Gene(input_image, image_strings, seed, prompt_length, cfg_scale, prompt_list[i])
        genes.append(gene)
        print(f"\033[95m遺伝子{i+1} の情報: {genes[i]}\033[0m")

    return genes