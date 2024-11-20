# SD.py の print メッセージは「青色」で表示される
import os
import argparse
import numpy as np
import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
from dotenv import load_dotenv
from GENE import Gene

class ImageGenerator:
    def __init__(self, width=256, height=256, num_images=8):
        self.model_id = self._get_model_id()
        self.width = width
        self.height = height
        self.num_images = num_images
        self.device, self.dtype = self._get_device_and_dtype()
        self.image_names = [] # 生成した画像のファイル名を格納し UI.py に返すためのリスト

    def _get_model_id(self):
        # .envファイルの読み込み
        load_dotenv(dotenv_path='settings.env')
        if not os.path.exists('settings.env'):
            print('\033[94msettings.env の読み込みに失敗した為、SD_MODEL はデフォルト値を使用します\033[0m')
        
        model_id = os.getenv("SD_MODEL", "Lykon/dreamshaper-7")
        return model_id

    def _get_device_and_dtype(self):
        if torch.cuda.is_available():
            print("\033[93mCUDAが利用可能です。GPUを使用します。\033[0m")
            return 'cuda', torch.float32
        else:
            print("\033[93mCUDAが利用できません。CPUを使用します。\033[0m")
            return 'cpu', torch.float32

    def _save_image(self, image):
        if not os.path.exists("generated_images"):
            os.makedirs("generated_images")
        
        image_files = os.listdir("generated_images")
        image_numbers = [int(f.split("_")[-1].split(".")[0]) for f in image_files if f.startswith("generated_image_")]
        image_numbers.sort()
        
        if image_numbers:
            last_image_number = image_numbers[-1]
        else:
            last_image_number = 0
            print("\033[93mgenerated_imagesディレクトリ内に画像が存在しないため、generated_image_1.jpgとして保存します。\033[0m")

        image_name = "generated_image_" + str(last_image_number + 1) + ".jpg"
        image.save(os.path.join("generated_images", image_name))
        return image_name
    
    def _load_pipeline(self, pipeline_class):
        pipe = pipeline_class.from_pretrained(
            self.model_id, 
            torch_dtype=self.dtype,
            # safety_checker=None, diffusersチームとHugging Faceの両方は、一般公開されるすべての状況でセーフティフィルタを有効にしておくことを強く推奨
        ).to(self.device)

        return pipe

    def generate_images(self, genes):
        pipe = self._load_pipeline(StableDiffusionImg2ImgPipeline)
        images = []

        for i, gene in enumerate(genes):
            # init_image の型は PIL.Image.Image であるが、エラーの影響で numpy.ndarray に変換
            gene.init_image = gene.init_image.resize((self.width, self.height))
            gene.init_image = gene.init_image.convert("RGB")

            prompt = ", ".join(gene.prompt)
            generator = torch.Generator(device=self.device).manual_seed(gene.seed)
            # num_inference_steps * image_strengs = stepsとなるように調整
            num_inference_steps = int(gene.steps / gene.image_strengs) + 1

            image = pipe(
                # Geneクラスのプロパティを使用
                prompt,
                guidance_scale = gene.cfg_scale,
                image = gene.init_image,
                strength = gene.image_strengs,
                generator = generator,
                num_inference_steps = num_inference_steps,
                
                # ImageGeneratorクラスのプロパティを使用
                width = self.width, 
                height = self.height,
            ).images[0]

            image_name = self._save_image(image)
            self.image_names.append(image_name)
            images.append(image)
            print(f"\033[94m{i+1}枚目の画像を生成しました: {image_name}\033[0m")
        
        return images


