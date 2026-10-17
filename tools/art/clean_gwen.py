"""import_native TIDY step for Gwen: the scissors' heart holes. design_gwen2 marks them #ff00ff (opaque through the
rig and the import's outline pass, which would outline a clear hole shut); here, after that pass, the marker turns
transparent so the ground shows through the loops in every frame."""
import numpy as np

HOLE = (255, 0, 255)


def tidy(tag, k, a):
    m = (a[..., 3] > 0) & (a[..., :3] == HOLE).all(-1)
    a[m] = 0
    return a
