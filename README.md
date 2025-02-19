# SD_IGA_system の引き継ぎ用 README.md

## 環境構築方法

### 適切なバージョンの python をインストール
1. python 3.10.11（動作確認済み）のインストーラーをブラウザ等からダウンロードする
2. インストーラーを起動する
3. 下のほうの「add python.exe to PATH」にチェックを入れた上で、customize installation を押す
4. install python 3.10 for all users にチェックを入れ、自動的に precompile standard library にもチェックが入ったことを確認して、install を押して管理者権限を許可する

### ライブラリのインストール
5. 当フォルダ「SD_IGA_system」を任意の場所にコピペする
6. vscode をインストールし、vscode 上でこのディレクトリを開き、ctrl+@などでターミナルも起動し、「PS 任意の場所/SD_IGA_system> 」と表示されていることを確認する
7. 「pip install  -r requirement.txt」を実行し、使用するライブラリをインストールする
8. （NVIDIA GeForce RTX 3060 Ti を使用）「pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124」を実行し pytorch をインストールする（最新バージョンは https://pytorch.org/ のページで 「Compute Platform」が「cu124」の物を探せば良い）
8. （上記以外の GPU を使用）GPU の型番に合った GPU ドライバを調べてインストールし、その GPU ドライバに合ったバージョンの pytorch を調べてインストールする
8. （GPU を非使用）「pip instal torch」を実行 pytorch をインストールする（恐らく最新バージョンで問題無いが、動作確認済みは「pip instal torch==2.6.0」）

### openai の API キーと hugging face の token の設定
9. 「https://platform.openai.com/docs/overview」にアクセスしてログインする
10. 諸設定（クレジットカードの登録と最小5ドルの課金を含む）を完了させ、API キーを作成し取得する（以下にある画像を参考）
11. SD_IGA_system 内にある「OPENAI_API_KEY.env」に API キーを書き加えて保存する
12. 「https://huggingface.co/」にアクセスしてログインする
13. 設定内の「Access Tokens」から Token を作成し取得する（以下にある画像を参考）
14. SD_IGA_system 内にある「settings.env」の一番下に token を書き加えて保存する

### 起動
15. 上述したターミナル「PS 任意の場所/SD_IGA_system> 」にて、「python UI.py」を実行する

![OpenAI APIキーの取得](for_readme_reference\openai.png)
![Hugging Faceトークンの取得](for_readme_reference\hugging_face.png)

## ディレクトリ構成と各ソースコードの実装意図に関する説明

### 各ソースコードの実装内容に対する説明書き

- UI.py
a

- SD.py
a

- GPT.py
a

- GENE.py
a

- IGA_module_4.py
a

- CSV.py
a

### ディレクトリ構成図とそれぞれの説明書き

SD_IGA_system               : 提案システムです。作成目的は卒論をご確認ください。
├── generated_images        : 実行結果として生成された画像が全て保管され、ここを参照してUI表示します。
├── favorite_images         : お気に入りに選択された画像がここに複製されます。
├── sample_images           : 画像生成の初期画像として使えるかなと思った画像がストックされています。
├── projects                : csv 形式で実行時の情報をここに保存します。
│ ├── dictionary.csv        : これだけ画像生成前に生成されます。GPTの返答結果の50件が書き込まれます
│ ├── project.csv           : 全ての遺伝子が記録されるメインの csv です。
│ ├── favorite.csv          : お気に入りに選択された画像の遺伝子を記録します。
│ ├── additional_prompt.csv : 世代ごとの追加プロンプト機能の使用を記録します。
│ └── show_gene_count.csv   : 世代ごとの生成元プロンプト確認機能の使用を記録します。
├── IGA_modules             : 複数の IGA アルゴリズムを切り替える想定でしたが、実際はしませんでした。
│ ├── IGA_modules_1.py から IGA_modules_3.py まで : 実装途中の物で、見る必要はありません。
│ └── IGA_modules_4.py      : 実験に使っているIGAのアルゴリズムのソースコードです。上述の通りです。
├── .gitattributes と .gitignore : git 関連の自動生成されたファイルです。
├── requirements.txt        : 実行に必要な python のライブラリが書かれた自動生成ファイルです。 
├── before_star_image.png と after_star_image.png : UIにボタンとして表示する画像です
├── OPENAI_API_KEY.env      : ここに GPT の API キーを書かないとエラーになります。
├── settings.env            : 末尾に huggingface の token を書架ないとエラーになります。他の変数は画像生成パラメータ等の調整・管理を容易にする目的で作成しましたが、最終的に利用していないか変更する必要が無い状態です。
├── memo.txt                : プロンプトを書き置く必要がある際に使用していました。
├── UI.py                   : 上述の通りです。
├── SD.py                   : 上述の通りです。
├── GPT.py                  : 上述の通りです。
├── GENE.py                 : 上述の通りです。
└── CSV.py                  : 上述の通りです。
