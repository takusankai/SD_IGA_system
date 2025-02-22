# SD.py の print メッセージは「青色」\033[94m で表示される
import os
import torch
from PIL import Image
from diffusers import DiffusionPipeline, StableDiffusion3Pipeline, StableDiffusionImg2ImgPipeline, StableDiffusionXLImg2ImgPipeline, AutoPipelineForImage2Image, AutoPipelineForText2Image, StableDiffusionXLControlNetPipeline, ControlNetModel
from dotenv import load_dotenv
from huggingface_hub import login

class ImageGenerator:
    def __init__(self, width=256, height=256, num_images=8):
        self.model_id = self._get_model_id()
        self.width = width
        self.height = height
        self.num_images = num_images
        self.device, self.dtype = self._get_device_and_dtype()
        self._login_to_huggingface()

    def _get_model_id(self):
        # .envファイルの読み込み
        load_dotenv(dotenv_path='settings.env')
        if not os.path.exists('settings.env'):
            print('\033[94msettings.env の読み込みに失敗した為、SD_MODEL はデフォルト値を使用します\033[0m')
        
        model_id = os.getenv("SD_MODEL", "stabilityai/stable-diffusion-3.5-large-turbo")
        return model_id

    def _get_device_and_dtype(self):
        if torch.cuda.is_available():
            print("\033[94mCUDAが利用可能です。GPUを使用します。\033[0m")
            return 'cuda', torch.float16
        else:
            print("\033[94mCUDAが利用できません。CPUを使用します。\033[0m")
            return 'cpu', torch.float32

    def _login_to_huggingface(self):
        token = os.getenv("HUGGINGFACE_TOKEN")
        if token:
            login(token=token)
            print("\033[94mHugging Faceにログインしました。\033[0m")
        else:
            print("\033[94mHugging Faceのトークンが設定されていません。\033[0m")

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
            custom_pipeline="lpw_stable_diffusion_xl",
            torch_dtype=self.dtype,
            # safety_checker=None, diffusersチームとHugging Faceの両方は、一般公開されるすべての状況でセーフティフィルタを有効にしておくことを強く推奨
        ).to(self.device)

        return pipe

    def i2i_generate_images(self, genes, first_image_path):
        pipe = self._load_pipeline(AutoPipelineForImage2Image)
        images = []
        image_paths = []
        init_image = Image.open(first_image_path).resize((self.width, self.height)).convert("RGB")

        for i, gene in enumerate(genes):
            prompt = ", ".join(gene.prompt())
            generator = torch.Generator(device=self.device).manual_seed(gene.seed)  # シード指定

            # 品質系ポジティブ・ネガティブプロンプトを用意
            # positive_prompt = "realistic, masterpiece, best quality, high quality, ultra detailed, high resolution, 8K, HD"
            # negative_prompt = "worst quality, low quality, blurry, low resolution, out of focus, ugly, bad, poor quality, artifact, jpeg artifacts, error, broken"

            # num_inference_steps * image_strength = stepsとなるように調整
            # num_inference_steps = int(gene.steps / gene.image_strength) + 1
            # num_inference_steps = int(4 / gene.image_strength) + 1
            num_inference_steps = int(4 / 0.6) + 1

            # positive_embeds, negative_embeds = self.token_auto_concat_embeds(pipe, prompt)

            result = pipe(
                prompt,
                # negative_prompt=neg_prompt,
                # prompt_embeds=positive_embeds,
                # negative_prompt_embeds=negative_embeds,
                image = init_image,
                # strength = gene.image_strength,
                # generator = generator,
                # guidance_scale = gene.cfg_scale,
                num_inference_steps = num_inference_steps,
                width = self.width, 
                height = self.height,
                
                # ハードコーディング
                strength = 0.6,
                guidance_scale = 0.0,
                # num_inference_steps = 10,
                # max_embeddings_multiples = 5.0, # デフォルトだと75トークンが限界なので5倍に拡張
                # prompt_2 = positive_prompt,
                # negative_prompt = negative_prompt,
            )

            image = result.images[0]
            images.append(image)
            image_path = self._save_image(image)
            image_paths.append(image_path)
            print(f"\033[94m{i+1}枚目の画像を生成しました: {image_path}\033[0m")

        return images, image_paths
    
    def t2i_generate_images(self, genes):
        pipe = self._load_pipeline(AutoPipelineForText2Image)
        images = []
        image_paths = []

        for i, gene in enumerate(genes):
            prompt = ", ".join(gene.prompt())
            # generator = torch.Generator(device=self.device).manual_seed(gene.seed)  # シード指定

            # 品質系ポジティブ・ネガティブプロンプトを用意
            # positive_prompt = "realistic, masterpiece, best quality, high quality, ultra detailed, high resolution, 8K, HD"
            # negative_prompt = "worst quality, low quality, blurry, low resolution, out of focus, ugly, bad, poor quality, artifact, jpeg artifacts, error, broken"

            # positive_embeds, negative_embeds = self.token_auto_concat_embeds(pipe, prompt)

            result = pipe(
                prompt,
                # negative_prompt=neg_prompt,
                # prompt_embeds=positive_embeds,
                # negative_prompt_embeds=negative_embeds,
                # generator = generator,
                # guidance_scale = gene.cfg_scale,
                # num_inference_steps = num_inference_steps,
                width = self.width, 
                height = self.height,
                
                # ハードコーディング
                guidance_scale = 0.0,
                num_inference_steps = 4,
                # max_embeddings_multiples = 5.0, # デフォルトだと75トークンが限界なので5倍に拡張
                # prompt_2 = positive_prompt,
                # negative_prompt = negative_prompt,
            )

            image = result.images[0]
            images.append(image)
            image_path = self._save_image(image)
            image_paths.append(image_path)
            print(f"\033[94m{i+1}枚目の画像を生成しました: {image_path}\033[0m")

        return images, image_paths
    
    # >77問題は、単にlpw_stable_diffusion_xlを使用することで解決した
    # 問題が再度発生する場合に備えて、代案である以下の重み付けの関数をコメントアウトして残しておく
    # def token_auto_concat_embeds(self, pipe, prompt):
    #     max_length = pipe.tokenizer.model_max_length
    #     # positive_length = pipe.tokenizer(positive, return_tensors="pt").input_ids.shape[-1]
    #     # negative_length = pipe.tokenizer(negative, return_tensors="pt").input_ids.shape[-1]
        
    #     # print(f'Token length is model maximum: {max_length}, positive length: {positive_length}, negative length: {negative_length}.')
    #     # if max_length < positive_length or max_length < negative_length:
    #     #     print('Concatenated embedding.')
    #     #     if positive_length > negative_length:
    #     #         positive_ids = pipe.tokenizer(positive, return_tensors="pt").input_ids.to("cuda")
    #     #         negative_ids = pipe.tokenizer(negative, truncation=False, padding="max_length", max_length=positive_ids.shape[-1], return_tensors="pt").input_ids.to("cuda")
    #     #     else:
    #     #         negative_ids = pipe.tokenizer(negative, return_tensors="pt").input_ids.to("cuda")  
    #     #         positive_ids = pipe.tokenizer(positive, truncation=False, padding="max_length", max_length=negative_ids.shape[-1],  return_tensors="pt").input_ids.to("cuda")
    #     # else:
    #     #     positive_ids = pipe.tokenizer(positive, truncation=False, padding="max_length", max_length=max_length,  return_tensors="pt").input_ids.to("cuda")
    #     #     negative_ids = pipe.tokenizer(negative, truncation=False, padding="max_length", max_length=max_length, return_tensors="pt").input_ids.to("cuda")
        
    #     # positive_concat_embeds = []
    #     # negative_concat_embeds = []
    #     # for i in range(0, positive_ids.shape[-1], max_length):
    #     #     positive_concat_embeds.append(pipe.text_encoder(positive_ids[:, i: i + max_length])[0])
    #     #     negative_concat_embeds.append(pipe.text_encoder(negative_ids[:, i: i + max_length])[0])
        
    #     # positive_prompt_embeds = torch.cat(positive_concat_embeds, dim=1)
    #     # negative_prompt_embeds = torch.cat(negative_concat_embeds, dim=1)

    #     max_length = pipe.tokenizer.model_max_length

    #     input_ids = pipe.tokenizer(prompt, return_tensors="pt").input_ids
    #     input_ids = input_ids.to("cuda")

    #     negative_ids = pipe.tokenizer("", truncation=False, padding="max_length", max_length=input_ids.shape[-1], return_tensors="pt").input_ids                                                                                                     
    #     negative_ids = negative_ids.to("cuda")

    #     concat_embeds = []
    #     neg_embeds = []
    #     for i in range(0, input_ids.shape[-1], max_length):
    #         concat_embeds.append(pipe.text_encoder(input_ids[:, i: i + max_length])[0])
    #         neg_embeds.append(pipe.text_encoder(negative_ids[:, i: i + max_length])[0])

    #     prompt_embeds = torch.cat(concat_embeds, dim=1)
    #     negative_prompt_embeds = torch.cat(neg_embeds, dim=1)
    #     return prompt_embeds, negative_prompt_embeds