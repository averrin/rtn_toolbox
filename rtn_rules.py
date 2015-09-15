prefixes = [
    # '[ZLMC]',
    # '[ZFWK]',
#     '[ZADV]',
    # '[ZDCT]',
#     '[ZADT]'
    ]

rules = {
    "important": {"color": "yellow", "attrs": [], "check": lambda p, t, l: "[!]" in l},
    "rtnui": {"color": "white", "attrs": [], "check": lambda p, t, l: "RTNUI" in l},
    "prefixes": {"color": "white", "attrs": [], "check": lambda p, t, l: p in prefixes},
    "zdct": {"color": "green", "attrs": [], "check": lambda p, t, l: p == "[ZDCT]"},
    "zadt": {"color": "green", "attrs": [], "check": lambda p, t, l: p == "[ZADT]"},
    "dc": {"color": "green", "attrs": [], "check": lambda p, t, l: l.startswith("[dc")},
    "tunes": {"color": "blue", "attrs": ["bold"], "check": lambda p, t, l: l.startswith("[EventAggregator] [channel_tunes]")},
    "inject": {"color": "white", "attrs": ["bold"], "check": lambda p, t, l: "[shell]" in l},
    "zinject": {"color": "white", "attrs": ["bold"], "check": lambda p, t, l: "[zshell]" in l},
    "zfwk": {"color": "white", "attrs": [], "check": lambda p, t, l: p == '[ZFWK]'},
    "errors": {"color": "red", "attrs": [], "check": lambda p, t, l: "[E]" in l}
}

active_rules = [
    'tunes', 'inject', 'zinject', 'dc', 'important'
]
