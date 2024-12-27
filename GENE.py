import os
import csv
from typing import List
from deep_translator import GoogleTranslator

class Gene:
    def __init__(self,
                 image_strengs: float = 0.0,
                 seed: int = 0,
                 steps: int = 0,
                 prompt_length: int = 0,
                 cfg_scale: float = 0.0,
                 weight_list: List[int] = None,
                 this_image_path: str = "",
                 evaluation_score: int = 0):
        
        # 初めに設定する
        self.image_strengs = image_strengs
        self.seed = seed
        self.steps = steps # 基本使わない
        self.prompt_length = prompt_length # 基本使わない
        self.cfg_scale = cfg_scale # 基本使わない
        self.weight_list = weight_list if weight_list is not None else [0 for _ in range(50)]

        # 追記する
        self.this_image_path = this_image_path
        self.evaluation_score = evaluation_score

    def prompt(self):
        # dictionary_N.csv から読み込む
        prompt_dictionaly = self.get_last_dictionaly()

        # weight_list の値と組み合わせて、["(aaa:1.5)", "(bbb:0.5)"] のように返す
        # weight_list が 0 なら返さない、1 なら 0.5、2 ならそのまま、3 なら 1.5 とする
        prompt = []
        for i in range(len(self.weight_list)):
            if self.weight_list[i] == 0:
                continue
            elif self.weight_list[i] == 1:
                prompt.append(f"({prompt_dictionaly[i]}:0.5)")
            elif self.weight_list[i] == 2:
                prompt.append(f"{prompt_dictionaly[i]}")
            elif self.weight_list[i] == 3:
                prompt.append(f"({prompt_dictionaly[i]}:1.5)")
        
        return prompt
    
    def get_last_dictionaly(self):
        dictionary_files = os.listdir("projects")
        dictionary_numbers = [int(f.split("_")[-1].split(".")[0]) for f in dictionary_files if f.startswith("dictionary_")]
        dictionary_numbers.sort()
        dictionary_name = "dictionary_" + str(dictionary_numbers[-1]) + ".csv"
        last_dictionaly = []
        # 項目建てもなく、1行に50個の単語が書かれたcsvを読み込み、リストにする
        with open(os.path.join("projects", dictionary_name), "r", encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                # row の要素を最初から最後まで last_dictionaly に追加
                last_dictionaly.extend(row)
        
        return last_dictionaly

    def __str__(self):
        # prompt は結合し、翻訳する
        prompt = ", ".join(self.prompt())
        translator = GoogleTranslator(source='en', target='ja')
        translated_prompt = translator.translate(prompt)

        return (
            # f"参考画像の優先度: {self.image_strengs}\n"
            # f"シード値（乱数）: {self.seed}\n"
            f"プロンプト:\n{translated_prompt}\n"
        )