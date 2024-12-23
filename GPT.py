# GPT.py の print メッセージは「緑色」\033[92m で表示される
import os
import openai
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

def create_base_dictionaly_from_GPT(input_text):
    print("\033[92mプロンプトを作成するためにGPTにアクセスします\033[0m")

    dictionary_size, dictionary_language = load_env_settings()
    print(f"\033[92m辞書語数: {dictionary_size}\033[0m")
    print(f"\033[92m辞書言語: {dictionary_language}\033[0m")
    # なぜか 1 少なく返してくるので、 str の dictionary_size を int を経由し +1 して str に戻す
    dictionary_size = str(int(dictionary_size) + 1)

    system_message = f"""
あなたは優秀なプロンプトエンジニアで、ユーザーの入力に基づいて、画像生成AIのための具体的なプロンプトを提案します。

# Steps

1. ユーザーから入力として提供された入力を確認し、目標の画像を生成するために有効なキーワードを特定します。
2. 特定したキーワードに基づき、具体的に1から3単語で構成されるフレーズを考案します。
3. フレーズをOutput Formatに従った形で {dictionary_size} 個生成し、プロンプトとします。
4. 生成されたプロンプトがrulesとOutput Formatに従っていれば提供し、そうでない場合(特に提案フレーズが {dictionary_size} 個でない場合)は再生成します。

# rules
- 提案するフレーズの数は {dictionary_size} 個です。
- 提案するフレーズは{dictionary_language}で構成します。
- 完全に同じフレーズは提案してはいけませんが、一部の単語が一致したフレーズを提案することは可能です。

# Output Format

- 各プロンプトは{dictionary_language}の1から3単語で構成されます。
- 提案するプロンプトは合計で {dictionary_size} 個。
- 次の形式で出力してください: {{1: "word phrase one", 2: "word phrase two", ..., {dictionary_size}: "word phrase N"}}

# Examples

- 入力例1: [滑り台、揺れる動物の遊具などが設置された公園]
- 出力フレーズ例:
    1. "Rocking animals"
    2. "Slide"
    3. "slides and swings"

- 入力例2: [デスク、ベットなどを青色を基調に統一したインテリアデザイン]
- 出力フレーズ例:
    1. "blue"
    2. "blue desk"
    3. "monotone furniture"

# Notes

- 1語のフレーズから4語のフレーズまでバランスよく提案してください。
- 重要度の高い単語は多くのフレーズに含める一方で、多様性の無いプロンプトにはなることは避けてください。
- フレーズには具体的なオブジェクトを表す単語を必ず1つ以上含めるようにしてください。
- ユーザーの入力に応じて柔軟に調整してください。
"""
    
    # 50個のプロンプト単語を含む返却があるまでループ
    is_fifty_words = True
    while is_fifty_words:
        # GPTへのリクエスト
        completion = openai.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": input_text},
            ],
            max_tokens=5000,
            response_format=CreateResponseFormat,
        )
        response = completion.choices[0].message

        # レスポンスをstrのリストに変換
        prompt_dictionaly = {word for word in response.parsed.prompt_dictionaly}

        # レスポンスが何個のプロンプト単語を含むリストであるかを確認
        if len(prompt_dictionaly) == 50:
            is_fifty_words = False
        else:
            print("\033[92m50個のプロンプト単語を含むリストが生成されていません\033[0m")
        print(f"\033[92mレスポンスのプロンプト単語数: {len(prompt_dictionaly)}\033[0m")

    # レスポンスのプロンプト単語を確認
    for i, word in enumerate(prompt_dictionaly):
        print(f"\033[92mレスポンスのプロンプト単語{i+1}: {word}\033[0m")
    
    # 生成に使われたトークン量を取得
    total_tokens = completion.usage.total_tokens
    print(f"\033[92m生成に使われたトークン量: {total_tokens}\033[0m")
    
    return prompt_dictionaly

# 遺伝子変異用の返答フォーマットの定義
class MutateResponseFormat(BaseModel):
    mutated_prompt_words: list[str]

def mutate(prompt, length):
    print("\033[92m遺伝子を変異させるためにGPTにアクセスします\033[0m")

    _, dictionary_language = load_env_settings()
    print(f"\033[92m辞書言語: {dictionary_language}\033[0m")

    prompt = " ".join(prompt)
    input_design_target = "滑り台、揺れる動物の遊具、ブランコなどの遊具が多く設置された楽しい子供向けの公園"

    system_message = f"""
あなたは優秀なプロンプトエンジニアで、ユーザーの入力に基づいて、画像生成AIのための具体的なプロンプトを提案します。

## design goal
- デザイン目標: {input_design_target}

## rules
- 各フレーズは1から4単語で構成
- フレーズの数: {str(length)}
- {dictionary_language}で構成

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
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=5000,
        response_format=MutateResponseFormat,
    )
    response = completion.choices[0].message

    # レスポンスを確認
    print(f"\033[92m提案されたレスポンスのプロンプト単語数: {len(response.parsed.mutated_prompt_words)}\033[0m")
    print(f"\033[92m提案されたレスポンスのプロンプト単語: {response.parsed.mutated_prompt_words}\033[0m")
    total_tokens = completion.usage.total_tokens
    print(f"\033[92m生成に使われたトークン量: {total_tokens}\033[0m")

    return response.parsed.mutated_prompt_words