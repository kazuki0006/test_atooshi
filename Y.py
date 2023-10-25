# ライブラリのインポート
import datetime
import json
import urllib.parse
import urllib.request
import time
import streamlit as st #フロントエンドを扱うstreamlitの機能をインポート
from PIL import Image
import googlemaps
import pandas as pd
import base64
from io import BytesIO

# Google MapsのエンドポイントとAPIキーの入力
endpoint = "https://maps.googleapis.com/maps/api/directions/json?"
api_key = "AIzaSyBH_m_Cg48Sgp7fw_AwfITti0S9WcWKNf8"

# ライブラリのインポート (スクレイピング用)
import re  # 正規表現を使用するためにインポート

import requests
from bs4 import BeautifulSoup

# 画像のディレクトリ指定
image_directory = "image/"

# session_stateの初期化
if 'page2' not in st.session_state:
    st.session_state.page2 = False
    
if not st.session_state.page2:   
    st.set_page_config(
            page_title="Y",
            layout="wide", 
            menu_items={
                 'Get Help': 'https://www.google.com',
                 'Report a bug': "https://www.google.com",
                 'About': """
                 # 物件の最終判断を後押しするアプリ
                 このアプリはtech0の有志チームが作成しています。
                 """
             })

    #バナー指定
    image = Image.open('image/INPUT_TOP.png')
    st.image(image, use_column_width=True)



    #SERVICE説明
    html_message = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 32px;'>SERVICE</p>"
    st.markdown(html_message, unsafe_allow_html=True)
    html_message0 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 24px;'>新しい居住地。<br>転勤で引越しをするときは慌ただしく転居先を決める必要があります。<br>見知らぬ地への転勤であなたは大事にしたいポイントを押さえられていますか。<br>あなたが物件選びで重視したいポイントを教えてください。<br>「最終判断後押しくん」は物件情報だけではわからない、あなたが大事にするポイントをスコア化して<br>物件の最終判断を後押しします。</p>"
    st.markdown(html_message0, unsafe_allow_html=True)
    image1 = Image.open('image/INPUT_SCORE.png') 
    st.image(image1, use_column_width=True)
    #スコア名表示部分
    col1, col2, col3, col4 = st.columns(4)

    html_message2 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 24px;'>働きやすさスコア</p>"
    col1.markdown(html_message2, unsafe_allow_html=True)

    html_message3 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 24px;'>生活スコア</p>"
    col2.markdown(html_message3, unsafe_allow_html=True)

    html_message4= "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 24px;'>子育てスコア</p>"
    col3.markdown(html_message4, unsafe_allow_html=True)

    html_message5 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 24px;'>安心スコア</p>"
    col4.markdown(html_message5, unsafe_allow_html=True)

    ######################################################################################
    #スコア解説表示部分
    col1, col2, col3, col4 = st.columns(4)

    html_message6 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 16px;'>勤務地と検討物件との距離<br>からスコアを算出</p>"
    col1.markdown(html_message6, unsafe_allow_html=True)

    html_message7 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 16px;'>検討物件の近隣にあるスーパー、<br>飲食店との距離・施設数から算出</p>"
    col2.markdown(html_message7, unsafe_allow_html=True)

    html_message8= "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 16px;'>検討物件の近隣にある保育園、<br>小学校、公園との距離・施設数から算出</p>"
    col3.markdown(html_message8, unsafe_allow_html=True)

    html_message9 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 16px;'>検討物件の近隣にある交番、<br>消防署との距離・施設数から算出</p>"
    col4.markdown(html_message9, unsafe_allow_html=True)


    #空白行の追加
    st.markdown('#')
    st.markdown('#')


    #配分入力方法説明
    html_message10 = "<p style='font-family: Hiragino Sans GB; text-align: center; font-size: 24px;'>すべてのスコアが100％となるように重視したいポイントを調整してください</p>"
    st.markdown(html_message10, unsafe_allow_html=True)

    ## C: カテゴリーの重要度を入力（Scoringに使用するWeightを受け取る) ##

    # 入力値の合計が100でない場合は再入力
    while True:
        col1, col2, col3, col4 = st.columns(4)
        col1.write("<div style='text-align:center'>働きやすさの重要度 (%):</div>", unsafe_allow_html=True)
        weight_work = col1.number_input('', value=25, min_value=0, max_value=100,key="weight_work")
        col2.write("<div style='text-align:center'>暮らしやすさの重要度 (%):</div>", unsafe_allow_html=True)
        weight_life = col2.number_input("", value=25, min_value=0, max_value=100,key="weight_life")
        col3.write("<div style='text-align:center'>育てやすさの重要度　 (%):</div>", unsafe_allow_html=True)
        weight_kids = col3.number_input("", value=25, min_value=0, max_value=100,key="weight_kids")

        # 各入力を数値に変換
        # 数値でなければ指摘
        try:
            weight_work = float(weight_work)
            weight_life = float(weight_life)
            weight_kids = float(weight_kids)
        except ValueError:
            st.write("数値を入力してください。")
            continue

        col4.write("<div style='text-align:center'>安心しやすさの重要度(%):</div>", unsafe_allow_html=True)
        weight_safe = col4.number_input("",100 - weight_work - weight_life - weight_kids,key="weight_safe")

        # 最後の項目の重要度が0以上であることを確認
        if weight_safe < 0:
            st.write("重要度の合計が100を超えないように入力してください。")
        else:
            break



    ## D: カテゴリー内の細目の重要度を入力（Scoringに使用するWeightを受け取る) ##

    # ②暮らしやすさの細目の重要度を入力
    #暮らしやすさの内訳入力部分
    # 4つのカラムを作成
    col1, col2, col3, col4 = st.columns(4)
    # ボタン1を2列目に配置（中央揃え）
    with col2:
        st.markdown("""
            <style>
                div.stButton > button {
                    display: block;
                    margin: 0 auto;
                }
            </style>
        """, unsafe_allow_html=True)

        life_expander = st.expander("暮らしやすさの詳細", expanded=False)
        with life_expander:
            # 入力値の合計が100でない場合は再入力
            while True:
                weight_life_supermarket = st.number_input("スーパーの重要度を入力 (%): ", value=33,key="weight_life_supermarket")
                weight_life_hospital = st.number_input("病院の重要度を入力 (%): ", value=33,key="weight_life_hospital")

                # 各入力を数値に変換
                # 数値でなければ指摘
                try:
                    weight_life_supermarket = float(weight_life_supermarket)
                    weight_life_hospital = float(weight_life_hospital)
                except ValueError:
                    st.write("数値を入力してください。")
                    continue

                weight_life_restaurant = st.number_input("飲食店の重要度", 100 - (weight_life_supermarket + weight_life_hospital),key="weight_life_restaurant")
    ## E: 細目 (暮らしやすさ) における飲食店の好みを入力 (検索に入力する料理ジャンルを受け取る) ##

    # 好みの料理店ジャンル
                place_name_favorite = st.text_input("好みの食事ジャンルを入力 (例:ラーメン) : ")      
                # 最後の項目の重要度が0以上であることを確認
                if weight_life_restaurant < 0:
                    st.write("重要度の合計が100を超えないように入力してください。")
                else:
                    break

    #③育てやすさの細目の重要度を入力
    #育てやすさの内訳入力部分
    # ボタン2を3列目に配置（中央揃え）
    with col3:
        st.markdown("""
            <style>
                div.stButton > button {
                    display: block;
                    margin: 0 auto;
                }
            </style>
        """, unsafe_allow_html=True)

        kids_expander = st.expander("育てやすさの詳細", expanded=False)
        with kids_expander:
    # 入力値の合計が100でない場合は再入力
            while True:
                weight_kids_nursery = st.number_input("保育園の重要度を入力 (%): ", value=25,key="weight_kids_nursery")
                weight_kids_kindergarten = st.number_input("幼稚園の重要度を入力 (%): ", value=25,key="weight_kids_kindergarten")
                weight_kids_elementary = st.number_input("小学校の重要度を入力 (%): ", value=25,key="weight_kids_elementary")

                # 各入力を数値に変換
                # 数値でなければ指摘
                try:
                    weight_kids_nursery = float(weight_kids_nursery)
                    weight_kids_kindergarten = float(weight_kids_kindergarten)
                    weight_kids_elementary = float(weight_kids_elementary)
                except ValueError:
                    print("数値を入力してください。")
                    continue

                weight_kids_park = st.number_input("公園の重要度",100 - (
                    weight_kids_nursery + weight_kids_kindergarten + weight_kids_elementary
                ),key="weight_kids_park")

                # 最後の項目の重要度が0以上であることを確認
                if weight_kids_park < 0:
                    st.write("重要度の合計が100を超えないように入力してください。")
                else:
                    break        





    #B: 勤務地の住所を入力
    html_message1 = "<p style='text-align: center; font-size: 24px;'>勤務先の住所を入力してください</p>"
    st.markdown(html_message1, unsafe_allow_html=True)
    workplace = st.text_input("勤務地の住所を入力")


    ## A-1: 3つの候補物件のURLまたは住所をリストとして受け取る ##
    html_message2 = "<p style='text-align: center; font-size: 24px;'>検討している物件のURLを3件まで入力してください</p>"
    st.markdown(html_message2, unsafe_allow_html=True)
    addresses_original = [
        st.text_input("候補物件①のURLまたは住所を入力: "),
        st.text_input("候補物件②のURLまたは住所を入力: "),
        st.text_input("候補物件③のURLまたは住所を入力: "),
    ]

## A-2: 入力内容がURLかを判定し、是ならスクレイピングで住所を取得し上書きする ##

    # 関数の定義: ①スクレイピングで物件名を取得
    def scraping_name(address_original):
        # URLからHTMLソースコードを取得
        response = requests.get(address_original)

        # リクエストが成功したかを確認
        if response.status_code == 200:
            # HTMLをBeautiful Soupを使用して解析
            soup = BeautifulSoup(response.text, "html.parser")

            # センテニアルタワーの物件名を抜き出す
            property_name = soup.find("h1", class_="section_h1-header-title").text

            return property_name
        else:
            return f"{addresses_original} からデータを取得できませんでした。"


    # 関数の定義: ②入力内容がURLかどうかを判定し、物件名を取得
    def confirm_url_scraping_name(address):
        # 正規表現を使用してURLかどうかを確認
        url_pattern = re.compile(r"https?://\S+")
        if url_pattern.match(address):
            return scraping_name(address)  # URLの場合、scraping_name関数を適用
        else:
            return f"{addresses_original} からデータを取得できませんでした。"


    ## 物件名の取得 ##
    property_names = []
    
    for address in addresses_original:
        property_name = confirm_url_scraping_name(address)
        property_names.append(property_name)    
    
    
 ## A-3: 入力内容がURLかを判定し、是ならスクレイピングで住所を取得し上書きする ##

    ## 設定・準備 ##


    # 関数の定義: ①スクレイピングで物件情報を取得
    def scraping_data(address):
        response = requests.get(address)
        soup = BeautifulSoup(response.text, "html.parser")
        data = {}

        # データを特定のセレクタを使って取得
        rows = soup.find_all("tr")
        for row in rows:
            key = row.find("th", class_="property_view_table-title")
            value = row.find("td", class_="property_view_table-body")
            if key and value:
                key = key.text.strip()
                value = value.text.strip()
                data[key] = value

        # 特定のテーブルを取得
        table = soup.find("table", {"class": "data_table table_gaiyou"})

        # テーブル内のtr要素を取得
        if table:
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th", class_="data_01")
                td = row.find("td")

                if th and td:
                    key = th.text.strip()
                    value = td.text.strip()
                    data[key] = value

            # 特定のテーブル内のtr要素を取得
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th", class_="data_02")
                td = row.find("td")

                if th and td:
                    key = th.text.strip()
                    # 次の兄弟要素のtdを取得
                    value = td.find_next_sibling("td").text.strip()
                    data[key] = value

        return data


    # 関数の定義: ②入力内容がURLかどうかを判定
    def confirm_url_scraping_data(address):
        # 正規表現を使用してURLかどうかを確認
        url_pattern = re.compile(r"https?://\S+")
        if url_pattern.match(address):
            return scraping_data(address)  # URLの場合、scraping_data関数を適用
        else:
            return {"所在地": address}  # URLでない場合、所在地情報を含む辞書を返す


    ## 住所の更新 ##

    # 所在地情報を取得し、住所を更新
    addresses = [
        confirm_url_scraping_data(address).get("所在地", "所在地情報なし")
        for address in addresses_original
    ]
        
   
    # ボタンがクリックされたかどうかの状態を初期化
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False

    #空白行の追加
    st.markdown('#')
    
    st.session_state.input_data = []   
    
    if st.button("Score Check!"):

        st.session_state.input_data = {
            "weight_work": weight_work,
            "weight_life": weight_life,
            "weight_kids": weight_kids,
            "weight_safe": weight_safe,
            "weight_life_supermarket": weight_life_supermarket,
            "weight_life_hospital": weight_life_hospital,
            "weight_life_restaurant": weight_life_restaurant,
            "weight_kids_nursery": weight_kids_nursery,
            "weight_kids_kindergarten": weight_kids_kindergarten,
            "weight_kids_elementary": weight_kids_elementary,
            "weight_kids_park": weight_kids_park,
            "workplace": workplace,
            "addresses": addresses,
            "place_name_favorite": place_name_favorite,
            "property_names": property_names,
        }

        st.session_state.button_clicked = True
        st.session_state.page2 = True
        st.experimental_rerun()  # ページをリフレッシュ

########################################################################################################


if st.session_state.page2:
    st.set_page_config(
        page_title="YY",
        layout="wide", 
        menu_items={
             'Get Help': 'https://www.google.com',
             'Report a bug': "https://www.google.com",
             'About': """
             # 物件の最終判断を後押しするアプリ
             このアプリはtech0の有志チームが作成しています。
             """
         })    



    

    df = pd.DataFrame([st.session_state.input_data],)
    df.columns = [
        "重要度(%): 働きやすさ",
        "重要度(%): 暮らしやすさ",
        "重要度(%): 育てやすさ",
        "重要度(%): 安心しやすさ",
        "重要度(%): スーパー",
        "重要度(%): 病院",
        "重要度(%): 飲食店",
        "重要度(%): 保育園",
        "重要度(%): 幼稚園",
        "重要度(%): 小学校",
        "重要度(%): 公園",        
        "勤務地住所",
        "候補物件住所",
        "好みの食事ジャンル",
        "物件名",
    ]


    
####################################################################################################################################################################################################
# 今日の日付を取得し、文字列として表示（YYYY-MM-DD形式）
    today = datetime.date.today()
    today_str = today.strftime("%Y/%m/%d")

    # データを格納するためのリストを作成
    data_work = []


    # スコアリングの定義: 勤務地までの時間
    def calculation_work(duration_work):
        if duration_work <= 15:
            return 100
        elif duration_work <= 20:
            return 90
        elif duration_work <= 30:
            return 80
        elif duration_work <= 40:
            return 70
        elif duration_work <= 50:
            return 60
        elif duration_work <= 60:
            return 50
        else:
            return 30
###################################################################################################
    
    addresses = st.session_state.input_data.get("addresses", [])
    workplace = st.session_state.input_data.get("workplace", [])
    place_name_favorite = st.session_state.input_data.get("place_name_favorite", [])
    weight_life_supermarket = st.session_state.input_data.get("weight_life_supermarket", [])
    weight_life_hospital = st.session_state.input_data.get("weight_life_hospital", [])
    weight_life_restaurant = st.session_state.input_data.get("weight_life_restaurant", [])
    weight_kids_nursery = st.session_state.input_data.get("weight_kids_nursery", [])
    weight_kids_kindergarten = st.session_state.input_data.get("weight_kids_kindergarten", [])
    weight_kids_elementary = st.session_state.input_data.get("weight_kids_elementary", [])
    weight_kids_park = st.session_state.input_data.get("weight_kids_park", [])
    weight_work = st.session_state.input_data.get("weight_work", [])
    weight_life = st.session_state.input_data.get("weight_life", [])
    weight_kids = st.session_state.input_data.get("weight_kids", [])
    weight_safe = st.session_state.input_data.get("weight_safe", [])
    property_names = st.session_state.input_data.get("property_names", [])
    
######################################################################################################


# 各住所に対して処理を繰り返す
    for address in addresses:
        nav_request = "language=ja&origin={}&destination={}&key={}".format(
            address, workplace, api_key
        )  # 👈改善ポイント: 電車での出力は一意にならずDF化が難しいため車での時間表示となっている
        nav_request = urllib.parse.quote_plus(nav_request, safe="=&")
        request = endpoint + nav_request

        # Google Maps Platform Directions APIを実行
        response = urllib.request.urlopen(request).read()

        # 結果(JSON)を取得
        directions = json.loads(response)

        # 所要時間を取得
        for key in directions["routes"]:
            for key2 in key["legs"]:
                distance_work = key2["distance"]["text"]
                duration_work = key2["duration"]["text"]

                # 距離の文字列から"km"を取り除いて数値に変換
                distance_work = float(distance_work.replace(" km", "").replace(",", ""))

                # 時間の文字列から"分"を取り除いて数値に変換
                duration_work = (
                    int(duration_work.replace("分", "")) + 5
                )  # 👈改善ポイント: ① 1時間を超えると"xx時間"と表示されるためエラーになる, ② 車の方が電車よりも時間が短くなるため、便宜的に一律5分上乗せ

                # スコアリング: 勤務地までの時間
                score_work = calculation_work(duration_work)

                # 必要なデータをリストに格納
                data_work.append([address, score_work, distance_work, duration_work])

    # データをDataFrameに変換
    df_work = pd.DataFrame(
        data_work, columns=["候補物件住所", "働きやすさスコア", "目的地までの距離(km)", "到着までにかかる時間(分)"]
    )

    
###############################################################################################################
### 暮らしやすさのスコアリング ###

    ## 設定・準備 ##

    # クライアントの生成
    gmaps = googlemaps.Client(key=api_key)

    # データを格納するためのリストを作成
    data_life = []


    # スコアリングの定義: スーパー数
    def calculation_life_supermarket_number(number_supermarket):
        if number_supermarket >= 3:
            return 100
        elif 2 <= number_supermarket < 3:
            return 75
        elif 1 <= number_supermarket < 2:
            return 50
        else:
            return 30


    # スコアリングの定義: スーパー所要時間
    def calculation_life_supermarket_duration(nearest_supermarket_duration):
        duration_int = int(nearest_supermarket_duration.replace("分", ""))

        if duration_int < 3:
            return 100
        elif duration_int < 16:
            return 100 - (duration_int - 2) * 5
        else:
            return 30


    # スコアリングの定義: 病院数
    def calculation_life_hospital_number(number_hospital):
        if number_hospital >= 5:
            return 100
        elif 4 <= number_hospital < 5:
            return 90
        elif 3 <= number_hospital < 4:
            return 80
        elif 2 <= number_hospital < 3:
            return 65
        elif 1 <= number_hospital < 2:
            return 50
        else:
            return 30


    # スコアリングの定義: 病院所要時間
    def calculation_life_hospital_duration(nearest_hospital_duration):
        duration_int = int(nearest_hospital_duration.replace("分", ""))

        if duration_int < 3:
            return 100
        elif duration_int < 16:
            return 100 - (duration_int - 2) * 5
        else:
            return 30


    # スコアリングの定義: 高評価飲食店数
    def calculation_life_restaurant_number(number_restaurant_highrated):
        if number_restaurant_highrated >= 10:
            return 100
        elif 7 <= number_restaurant_highrated < 10:
            return 90
        elif 5 <= number_restaurant_highrated < 7:
            return 80
        elif 4 <= number_restaurant_highrated < 5:
            return 70
        elif 3 <= number_restaurant_highrated < 4:
            return 60
        elif 2 <= number_restaurant_highrated < 3:
            return 50
        elif 1 <= number_restaurant_highrated < 2:
            return 40
        else:
            return 30


    # スコアリングの定義: 飲食店最高評価 (30点を底点として、Googleの飲食店スコア5点満点を (3点を引くことで) 2点満点に換算し、それを35倍することで70点分にスケーリング。最高評価が3.0以下の場合は0点 (/70点) とする)
    def calculation_life_restaurant_rating(rating_restaurant_highest):
        if restaurant_highestrated:
            if rating_restaurant_highest > 3:
                return 30 + (rating_restaurant_highest - 3) * 35
            else:
                return 30
        else:
            return 0


    ## スコアリング ##

    # 各住所に対して処理を繰り返す
    for address in addresses:
        # 住所から緯度経度を取得
        geocode_result = gmaps.geocode(address)
        location = geocode_result[0]["geometry"]["location"]

        ## スコアリング: スーパー ##

        # 施設名の指定
        place_name = "supermarket"

        # 検索範囲の指定
        radius = 800

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_supermarket = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_supermarket = distance_matrix_result["rows"][0]["elements"][0][
                "distance"
            ]["value"]

            # 検索範囲の場合にカウント
            if distance_supermarket <= radius:
                number_supermarket += 1

        # スコアリング: 施設数
        score_life_supermarket_number = calculation_life_supermarket_number(
            number_supermarket
        )

        # 最も近い施設までの所要時間を整数に変換してスコアリング
        nearest_supermarket_distance = float("inf")
        nearest_supermarket_duration = None
        nearest_supermarket_name = None

        for place in places_result["results"]:
            # 施設までの所要時間を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            duration_supermarket = distance_matrix_result["rows"][0]["elements"][0][
                "duration"
            ]["text"]

            # 最も近い施設を更新
            if "distance" in distance_matrix_result["rows"][0]["elements"][0]:
                distance_supermarket = distance_matrix_result["rows"][0]["elements"][0][
                    "distance"
                ]["value"]
                if distance_supermarket < nearest_supermarket_distance:
                    nearest_supermarket_distance = distance_supermarket
                    nearest_supermarket_duration = duration_supermarket
                    nearest_supermarket_name = place["name"]

        # スコアリング: 所要時間
        score_life_supermarket_duration = calculation_life_supermarket_duration(
            nearest_supermarket_duration
        )

        # スコアリング: 施設数＋所要時間
        score_life_supermarket = (
            score_life_supermarket_number + score_life_supermarket_duration
        ) / 2

        ## スコアリング: 病院 ##

        # 施設名の指定
        place_name = "病院"  # 👈改善ポイント: 英語の場合、「hospital」 → 「XX病院」、「clinic」 →　「XX病院」以外の「XXクリニック」しか検索できないため、暫定的に日本語で検索

        # 検索範囲の指定
        radius = 800

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_hospital = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_hospital = distance_matrix_result["rows"][0]["elements"][0][
                "distance"
            ]["value"]

            # 検索範囲の場合にカウント
            if distance_hospital <= radius:
                number_hospital += 1

        # スコアリング: 施設数
        score_life_hospital_number = calculation_life_hospital_number(number_hospital)

        # 最も近い施設までの所要時間を整数に変換してスコアリング
        nearest_hospital_distance = float("inf")
        nearest_hospital_duration = None
        nearest_hospital_name = None

        for place in places_result["results"]:
            # 施設までの所要時間を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            duration_hospital = distance_matrix_result["rows"][0]["elements"][0][
                "duration"
            ]["text"]

            # 最も近い施設を更新
            if "distance" in distance_matrix_result["rows"][0]["elements"][0]:
                distance_hospital = distance_matrix_result["rows"][0]["elements"][0][
                    "distance"
                ]["value"]
                if distance_hospital < nearest_hospital_distance:
                    nearest_hospital_distance = distance_hospital
                    nearest_hospital_duration = duration_hospital
                    nearest_hospital_name = place["name"]

        # スコアリング: 所要時間
        score_life_hospital_duration = calculation_life_hospital_duration(
            nearest_hospital_duration
        )

        # スコアリング: 施設数＋所要時間
        score_life_hospital = (
            score_life_hospital_number + score_life_hospital_duration
        ) / 2

        ## スコアリング: 飲食店 ##

        # 施設名はインプットした変数を引用

        # 検索範囲の指定
        radius = 800

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name_favorite, language="ja"
        )

        # 検索範囲の評価が3.5以上の飲食店数をカウントする変数
        number_restaurant_highrated = 0

        # 検索結果をループして検索範囲の高評価店数をカウント
        for place in places_result["results"]:
            # 施設までの所要時間(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance = distance_matrix_result["rows"][0]["elements"][0]["distance"]["value"]

            # 検索範囲の高評価店数をカウント
            if distance <= radius:
                rating_restaurant = place.get("rating", 0)
                if rating_restaurant >= 3.5:
                    number_restaurant_highrated += 1

        # スコアリング: 高評価店数
        score_life_restaurant_number = calculation_life_restaurant_number(
            number_restaurant_highrated
        )

        # 最も評価の高い飲食店の評価を特定
        rating_restaurant_highest = 0
        restaurant_highestrated = None

        for place in places_result["results"]:
            place_id = place["place_id"]

            # Place Details APIを使用して評価情報を取得
            details_result = gmaps.place(place_id)

            if "result" in details_result:
                rating_restaurant = details_result["result"].get("rating", 0)

                if rating_restaurant > rating_restaurant_highest:
                    rating_restaurant_highest = rating_restaurant
                    restaurant_highestrated = place["name"]

        # スコアリング: 最高評価
        score_life_restaurant_rating = calculation_life_restaurant_rating(
            rating_restaurant_highest
        )

        # スコアリング: 高評価店数＋最高評価
        score_life_restaurant = (
            score_life_restaurant_number + score_life_restaurant_rating
        ) / 2

        ## スコアリング: 暮らしやすさ ##

        # 重要度を乗じてスコアを算出
        score_life = (
            score_life_supermarket * weight_life_supermarket / 100
            + score_life_hospital * weight_life_hospital / 100
            + score_life_restaurant * weight_life_restaurant / 100
        )

        # 必要なデータをリストに格納
        data_life.append(
            [
                address,
                score_life,
                score_life_supermarket,
                score_life_hospital,
                score_life_restaurant,
                score_life_supermarket_number,
                score_life_supermarket_duration,
                number_supermarket,
                nearest_supermarket_name,
                nearest_supermarket_duration,
                score_life_hospital_number,
                score_life_hospital_duration,
                number_hospital,
                nearest_hospital_name,
                nearest_hospital_duration,
                score_life_restaurant_number,
                score_life_restaurant_rating,
                number_restaurant_highrated,
                restaurant_highestrated,
                rating_restaurant_highest,
            ]
        )

    # データをDataFrameに変換
    df_life = pd.DataFrame(
        data_life,
        columns=[
            "候補物件住所",
            "暮らしやすさスコア",
            "スーパースコア",
            "病院スコア",
            "飲食店スコア",
            "スーパー数スコア",
            "スーパー所要時間スコア",
            "エリア内のスーパー数",
            "最も近いスーパー名",
            "最も近いスーパーまでの所要時間(分)",
            "病院数スコア",
            "病院所要時間スコア",
            "エリア内の病院数",
            "最も近い病院名",
            "最も近い病院までの所要時間(分)",
            "飲食店数スコア",
            "飲食店評価スコア",
            "エリア内の飲食店数",
            "最も評価の高い飲食店名",
            "最も評価の高い飲食店における評価(星)",
        ],
    )

######################################################################################################################################################################################################
### 育てやすさのスコアリング ###

    ## 設定・準備 ##

    # クライアントの生成
    gmaps = googlemaps.Client(key=api_key)

    # データを格納するためのリストを作成
    data_kids = []


    # スコアリングの定義: 保育園数
    def calculation_kids_nursery_number(number_nursery):
        if number_nursery >= 5:
            return 100
        elif 4 <= number_nursery < 5:
            return 95
        elif 3 <= number_nursery < 4:
            return 85
        elif 2 <= number_nursery < 3:
            return 70
        elif 1 <= number_nursery < 2:
            return 50
        else:
            return 30


    # スコアリングの定義: 保育園所要時間
    def calculation_kids_nursery_duration(nearest_nursery_duration):
        duration_int = int(nearest_nursery_duration.replace("分", ""))

        if duration_int < 3:
            return 100
        elif duration_int < 16:
            return 100 - (duration_int - 2) * 5
        else:
            return 30


    # スコアリングの定義: 幼稚園数
    def calculation_kids_kindergarten_number(number_kindergarten):
        if number_kindergarten >= 5:
            return 100
        elif 4 <= number_kindergarten < 5:
            return 95
        elif 3 <= number_kindergarten < 4:
            return 85
        elif 2 <= number_kindergarten < 3:
            return 70
        elif 1 <= number_kindergarten < 2:
            return 50
        else:
            return 30


    # スコアリングの定義: 幼稚園所要時間
    def calculation_kids_kindergarten_duration(nearest_kindergarten_duration):
        duration_int = int(nearest_kindergarten_duration.replace("分", ""))

        if duration_int < 3:
            return 100
        elif duration_int < 16:
            return 100 - (duration_int - 2) * 5
        else:
            return 30


    # スコアリングの定義: 小学校所要時間
    def calculation_kids_elementary(nearest_elementary_duration):
        duration_int = int(nearest_elementary_duration.replace("分", ""))

        if duration_int < 3:
            return 100
        elif duration_int < 20:
            return 100 - (duration_int - 2) * 4
        else:
            return 30


    # スコアリングの定義: 公園数
    def calculation_kids_park(number_park):
        if number_park >= 4:
            return 100
        elif 3 <= number_park < 4:
            return 90
        elif 2 <= number_park < 3:
            return 75
        elif 1 <= number_park < 2:
            return 60
        else:
            return 30


    ## スコアリング ##

    # 各住所に対して処理を繰り返す
    for address in addresses:
        # 住所から緯度経度を取得
        geocode_result = gmaps.geocode(address)
        location = geocode_result[0]["geometry"]["location"]

        ## スコアリング: 保育園 ##

        # 施設名の指定
        place_name = "nursery"

        # 検索範囲の指定
        radius = 800

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_nursery = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_nursery = distance_matrix_result["rows"][0]["elements"][0]["distance"][
                "value"
            ]

            # 検索範囲の場合にカウント
            if distance_nursery <= radius:
                number_nursery += 1

        # スコアリング: 施設数
        score_kids_nursery_number = calculation_kids_nursery_number(number_nursery)

        # 最も近い施設までの所要時間を整数に変換してスコアリング
        nearest_nursery_distance = float("inf")
        nearest_nursery_duration = None
        nearest_nursery_name = None

        for place in places_result["results"]:
            # 施設までの所要時間を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            duration_nursery = distance_matrix_result["rows"][0]["elements"][0]["duration"][
                "text"
            ]

            # 最も近い施設を更新
            if "distance" in distance_matrix_result["rows"][0]["elements"][0]:
                distance_nursery = distance_matrix_result["rows"][0]["elements"][0][
                    "distance"
                ]["value"]
                if distance_nursery < nearest_nursery_distance:
                    nearest_nursery_distance = distance_nursery
                    nearest_nursery_duration = duration_nursery
                    nearest_nursery_name = place["name"]

        # スコアリング: 所要時間
        score_kids_nursery_duration = calculation_kids_nursery_duration(
            nearest_nursery_duration
        )

        # スコアリング: 施設数＋所要時間
        score_kids_nursery = (score_kids_nursery_number + score_kids_nursery_duration) / 2

        ## スコアリング: 幼稚園 ##

        # 施設名の指定
        place_name = "kindergarten"

        # 検索範囲の指定
        radius = 800

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_kindergarten = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_kindergarten = distance_matrix_result["rows"][0]["elements"][0][
                "distance"
            ]["value"]

            # 検索範囲の場合にカウント
            if distance_kindergarten <= radius:
                number_kindergarten += 1

        # スコアリング: 施設数
        score_kids_kindergarten_number = calculation_kids_kindergarten_number(
            number_kindergarten
        )

        # 最も近い施設までの所要時間を整数に変換してスコアリング
        nearest_kindergarten_distance = float("inf")
        nearest_kindergarten_duration = None
        nearest_kindergarten_name = None

        for place in places_result["results"]:
            # 施設までの所要時間を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            duration_kindergarten = distance_matrix_result["rows"][0]["elements"][0][
                "duration"
            ]["text"]

            # 最も近い施設を更新
            if "distance" in distance_matrix_result["rows"][0]["elements"][0]:
                distance_kindergarten = distance_matrix_result["rows"][0]["elements"][0][
                    "distance"
                ]["value"]
                if distance_kindergarten < nearest_kindergarten_distance:
                    nearest_kindergarten_distance = distance_kindergarten
                    nearest_kindergarten_duration = duration_kindergarten
                    nearest_kindergarten_name = place["name"]

        # スコアリング: 所要時間
        score_kids_kindergarten_duration = calculation_kids_kindergarten_duration(
            nearest_kindergarten_duration
        )

        # スコアリング: 施設数＋所要時間
        score_kids_kindergarten = (
            score_kids_kindergarten_number + score_kids_kindergarten_duration
        ) / 2

        ## スコアリング: 小学校 ##

        # 施設名の指定
        place_name = "elementary school"

        # 検索範囲の指定
        radius = 1600

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 最も近い施設までの所要時間を整数に変換してスコアリング
        nearest_elementary_distance = float("inf")
        nearest_elementary_duration = None
        nearest_elementary_name = None

        for place in places_result["results"]:
            # 施設までの所要時間を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            duration_elementary = distance_matrix_result["rows"][0]["elements"][0][
                "duration"
            ]["text"]

            # 最も近い施設を更新
            if "distance" in distance_matrix_result["rows"][0]["elements"][0]:
                distance_elementary = distance_matrix_result["rows"][0]["elements"][0][
                    "distance"
                ]["value"]
                if distance_elementary < nearest_elementary_distance:
                    nearest_elementary_distance = distance_elementary
                    nearest_elementary_duration = duration_elementary
                    nearest_elementary_name = place["name"]

        # スコアリング: 所要時間
        score_kids_elementary = calculation_kids_elementary(nearest_elementary_duration)

        ## スコアリング: 公園 ##

        # 施設名の指定
        place_name = "park"

        # 検索範囲の指定
        radius = 600

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_park = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_park = distance_matrix_result["rows"][0]["elements"][0]["distance"][
                "value"
            ]

            # 検索範囲の場合にカウント
            if distance_park <= radius:
                number_park += 1

        # スコアリング: 施設数
        score_kids_park = calculation_kids_park(number_park)

        ## スコアリング: 育てやすさ ##

        # 重要度を乗じてスコアを算出
        score_kids = (
            score_kids_nursery * weight_kids_nursery / 100
            + score_kids_kindergarten * weight_kids_kindergarten / 100
            + score_kids_elementary * weight_kids_elementary / 100
            + score_kids_park * weight_kids_park / 100
        )

        # 必要なデータをリストに格納
        data_kids.append(
            [
                address,
                score_kids,
                score_kids_nursery,
                score_kids_kindergarten,
                score_kids_elementary,
                score_kids_park,
                score_kids_nursery_number,
                score_kids_nursery_duration,
                number_nursery,
                nearest_nursery_name,
                nearest_nursery_duration,
                score_kids_kindergarten_number,
                score_kids_kindergarten_duration,
                number_kindergarten,
                nearest_kindergarten_name,
                nearest_kindergarten_duration,
                nearest_elementary_name,
                nearest_elementary_duration,
                number_park,
            ]
        )

    # データをDataFrameに変換
    df_kids = pd.DataFrame(
        data_kids,
        columns=[
            "候補物件住所",
            "育てやすさスコア",
            "保育園スコア",
            "幼稚園スコア",
            "小学校スコア",
            "公園スコア",
            "保育園数スコア",
            "保育園所要時間スコア",
            "エリア内の保育園数",
            "最も近い保育園名",
            "最も近い保育園までの所要時間(分)",
            "幼稚園数スコア",
            "幼稚園所要時間スコア",
            "エリア内の幼稚園数",
            "最も近い幼稚園名",
            "最も近い幼稚園までの所要時間(分)",
            "最も近い小学校名",
            "最も近い小学校までの所要時間(分)",
            "エリア内の公園数",
        ],
    )  

######################################################################################################   
### 安心しやすさのスコアリング ###

    ## 設定・準備 ##

    # クライアントの生成
    gmaps = googlemaps.Client(key=api_key)

    # データを格納するためのリストを作成
    data_safe = []


    # スコアリングの定義:
    def calculation_safe(score_safe_fire, score_safe_police):
        if score_safe_fire == 1 and score_safe_police == 1:
            return 100
        elif score_safe_fire == 1 and score_safe_police == 2:
            return 85
        elif score_safe_fire == 1 and score_safe_police == 3:
            return 70
        elif score_safe_fire == 2 and score_safe_police == 1:
            return 85
        elif score_safe_fire == 2 and score_safe_police == 2:
            return 70
        elif score_safe_fire == 2 and score_safe_police == 3:
            return 55
        elif score_safe_fire == 3 and score_safe_police == 1:
            return 70
        elif score_safe_fire == 3 and score_safe_police == 2:
            return 55
        elif score_safe_fire == 3 and score_safe_police == 3:
            return 40
        else:
            return 30


    ## スコアリング ##

    # 各住所に対して処理を繰り返す
    for address in addresses:
        # 住所から緯度経度を取得
        geocode_result = gmaps.geocode(address)
        location = geocode_result[0]["geometry"]["location"]

        # スコアリング: 消防署

        # 施設名の指定
        place_name = "消防署"  # 👈備考: 英語の場合、「fire department」 → ヒット数少ない、「fire」 →　料理店が含まれやすい、という事情から日本語で検索

        # 検索範囲の指定
        radius = 600

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_fire_near = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_fire = distance_matrix_result["rows"][0]["elements"][0]["distance"][
                "value"
            ]

            # 検索範囲の場合にカウント
            if distance_fire <= radius:
                number_fire_near += 1

        # 検索範囲の指定
        radius = 1200

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_fire_far = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_fire = distance_matrix_result["rows"][0]["elements"][0]["distance"][
                "value"
            ]

            # 検索範囲の場合にカウント
            if distance_fire <= radius:
                number_fire_far += 1

        # スコアリング: 消防署
        if number_fire_near >= 1:
            score_safe_fire = 1
        elif number_fire_far >= 1:
            score_safe_fire = 2
        else:
            score_safe_fire = 3

        # スコアリング: 交番

        # 施設名の指定
        place_name = "警察署"  # 👈備考: 英語「police」 → 交番が含まれないケースがあるため、日本語で検索。「交番」 →　警察署が含まれない、「警察署」 → 交番が含まれる、という包含関係から「警察署」で検索

        # 検索範囲の指定
        radius = 500

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_police_near = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_police = distance_matrix_result["rows"][0]["elements"][0]["distance"][
                "value"
            ]

            # 検索範囲の場合にカウント
            if distance_police <= radius:
                number_police_near += 1

        # 検索範囲の指定
        radius = 1000

        # 検索結果を取得
        places_result = gmaps.places_nearby(
            location=location, radius=radius, keyword=place_name, language="ja"
        )

        # 検索範囲の施設数を格納する変数を作成
        number_police_far = 0

        # 検索結果をループして検索範囲の施設数をカウント
        for place in places_result["results"]:
            # 施設までの距離(徒歩)を取得
            distance_matrix_result = gmaps.distance_matrix(
                location,
                place["geometry"]["location"],
                mode="walking",
                language="ja",
                units="metric",
            )
            distance_police = distance_matrix_result["rows"][0]["elements"][0]["distance"][
                "value"
            ]

            # 検索範囲の場合にカウント
            if distance_police <= radius:
                number_police_far += 1

        # スコアリング: 交番
        if number_police_near >= 1:
            score_safe_police = 1
        elif number_police_far >= 1:
            score_safe_police = 2
        else:
            score_safe_police = 3

        # スコアリング: 施設数＋所要時間
        score_safe = calculation_safe(score_safe_fire, score_safe_police)

        # 必要なデータをリストに格納
        data_safe.append([address, score_safe, score_safe_fire, score_safe_police])

    # データをDataFrameに変換
    df_safe = pd.DataFrame(
        data_safe, columns=["候補物件住所", "安心しやすさスコア", "消防署スコア_3段階", "交番スコア_3段階"]
    )

#########################################################################################################
## 設定・準備 ##


    # 総合スコアに対する表示コメントの定義
    def generate_comment(score_total):
        if score_total >= 90:
            return "運命の出会いとなる物件です！！チャンスを逃さないようすぐに契約に進みましょう！！"
        elif score_total >= 80:
            return "あなたにあった物件です！これ以上魅力的な物件はそうそう見つからないでしょう！"
        elif score_total >= 70:
            return "バランスのよい物件です！スコアが低い部分が問題ないか確認することをお勧めします。"
        elif score_total >= 60:
            return "良い物件かもしれません。ただ大きな弱点がありますので、よく確認しましょう。"
        elif score_total >= 50:
            return "間取りや築年数だけで選んでいませんか？詳細を見て具体的に生活をイメージしてみましょう。"
        else:
            return "Suumoではもっとよい物件があなたを待っています！オススメ物件を参考に再トライしましょう！"


    # データフレームを '候補物件住所' 列をキーに横方向に結合
    df_total = (
        df_work.merge(df_life, on="候補物件住所", how="inner")
        .merge(df_kids, on="候補物件住所", how="inner")
        .merge(df_safe, on="候補物件住所", how="inner")
    )

    # '総合スコア' 列を算出しデータフレームに追加
    df_total["総合スコア"] = (
        df_total["働きやすさスコア"] * weight_work / 100
        + df_total["暮らしやすさスコア"] * weight_life / 100
        + df_total["育てやすさスコア"] * weight_kids / 100
        + df_total["安心しやすさスコア"] * weight_safe / 100
    )

    # '評価コメント' 列を追加
    df_total["評価コメント"] = df_total["総合スコア"].apply(generate_comment)

    # 総合スコアを左から2番目、評価コメントを左から3番目に持ってくる
    column_order = list(df_total.columns)
    column_order.insert(1, column_order.pop(column_order.index("総合スコア")))
    column_order.insert(2, column_order.pop(column_order.index("評価コメント")))
    df_total = df_total[column_order]
    df_total["総合スコア"] = df_total["総合スコア"].round(1).astype(int)
    df_total["暮らしやすさスコア"] = df_total["暮らしやすさスコア"].round(1).astype(int)
    df_total["育てやすさスコア"] = df_total["育てやすさスコア"].round(1).astype(int)
    df_total["安心しやすさスコア"] = df_total["安心しやすさスコア"].round(1).astype(int)


##########################################################################################################

    #OUTPUTトップ画像
    image = Image.open('image/OUTPUT_TOP.png')
    st.image(image, use_column_width=True)
    
    # 建物名表示部分
    col1, col2, col3, col4 = st.columns(4)

    # col1 に空欄を挿入
    with col1:
        st.write("")

    # col2, col3, col4 に建物名を表示
    for i, property_name in enumerate(property_names):
        with col2 if i == 0 else col3 if i == 1 else col4:
            st.write(f'<p style="text-align: center;">{property_name}</p>', unsafe_allow_html=True)
    
    #建物画像表示部分ーーーーー＞＞＞＞＞＞＞＞＞＞＞＞＞要取得*2、3、4カラム使用
    col1, col2, col3, col4 = st.columns(4)  
    # 画像のパス
    image_paths = [
        'image/OUTPUT_property1.png',
        'image/OUTPUT_property2.png',
        'image/OUTPUT_property3.png'
    ]

    # col1 に空欄を挿入
    with col1:
        st.write("")

    # col2, col3, col4 に画像を中央揃えで挿入
    for i, image_path in enumerate(image_paths):
        with col2 if i == 0 else col3 if i == 1 else col4:
            st.image(image_path, use_column_width=True)
    
    
    #建物住所表示部分
    col1, col2, col3, col4 = st.columns(4)
    # col1 は空欄
    with col1:
        st.write("")
    # col2, col3, col4 に住所を表示
    for i, address in enumerate(addresses):
        with col2 if i == 0 else col3 if i == 1 else col4:
            st.write(f'<p style="text-align: center;">物件住所: {address}</p>', unsafe_allow_html=True)
   ##############################################################################################################
    #トータルスコア表示部分
    col1, col2, col3, col4 = st.columns(4)
    
    #Fontsize指定
    font_size = 70 
    
    #TotalScore画像サイズ変更処理
    image2_path = 'image/OUTPUT_TotalScore.png'
    
    def image_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # TotalScore画像を半分に縮小する関数
    def resize_image(image, factor=0.5):
        width, height = image.size
        new_width = int(width * factor)
        new_height = int(height * factor)
        return image.resize((new_width, new_height))
    
    image2 = Image.open(image2_path)
    resized_image2 = resize_image(image2, factor=1.3)
    
    # col1にTotalScore挿入
    # 画像をMarkdown形式で表示し、スタイルを指定して中央揃え
    col1.markdown(f'<p style="text-align: center;"><img src="data:image/png;base64,{image_to_base64(resized_image2)}" alt="Image"></p>', unsafe_allow_html=True)

    # col2, col3, col4 に総スコアを中央揃えで表示
    for i, score in enumerate(df_total["総合スコア"]):
        with col2 if i == 0 else col3 if i == 1 else col4:
            st.write(f'<p style="text-align: center; font-size:{font_size}px;"> {score}</p>', unsafe_allow_html=True)
            
###################################################################################################
    #コメント表示部分
    col1, col2, col3, col4 = st.columns(4)
        # 空欄を表示するためのcol1
    col1.write("")
    
    #Fontsize指定
    font_size = 24
    
    # 各行のスコアに対応するコメントを選択
    for i, score in enumerate(df_total["評価コメント"]):
        with col2 if i == 0 else col3 if i == 1 else col4:
            st.write(f'<p style="text-align: center; font-size:{font_size}px;"> {score}</p>', unsafe_allow_html=True)

###################################################################################################
#詳細スコア展開(働きやすさスコア)

    with st.expander('働きやすさスコアの詳細を見る'):
        columns = st.columns(4)
        for i, (work_score, duration_work) in enumerate(zip(df_total["働きやすさスコア"], df_total["到着までにかかる時間(分)"])):
            with columns[i + 1]:
                # Markdownを使用してフォントサイズを変更
                st.markdown(f"<p style='font-size: 30px;'>働きやすさスコア: {work_score}</p>", unsafe_allow_html=True)
                st.write(f"到着までにかかる時間(分): {duration_work}")

###################################################################################################
#詳細スコア展開(生活スコア)
    with st.expander('暮らしやすさスコアの詳細を見る'):
        columns = st.columns(4)
        for i, (score_life, number_supermarket, nearest_supermarket_duration, number_hospital, nearest_hospital_duration, number_restaurant_highrated, restaurant_highestrated, rating_restaurant_highest) in enumerate(zip(df_total["暮らしやすさスコア"], df_total["エリア内のスーパー数"],df_total["最も近いスーパーまでの所要時間(分)"], df_total["エリア内の病院数"], df_total["最も近い病院までの所要時間(分)"], df_total["エリア内の飲食店数"], df_total["最も評価の高い飲食店名"], df_total["最も評価の高い飲食店における評価(星)"])):
            with columns[i + 1]:
                # Markdownを使用してフォントサイズを変更
                st.markdown(f"<p style='font-size: 30px;'>暮らしやすさスコア: {score_life}</p>", unsafe_allow_html=True)
                st.write(f"エリア内のスーパー数: {number_supermarket}")
                st.write(f"最も近いスーパーまでの所要時間(分): {nearest_supermarket_duration}")
                st.write(f"エリア内の病院数: {number_hospital}")
                st.write(f"最も近い病院までの所要時間(分): {nearest_hospital_duration}")
                st.write(f"エリア内の飲食店数: {number_restaurant_highrated}")
                st.write(f"最も評価の高い飲食店名: {restaurant_highestrated}")
                st.write(f"最も評価の高い飲食店における評価(星): {rating_restaurant_highest}")

###################################################################################################
#詳細スコア展開(育てやすさスコア)
    with st.expander('育てやすさスコアの詳細を見る'):
        columns = st.columns(4)
        for i, (score_kids, number_nursery, nearest_nursery_name, nearest_nursery_duration, number_kindergarten, nearest_kindergarten_name, nearest_kindergarten_duration, nearest_elementary_name, nearest_elementary_duration, number_park) in enumerate(zip(df_total["育てやすさスコア"], df_total["エリア内の保育園数"], df_total["最も近い保育園名"], df_total["最も近い保育園までの所要時間(分)"], df_total["エリア内の幼稚園数"], df_total["最も近い幼稚園名"], df_total["最も近い幼稚園までの所要時間(分)"], df_total["最も近い小学校名"], df_total["最も近い小学校までの所要時間(分)"], df_total["エリア内の公園数"])):
            with columns[i + 1]:
                # Markdownを使用してフォントサイズを変更
                st.markdown(f"<p style='font-size: 30px;'>育てやすさスコア: {score_life}</p>", unsafe_allow_html=True)
                st.write(f"エリア内の保育園数: {number_nursery}")
                st.write(f"最も近い保育園名: {nearest_nursery_name}")
                st.write(f"最も近い保育園までの所要時間（分）: {nearest_nursery_duration}")
                st.write(f"エリア内の幼稚園数: {number_kindergarten}")
                st.write(f"最も近い幼稚園名: {nearest_kindergarten_name}")
                st.write(f"最も近い幼稚園までの所要時間(分): {nearest_kindergarten_duration}")
                st.write(f"最も近い小学校名: {nearest_elementary_name}")
                st.write(f"最も近い小学校までの所要時間(分): {nearest_elementary_duration}")            
                st.write(f"エリア内の公園数: {number_park}")
            
            
            
###################################################################################################
#詳細スコア展開(安心しやすさスコア)
    with st.expander('安心しやすさスコアの詳細を見る'):
        columns = st.columns(4)
        for i, score_safe in enumerate(df_total["安心しやすさスコア"]):
            with columns[i + 1]:
                # Markdownを使用してフォントサイズを変更
                st.markdown(f"<p style='font-size: 30px;'>安心しやすさスコア: {score_safe}</p>", unsafe_allow_html=True)

                
################################################################################################################### 
    #ライン挿入
    image = Image.open('image/OUTPUT_line.png')
    st.image(image, use_column_width=True)
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    col1.markdown('<p style="text-align: center; font-size: 20px;">おすすめ物件</p>', unsafe_allow_html=True)
    
    # TotalScore画像を半分に縮小する関数
    def resize_image(image, factor=0.5):
        width, height = image.size
        new_width = int(width * factor)
        new_height = int(height * factor)
        return image.resize((new_width, new_height))

    import base64
    from PIL import Image
    from io import BytesIO

    def image_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


    # 各画像のパス
    image1_path = 'image/OUTPUT_recommendsample.png'
    image2_path = 'image/OUTPUT_TotalScore.png'
    image4_path = 'image/OUTPUT_RecommendWorking.png'
    image5_path = 'image/OUTPUT_RecommendLiving.png'
    image6_path = 'image/OUTPUT_RecommendKids.png'
    image7_path = 'image/OUTPUT_RecommendSafety.png'

    # 画像読み込み
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    image4 = Image.open(image4_path)
    image5 = Image.open(image5_path)
    image6 = Image.open(image6_path)
    image7 = Image.open(image7_path)

    # 画像を半分に縮小
    resized_image2 = resize_image(image2, factor=1.3)

    # 1行目の列
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    # 画像を表示
    col1.image(image1, use_column_width=True)
    # 画像を中央に配置
    # 画像をMarkdown形式で表示し、スタイルを指定して中央揃え
    col2.markdown(f'<p style="text-align: center;"><img src="data:image/png;base64,{image_to_base64(resized_image2)}" alt="Image"></p>', unsafe_allow_html=True)


    
    font_size = 50 
    
    # 画像とテキストを同じ列に配置------------------------------------------>>>>>数字仮置き
    col4.image(image4, use_column_width=True)
    col4.markdown(f'<div style="text-align:center;"><span style="font-size:{font_size}px;"> {st.session_state.input_data["weight_work"]}</span></div>', unsafe_allow_html=True)

    col5.image(image5, use_column_width=True)
    col5.markdown(f'<div style="text-align:center;"><span style="font-size:{font_size}px;"> {st.session_state.input_data["weight_life"]}</span></div>', unsafe_allow_html=True)

    col6.image(image6, use_column_width=True)
    col6.markdown(f'<div style="text-align:center;"><span style="font-size:{font_size}px;"> {st.session_state.input_data["weight_kids"]}</span></div>', unsafe_allow_html=True)

    col7.image(image7, use_column_width=True)
    col7.markdown(f'<div style="text-align:center;"><span style="font-size:{font_size}px;"> {st.session_state.input_data["weight_safe"]}</span></div>', unsafe_allow_html=True)


    
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # col1の中で "おすすめ物件" をセンター表示
    col1.markdown('<p style="text-align: center; font-size: 20px;">https://suumo.jp/chintai/jnc_000065032568/?bc=100345163904</p>', unsafe_allow_html=True)

##############################################################################################################

    #空白行の追加
    st.markdown('#')
    st.markdown('#')
 
    #mail送付部分
    # 3つのカラムを作成
    col1, col2, col3 = st.columns(3)

    # ボタン1を2列目に配置（中央揃え）
    with col2:
        st.markdown("""
            <style>
                div.stButton > button {
                    display: block;
                    margin: 0 auto;
                    font-size: 10em;
                    }
            </style>
        """, unsafe_allow_html=True)

        mail_expander = st.expander("Send your email", expanded=False)
        with mail_expander:
            mail_sender = st.text_input(
                '検索結果と引越時に役立つ情報をメールアドレスに送付します。',
                value='',  # 初期値を空の文字列に設定
                key='mail_sender_input',
                help='メールアドレスを入力する'
            )

            
    #空白行の追加
    st.markdown('#')
    st.markdown('#')

    
    ###############更新されないように調整用😃
    # Once again! ボタンが押下されたかどうかの状態を初期化
    if st.button("Once again!"):
        # Reset session state variables
        st.session_state.page2 = False
        st.session_state.button_clicked = False

        # Redirect to Page 1
        st.experimental_rerun()

    #空白行の追加
    st.markdown('#')
    st.markdown('#')
    
    
    #バナー指定
    image = Image.open('image/OUTPUT_banner.png')
    st.image(image, use_column_width=True)