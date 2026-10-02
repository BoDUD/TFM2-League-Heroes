#!/usr/bin/env python3
"""LeBlanc's stray squares (the user: "乐芙兰有多余的像素没清理干净啊 看起来还有很多不干净的地方", pointing at the hem).

A library for tools/art/fix_leblanc_strips.py (every frame, last) and tools/art/design_leblanc.py (the design).
1. The design's hem, by hand (HEM, in the idle frame's squares): cutting Codex's 75-row drawing to 43 rows took about
   every other row of the skirt, so its bottom came apart - the crimson panel's last square hung under the hem in its
   own outline, the near shoe was a gold strap over a navy bar with the outline between them, the gown's gold trim
   broke off at the knee and dark squares were left alone in the red. Every frame that holds the design's lower body
   (found square for square: the idle, the first and last frames of the attack, Q, E and R) gets the same squares.
   Shown A (this) and B (this and the skirt's lone specks merged into the colours round them), the user picked A.
2. The run (RUN_NUB): one outline square stood up off the staircase of the cape's top edge in all eight frames (they
   share frame 3's upper body).
Codex's other frames were checked square by square for outline bumps, crumbs and squares hanging off the edge: what a
rule finds there are the heel tips and toes of the shoes (drawn in the outline colour) and the claws of the staff's
bat wings - drawn on purpose, left alone (a first rule that cleared them cut the shoes in W).
"""
OUTLINE = (0x06, 0x02, 0x12)
LEG = {"#": OUTLINE, "a": (0x1C, 0x19, 0x48), "b": (0xF4, 0xAA, 0x45), "e": (0x7F, 0x00, 0x15),
       "c": (0xAA, 0x01, 0x1B)}
BODY = (33, 52, 57, 68)         # the design's lower body in the idle frame (x0, y0, x1, y1): what frames are searched for
# (x, y, letter or None for clear), the idle frame's squares
HEM = [
    (48, 66, "#"), (48, 67, None), (50, 66, "#"),    # the crimson panel's last square: the hem's outline runs straight
    (40, 65, "a"), (41, 65, "#"),                    # the near shoe: navy under its gold strap, outlined
    (43, 64, "#"),                                   # the dent in the outline between the near leg and the crimson panel
    (47, 60, "b"), (48, 61, "b"),                    # the gown's gold trim, knee to hem, joined
    (39, 64, "e"),                                   # a crimson square alone in the dark-red lining over the shoe
    (49, 59, "c"), (54, 60, "e"),                    # dark squares alone in the red
]
RUN_NUB = (28, 56)              # in the run's frame 3 (the upper body every run frame wears)


def find_body(f, ref):
    """(dx, dy, share): where the design's lower body (ref: the idle frame as Codex delivered it) sits in the frame."""
    x0, y0, x1, y1 = BODY
    tpl = ref[y0:y1, x0:x1]
    m = tpl[..., 3] > 0
    th, tw = m.shape
    best = (0, 0, 0.0)
    for y in range(f.shape[0] - th + 1):
        for x in range(f.shape[1] - tw + 1):
            s = ((f[y:y + th, x:x + tw] == tpl).all(-1) & m).sum() / m.sum()
            if s > best[2]:
                best = (x - x0, y - y0, s)
    return best


def hem(f, dx, dy):
    g = f.copy()
    for x, y, ch in HEM:
        if ch is None:
            g[y + dy, x + dx] = 0
        else:
            g[y + dy, x + dx, :3] = LEG[ch]
            g[y + dy, x + dx, 3] = 255
    return g


def clean(f, ref):
    """Part 1 where the design's lower body is: (frame, what was done)."""
    dx, dy, share = find_body(f, ref)
    if share < 1:
        return f, []
    return hem(f, dx, dy), [f"hem at {dx:+d},{dy:+d}"]


def run_nub(body):
    """Part 2 on the run's shared upper body (frame 3's)."""
    x, y = RUN_NUB
    assert tuple(int(v) for v in body[y, x, :3]) == OUTLINE and body[y, x, 3], "the run's nub moved"
    g = body.copy()
    g[y, x] = 0
    return g
