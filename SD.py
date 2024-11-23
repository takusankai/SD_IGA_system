# SD.py の print メッセージは「青色」\033[94m で表示される
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

    def _get_model_id(self):
        # .envファイルの読み込み
        load_dotenv(dotenv_path='settings.env')
        if not os.path.exists('settings.env'):
            print('\033[94msettings.env の読み込みに失敗した為、SD_MODEL はデフォルト値を使用します\033[0m')
        
        model_id = os.getenv("SD_MODEL", "Lykon/dreamshaper-7")
        return model_id

    def _get_device_and_dtype(self):
        if torch.cuda.is_available():
            print("\033[94mCUDAが利用可能です。GPUを使用します。\033[0m")
            return 'cuda', torch.float32
        else:
            print("\033[94mCUDAが利用できません。CPUを使用します。\033[0m")
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
            print("\033[94mgenerated_imagesディレクトリ内に画像が存在しないため、generated_image_1.jpgとして保存します。\033[0m")

        image_name = "generated_image_" + str(last_image_number + 1) + ".jpg"
        image.save(os.path.join("generated_images", image_name))

        # image_name を path にして返す
        # .envファイルの読み込み
        load_dotenv(dotenv_path='settings.env')
        if not os.path.exists('settings.env'):
            print('\033[94msettings.env の読み込みに失敗した為、UI 設定はデフォルト値を使用します\033[0m')
        # 環境変数の取得(読み込めなければデフォルト値を使用)
        GENERATE_PATH = str(os.getenv("GENERATE_PATH", "D:/downloads/develop/SD_IGA_system/generated_images"))
        image_path = os.path.normpath(os.path.join(GENERATE_PATH, image_name))
        return image_path
    
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
        image_paths = []

        for i, gene in enumerate(genes):
            init_image = Image.open(gene.init_image_path).resize((self.width, self.height))
            init_image = init_image.convert("RGB")

            prompt = ", ".join(gene.prompt)
            generator = torch.Generator(device=self.device).manual_seed(gene.seed)
            # num_inference_steps * image_strengs = stepsとなるように調整
            num_inference_steps = int(gene.steps / gene.image_strengs) + 1

            image = pipe(
                # Geneクラスのプロパティを使用
                prompt,
                guidance_scale = gene.cfg_scale,
                image = init_image,
                strength = gene.image_strengs,
                generator = generator,
                num_inference_steps = num_inference_steps,
                
                # ImageGeneratorクラスのプロパティを使用
                width = self.width, 
                height = self.height,
            ).images[0]

            images.append(image)
            image_path = self._save_image(image)
            image_paths.append(image_path)
            print(f"\033[94m{i+1}枚目の画像を生成しました: {image_path}\033[0m")
        
        return images, image_paths