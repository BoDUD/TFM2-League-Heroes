"""Lissandra's hand-drawn design palette: one character per colour (design_lz.py grids)."""
PAL = {
    "K": "0B0A14",                                              # outline
    "1": "0F1028", "2": "1B1F42", "3": "2C3566", "4": "4A5A9C", "5": "8098D8",   # navy crown / bodice / gown
    "a": "34509C", "b": "5A7ED0", "c": "A6C4F4",                # ice-crystal hem
    "s": "6C8CC0", "t": "9CB8E4", "u": "CFE0F8",                # skin
    "g": "3FA8E8", "h": "7AD8FF", "j": "C8F4FF",                # glowing forearms / hands
    "x": "1E78D0", "y": "40B4FF", "z": "A8ECFF", "w": "F2FCFF", # crystals, crescent, glints
    "p": "6FA0C8", "q": "A8D4EE", "r": "E2F4FF",                # braid
    "m": "1A1830", "n": "2E2C50",                               # hood-locks
    "L": "24305E",                                              # lips
}
RGB = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in PAL.items()}
