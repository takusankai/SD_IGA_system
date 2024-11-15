# IGA.py の print メッセージは「マゼンタ」で表示される
from PIL import Image
from typing import List
import random

class Gene:
    def __init__(self, init_image: Image.Image, image_strengs: float, seed: int, prompt_length: int, cfg_scale: float, prompts: List[str]):
        self.init_image = init_image
        self.image_strings = image_strengs
        self.seed = seed
        self.prompt_length = prompt_length
        self.cfg_scale = cfg_scale
        self.prompts = prompts
    
    def __str__(self):
        return f"init_image={self.init_image}, image_strings={self.image_strings}, seed={self.seed}, prompt_length={self.prompt_length}, cfg_scale={self.cfg_scale}, prompts={self.prompts}"
    
    # 初期遺伝子の構築
    def create_base_gene(self):
        print("\033[95m初期遺伝子を作成します\033[0m")
        # image_strings は 0.1 から 0.9 の間でランダムに生成
        self.image_strings = round(random.uniform(0.1, 0.9), 2)
        # seed は 0 から 100000 の間でランダムに生成
        self.seed = random.randint(0, 100000)
        # prompt_length は 10 から 15 の間でランダムに生成
        self.prompt_length = random.randint(10, 15)
        # cfg_scale は 6.0 から 12.0 の間でランダムに生成
        self.cfg_scale = round(random.uniform(6.0, 12.0), 2)

        # prompts は prompt_length の数だけランダムな文字列を生成
        self.prompts = ["".join([random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10)]) for _ in range(self.prompt_length)]