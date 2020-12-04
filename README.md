# Home Env Dashboard

家の環境をグラフ、ダッシュボードで見る「Home Env Dashboard」のダッシュボード本体です。Plotly Dash を利用して作成しています。

センサーノードの構築はこちらを参考にしてください。 -> [hrsano645/homeenvdash_sensor_node: 家環境ダッシュボードのセンサーノード](https://github.com/hrsano645/homeenvdash_sensor_node)

## 動作環境

- python 3.7以上（pipenvでは3.7）
- Windows 10, Ubuntu 20.04

## 利用したPythonパッケージ

[Pipfile](./Pipfile)で確認できます。

## 使い方

[homeenvdash_sensor_node](https://github.com/hrsano645/homeenvdash_sensor_node)のセットアップ時に作成したGoogleサービスアカウントの鍵ファイルを用意します。

配置する場所は任意ですが、`プロジェクトフォルダの直下/oauth_service_account_key.json` を想定しています。

次に、config.pyを作成します。config_sample.pyファイルをコピーしてリネームしてください。

- TITLE: ダッシュボードのタイトル
- SERVICE_ACCOUNT_FILE: Googleサービスアカウントの鍵ファイルのパス
- LOCATION_LIST: センサーノードを区別するための名称（部屋名）とhomeenvdash_sensor_nodeで設定したGoogleスプレッドシートID

```python
# config.py

TITLE = "Home Env Dashboard"

# Googleサービスアカウントの鍵ファイルのパス
SERVICE_ACCOUNT_FILE = Path(__file__).parent / "oauth_service_account_key.json"

# [スプレッドシートID]の部分をIDのみ記載します。
LOCATION_LIST = {
    "myroom": {
        "spreadsheet_id": "[スプレッドシートのID]",
    },
}
```

最後にpipenvで環境を作成し、ダッシュボード（Dashアプリ）を起動します。

```bash
pipenv install
pipenv run ./homeenvdash.py
```

Dashアプリが起動したら`http://127.0.0.1:8050`へアクセスしてください。
