import re
import datetime
import schedule
from time import sleep
from bs4 import BeautifulSoup
import requests
import json
import urllib.parse

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,URIAction,DatetimePickerAction,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction

line_bot_api = LineBotApi(open("secrets/line_channel_access_token.txt").read().strip())
google_api_key = open("secrets/google_api_key.txt").read().strip()
nearbysearch_api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/"
geocode_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
google_map_url = "https://www.google.com/maps/search/?api=1"
url_first = "https://www.google.com/maps/place/?q=place_id:"
url_last = "?g_st=il"

start_message = "待ち合わせにゃね！どこで待ち合わせするにゃ？"
user_want_time_question = "いつ待ち合わせするにゃ？"
timer_message = "その時になったら連絡ほしいにゃ？"
goodlack_message = "わかったにゃ！楽しんできてにゃ！"
error_message = "認識できなかったにゃ．．．ごめんにゃ．．もう一度やり直してほしいにゃ．．．"

#その日を確認する
def meeting_timer_check_day(year,month,day):
    flag_next_timer = False
    now = datetime.datetime.now()
    now_year = str(now.year)
    now_month = str(now.month)
    now_day = str(now.day)
    if now_year == year:
        if now_month == month:
            if now_day == day:
                flag_next_timer = True
    return flag_next_timer

#時間を確認する
def send_meeting_time_checker(hour,minute):
    flag_meeting_time = False
    now = datetime.datetime.now()
    now_hour = str(now.hour)
    now_minute = str(now.minute)
    if now_hour == hour and now_minute == minute:
        flag_meeting_time = True
    return flag_meeting_time

def meeting_recomend(chatcat,event):
    try:
        flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time,flag_flow_timer,flag_loop = chatcat.data["meeting_flag"]
        recommend_place,decide_place,decide_time = chatcat.data["meeting_data"]
        year,month,day,hour,minute = chatcat.data["meeting_time"]
        search_results = chatcat.data["search_results"]
    except:
        flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time,flag_flow_timer,flag_loop = True, False, False, False, False, False
        recommend_place,decide_place,decide_time = [],"Init","Init"
        year,month,day,hour,minute = 0,0,0,0,0
        search_results = []

    #タイマー
    if flag_flow_timer == True:
        flag_flow_timer = False
        before_meeting_time_message = f"あと１時間で{decide_place}で待ち合わせにゃ！急ぐにゃ！！"
        timer_set_message = f"{decide_place}での待ち合わせの１時間前にお知らせするにゃ！任せろにゃ！！"
        year = str(year)
        month = str(month)
        day = str(day)
        hour = str(hour)
        minute = str(minute)
        #使用するとき
        if event.postback.data == "use_timer":
            flag_loop = True
            schedule.every().days.at("00:00").do(meeting_timer_check_day)
            #当日にタイマーセット
            if meeting_timer_check_day(year,month,day) == True:
                schedule.every().day.at(f"{hour}:{minute}").do(send_meeting_time_checker)
                chatcat.talk(timer_set_message)
                chatcat.mode = "normal"
            #それ以外
            else:
                chatcat.talk(timer_set_message)
                while flag_loop == True:
                    schedule.run_pending()
                    if meeting_timer_check_day(year,month,day) == True:
                        flag_loop = False
                        schedule.every().day.at(f"{hour}:{minute}").do(send_meeting_time_checker)
                        break
                    sleep(10)
            #時間が来たらメッセージを送る
            if send_meeting_time_checker(hour,minute) == True:
                chatcat.talk(before_meeting_time_message)
                chatcat.mode = "normal"
        #使わないとき
        elif event.postback.data == "no_use_timer":
            chatcat.talk(goodlack_message)
            chatcat.mode = "normal"

    #時間決める
    if flag_flow_decide_time == True:
        tmp_time = re.split('[-T:]',event.postback.params["datetime"])
        year = int(tmp_time[0])
        month = int(tmp_time[1])
        day = int(tmp_time[2])
        hour = int(tmp_time[3])
        minute = int(tmp_time[4])
        flag_flow_decide_time = False
        flag_flow_timer = True
        #時間調（ex　2000年1月1日00：00待ち合わせ→1999年12月31日23：00にタイマー）
        if hour == 0:
            day = day - 1
        if day < 0:
            month = month - 1
            if month == 2:
                if (year / 4) == 0:
                    day = 28
                else:
                    day = 27
            elif month == 4 or month == 6 or month == 9 or  month == 11:
                day = 30
            else:
                day = 31
        if month < 0:
            year = year - 1
        decide_time = f"{tmp_time[0]}年{tmp_time[1]}月{tmp_time[2]}日 {tmp_time[3]}：{tmp_time[4]}"
        columns_list = []
        columns_list.append(
            CarouselColumn(
                title="時間になったらメッセージを送るにゃ？",
                text="「送る」を選択すると待ち合わせ時間の１時間前にメッセージを送ります",
                actions=[
                    PostbackAction(label="送る", data="use_timer"),
                    PostbackAction(label="送らない", data="no_use_timer")
                ]
            )
        )
        decide_message = f"{decide_time}に{decide_place}で待ち合わせにゃね！"
        chatcat.talk(decide_message + timer_message)
        chatcat.add_carousel("タイマー",columns_list)

    #場所選択
    if flag_flow_decide_place == True:
        if event.postback.data == 0:
            decide_place = recommend_place[0]
        elif event.postback.data == 1:
            decide_place = recommend_place[1]
        elif event.postback.data == 2:
            decide_place = recommend_place[2]
        flag_flow_decide_place = False
        flag_flow_decide_time = True
        columns_list = []
        columns_list.append(
            CarouselColumn(
                thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                title="待ち合わせ時間",
                text=f"{decide_place}で待ち合わせする時間を選択してください",
                actions=[
                    DatetimePickerAction(label = "待ち合わせ時間",mode = "datetime",data = "user_want_time")
                ]
            )
        )
        place_dicide_message = f"{decide_place}で待ち合わせにゃね。"
        chatcat.talk(place_dicide_message + user_want_time_question)
        chatcat.add_carousel("時間指定",columns_list)

    #場所決め
    if flag_flow_select_place == True:
        select_message = f"{event.message.text}で待ち合わせするなら、ここがおすすめにゃ！"
        chatcat.talk(select_message)
        messaged_place_name(chatcat,event,search_results,recommend_place)
        recommend_place[0] = ""
        recommend_place[1] = "kyoto"
        recommend_place[2] = "kobe"
        flag_flow_select_place = False
        if recommend_place[0] == "Init" and recommend_place[1] == "Init" and recommend_place[2] == "Init":
            flag_meeting_start = True
            chatcat.talk(error_message)
        else:
            flag_flow_decide_place = True
            #カルーセル内容
            # columns_list = []
            # columns_list.append(
            #     CarouselColumn(
            #         thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
            #         title=recommend_place_no1,
            #         text="USJがあるところです",
            #         actions=[
            #             PostbackAction(label="決定", data="place_no1")
            #         ]
            #     )
            # )
            # columns_list.append(
            #     CarouselColumn(
            #         thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
            #         title=recommend_place_no2,
            #         text="お寺があるとこです",
            #         actions=[
            #             PostbackAction(label="決定", data="place_no2")
            #         ]
            #     )
            # )
            # columns_list.append(
            #     CarouselColumn(
            #         thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
            #         title=recommend_place_no3,
            #         text="お城があるとこです",
            #         actions=[
            #             PostbackAction(label="決定", data="place_no3")
            #         ]
            #     )
            # )
    #起動メッセージ
    if flag_meeting_start == True:
        flag_meeting_start = False
        flag_flow_select_place = True
        chatcat.talk(start_message)

    chatcat.data["meeting_flag"] = [flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time,flag_flow_timer,flag_loop]
    chatcat.data["meeting_data"] = [recommend_place,decide_place,decide_time]
    chatcat.data["meeting_time"] = [year,month,day,hour,minute]
    chatcat.data["search_results"] = search_results

def messaged_place_name(chatcat,event,search_results,recommend_place):
    global nearbysearch_api_url,geocode_api_url, google_api_key

    params = {
        "address": f"{event.message.text}",  # 検索対象の住所
        "language": "ja",  # レスポンスの言語
        "key": f"{google_api_key}"  # APIキー
    }

    # リクエストを送信する
    response = requests.get(geocode_api_url, params=params)

    # レスポンスのJSONデータを取得する
    data = response.json()

    # 緯度経度を取得する
    location = data["results"][0]["geometry"]["location"]
    latitude = location["lat"]
    longitude = location["lng"]
    
    # 取得した位置情報をfind_restaurant()に渡す。
    find_meeting_place(chatcat,latitude,longitude,"待ち合わせ 広場",search_results,recommend_place)


#緯度、経度から指定された場所の半径1km以内の店舗を探す
def find_meeting_place(chatcat,latitude, longitude, keyword,search_results,recommend_place):
    global nearbysearch_api_url, google_api_key

    # 半径1km県内の店を取得します
    places_parameter = f"json?keyword={keyword}&types=food?language=ja&location={latitude},{longitude}&radius=1000&key={google_api_key}"
    places_api = nearbysearch_api_url + places_parameter

    response = requests.get(places_api)
    soup = BeautifulSoup(response.content)
    data = json.loads(soup.text)

    columns_list = []
    search_results = []
    count  = 0
    for result in data["results"]:
        name = result["name"]
        recommend_place.append(result["name"])
        place_id = result["place_id"]
        url = f"{url_first}{place_id}"

        if clean_up(chatcat,name,url,data,count,columns_list):
            search_results.append(result)
            count += 1
        if count == 3:
            break
    chatcat.data["search_results"] = search_results
    chatcat.add_carousel("おすすめ一覧",columns_list)

#URLの変更、写真の取得
def clean_up(chatcat,name,url,data,i,columns_list):
    #nameが20文字以上なら一つ目の空白以降を切り捨てる
    if len(name) > 20:
        name = name[:name.find(' ', 20)]
        if len(name) > 20:
            name = name[:20]

    if data['status'] == 'ZERO_RESULTS':
        # 結果が見つからない場合の処理
        return None
    elif data['status'] == 'OK':
        try:
            # 結果が見つかった場合の処理
            # 写真のリファレンスを取得
            photo_reference = data['results'][i]['photos'][0]['photo_reference']
            # 写真のURLを生成
            photo_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={google_api_key}'
        except:
            return None

    columns_list.append(CarouselColumn(
        thumbnail_image_url=f'{photo_url}',
        title=f'{name}',
        text=f'お店の説明',
        actions=[URIAction( label=f'{name}',uri = f'{url}',),
                 PostbackAction(label="決定",data=i)])
    )
    return "OK"
