# GPT.py の print メッセージは「緑色」\033[92m で表示される
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
    # .envファイルの読み込み
    load_dotenv(dotenv_path='settings.env')
    if not os.path.exists('settings.env'):
        print('\033[92msettings.env の読み込みに失敗した為、辞書語数はデフォルト値を使用します\033[0m')

    dictionary_size = os.getenv("DICTIONARY_SIZE", "100")
    dictionary_language = os.getenv("DICTIONARY_LANGUAGE", "English")
    prompt_list = []
    
    # GPTへのリクエスト
    completion = openai.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            # あなたはユーザーの入力を受け取って、その内容に関連した {dictionary_size} 個の画像生成AIのプロンプトとなる {dictionary_language] の単語を提案します。
            {"role": "system", "content": f"You take the user's input and suggest {dictionary_size} {dictionary_language} words that will prompt for the image-generating AI related to that content."},
            {"role": "user", "content": input_text},
        ],
        response_format=response_format,
    )
    response = completion.choices[0].message

    # レスポンスが何個のプロンプト単語を含むリストであるかを確認
    print(f"\033[92mレスポンスのプロンプト単語数: {len(response.parsed.prompt_words)}\033[0m")
    print(f"\033[92mレスポンスのプロンプト単語: {response.parsed.prompt_words}\033[0m")

    # 8個のプロンプトを作成し、リストに追加
    for i in range(8):
        # ランダムに、かつ重複なく length_list[i] 個のプロンプトを選択してリストにする
        prompt = random.sample(response.parsed.prompt_words, length_list[i])
        prompt_list.append(prompt)

    return prompt_list

def mutate(prompt, length):
    print("\033[92m遺伝子を変異させるためにGPTにアクセスします\033[0m")
    prompt = " ".join(prompt)

    # GPTへのリクエスト
    completion = openai.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            # あなたはユーザーの入力を受け取って、その内容に関連しつつも、どの単語とも重複しない {length_list} 個の単語からなる画像生成AIのプロンプトを提案します。
            {"role": "system", "content": f"You take the user's input and propose an image-generating AI prompt consisting of {str(length)} words that are relevant to the content but do not overlap with any words."},
            {"role": "user", "content": prompt},
        ],
        response_format=response_format,
    )
    response = completion.choices[0].message

    # レスポンスを確認
    print(f"\033[92m提案されたレスポンスのプロンプト単語数: {len(response.parsed.prompt_words)}\033[0m")
    print(f"\033[92m提案されたレスポンスのプロンプト単語: {response.parsed.prompt_words}\033[0m")

    return response.parsed.prompt_words

# UI経由でない直接呼出し用
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--mutate", action="store_true")
    parser.add_argument("--input_text", type=str)
    parser.add_argument("--length_list", type=int, nargs="+")
    
    args = parser.parse_args()
    if args.create:
        create_base_gene_prompts_from_GPT(args.length_list, args.input_text)
    if args.mutate:
        mutate(args.input_text, args.length_list)