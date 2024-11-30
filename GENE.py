import os
from PIL import Image
from typing import List
from deep_translator import GoogleTranslator

class Gene:
    def __init__(self, init_image_path: str, image_strengs: float, seed: int, steps: int, prompt_length: int, cfg_scale: float, prompt: List[str], this_image_path: str, evaluation_score: int):
        
        # 初めに設定する
        self.init_image_path = init_image_path
        self.image_strengs = image_strengs
        self.seed = seed
        self.steps = steps
        self.prompt_length = prompt_length
        self.cfg_scale = cfg_scale
        self.prompt = prompt

        # 追記する
        self.this_image_path = this_image_path if this_image_path else ""
        self.evaluation_score = evaluation_score if evaluation_score else 0

    def __str__(self):
        init_image_name = os.path.basename(self.init_image_path)
        # prompt は結合し、翻訳する
        prompt = ", ".join(self.prompt)
        translator = GoogleTranslator(source='en', target='ja')
        translated_prompt = translator.translate(prompt)

        return (
            f"参考画像の名前: {init_image_name}\n"
            f"参考画像の優先度: {self.image_strengs}\n"
            f"シード値（乱数）: {self.seed}\n"
            f"生成ステップ数: {self.steps}\n"
            f"プロンプトの単語数: {self.prompt_length}\n"
            f"プロンプトの優先度: {self.cfg_scale}\n"
            f"プロンプト:\n{translated_prompt}"
        )