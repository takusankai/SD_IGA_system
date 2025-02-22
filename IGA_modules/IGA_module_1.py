# IGA_module の print メッセージは「シアン」\033[96m で表示される
import random
from GENE import Gene
from GPT import create_base_gene_prompts_from_GPT

# 初期の8個の遺伝子の構築
def create_base_genes(input_text, input_image_path):
    print("\033[96m初期の8個の遺伝子を作成します\033[0m")
    genes = []
    length_list = [random.randint(10, 20) for _ in range(8)]
    prompt_list = create_base_gene_prompts_from_GPT(length_list, input_text)
    
    for i in range(8):
        # image_strength は 0.1 から 0.3 の間でランダムに生成
        image_strength = round(random.uniform(0.1, 0.3), 2)
        # seed は 0 から 10000 の間でランダムに生成
        seed = random.randint(0, 10000)
        # steps は 1 から 4 の間でランダムに生成
        steps = random.randint(1, 4)
        # prompt_length は 10 から 20 の間でランダムに生成
        prompt_length = length_list[i]
        # cfg_scale は 6.0 から 20.0 の間でランダムに生成
        cfg_scale = round(random.uniform(6.0, 20.0), 1)
        
        gene = Gene(input_image_path, image_strength, seed, steps, prompt_length, cfg_scale, prompt_list[i], "", 0)
        genes.append(gene)

    print(f"\033[96m初期の8個の遺伝子を作成しました\033[0m")
    return genes, prompt_list

def create_next_generation_genes(genes):
    print("\033[96m選択された遺伝的アルゴリズムは1番。デバッグ用の処理を行います。\033[0m")
    return genes