from bs4 import BeautifulSoup
import requests
import json
import urllib.parse

from linebot import LineBotApi
from linebot.models import (
    MessageEvent,URIAction,ButtonsTemplate,TemplateSendMessage, LocationSendMessage,ButtonsTemplate,MessageTemplateAction,TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,PostbackEvent,QuickReply, QuickReplyButton,URITemplateAction
    )
from linebot.models.actions import (PostbackAction,LocationAction,MessageAction)

line_bot_api = LineBotApi(open("secrets/line_channel_access_token.txt").read().strip())
google_api_key = open("secrets/google_api_key.txt").read().strip()
nearbysearch_api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/"
geocode_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
google_map_url = "https://www.google.com/maps/search/?api=1"
url_first = "https://www.google.com/maps/place/?q=place_id:"
url_last = "?g_st=il"

def restaurant_recomend(chatcat,event):
    # 保存している変数を取り出す
    try:
        columns_list,message_count = chatcat.data["restaurant_data"]
        search_results = chatcat.data["search_results"]
    except:
        columns_list,message_count,search_results = [],0,[]

    if event.type == "postback":
        if event.postback.data == "restaurant":
            selected_restaurant(chatcat,event)

        elif event.postback.data == "help":
            selected_help(chatcat,event)
            chatcat.mode = "normal"

        elif event.postback.data == "word_search":
            chatcat.talk("検索したい場所を入力してください。")


    elif event.message.type == "text":
        messaged_place_name(chatcat,event,search_results)
        chatcat.mode = "normal"

    elif event.message.type == "location":
        find_restaurant(chatcat,event.message.latitude, event.message.longitude, "飲食店",search_results)
        chatcat.mode = "normal"

    chatcat.data["restaurant_data"] = columns_list,message_count



def selected_restaurant(chatcat,event):
    items = [
        QuickReplyButton(action=PostbackAction(label="文字で検索",data="word_search")),
        QuickReplyButton(action=LocationAction(label="位置で検索。"))
    ]

    chatcat.add_quick_reply("検索方法を指定",items)

def selected_help(chatcat,event):
    text = "helpメッセージ"
    chatcat.talk(text)

def messaged_place_name(chatcat,event,search_results):
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
    find_restaurant(chatcat,latitude,longitude,"飲食店",search_results)


#緯度、経度から指定された場所の半径1km以内の店舗を探す
def find_restaurant(chatcat,latitude, longitude, keyword,search_results):
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
        place_id = result["place_id"]
        url = f"{url_first}{place_id}"

        if clean_up(chatcat,name,url,data,count,columns_list):
            search_results.append(result)
            count += 1
        if count == 10:
            break
    chatcat.data["search_results"] = search_results
    chatcat.add_carousel("店舗表示",columns_list)

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
        actions=[URIAction( label=f'{name}',uri = f'{url}',)])
    )
    return "OK"
