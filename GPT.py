# GPT.py の print メッセージは「緑色」で表示される
import os
import openai
import argparse
import random
from pydantic import BaseModel
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv(dotenv_path='OPENAI_API_KEY.env')
# APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# 返答フォーマットの定義
class response_format(BaseModel):
    prompt_words: list[str]

def create_base_gene_prompts_from_GPT(length_list, input_text):
    print("\033[92mGPTを使用して初期遺伝子のプロンプトを生成します\033[0m")
    prompt_list = []

    # GPTへのリクエスト
    completion = openai.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            # あなたはユーザーの入力を受け取って、その内容に関連した100個の画像生成AIのプロンプトとなる英語の単語を提案します。
            {"role": "system", "content": "You take the user's input and suggest 100 English words that will prompt for the image-generating AI related to that content."},
            {"role": "user", "content": input_text},
        ],
        response_format=response_format,
    )
    response = completion.choices[0].message

    # レスポンスが何個のプロンプト単語を含むリストであるかを確認
    print(f"\033[92mレスポンスのプロンプト単語数: {len(response.parsed.prompt_words)}\033[0m")    

    # 8個のプロンプトを作成し、リストに追加
    for i in range(8):
        # ランダムに、かつ重複なく length_list[i] 個のプロンプトを選択してリストにする
        prompt = random.sample(response.parsed.prompt_words, length_list[i])
        prompt_list.append(prompt)

    return prompt_list

def mutate():
    print("\033[92m遺伝子を変異させます\033[0m")
    return

# UI経由でない直接呼出し用
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--input_text", type=str)
    parser.add_argument("--length_list", type=int, nargs="+")
    parser.add_argument("--mutate", action="store_true")
    # 後で作るparser.add_argument("--input_image", type=str)

    args = parser.parse_args()
    if args.create:
        create_base_gene_prompts_from_GPT(args.length_list, args.input_text)
    if args.mutate:
        mutate()