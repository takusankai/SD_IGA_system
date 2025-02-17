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
8. （NVIDIA GeForse RTX 3060 Ti を使用）「pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124」を実行し pytorch をインストールする（最新バージョンは https://pytorch.org/ のページで 「Compute Platform」が「cu124」の物を探せば良い）
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