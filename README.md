# SD_IGA_system の引き継ぎ用 README.md

マークダウン形式で書かれています。github等のマークダウンが表示できる環境で閲覧下さい。<br>

## 環境構築方法

### 適切なバージョンの python をインストール
1. python 3.10.11（動作確認済み）のインストーラーをブラウザ等からダウンロードする
2. インストーラーを起動する
3. 下のほうの「add python.exe to PATH」にチェックを入れた上で、「customize installation」を押す
4. 「install python 3.10 for all users」にチェックを入れ、自動的に「precompile standard library」にもチェックが入ったことを確認して、「install」を押して管理者権限を許可する

### ライブラリのインストール
5. 当フォルダ「SD_IGA_system」を任意の場所にコピペする
6. vscode をインストールし、vscode 上でこのディレクトリを開き、`ctrl + @`などでターミナルも起動し、`PS 任意の場所/SD_IGA_system> `と表示されていることを確認する
7. `pip install  -r requirement.txt`を実行し、使用するライブラリをインストールする
8. 使用する環境に応じて、以下のいずれかの手順でPyTorchをインストールする
    1. （NVIDIA GeForce RTX 3060 Ti を使用）`pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124`を実行し pytorch をインストールする（最新バージョンは 「[PyTorch公式サイト](https://pytorch.org/)」のページで 「Compute Platform」が「cu124」の物を探せば良い）
    2. （上記以外の GPU を使用）GPU の型番に合った GPU ドライバを調べてインストールし、その GPU ドライバに合ったバージョンの pytorch を調べてインストールする
    3. （GPU を非使用）`pip install torch`を実行 pytorch をインストールする（恐らく最新バージョンで問題無いが、動作確認済みバージョンは`pip install torch==2.6.0`）

### openai の API キーと hugging face の token の設定
9. 「[OpenAI Platform](https://platform.openai.com/docs/overview)」にアクセスしてログインする
10. 諸設定（クレジットカードの登録と最小5ドルの課金を含む）を完了させ、API キーを作成し取得する（以下にある画像を参考）
11. SD_IGA_system 内にある「OPENAI_API_KEY.env」に API キーを書き加えて保存する
12. 「[Hugging Face](https://huggingface.co/)」にアクセスしてログインする
13. 設定内の「Access Tokens」から Token を作成し取得する（以下にある画像を参考）
14. SD_IGA_system 内にある「settings.env」の一番下に token を書き加えて保存する

### システムの起動
15. 上述したターミナル`PS 任意の場所/SD_IGA_system> `にて、`python UI.py`を実行する
16. 初回の画像生成実行時は、画像生成AIモデル（10GB 程度）のダウンロードが入るため時間がかかる。
17. 実行すると「画像、お気に入り画像、csvファイル5点」が作られる。既存のものがある場合は連番で作っていくので、混ざって取り扱いにくくならないよう、予めこまめに削除や移動しておくことが推奨される。
<br>

<details>
<summary>OpenAI APIキーの取得画面の例</summary>

![OpenAI APIキーの取得](https://github.com/user-attachments/assets/12005de8-4e89-474e-84be-c0d02e19ef83)

</details>

<details>

<br>

<summary>Hugging Faceトークンの取得画面の例</summary>

![Hugging Faceトークンの取得](https://github.com/user-attachments/assets/c4f7a9bc-4505-4bc8-bb87-b94b05b5f600)

</details>

<br>

## ディレクトリ構成と各ソースコードの実装意図に関する説明

### 各ソースコードの実装内容に対する説明書き

- UI.py<br>
`def setup_ui()` : tkinter ライブラリを使って全ての UI 要素を宣言し、起動してます。初めにここが呼ばれます。<br>
`def show_○○○_UI()` : 各画面の要素を表示させます。<br>
`def first_iga_loop()` : 画像生成の一回目は特殊な処理です。初期遺伝子とプロンプト辞書を作成をするため、GPT.py が呼ばれます。<br>
`def first_iga_loop_generate_thread(genes)` : 画像生成はスレッドを用いた並列処理されます。一回目は CSV.py で保存先の作成を含めた保存をします。<br>
`def iga_loop()` : 二回目以降はループするように作っています。こちらで IGA_module_4.py が呼ばれます。<br>
`def iga_loop_generate_thread(next_genes)` : 画像生成はスレッドを用いた並列処理されます。二回目以降はループするように作っています。こちらで SD.py と CSV.py が呼ばれます。<br>
（説明）UI.pyがメインの制御コードです。`def setup_ui()`関数を起動時に呼び出して、表示したUIのボタンと紐づいた関数などから処理が進みます。<br>
（課題）突貫的に拡張したのでおかしな実装があります。スレッドの分け方についてはもっと良い方法があると思います。GUIもtk以外で作れば良かったかなと感じています。いちいち遺伝子情報をproject.csvに書き込み読み出ししているのもやや冗長です。<br>
<br>

- GENE.py<br>
（説明）対話型遺伝的アルゴリズムの基礎となる遺伝子型`class GENE`を定義しています。printで確認したくてstrをオーバーライドしている点に気をつけて下さい。<br>
<br>

- GPT.py<br>
`def create_base_dictionary_from_GPT(input_text)` : 初期の50個の画像生成AI向けプロンプト要素を作りますが、GPTプロンプトはこれが最善ではないでしょう…。質に直結する部分である一方で毎回50個帰ってくることを固定すらできていません。なんとかして下さい。また、GPT API の仕様はガンガン変わるので、ここの API の叩き方は直さないと動かない可能性があります。<br>
`def mutate(prompt, length)` : 初期以外にも GPT や類義語辞典を使ったプロンプトの作成を行い突然変異としようと考えていましたが、最終的には全く使っていません。<br>
<br>

- IGA_module_4.py<br>
`def additional(genes, additional_prompt_strength)` : 追加プロンプトが入力された場合に、まず51個目以降のプロンプト要素に対応した形にcsvを調整する。<br>
`def select(genes)` : IGA の選択ステップです。評価値を元に確率で選択します。以降評価値は使われません。<br>
`def crossover(parent_gene_pairs, new_genes)` : IGA の交叉ステップです。シンプルな1点交叉です。<br>
`def mutate(parent_gene_pairs, new_genes)` : IGA の突然変異ステップです。0.1%でランダムに入れ替える単純な処理です。<br>
（説明）これだけ IGA.py でないのは切り替えて試そうと当初思っていたためです。前世代の遺伝子を受け取り次世代の遺伝子を返す単純な入出力にしています。<br>
（課題）シンプルな1点交叉や乱数による突然変異を実装していますが、もっともっと利用者の評価を色濃く反映するようなアルゴリズムを考えた方が良いかもしれません。現状だと10世代程度ではあまり収束した印象を与えません。また、後述しますが実際はプロンプトのみをIGAの対象としており、サンプリングステップやCFGスケールを対象と含めていないので無駄な用意をしている部分が多くあります。<br>
<br>

- SD.py<br>
`class ImageGenerator` : モデル呼び出しなどは i2i も t2i も共通なのでまとめています。<br>
`def i2i_generate_images(self, genes, first_image_path)` : 初期画像を含めたi2i生成です。<br>
`def t2i_generate_images(self, genes)` : テキストのみでのt2i生成です。<br>
（課題）コメントアウトされている部分が多いです。画像生成AIのパイプラインではhuggingfaceで確認できるように様々なパラメータが指定できるようになっており、本来これを変更して精度の向上を目指します。しかし、このコードでは最終的に簡略化のために大体使わないことにして、デフォルトで生成するようにしてしまっています。工夫すればサンプリングステップ数やシード値などもIGAで取り扱い、より面白い生成画像の調整ができるかもしれません。<br>
<br>

- CSV.py<br>
`def init_○○○_csv()` : 新しい連番のcsvファイルを作り、ヘッダーや初回の記録を書き込みます。<br>
`def save_○○○_csv()` : 既存の最新番号のcsvを探し、追加の記録を書き込みます。<br>
`def get_last_generation_genes()` : 遺伝子情報を読み出します。<br>
（説明）csv出力がまとめられています。長くて似てる部分は大体連番にするための処理です。<br>
（課題）段階的に拡張されたのですが、結果的にデータベース（mysqlとか）にすれば良かったかもしれません。<br>
<br>

### ディレクトリ構成図とそれぞれの説明書き

SD_IGA_system               : 提案システムです。作成目的は卒論をご確認ください。<br>
├── generated_images        : 無ければシステムが作成します。実行結果として生成された画像が全て保管され、ここを参照してUI表示します。<br>
├── favorite_images         : 無ければシステムが作成します。お気に入りに選択された画像がここに複製されます。<br>
├── sample_images           : 画像生成の初期画像として使えるかなと思った画像がストックされています。<br>
├── projects                : csv 形式で実行時の情報をここに保存します。<br>
│ ├── dictionary.csv        : これだけ画像生成前に生成されます。GPTの返答結果の50件が書き込まれます<br>
│ ├── project.csv           : 全ての遺伝子が記録されるメインの csv です。<br>
│ ├── favorite.csv          : お気に入りに選択された画像の遺伝子を記録します。<br>
│ ├── additional_prompt.csv : 世代ごとの追加プロンプト機能の使用を記録します。<br>
│ └── show_gene_count.csv   : 世代ごとの生成元プロンプト確認機能の使用を記録します。<br>
├── IGA_modules             : 複数の IGA アルゴリズムを切り替える想定でしたが、実際はしませんでした。<br>
│ ├── IGA_modules_1.py～3.py : 実装途中の物で、見る必要はありません。<br>
│ └── IGA_modules_4.py      : 実験に使っているIGAのアルゴリズムのソースコードです。上述の通りです。<br>
├── .gitattributes/.gitignore : git 関連の自動生成されたファイルです。<br>
├── requirements.txt        : 実行に必要な python のライブラリが書かれた自動生成ファイルです。<br>
├── before_star_image.png/after_star_image.png : UIにボタンとして表示する画像です<br>
├── OPENAI_API_KEY.env      : ここに GPT の API キーを書かないとエラーになります。<br>
├── settings.env            : 末尾に huggingface の token を書かないとエラーになります。他の変数は画像生成パラメータ等の調整・管理を容易にする目的で作成しましたが、最終的に利用していないか変更する必要が無い状態です。<br>
├── memo.txt                : プロンプトを書き置く必要がある際に使用していました。<br>
├── UI.py                   : 上述の通りです。<br>
├── SD.py                   : 上述の通りです。<br>
├── GPT.py                  : 上述の通りです。<br>
├── GENE.py                 : 上述の通りです。<br>
└── CSV.py                  : 上述の通りです。<br>
