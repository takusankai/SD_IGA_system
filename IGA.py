# IGA.py の print メッセージは「マゼンタ」\033[95m で表示される
import random
from GENE import Gene
from GPT import create_base_gene_prompts_from_GPT
    
# 初期の8個の遺伝子の構築
def create_base_genes(input_text, input_image_path):
    print("\033[95m初期の8個の遺伝子を作成します\033[0m")
    genes = []
    length_list = [random.randint(10, 15) for _ in range(8)]
    prompt_list = create_base_gene_prompts_from_GPT(length_list, input_text)
    
    for i in range(8):
        # image_strengs は 0.1 から 0.3 の間でランダムに生成
        image_strengs = round(random.uniform(0.1, 0.3), 2)
        # seed は 0 から 10000 の間でランダムに生成
        seed = random.randint(0, 10000)
        # steps は 50 から 100 の間でランダムに生成
        steps = random.randint(50, 100)
        # prompt_length は 10 から 15 の間でランダムに生成
        prompt_length = length_list[i]
        # cfg_scale は 6.0 から 12.0 の間でランダムに生成
        cfg_scale = round(random.uniform(6.0, 12.0), 1)
        
        gene = Gene(input_image_path, image_strengs, seed, steps, prompt_length, cfg_scale, prompt_list[i], "", 0)
        genes.append(gene)

    print(f"\033[95m初期の8個の遺伝子を作成しました\033[0m")
    return genes
