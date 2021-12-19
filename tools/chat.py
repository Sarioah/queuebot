from tools.colours import colourise as col

def format_badges(tags):
    badges = tags['badges']
    res = ''
    roles = [("RED",    ("broadcaster",),          "B"),
             ("GREEN",  ("moderator",),            "M"),
             ("BLUE",   ("subscriber", "premium"), "S"),
             ("PURPLE", ("vip",),                  "V")]

    for role in roles:
        res += col(role[2], role[0]) if role_check(badges, *role[1]) else ''
    return res

def role_check(badges, *roles):
    roles = roles or ("moderator", "broadcaster")
    try: return any([role in badge for badge in badges.split(",")
                                   for role in roles])
    except AttributeError: return False
