from bs4 import BeautifulSoup
import requests
import json

from linebot import LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,PostbackEvent,QuickReply, QuickReplyButton,URITemplateAction
    )
from linebot.models.actions import (PostbackAction)


google_api_key = open("secrets/google_api_key.txt").read().strip()
nearbysearch_api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/"
geocode_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
google_map_url = "https://www.google.com/maps/search/?api=1"


message_count = 0

def restaurant_recomend(chatcat,event):
    
    global message_count
    
    if event.type == "postback":
        if event.postback.data == "restaurant": 
            selected_restaurant(chatcat,event)
        
        elif event.postback.data == "help":
            selected_help(chatcat,event)
        
        elif event.postback.data == "now_location":
            selected_now_location(chatcat,event)
        
        elif event.postback.data == "select_location":
            selected_select_location(chatcat,event)
            message_count = 1
    
    if event.type == "message":
        if message_count == 1:
            reply = messaged_place_name(chatcat,event)
            chatcat.talk(reply)
            



def selected_restaurant(chatcat,event):
    columns_list = []
    columns_list.append(
    CarouselColumn(
        #thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
        title="検索位置の指定",
        text="指定された場所周辺の飲食店を検索します",
        actions=[
                    PostbackAction(label="現在地から検索", data="now_location"),
                    PostbackAction(label="場所を指定して検索", data="select_location")]))
    chatcat.add_carousel("検索の返信",columns_list)

def selected_help(chatcat,event):
    text = "helpメッセージ"
    chatcat.talk(text)
    
def selected_now_location(chatcat,event):
    pass

def selected_select_location(chatcat,event):
    text = "位置を指定して下さい"
    chatcat.talk(text)
    
 
def messaged_place_name(chatbot,event):
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
    # 取得した位置情報を1kmいないの店を探すメソッドに渡す。
    reply = find_restaurant(latitude,longitude,"待ち合わせ場所")
    return reply


#緯度、経度から指定された場所の半径1km以内の店舗を探す
def find_restaurant(latitude, longitude, keyword)->str:
    count  = 0
    global nearbysearch_api_url, google_api_key
    # 半径1km県内の店を取得します
    places_parameter = f"json?keyword={keyword}&types=food?language=ja&location={latitude},{longitude}&radius=1000&key={google_api_key}"
    places_api = nearbysearch_api_url + places_parameter

    response = requests.get(places_api)
    soup = BeautifulSoup(response.content)
    data = json.loads(soup.text)
    reply = ""
    for result in data["results"]:
        name = result["name"].replace(" ","+")
        location = result["vicinity"].replace(" ","+")
        reply += google_map_url+f"&query={name}+{location}\n"
        count += 1
        if count == 3:
            break
    return reply