# IGA_module_2.py の print メッセージは「シアン」\033[96m で表示される
import random
from PIL import Image
from GENE import Gene
from GPT import create_base_gene_prompts_from_GPT, mutate
import os
from dotenv import load_dotenv

# 初期の8個の遺伝子の構築
def create_base_genes(input_text, input_image_path):
    print("\033[96m初期の8個の遺伝子を作成します\033[0m")

    # setting.env から範囲変数を読み込む
    image_strengs_min, image_strengs_max, seed_min, seed_max, steps_min, steps_max, prompt_length_min, prompt_length_max, cfg_scale_min, cfg_scale_max, _, _, _ = load_settings()
   
    genes = []
    length_list = [random.randint(prompt_length_min, prompt_length_max) for _ in range(8)]
    prompt_list = create_base_gene_prompts_from_GPT(length_list, input_text)
    
    for i in range(8):
        # image_strengs は image_strengs_min から image_strengs_max の間でランダムに生成
        image_strengs = round(random.uniform(image_strengs_min, image_strengs_max), 2)
        # seed は seed_min から seed_max の間でランダムに生成
        seed = random.randint(seed_min, seed_max)
        # steps は steps_min から steps_max の間でランダムに生成
        steps = random.randint(steps_min, steps_max)
        # prompt_length は prompt_length_min から prompt_length_max の間でランダムに生成
        prompt_length = length_list[i]
        # cfg_scale は cfg_scale_min から cfg_scale_max の間でランダムに生成
        cfg_scale = round(random.uniform(cfg_scale_min, cfg_scale_max), 1)
        
        gene = Gene(input_image_path, image_strengs, seed, steps, prompt_length, cfg_scale, prompt_list[i], "", 0)
        genes.append(gene)

    print(f"\033[96m初期の8個の遺伝子を作成しました\033[0m")
    return genes

def create_next_generation_genes(genes):
    print("\033[96m選択された遺伝的アルゴリズムは2番。基本的な方針による選択、交叉、突変を行います。\033[0m")
    # 次の遺伝子となる8個のgene型のリストを宣言
    new_genes = []
    for i in range(8):
        # init_image_path, image_strengs, seed, steps, prompt_length, cfg_scale, prompt, this_image_path, evaluation_score
        new_genes.append(Gene("", 0.0, 0, 0, 0, 0.0, [], "", 0))
    
    # 選択
    # 評価点を参照し、その個体の評価 / 合計評価の割合を確率として選択し、両親のペアを8組作成
    # 0点の評価を避けるために、全ての評価点に1を加算
    evaluation_scores = [gene.evaluation_score + 1 for gene in genes]
    # 両親が重複しないように選択
    parent_gene_pairs = []
    for _ in range(8):
        # 評価を重みとして 0-7 のインデックスを選択
        choiced_index = random.choices(range(8), evaluation_scores, k=2)
        while choiced_index[0] == choiced_index[1]:
            choiced_index = random.choices(range(8), evaluation_scores, k=2)
        parent_gene_pairs.append((genes[choiced_index[0]], genes[choiced_index[1]]))
        print(f"\033[96m選択された両親の遺伝子のインデックス: {choiced_index}\033[0m")

    print("") # for 抜けたので改行

    # 交叉
    # [image 交叉]
    # 両親の init_image 又は、両親の this_image という計4枚の画像から1枚の画像を選択していく
    for i in range(8):
        # 両親の画像をランダムに選択
        image_paths = [
            parent_gene_pairs[i][0].init_image_path,  # 1
            parent_gene_pairs[i][1].init_image_path,  # 2
            parent_gene_pairs[i][0].this_image_path,  # 3
            parent_gene_pairs[i][1].this_image_path   # 4
        ]
        # 画像をランダムに選択
        choiced_image_path = random.choice(image_paths)
        new_genes[i].init_image_path = choiced_image_path

        # 選択された画像を識別するためのインデックスを取得
        choiced_image_index = image_paths.index(choiced_image_path) + 1

        # 選択された画像を識別するためのメッセージを表示
        if choiced_image_index == 1:
            print(f"\033[96m選択された画像: 1 (parent_gene_pairs[{i}][0].init_image_path)\033[0m")
        elif choiced_image_index == 2:
            print(f"\033[96m選択された画像: 2 (parent_gene_pairs[{i}][1].init_image_path)\033[0m")
        elif choiced_image_index == 3:
            print(f"\033[96m選択された画像: 3 (parent_gene_pairs[{i}][0].this_image_path)\033[0m")
        elif choiced_image_index == 4:
            print(f"\033[96m選択された画像: 4 (parent_gene_pairs[{i}][1].this_image_path)\033[0m")
            
        # image_strengs の交叉は両親のどちらかの値をランダムに選択
        new_genes[i].image_strengs = random.choice([parent_gene_pairs[i][0].image_strengs, parent_gene_pairs[i][1].image_strengs])
        print(f"\033[96mnew_genes[{i}].image_strengs: {new_genes[i].image_strengs}\033[0m")
    
    print("") # for 抜けたので改行

    # [status 交叉]
    # seed, steps は両親のどちらかの値をランダムに選択
    for i in range(8):
        new_genes[i].seed = random.choice([parent_gene_pairs[i][0].seed, parent_gene_pairs[i][1].seed])
        new_genes[i].steps = random.choice([parent_gene_pairs[i][0].steps, parent_gene_pairs[i][1].steps])
        print(f"\033[96mnew_genes[{i}].seed: {new_genes[i].seed}\033[0m")
        print(f"\033[96mnew_genes[{i}].steps: {new_genes[i].steps}\033[0m")
    
    print("") # for 抜けたので改行

    # [prompt 交叉]
    # まず prompt_length, cfg_scale は両親のどちらかの値をランダムに選択
    # その後、prompt は単語を優先度順にリストにまとめ、上位のprompt_length個を選択
    for i in range(8):
        new_genes[i].prompt_length = random.choice([parent_gene_pairs[i][0].prompt_length, parent_gene_pairs[i][1].prompt_length])
        new_genes[i].cfg_scale = random.choice([parent_gene_pairs[i][0].cfg_scale, parent_gene_pairs[i][1].cfg_scale])
        print(f"\033[96mnew_genes[{i}].prompt_length: {new_genes[i].prompt_length}\033[0m")
        print(f"\033[96mnew_genes[{i}].cfg_scale: {new_genes[i].cfg_scale}\033[0m")

        # 両親のpromptから優先度順にリストにまとめる
        prompt_list = []
        # 両親のpromptで一致した単語があれば、そのインデックスの平均を取って優先度とし、（優先度, 単語）のタプルの形でリストに追加
        for word in parent_gene_pairs[i][0].prompt:
            if word in parent_gene_pairs[i][1].prompt:
                index = parent_gene_pairs[i][1].prompt.index(word)
                priority = (index + parent_gene_pairs[i][0].prompt.index(word)) / 2
                prompt_list.append((priority, word))

        # 両親のpromptで一致しない単語は、そのインデックスとその単語がある方のprompt_lengthの平均を取って優先度とし、（優先度, 単語）のタプルの形でリストに追加
        for word in parent_gene_pairs[i][0].prompt:
            if word not in parent_gene_pairs[i][1].prompt:
                index = parent_gene_pairs[i][0].prompt.index(word)
                priority = (index + parent_gene_pairs[i][0].prompt_length) / 2
                prompt_list.append((priority, word))
        
        for word in parent_gene_pairs[i][1].prompt:
            if word not in parent_gene_pairs[i][0].prompt:
                index = parent_gene_pairs[i][1].prompt.index(word)
                priority = (index + parent_gene_pairs[i][1].prompt_length) / 2
                prompt_list.append((priority, word))

        # 優先度順にソート
        prompt_list.sort(key=lambda x: x[0])
        # 上位のprompt_length個を選択
        new_genes[i].prompt = [word for _, word in prompt_list[:new_genes[i].prompt_length]]
        print(f"\033[96mnew_genes[{i}].prompt: {new_genes[i].prompt}\033[0m")
    
    print("") # for 抜けたので改行
    
    # setting.env から範囲変数と突然変異率を読み込む
    image_strengs_min, image_strengs_max, seed_min, seed_max, steps_min, steps_max, prompt_length_min, prompt_length_max, cfg_scale_min, cfg_scale_max, image_mutate_rate, status_mutate_rate, prompt_mutate_rate = load_settings()

    # 突変
    # [image 突変] 突然変異率： image_mutate_rate
    # init_image は全parent_image_pairsとthis_imagesをまとめたリストからランダムに選択
    mutate_image_list = []
    for i in range(8):
        mutate_image_list.append(parent_gene_pairs[i][0].init_image_path)
        mutate_image_list.append(parent_gene_pairs[i][1].init_image_path)
        mutate_image_list.append(parent_gene_pairs[i][0].this_image_path)
        mutate_image_list.append(parent_gene_pairs[i][1].this_image_path)

    for i in range(8):
        if random.random() < image_mutate_rate:
            print(f"\033[96mgene[{i}]のinit_imageを{new_genes[i].init_image_path}から突然変異\033[0m")
            new_genes[i].init_image_path = random.choice(mutate_image_list)
            print(f"\033[96mnew_genes[{i}].init_image: {new_genes[i].init_image_path}\033[0m")
        
    # image_strengs 突変は、image_mutate_rate の確率で image_strengs_min から image_strengs_max の間でランダムに生成
    for i in range(8):
        if random.random() < image_mutate_rate:
            print(f"\033[96mgene[{i}]のimage_strengsを{new_genes[i].image_strengs}から突然変異\033[0m")
            new_genes[i].image_strengs = round(random.uniform(image_strengs_min, image_strengs_max), 2)
            print(f"\033[96mnew_genes[{i}].image_strengs: {new_genes[i].image_strengs}\033[0m")
    
    print("") # for 抜けたので改行

    # [status 突変] 突然変異率： status_mutate_rate
    # seed, steps は seed_min から seed_max, steps_min から steps_max の間でランダムに生成
    for i in range(8):
        if random.random() < status_mutate_rate:
            print(f"\033[96mgene[{i}]のseedを{new_genes[i].seed}から突然変異\033[0m")
            new_genes[i].seed = random.randint(seed_min, seed_max)
            print(f"\033[96mnew_genes[{i}].seed: {new_genes[i].seed}\033[0m")
        
        if random.random() < status_mutate_rate:
            print(f"\033[96mgene[{i}]のstepsを{new_genes[i].steps}から突然変異\033[0m")
            new_genes[i].steps = random.randint(steps_min, steps_max)
            print(f"\033[96mnew_genes[{i}].steps: {new_genes[i].steps}\033[0m")
    
    print("") # for 抜けたので改行

    # [prompt 突変] 突然変異率： prompt_mutate_rate
    # prompt_length は prompt_length_min から prompt_length_max の間でランダムに生成, cfg_scale は cfg_scale_min から cfg_scale_max の間でランダムに生成
    for i in range(8):
        if random.random() < prompt_mutate_rate:
            print(f"\033[96mgene[{i}]のprompt_lengthを{new_genes[i].prompt_length}から突然変異\033[0m")
            new_genes[i].prompt_length = random.randint(prompt_length_min, prompt_length_max)
            print(f"\033[96mnew_genes[{i}].prompt_length: {new_genes[i].prompt_length}\033[0m")
        
        if random.random() < 0.3:
            print(f"\033[96mgene[{i}]のcfg_scaleを{new_genes[i].cfg_scale}から突然変異\033[0m")
            new_genes[i].cfg_scale = round(random.uniform(cfg_scale_min, cfg_scale_max), 1)
            print(f"\033[96mnew_genes[{i}].cfg_scale: {new_genes[i].cfg_scale}\033[0m")
    
    # prompt は GPT で置き換える
    for i in range(8):
        if random.random() < prompt_mutate_rate:
            print(f"\033[96mgene[{i}]のpromptを{new_genes[i].prompt}（{new_genes[i].prompt_length}個）から突然変異\033[0m")
            new_genes[i].prompt = mutate(new_genes[i].prompt, new_genes[i].prompt_length)
            print(f"\033[96mnew_genes[{i}].prompt: {new_genes[i].prompt}\033[0m")
    
    print("") # for 抜けたので改行

    return new_genes

def load_settings():
     # 範囲変数を setting.env から読み込む
    load_dotenv(dotenv_path='settings.env')
    if not os.path.exists('settings.env'):
        print('\033[96msettings.env の読み込みに失敗した為、初期遺伝子の設定はデフォルト値を使用します\033[0m')
    # 環境変数の取得(読み込めなければデフォルト値を使用)
    image_strengs_min = float(os.getenv("IMAGE_STRENGS_MIN", 0.1))
    image_strengs_max = float(os.getenv("IMAGE_STRENGS_MAX", 0.3))
    seed_min = int(os.getenv("SEED_MIN", 0))
    seed_max = int(os.getenv("SEED_MAX", 10000))
    steps_min = int(os.getenv("STEPS_MIN", 1))
    steps_max = int(os.getenv("STEPS_MAX", 4))
    prompt_length_min = int(os.getenv("PROMPT_LENGTH_MIN", 10))
    prompt_length_max = int(os.getenv("PROMPT_LENGTH_MAX", 20))
    cfg_scale_min = float(os.getenv("CFG_SCALE_MIN", 6.0))
    cfg_scale_max = float(os.getenv("CFG_SCALE_MAX", 20.0))
    image_mutate_rate = float(os.getenv("IMAGE_MUTATE_RATE", 0.3))
    status_mutate_rate = float(os.getenv("STATUS_MUTATE_RATE", 0.3))
    prompt_mutate_rate = float(os.getenv("PROMPT_MUTATE_RATE", 0.3))

    return image_strengs_min, image_strengs_max, seed_min, seed_max, steps_min, steps_max, prompt_length_min, prompt_length_max, cfg_scale_min, cfg_scale_max, image_mutate_rate, status_mutate_rate, prompt_mutate_rate