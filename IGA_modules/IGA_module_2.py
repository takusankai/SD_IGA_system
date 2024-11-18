import random

def interactive_Genetic_algorithm(genes):
    print("\033[95m選択された遺伝的アルゴリズムは2番。基本的な方針による選択、交叉、突変を行います。\033[0m")
    new_genes = []

    # 選択
    # 評価点を参照し、その個体の評価 / 合計評価の割合を確率として選択し、両親のペアを8組作成
    # 0点の評価を避けるために、全ての評価点に1を加算
    evaluation_scores = [gene.evaluation_score + 1 for gene in genes]
    evaluation_total = sum(evaluation_scores)
    evaluation_probabilities = [score / evaluation_total for score in evaluation_scores]
    # 両親が重複しないように選択
    parent_pairs = []
    for _ in range(8):
        parent1 = random.choices(genes, weights=evaluation_probabilities, k=1)[0]
        parent2 = random.choices(genes, weights=evaluation_probabilities, k=1)[0]
        while parent1 == parent2:
            parent2 = random.choices(genes, weights=evaluation_probabilities, k=1)[0]
        parent_pairs.append((parent1, parent2))
    print(f"\033[95m選択された両親のペア: {parent_pairs}\033[0m")

    # 交叉
    # image の交叉
        
    # status の交叉

    # prompt の交叉


    # 突変
    # image の突変

    # status の突変

    # prompt の突変
    

    return new_genes