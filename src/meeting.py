def meeting_recomend(chatcat,event):
    meeting_start_message = "待ち合わせにゃね！いつ、どこで会うにゃ？"
    if_null_message = "入力ができてないにゃ！"
    
    tmp_user_message = event.message.text
    user_message = tmp_user_message.split('、')

    try:
        flag_meeting_start, flag_flow_select_place, flag_flow_time = chatcat.data["meeting_flag"]
        user_want_message_no1,user_want_message_no2 = chatcat.deta["meeting_deta"]
    except:
        flag_meeting_start, flag_flow_select_place, flag_flow_time = True, False, False

    
    if user_message[0] != None:
        user_want_message_no1 = user_message[0]
        if user_message[1] != None:
            user_want_message_no2 = user_message[1]
    else:
        chatcat.talk(if_null_message)
        chatcat.talk(meeting_start_message)

    if flag_flow_select_place == True and flag_flow_time == True:
        if type(user_want_message_no1) == str:
            flag_flow_time == False
        else:
            flag_flow_select_place == False

    if flag_meeting_start == True:
        flag_meeting_start = False
        flag_flow_select_place = True
        flag_flow_time = True
        chatcat.talk(meeting_start_message)

    chatcat.data["restaurant_data"] = [flag_meeting_start, flag_flow_select_place, flag_flow_time]
    chatcat.deta["meeting_deta"] =[user_want_message_no1,user_want_message_no2]