# GPT.py の print メッセージは「緑色」\033[92m で表示される
import os
from typing import Dict
import openai
import argparse
import random
from pydantic import BaseModel
from dotenv import load_dotenv

def load_env_settings():
    # APIキーの設定
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # .envファイルの読み込み
    load_dotenv(dotenv_path='OPENAI_API_KEY.env')

    # .envファイルの読み込み
    load_dotenv(dotenv_path='settings.env')
    if not os.path.exists('settings.env'):
        print('\033[92msettings.env の読み込みに失敗した為、辞書語数はデフォルト値を使用します\033[0m')

    # 環境変数の取得(読み込めなければデフォルト値を使用)
    dictionary_size = os.getenv("DICTIONARY_SIZE", "100")
    dictionary_language = os.getenv("DICTIONARY_LANGUAGE", "English")

    return dictionary_size, dictionary_language

# 遺伝子作成用の返答フォーマットの定義
class CreateResponseFormat(BaseModel):
    prompt_dictionaly: list[str]

def create_base_gene_prompts_from_GPT(length_list, input_text):
    print("\033[92mプロンプトを作成するためにGPTにアクセスします\033[0m")

    dictionary_size, dictionary_language = load_env_settings()
    # なぜか 1 少なく返してくるので、 str の dictionary_size を int を経由し +1 して str に戻す
    dictionary_size = str(int(dictionary_size) + 1)
    prompt_list = []
    system_message = f"""
あなたの目標は、ユーザーの入力に基づいて、画像生成AIが特定のデザインテーマに関連する画像を生成するための具体的なプロンプトを提案することです。

- 入力として提供された情報を基に、テーマに関連する1から4単語で構成されるプロンプトを考え出します。
- 完全に同じフレーズは提案してはいけませんが、一部の単語が一致したフレーズを提案することは可能です。
- 提案するプロンプトの数は {dictionary_size} 個です。
- プロンプトは可能な限り具体的で視覚的に明確なイメージを伝える単語を選んでください。
- 提案するプロンプトは{dictionary_language}で構成します。

# Steps

1. ユーザーから提供された情報を分析し、テーマに関連するキーワードやテーマを特定します。
2. 特定したテーマに基づき、具体的な単語やフレーズを選定します。
3. 1から4単語で構成されるプロンプトを {dictionary_size} 個生成します。
4. プロンプトが視覚的にわかりやすいイメージを伝えられるよう工夫します。

# Output Format

- 各プロンプトは{dictionary_language}の1から4単語で構成されます。
- 提案するプロンプトは合計で {dictionary_size} 個。
- 以下の形式で出力してください: 
{{1: "word phrase one", 2: "word phrase two", ..., {dictionary_size}: "word phrase N"}}

# Examples

- 入力例1: [滑り台、揺れる動物の遊具などが設置された公園]
- プロンプト:
    1. "Rocking animals"
    2. "Slide Structures"
    3. "Children's playground"

- 入力例2: [デスク、テーブルなどを青色を基調に統一したインテリアデザイン]
- プロンプト:
    1. "blue furniture"
    2. "compact table"
    3. "monotone Design"

(実際の例では、ユーザーからの入力に応じて調整してください。)

# Notes

- エッジケースとして、非現実的な入力があった場合は、現実的なデザインに関連するプロンプトを生成してください。
- 提案する単語が視覚的イメージを効果的に伝えられるように具体的なオブジェクトを表す名詞を含めるようにするなどの工夫してください。
    """
    
    # GPTへのリクエスト
    completion = openai.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": input_text},
        ],
        response_format=CreateResponseFormat,
    )
    response = completion.choices[0].message

    # レスポンスを辞書形式に変換
    prompt_dictionaly = {i + 1: word for i, word in enumerate(response.parsed.prompt_dictionaly)}

    # レスポンスが何個のプロンプト単語を含むリストであるかを確認
    print(f"\033[92mレスポンスのプロンプト単語数: {len(prompt_dictionaly)}\033[0m")
    # レスポンスのプロンプト単語を確認
    for i, word in prompt_dictionaly.items():
        print(f"\033[92mレスポンスのプロンプト単語{i}: {word}\033[0m")

    # 8個のプロンプトを作成し、リストに追加
    for i in range(8):
        # ランダムに、かつ重複なく length_list[i] 個のプロンプトを選択してリストにする
        prompt = random.sample(list(prompt_dictionaly.values()), length_list[i])
        prompt_list.append(prompt)

    return prompt_list

# 遺伝子変異用の返答フォーマットの定義
class MutateResponseFormat(BaseModel):
    mutated_prompt_words: list[str]

def mutate(prompt, length):
    print("\033[92m遺伝子を変異させるためにGPTにアクセスします\033[0m")
    _, dictionary_language = load_env_settings()
    prompt = " ".join(prompt)
    input_design_target = "滑り台、揺れる動物の遊具、ブランコなどの遊具が多く設置された楽しい子供向けの公園"
    system_message = f"""
あなたは優秀なプロンプトエンジニアで、具体的な単語で構成されるデザインのための画像生成AIのプロンプトを{dictionary_language}で提案します。

## design goal
- デザイン目標: {input_design_target}

## rules
- 各フレーズは1から4単語ほどで構成
- フレーズの数: {str(length)}

## approach
- 入力としてベースとなるフレーズを受け取り、このフレーズの順序を並び変える
- その後、一部を類似しつつも一致はしない新しいフレーズに置き換える

# Steps

1. ユーザー提供のデザイン目標を確認
2. ユーザーの入力を受け取り、目標の達成への貢献度順に並び変える
3. 並び変えたフレーズの一部を類似のフレーズに置き換える
4. rulesに従っているか確認し、提案されたフレーズを提供

# Output Format

- 各フレーズは約1〜4語で構成されたフレーズを{str(length)}個リストにして提供する。
- pythonにてAPIの出力を受け取るため、pythonのlist[str]形式で提供する。

# Examples

### Input
デザイン目標: 滑り台、揺れる動物の遊具、ブランコなどの遊具が多く設置された楽しい子供向けの公園

### Output
- "Rocking animals"
- "Slide Structures"
- "Children's playground"

# Notes

- 類似のニュアンスを伝えるために創造性を活用すること
- フレーズには具体的な単語を使用し、視覚的なイメージを伝えるようにする
    """

    # GPTへのリクエスト
    completion = openai.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            # あなたはプロンプトエンジニアで、なるべく具体的な単語で構成される公園のデザインのための画像生成AIのプロンプトを提案します。
            # 今回のデザイン目標は次の通りです: 滑り台、揺れる動物の遊具、ブランコなど、多くの遊具が設置された子供向けの公園
            # あなたはユーザーの入力を受け取って、そのフレーズを並び変えたり類義語に置き換えたりすることで、新しい1から4単語程度からなる語句を {str(length)} 個提案します。
            # {"role": "system", "content": f"You are a prompt engineer and suggest prompts for an image generation AI for designing a park, consisting of specific words as much as possible."},
            # {"role": "system", "content": f"The design goal this time is as follows: a children's park with many play equipment such as slides, rocking animal play equipment, and swings."},
            # {"role": "system", "content": f"You take the user's input and suggest {str(length)} new phrases consisting of about 1 to 4 words by reordering the phrases and replacing them with synonyms."},
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        response_format=MutateResponseFormat,
    )
    response = completion.choices[0].message

    # レスポンスを確認
    print(f"\033[92m提案されたレスポンスのプロンプト単語数: {len(response.parsed.mutated_prompt_words)}\033[0m")
    print(f"\033[92m提案されたレスポンスのプロンプト単語: {response.parsed.mutated_prompt_words}\033[0m")

    return response.parsed.mutated_prompt_words