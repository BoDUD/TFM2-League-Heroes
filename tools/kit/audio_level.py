"""Shared peak limiter for the Workshop audio builds."""

import numpy as np


def limiter(x, ceiling, block=256, width=9):
    """Limit channel peaks together and smooth the gain across neighbouring blocks."""
    n = -(-len(x) // block)
    pad = np.zeros((n * block, x.shape[1]))
    pad[: len(x)] = x
    peak = np.abs(pad).reshape(n, block, -1).max((1, 2))
    g = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    gp = np.pad(g, width // 2, mode="edge")
    g = np.lib.stride_tricks.sliding_window_view(gp, width).min(1)
    gp = np.pad(g, width // 2 - 1, mode="edge")
    g = np.lib.stride_tricks.sliding_window_view(gp, width - 2).mean(1)
    centres = np.arange(n) * block + block / 2
    # Each interpolated gain is bounded by the peaks of its block and both neighbours.
    gs = np.interp(np.arange(n * block), centres, g)
    return (pad * gs[:, None])[: len(x)]
