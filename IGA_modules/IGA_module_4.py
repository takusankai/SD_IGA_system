# IGA_module_3.py の print メッセージは「シアン」\033[96m で表示される
import random
from GENE import Gene
from GPT import create_base_dictionary_from_GPT, mutate
import os
from dotenv import load_dotenv

# 初期の8個の遺伝子の構築
def create_base_genes(input_text):
    print("\033[96m初期の8個の遺伝子を作成します\033[0m")

    # setting.env から範囲変数を読み込む
    (image_strength_min, image_strength_max, seed_min, seed_max, steps_min, steps_max, prompt_length_min, prompt_length_max, cfg_scale_min, cfg_scale_max, _, _, _, _, _, _) = load_settings()
    
    # 初期の遺伝子となる8個のgeneのリストを作成
    genes = [Gene() for _ in range(8)]
    
    for i in range(8):
        # image_strength は image_strength_min から image_strength_max の間でランダムに生成
        genes[i].image_strength = round(random.uniform(image_strength_min, image_strength_max), 2)
        # seed は seed_min から seed_max の間でランダムに生成
        genes[i].seed = random.randint(seed_min, seed_max)
        # steps は steps_min から steps_max の間でランダムに生成
        genes[i].steps = random.randint(steps_min, steps_max)
        # prompt_length は prompt_length_min から prompt_length_max の間でランダムに生成
        genes[i].prompt_length = random.randint(prompt_length_min, prompt_length_max)
        # cfg_scale は cfg_scale_min から cfg_scale_max の間でランダムに生成
        genes[i].cfg_scale = round(random.uniform(cfg_scale_min, cfg_scale_max), 1)
        # weight_list は 50 個を 0 が 35 つ、1 が 5 つ、2 が 5 つ、3 が 5 つになるようにランダムに生成
        weight_list = [0] * 35 + [1] * 5 + [2] * 5 + [3] * 5
        random.shuffle(weight_list)
        genes[i].weight_list = weight_list

    print(f"\033[96m初期の8個の遺伝子を作成しました\033[0m")

    # 折角 GPT を import してるので、ついでにここで prompt_dictionary を作成
    prompt_dictionary = create_base_dictionary_from_GPT(input_text)
    return genes, prompt_dictionary

def create_next_generation_genes(genes, additional_prompt, additional_prompt_strength):
    print("\033[96m選択された遺伝的アルゴリズムは4番。\033[0m")

    # genes に追加プロンプトと強度を割り振る
    if additional_prompt:
        genes = additional(genes, additional_prompt_strength)
    # 次の遺伝子となる8個のgeneのリストを作成
    new_genes = [Gene() for _ in range(8)]
    # 選択
    parent_gene_pairs = select(genes)
    # 交叉
    new_genes = crossover(parent_gene_pairs, new_genes)
    # 突然変異
    new_genes = mutate(parent_gene_pairs, new_genes)

    return new_genes

def additional(genes, additional_prompt_strength):
    # 全ての gene.weight_list の末尾を additional_prompt_strength に応じた値に変更
    print(f"\033[96mgenesの数: {len(genes)}\033[0m")
    for gene in genes:
        # {addtional_prompt_strength}% の確率で weight_list の末尾を 1 から 3 に変更
        # 1 - {addtional_prompt_strength}% の確率で weight_list の末尾を 0 に変更
        additional_weight = random.choices([0, 1, 2, 3], [100 - additional_prompt_strength, additional_prompt_strength/3, additional_prompt_strength/3, additional_prompt_strength/3])
        # list になっているので、0番目の要素をintに変換
        gene.weight_list[-1] = additional_weight[0]
        print(f"\033[96m追加されたweight_listの値: {additional_weight}\033[0m")
    return genes

def select(genes):
    # 評価点を参照し、その個体の評価 / 合計評価の割合を確率として選択し、両親のペアを4組作成

    # evaluation_scores == 0 が8個中7個以上ある場合は、全てに +1 して演算する
    if sum([gene.evaluation_score == 0 for gene in genes]) >= 7:
        evaluation_scores = [gene.evaluation_score + 1 for gene in genes]
    else:
        evaluation_scores = [gene.evaluation_score for gene in genes]
    
    parent_gene_pairs = []
    for _ in range(4):
        # 評価を重みとして 0-7 のインデックスを選択
        selected_indices = random.choices(range(8), evaluation_scores, k=2)
        while selected_indices[0] == selected_indices[1]:
            selected_indices = random.choices(range(8), evaluation_scores, k=2)
        parent_gene_pairs.append((genes[selected_indices[0]], genes[selected_indices[1]]))
        print(f"\033[96m選択された両親の遺伝子のインデックス: {selected_indices}\033[0m")

    print("") # for 抜けたので改行

    return parent_gene_pairs

def crossover(parent_gene_pairs, new_genes):
    # gene の weight_list が 何個の整数を持っているかを確認
    length = len(parent_gene_pairs[0][0].weight_list)

    # すぐ下のループで使う
    def create_gene_data_list(gene):
        gene_data_list = [gene.image_strength, gene.seed, gene.steps, gene.prompt_length, gene.cfg_scale]
        gene_data_list.extend(gene.weight_list)
        return gene_data_list

    for i in range(4):
        # 交叉点をランダムに選択(要素は 1 から 5 + length - 1)
        cross_point = random.randint(1, 5 + length - 1)
        print(f"\033[96m{i}番目の両親の交叉点: {cross_point}\033[0m")
        
        # gene_data_list (image_strength, seed, steps, prompt_length, cfg_scale, weight_list[0], weight_list[1], ..., weight_list[length-1]) を作成
        gene_data_list_1 = create_gene_data_list(parent_gene_pairs[i][0])
        gene_data_list_2 = create_gene_data_list(parent_gene_pairs[i][1])
        
        # 交叉点より前の遺伝子をgene_data_list_1から、交叉点より後の遺伝子をgene_data_list_2から取得し、new_gene_data_list_1に設定
        new_gene_data_list_1 = gene_data_list_1[:cross_point] + gene_data_list_2[cross_point:]
        print(f"\033[96mnew_gene_data_list_1: {new_gene_data_list_1}\033[0m")
        
        # 交叉点より前の遺伝子をgene_data_list_2から、交叉点より後の遺伝子をgene_data_list_1から取得し、new_gene_data_list_2に設定
        new_gene_data_list_2 = gene_data_list_2[:cross_point] + gene_data_list_1[cross_point:]
        print(f"\033[96mnew_gene_data_list_2: {new_gene_data_list_2}\033[0m")

        # new_gene_data_list_1 と new_gene_data_list_2 を new_genes に設定
        new_genes[i*2].image_strength = new_gene_data_list_1[0]
        new_genes[i*2].seed = new_gene_data_list_1[1]
        new_genes[i*2].steps = new_gene_data_list_1[2]
        new_genes[i*2].prompt_length = new_gene_data_list_1[3]
        new_genes[i*2].cfg_scale = new_gene_data_list_1[4]
        new_genes[i*2].weight_list = new_gene_data_list_1[5:]
        new_genes[i*2+1].image_strength = new_gene_data_list_2[0]
        new_genes[i*2+1].seed = new_gene_data_list_2[1]
        new_genes[i*2+1].steps = new_gene_data_list_2[2]
        new_genes[i*2+1].prompt_length = new_gene_data_list_2[3]
        new_genes[i*2+1].cfg_scale = new_gene_data_list_2[4]
        new_genes[i*2+1].weight_list = new_gene_data_list_2[5:]
    
    print("") # for 抜けたので改行
    return new_genes

def mutate(parent_gene_pairs, new_genes):
    # setting.env から範囲変数と突然変異率を読み込む
    (image_strength_min, image_strength_max, seed_min, seed_max, steps_min, steps_max, 
     prompt_length_min, prompt_length_max, cfg_scale_min, cfg_scale_max, 
     image_mutate_rate, seed_mutate_rate, steps_mutate_rate, 
     prompt_length_mutate_rate, cfg_scale_mutate_rate, weight_list_mutate_rate) = load_settings()

    for i in range(8):
        # image_strength 突変は、image_mutate_rate の確率で image_strength_min から image_strength_max の間でランダムに生成
        if random.random() < image_mutate_rate:
            print(f"\033[96mgene[{i}]のimage_strengthを{new_genes[i].image_strength}から突然変異\033[0m")
            new_genes[i].image_strength = round(random.uniform(image_strength_min, image_strength_max), 2)
            print(f"\033[96mnew_genes[{i}].image_strength: {new_genes[i].image_strength}\033[0m")

        # seed 突変は、seed_mutate_rate の確率で seed_min から seed_max の間でランダムに生成
        if random.random() < seed_mutate_rate:
            print(f"\033[96mgene[{i}]のseedを{new_genes[i].seed}から突然変異\033[0m")
            new_genes[i].seed = random.randint(seed_min, seed_max)
            print(f"\033[96mnew_genes[{i}].seed: {new_genes[i].seed}\033[0m")

        # steps 突変は、steps_mutate_rate の確率で steps_min から steps_max の間でランダムに生成
        if random.random() < steps_mutate_rate:
            print(f"\033[96mgene[{i}]のstepsを{new_genes[i].steps}から突然変異\033[0m")
            new_genes[i].steps = random.randint(steps_min, steps_max)
            print(f"\033[96mnew_genes[{i}].steps: {new_genes[i].steps}\033[0m")
        
        # prompt_length 突変は、prompt_length_mutate_rate の確率で prompt_length_min から prompt_length_max の間でランダムに生成
        if random.random() < prompt_length_mutate_rate:
            print(f"\033[96mgene[{i}]のprompt_lengthを{new_genes[i].prompt_length}から突然変異\033[0m")
            new_genes[i].prompt_length = random.randint(prompt_length_min, prompt_length_max)
            print(f"\033[96mnew_genes[{i}].prompt_length: {new_genes[i].prompt_length}\033[0m")
        
        # cfg_scale 突変は、cfg_scale_mutate_rate の確率で cfg_scale_min から cfg_scale_max の間でランダムに生成
        if random.random() < cfg_scale_mutate_rate:
            print(f"\033[96mgene[{i}]のcfg_scaleを{new_genes[i].cfg_scale}から突然変異\033[0m")
            new_genes[i].cfg_scale = round(random.uniform(cfg_scale_min, cfg_scale_max), 1)
            print(f"\033[96mnew_genes[{i}].cfg_scale: {new_genes[i].cfg_scale}\033[0m")
        
        # weight_list 突変は、len(weight_list) に対して、weight_list_mutate_rate の確率で 0 から 3 の間でランダムに生成
        for j in range(len(new_genes[i].weight_list)):
            if random.random() < weight_list_mutate_rate:
                print(f"\033[96mgene[{i}]のweight_list[{j}]を{new_genes[i].weight_list[j]}から突然変異\033[0m")
                # new_genes[i].weight_list[j] = random.randint(0, 3)
                # 0 になる確率を 0.5、1 になる確率を 0.17、2 になる確率を 0.17、3 になる確率を 0.16 に設定
                new_genes[i].weight_list[j] = random.choices([0, 1, 2, 3], [50, 17, 17, 16])[0]
                print(f"\033[96mnew_genes[{i}].weight_list[{j}]: {new_genes[i].weight_list[j]}\033[0m")

    print("") # for 抜けたので改行
    return new_genes

def load_settings():
    # 範囲変数を setting.env から読み込む
    load_dotenv(dotenv_path='settings.env')
    if not os.path.exists('settings.env'):
        print('\033[96msettings.env の読み込みに失敗した為、初期遺伝子の設定はデフォルト値を使用します\033[0m')
    # 環境変数の取得(読み込めなければデフォルト値を使用するが、settings.env があれば基本使われない)
    image_strength_min = float(os.getenv("IMAGE_STRENGTH_MIN", 0.1))
    image_strength_max = float(os.getenv("IMAGE_STRENGTH_MAX", 0.6))
    seed_min = int(os.getenv("SEED_MIN", 0))
    seed_max = int(os.getenv("SEED_MAX", 100))
    steps_min = int(os.getenv("STEPS_MIN", 1))
    steps_max = int(os.getenv("STEPS_MAX", 4))
    prompt_length_min = int(os.getenv("PROMPT_LENGTH_MIN", 10))
    prompt_length_max = int(os.getenv("PROMPT_LENGTH_MAX", 20))
    cfg_scale_min = float(os.getenv("CFG_SCALE_MIN", 6.0))
    cfg_scale_max = float(os.getenv("CFG_SCALE_MAX", 20.0))
    image_mutate_rate = float(os.getenv("IMAGE_STRENGTH_MUTATE_RATE", 0.1))
    seed_mutate_rate = float(os.getenv("SEED_MUTATE_RATE", 0.1))
    steps_mutate_rate = float(os.getenv("STEPS_MUTATE_RATE", 0.1))
    prompt_length_mutate_rate = float(os.getenv("PROMPT_LENGTH_MUTATE_RATE", 0.1))
    cfg_scale_mutate_rate = float(os.getenv("CFG_SCALE_MUTATE_RATE", 0.1))
    weight_list_mutate_rate = float(os.getenv("WEIGHT_LIST_MUTATE_RATE", 0.01))

    return (image_strength_min, image_strength_max, seed_min, seed_max, steps_min, steps_max, 
            prompt_length_min, prompt_length_max, cfg_scale_min, cfg_scale_max, 
            image_mutate_rate, seed_mutate_rate, steps_mutate_rate, 
            prompt_length_mutate_rate, cfg_scale_mutate_rate, weight_list_mutate_rate)