from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,DatetimePickerAction,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction
def meeting_recomend(chatcat,event):

    start_message = "待ち合わせにゃね！どこで待ち合わせするにゃ？"
    user_want_time_question = "いつ待ち合わせするにゃ？"

    try:
        flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time = chatcat.data["meeting_flag"]
        recommend_place_no1,recommend_place_no2,recommend_place_no3,decide_place,decide_time = chatcat.data["meeting_data"]
    except:
        flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time = True, False, False, False
        recommend_place_no1,recommend_place_no2,recommend_place_no3,decide_place,decide_time = "Init","Init","Init","Init","Init"

    if flag_flow_decide_place == True:
        if event.postback.params["data"] == "place_no1":
            decide_place = recommend_place_no1
        elif event.postback.params["data"] == "place_no2":
            decide_place = recommend_place_no2
        elif event.postback.params["data"] == "place_no3":
            decide_place = recommend_place_no3
        flag_flow_decide_place = False
        flag_flow_decide_time = True
        columns_list = []
        columns_list.append(
            CarouselColumn(
                thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                title=recommend_place_no1,
                text="USJがあるところです",
                actions=[
                    DatetimePickerAction(data="user_want_time")
                ]
            )
        )
        place_dicide_message = f"{decide_place}で待ち合わせにゃね。"
        chatcat.talk(place_dicide_message + user_want_time_question)

    if flag_flow_select_place == True:
        recommend_place_no1 = "osaka"
        recommend_place_no2 = "kyoto"
        recommend_place_no3 = "kobe"
        flag_flow_select_place = False
        if recommend_place_no1 == "Init" and recommend_place_no1 == "Init" and recommend_place_no1 == "Init":
            flag_meeting_start = True
        else:
            flag_flow_decide_place = True
            #カルーセル内容
            columns_list = []
            columns_list.append(
                CarouselColumn(
                    thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                    title=recommend_place_no1,
                    text="USJがあるところです",
                    actions=[
                        PostbackAction(label="決定", data="place_no1")
                    ]
                )
            )
            columns_list.append(
                CarouselColumn(
                    thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                    title=recommend_place_no2,
                    text="お寺があるとこです",
                    actions=[
                        PostbackAction(label="検索", data="place_no2")
                    ]
                )
            )
            columns_list.append(
                CarouselColumn(
                    thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                    title=recommend_place_no3,
                    text="お城があるとこです",
                    actions=[
                        PostbackAction(label="検索", data="place_no3")
                    ]
                )
            )
            select_message = f"{event.message.text}で待ち合わせするにゃら、ここがおすすめにゃ！"
            chatcat.talk(select_message)
            chatcat.add_carousel("おすすめ一覧",columns_list)
            
    if flag_meeting_start == True:
        flag_meeting_start = False
        flag_flow_select_place = True
        chatcat.talk(start_message)

    chatcat.data["meeting_flag"] = [flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time]
    chatcat.data["meeting_data"] = [recommend_place_no1,recommend_place_no2,recommend_place_no3,decide_place,decide_time]