from utils.myGPT import generate_text
def chat(chatcat,event):
    if event.type != "message":
        return
    chatcat.talk(generate_text(event.message.text))