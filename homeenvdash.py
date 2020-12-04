import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas
import plotly.express as px
from dash.dependencies import Input, Output
from google.oauth2 import service_account
from googleapiclient.discovery import build
import dash_bootstrap_components as dbc

import config

# 定数
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# 部屋の名前とgoogle sheetのアドレス, シートとセルの範囲のリストを作成
SAMPLE_RANGE_NAME = "A:D"
VALUE_RENDER_OPTION = "UNFORMATTED_VALUE"

# Googleの認証とAPI接続
credentials = service_account.Credentials.from_service_account_file(
    config.SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=credentials)
sheet = service.spreadsheets()

# 設定の読み込みと、UI用の項目生成
location_list = config.LOCATION_LIST
location_names = [k for k in location_list]

# dashアプリの初期化
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = config.TITLE
app.config.suppress_callback_exceptions = True


def generate_df(
    location_name: str,
    date_range: str = "day",
) -> pandas.DataFrame:
    """
    Args:
        date_range : グラフで表したい日数。dayかweekのどちらか
        location_name : センサーノードを置いてある場所。それぞれスプレッドシートIDが違う
    Returns:
        date_rangeで指定した日数のDataFrameを返します

    google sheet apiで取得した表をもとに、dataframeを生成する。
    day_rangeを day, week のどちらかでdfを出す。デフォルトは1日分
    センサーノードは30分毎に測定と記録を行います。

    dayの行数 = 24時間*2回 = 48件
    weekの行数 = 24時間*2回*7日 = 336行数

    また指定した日数に対して行数が足らない場合は、その分だけ行数のDataFrameを返します。
    """

    # google apiでデータを読み込む
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=location_list[location_name]["spreadsheet_id"],
            range=SAMPLE_RANGE_NAME,
            valueRenderOption=VALUE_RENDER_OPTION,
        )
        .execute()
    )

    result_values = result["values"]
    sheet_columns = result_values[0]
    sheet_values = result_values[1:]

    # df生成し終端から日数分のデータを取得
    base_df = pandas.DataFrame(sheet_values, columns=sheet_columns)

    if date_range == "day" and len(base_df) >= 48:
        return base_df.tail(48)
    elif date_range == "week" and len(base_df) >= 336:
        return base_df.tail(336)
    else:
        return base_df


def generate_graph_tabs(df: pandas.DataFrame) -> html.Div:
    """
    Args:
        df: センサーが記録した表から生成したDataFrame
    Returns:
        生成したグラフと切り替えのタブが入るhtml.Div

    dfを元にplotlyのグラフタブを生成する
    """
    # TODO:2020-11-24 ここは時間以外はオプション的な扱いにして、列ヘッダを見て設定できるととてもいい
    # 時間だけは絶対に必要にして、その列がない場合は例外を出して終了する

    # グラフを並べる（とりあえず右側
    fig1 = px.line(df, x="Time", y="Temperature", title="温度")
    fig2 = px.line(df, x="Time", y="Pressure", title="気圧")
    fig3 = px.line(df, x="Time", y="Humidity", title="湿度")

    return html.Div(
        [
            dbc.Tabs(
                [
                    dbc.Tab(dcc.Graph(id="tempature", figure=fig1), label="温度"),
                    dbc.Tab(dcc.Graph(id="humidity", figure=fig3), label="湿度"),
                    dbc.Tab(dcc.Graph(id="pressure", figure=fig2), label="気圧"),
                ]
            )
        ],
        id="graph_tabs",
    )


def generate_latest_view(df: pandas.DataFrame) -> html.Div:
    """
    Args:
        df: generate_dfで生成したDataFrame
    Returns:
        dfの終端（最新）のセンサー情報を入れたビュー(html.Divでレイアウト)

    generate_dfで作成したDataFrameの終端行を使い、最新のセンサー情報を入れたビューを生成します。
    レイアウトを構成して値を入れた状態のhtml.Divを返します。
    """
    latest_row = df.iloc[-1].to_dict()

    # TODO:2020-11-24 ここは時間以外はオプション的な扱いにして、列ヘッダを見て設定できるととてもいい
    #    時間だけは絶対に必要にして、その列がない場合は例外を出して終了する
    latest_datetime = latest_row["Time"]
    latest_temperature = latest_row["Temperature"]
    latest_pressure = latest_row["Pressure"]
    latest_humidity = latest_row["Humidity"]

    return html.Div(
        [
            dbc.Card(
                [
                    html.H6(f"気温: {latest_temperature}℃"),
                    html.H6(f"湿度: {latest_humidity}%"),
                    html.H6(f"気圧: {latest_pressure}hPa"),
                ],
                body=True,
            ),
            dbc.Label(f"更新時間 :{latest_datetime}"),
        ],
        id="latest_view",
    )


def _layout():
    """
    全体のレイアウト
    """
    # google sheet apiからdf生成
    sensor_df = generate_df(location_names[0], "day")

    latest_view = generate_latest_view(sensor_df)
    graph_tab = generate_graph_tabs(sensor_df)

    # 日付のドロップダウンリスト
    date_dd = dcc.Dropdown(
        id="date-range-dd",
        options=[
            {"label": "1日", "value": "day"},
            {"label": "1週間", "value": "week"},
        ],
        value="day",
        clearable=False,
    )

    # グラフとタブのビュー
    main_view = html.Div(
        [
            html.H4("環境グラフ", style={"textAlign": "center"}),
            date_dd,
            graph_tab,
        ]
    )

    # 部屋ごとのドロップダウンリスト
    location_dd = dcc.Dropdown(
        id="location-dd",
        options=[{"label": name, "value": name} for name in location_names],
        value=location_names[0],
        clearable=False,
    )

    return dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            html.H2(config.TITLE),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [dbc.Label("場所: "), location_dd, latest_view],
                        md=4,
                        id="sidebar",
                    ),
                    dbc.Col(main_view, md=8),
                ],
            ),
            dcc.Interval(
                id="interval-component",
                interval=10 * 60 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ],
    )


# 自動リロードとドロップダウンリストでのコールバック
@app.callback(
    [
        Output("latest_view", "children"),
        Output("graph_tabs", "children"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("date-range-dd", "value"),
        Input("location-dd", "value"),
    ],
)
def update_contents(n, date_dd_value, location_dd_value):
    # now = datetime.datetime.now().astimezone()
    # print(f"リロード時間:{now} 日付:{date_dd_value} 場所:{location_dd_value}")

    sensor_df = generate_df(location_dd_value, date_dd_value)
    sidebar = generate_latest_view(sensor_df)
    graph_tab = generate_graph_tabs(sensor_df)

    return sidebar, graph_tab


if __name__ == "__main__":

    app.layout = _layout
    app.run_server(debug=True, host="0.0.0.0")
