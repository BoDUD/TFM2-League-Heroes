"""Stray black: 8-connected pieces of dark pixels none of which touches an opaque non-dark pixel (a line or dot left
alone on the clear); and body pixels changed."""
import numpy as np
import wings as WG
def strays(c):
    h, w = c.shape[:2]
    op = c[..., 3] > 0
    K = np.zeros((h, w), bool); C = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            if op[y, x]:
                if WG.dark(c[y, x]): K[y, x] = True
                else: C[y, x] = True
    seen = np.zeros((h, w), bool); out = []
    for y0, x0 in zip(*np.nonzero(K)):
        if seen[y0, x0]: continue
        comp, stack, touch = [], [(y0, x0)], False; seen[y0, x0] = True
        while stack:
            y, x = stack.pop(); comp.append((x, y))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q, p = y + dy, x + dx
                    if (dy or dx) and 0 <= q < h and 0 <= p < w:
                        if C[q, p]: touch = True
                        if K[q, p] and not seen[q, p]: seen[q, p] = True; stack.append((q, p))
        if not touch: out.append(comp)
    return out
def body_changed(old, new):
    h, w = old.shape[:2]
    return [(x, y) for y in range(h) for x in range(w) if old[y, x, 3] > 0 and not WG.warm(old[y, x]) and not WG.dark(old[y, x]) and not np.array_equal(old[y, x], new[y, x])]
