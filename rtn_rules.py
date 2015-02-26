prefixes = [
    # '[ZLMC]',
    # '[ZFWK]',
#     '[ZADV]',
    # '[ZDCT]',
#     '[ZADT]'
    ]

color_pref = [
    {"color": "white", "attrs": [], "check": lambda p, t, l: p in prefixes, "name": "prefixes"},
    # {"color": "green", "attrs": [], "check": lambda p, t, l: p == "[ZDCT]", "name": ""},
#     {"color": "green", "attrs": [], "check": lambda p, t, l: p == "[ZADT]", "name": ""},
    {"color": "green", "attrs": [], "check": lambda p, t, l: l.startswith("[dc"), "name": "dc"},
    {"color": "blue", "attrs": ["bold"], "check": lambda p, t, l: l.startswith("[EventAggregator] [channel_tunes]"), "name": "tunes"},
    {"color": "yellow", "attrs": [], "check": lambda p, t, l: "[!]" in l, "name": "important"},
    {"color": "white", "attrs": ["bold"], "check": lambda p, t, l: "[shell]" in l, "name": "inject"},
]