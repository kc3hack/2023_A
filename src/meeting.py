import re
import datetime
import schedule
from time import sleep

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,CarouselTemplate,CarouselColumn,
    PostbackEvent,DatetimePickerAction,
    QuickReply, QuickReplyButton
)
from linebot.models.actions import PostbackAction

def meeting_timer_check_day(year,month,day):
    flag_next_timer = False
    tmp_now = str.strip(datetime.datetime.now())
    now = re.split('-:',tmp_now)
    now_year = now[0]
    now_month = now[1]
    now_day = now[2]
    if now_year == year:
        if now_month == month:
            if now_day == day:
                flag_next_timer = True
    return flag_next_timer

def send_meeting_time_checker(hour,minute):
    flag_meeting_time = False
    tmp_now = str.strip(datetime.datetime.now())
    now = re.split('-:',tmp_now)
    now_hour = now[3]
    now_minute = now[4]
    if now_hour == hour and now_minute == minute:
        flag_meeting_time = True
    return flag_meeting_time

def meeting_recomend(chatcat,event):

    start_message = "待ち合わせにゃね！どこで待ち合わせするにゃ？"
    user_want_time_question = "いつ待ち合わせするにゃ？"
    timer_message = "その時になったら連絡ほしいにゃ？"
    goodlack_message = "わかったにゃ！楽しんできてにゃ！"


    try:
        flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time,flag_flow_timer,flag_loop = chatcat.data["meeting_flag"]
        recommend_place_no1,recommend_place_no2,recommend_place_no3,decide_place,decide_time = chatcat.data["meeting_data"]
        year,month,day,hour,minute = chatcat.data["meeting_time"]
    except:
        flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time,flag_flow_timer,flag_loop = True, False, False, False, False, False
        recommend_place_no1,recommend_place_no2,recommend_place_no3,decide_place,decide_time = "Init","Init","Init","Init","Init"
        year,month,day,hour,minute = 0,0,0,0,0

    if flag_flow_timer == True:
        flag_flow_timer = False
        before_meeting_time_message = f"あと１時間で{decide_place}で待ち合わせにゃ！急ぐにゃ！！"
        timer_set_message = f"{decide_place}での待ち合わせの１時間前にお知らせするにゃ！任せろにゃ！！"
        year = str(year)
        month = str(month)
        day = str(day)
        hour = str(hour)
        minute = str(minute)
        if event.postback.data == "use_timer":
            flag_loop = True
            schedule.every().days.at("00:00").do(meeting_timer_check_day)
            if meeting_timer_check_day(year,month,day) == True:
                schedule.every().day.at(f"{hour}:{minute}").do(send_meeting_time_checker)
                chatcat.talk(timer_set_message)
            else:
                chatcat.talk(timer_set_message)
                while flag_loop == True:
                    schedule.run_pending()
                    if meeting_timer_check_day(year,month,day) == True:
                        flag_loop = False
                        schedule.every().day.at(f"{hour}:{minute}").do(send_meeting_time_checker)
                        break
                    sleep(10)
            if send_meeting_time_checker(hour,minute) == True:
                chatcat.talk(before_meeting_time_message)
        elif event.postback.data == "no_use_timer":
            chatcat.talk(goodlack_message)

    if flag_flow_decide_time == True:
        tmp_time = re.split('[-T:]',event.postback.params["datetime"])
        year = int(tmp_time[0])
        month = int(tmp_time[1])
        day = int(tmp_time[2])
        hour = int(tmp_time[3])
        minute = int(tmp_time[4])
        flag_flow_decide_time = False
        flag_flow_timer = True
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


    if flag_flow_decide_place == True:
        if event.postback.data == "place_no1":
            decide_place = recommend_place_no1
        elif event.postback.data == "place_no2":
            decide_place = recommend_place_no2
        elif event.postback.data == "place_no3":
            decide_place = recommend_place_no3
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
                        PostbackAction(label="決定", data="place_no2")
                    ]
                )
            )
            columns_list.append(
                CarouselColumn(
                    thumbnail_image_url="https://cdn.projectdesign.jp/uploads/201601/images/gazou/24_1.jpg",
                    title=recommend_place_no3,
                    text="お城があるとこです",
                    actions=[
                        PostbackAction(label="決定", data="place_no3")
                    ]
                )
            )
            select_message = f"{event.message.text}で待ち合わせするなら、ここがおすすめにゃ！"
            chatcat.talk(select_message)
            chatcat.add_carousel("おすすめ一覧",columns_list)
            
    if flag_meeting_start == True:
        flag_meeting_start = False
        flag_flow_select_place = True
        chatcat.talk(start_message)

    chatcat.data["meeting_flag"] = [flag_meeting_start,flag_flow_select_place,flag_flow_decide_place,flag_flow_decide_time,flag_flow_timer,flag_loop]
    chatcat.data["meeting_data"] = [recommend_place_no1,recommend_place_no2,recommend_place_no3,decide_place,decide_time]
    chatcat.data["meeting_time"] = year,month,day,hour,minute