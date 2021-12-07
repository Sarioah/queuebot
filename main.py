import random, time
from configparser import ConfigParser
from irc_bot import irc_bot
from queue import Queue, trunc

config = ConfigParser()
config.read(".config")
config = config["DEFAULT"]

q = Queue(config["channel"])
q.open()

def test(*a):
    import test
    for i in test.data: q.addsong(*i)
    return "Bot loaded with test queue"

commands = {"testqueue": test,
            "sr": q.addsong,
            "leave": q.leave,
            "openqueue": q.open,
            "closequeue": q.close,
            "removesong": q.removesong,
            "removeuser": q.removeuser,
            "listqueue": q.listsongs,
            "listusers": q.listusers,
            "currentsong": q.currentsong,
            "queue": q.status,
            "picked": q.played,
            "pick": q.picksong}

def message_handler(msg):
    chat_msg = msg.arguments[0]
    chat_command = chat_msg.split(" ", 1)
    chat_tags = {i["key"]: i["value"] for i in msg.tags}

    global q, commands
    print("*****\n%s: %s\n******\n" % (chat_tags["display-name"], chat_msg))
    for k in chat_tags: print("%s: %s" % (k, chat_tags[k]))
    try:
        if chat_msg[:1] == config["bot_prefix"]:
            cmd = commands[chat_command[0][1:]]
            user = chat_tags["display-name"]
            try: args = chat_command[1]
            except IndexError: args = ""
            res = cmd(user, args)
            return trunc(res, 450)
    except KeyError: pass

bot = irc_bot(config["bot_nick"], config["tmi_token"], config["channel"], message_handler)
bot.start_bot()

while not bot.joined:
    bot.poll()

print("Bot is ready for commands")


while True:
    #msg = input("> ")
    #boit.send_msg(msg)
    try:
        bot.poll()
    except Exception as e:
        import traceback
        print("oh no....anyway")
        traceback.print_exc()
    time.sleep(1)
