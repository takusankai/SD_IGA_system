from PIL import Image
from typing import List

class Gene:
    def __init__(self, init_image: Image.Image, image_strengs: float, seed: int, steps: int, prompt_length: int, cfg_scale: float, prompt: List[str], evaluation_score: int, init_image_name: str):
        self.init_image = init_image
        self.image_strengs = image_strengs
        self.seed = seed
        self.steps = steps
        self.prompt_length = prompt_length
        self.cfg_scale = cfg_scale
        self.prompt = prompt
        self.evaluation_score = evaluation_score
        self.init_image_name = init_image_name # プログラム上必要になったため追加、IGA処理とは関係しない
    
    def __str__(self):
        return f"init_image={self.init_image}, image_strengs={self.image_strengs}, seed={self.seed}, steps={self.steps}, prompt_length={self.prompt_length}, cfg_scale={self.cfg_scale}, prompt={self.prompt}"
