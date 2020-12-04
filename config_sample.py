from pathlib import Path

# home_sensor_dashboard config file

# TITLE:
# ページのタイトルです
# TITLE = "Home Env Dashboard"

# SERVICE_ACCOUNT_FILE:
# 認証に利用するGoogle oAuthサービスアカウントの鍵ファイルの保存先を指定してください。
# デフォルトはこのプロジェクトの配下の `oauth_service_account_key.json` ファイルになります。
# SERVICE_ACCOUNT_FILE = Path(__file__).parent / "oauth_service_account_key.json"
#
# LOCATION_LIST:
# 各部屋のセンサー情報が保存されるスプレッドシートのIDを指定してください。
# サンプルのスプレッドシートはこちらです。->https://docs.google.com/spreadsheets/d/12Y4pxrPcIyydN-zWOwN0vw33GRGuCl-GeleUJcsvqcg/edit?usp=sharing
# LOCATION_LIST = {
#     "myroom": {
#         "spreadsheet_id": "[スプレッドシートのID]",
#     },
# }
