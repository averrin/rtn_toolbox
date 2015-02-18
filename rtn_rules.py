prefixes = [
    # '[ZLMC]',
    # '[ZFWK]',
#     '[ZADV]',
    # '[ZDCT]',
#     '[ZADT]'
    ]

color_pref = [
    {"color": "white", "attrs": [], "check": lambda p, t, l: p in prefixes},
    # {"color": "green", "attrs": [], "check": lambda p, t, l: p == "[ZDCT]"},
#     {"color": "green", "attrs": [], "check": lambda p, t, l: p == "[ZADT]"},
#     {"color": "red", "attrs": [], "check": lambda p, t, l: t == "[E]"},
    # {"color": "blue", "attrs": ["bold"], "check": lambda p, t, l: l.startswith("[dc")}
    {"color": "green", "attrs": [], "check": lambda p, t, l: l.startswith("[dc")},
    {"color": "blue", "attrs": ["bold"], "check": lambda p, t, l: l.startswith("[EventAggregator] [channel_tunes]")},
    {"color": "yellow", "attrs": [], "check": lambda p, t, l: "[!]" in l},
    {"color": "white", "attrs": ["bold"], "check": lambda p, t, l: "[shell]" in l},
]