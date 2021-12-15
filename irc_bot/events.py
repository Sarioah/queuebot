from tools.colours import colourise as col
class handle_event():
    def __init__(self, *a):
        events = {"action"    : 0,
                  "pubnotice" : 0,
                  "privnotice": 0,
                  "usernotice": 0,
                  "whisper"   : 0}
    def __call__(self, *a):
        try: action = getattr(self, "on_" + a[1])
        except AttributeError: return
        res = action(**a[0])
        return res

    def on_action(self, msg, words, tags): return col(f"{tags['display-name']}: {msg}", "CYAN")
    def on_pubnotice(self, msg, words, tags): return col(msg, "GREY")
    def on_privnotice(self, msg, words, tags): return col(msg, "GREY")
    def on_usernotice(self, msg, words, tags):
        res = col(tags['system-msg'], "GREY" ) if 'system-msg' in tags else ''
        if res: return res + f" - {msg or '<no msg>'}"
    def on_whisper(self, msg, words, tags): return col(f"Whisper from {tags['display-name']}: {msg}", "GREY")
