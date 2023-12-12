# slack-ml-predict2

## Slack APIによるプログラミング　機械学習への応用編

Slack APIチュートリアル「NodeJSとSlack APIによるいまどきのネットワークプログラミング」の応用編として機械学習向けにアプリを公開する。

### UIから認識する

天気と気温の組み合わせで最も売れた商品データを学習し、メニューUIを通して指定した天気と気温から売れる商品を予測する。

#### 必要なパッケージをインストールする

コマンドライン上で次のコマンドを起動し、依存するPythonパッケージをインストールする。

```bash
pip install -r requirements.txt
```

#### 環境変数を設定する

本アプリを起動するには環境変数の設定が必要である。env.tplファイルをenv.batバッチファイルとしてコピーし、以下の環境変数を定義する。

```bash
copy env.tpl env.bat
```

|  変数名  |  説明  |
| ---- | ---- |
|  SLACK_BOT_TOKEN  | Botユーザーとして関連付けられたトークン。対象Slackワークスペースのアプリ設定 > [OAuth & Permissions] > [Bot User OAuth Token]から取得する。xoxb-で始まる文字列。 |
|  SLACK_APP_TOKEN  | 全ての組織を横断できるアプリレベルトークン。対象Slackワークスペースのアプリ設定 > [Basic Information] > [App-Level Tokens]から取得する。xapp-で始まる文字列。 |
|  SLACK_USER_TOKEN  | アプリをインストールまたは認証したユーザーに成り代わってAPIを呼び出すことができるトークン。対象Slackワークスペースのアプリ設定 > [OAuth & Permissions] > [User OAuth Token]から取得する。xoxp-で始まる文字列。 |
|  LOCAL_FOLDER  | Slackにアップロードしたファイルを暫定的に保存するローカルフォルダーの名前 |

#### 最も売れる商品を予測する

- 天気と気温の組み合わせで最も売れた商品データを学習し、指定した天気と気温で売れる商品を予測する
- 起動方法

```bash
env.bat
python predict_products.py
```

- スラッシュコマンド/drinksを起動し、天気と気温を入力する（30度を超える気温に設定しておく）
- 「販売予測」ボタンをクリックすると、最も売れると予測されるドリンクがモーダルビューで提示される
- 追加学習用のCSVファイル（DATA/drink_add.csv）をアップロードしたあと、「販売予測」ボタンを再度クリックする
- 追加学習した商品に変わることを確認する

### 更新履歴

- 2023-12-12 pandas.DataFrame.append()からconcat()へ切り替え
- 2023-02-01 初版
