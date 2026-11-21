"""Register one straight blue trident to the authored closed-hand sockets."""
import math

import numpy as np
from PIL import Image


LENGTH = 79
THICKNESS = 21
MIDLINE = THICKNESS // 2
SIZE = 128


def template(image):
    box = image.getbbox()
    crop = image.crop(box)
    assert crop.width > crop.height * 4
    # Measure the centre of the long undecorated shaft, apart from the fin
    # guard and butt. Remove any small source slope before downsampling.
    mask = np.asarray(crop)[:, :, 3] > 0
    columns = np.arange(round(crop.width * .22), round(crop.width * .68))
    axis = np.array([np.median(np.where(mask[:, x])[0]) for x in columns])
    assert np.isfinite(axis).all()
    incline = np.polyfit(columns, axis, 1)[0]
    if abs(incline) > .001:
        crop = crop.rotate(math.degrees(math.atan(incline)), Image.Resampling.NEAREST, expand=True)
        crop = crop.crop(crop.getbbox())
    height = round(crop.height / crop.width * LENGTH)
    assert 4 < height < THICKNESS
    shaft = crop.resize((LENGTH, height), Image.Resampling.NEAREST)
    prop = Image.new("RGBA", (LENGTH, THICKNESS))
    prop.paste(shaft, (0, (THICKNESS - height) // 2))
    ink = np.asarray(prop)[:, :, 3] > 0
    shaft_columns = ink[:, 18:54]
    assert shaft_columns.any(axis=0).all(), "A straight trident shaft must span its length"
    centres = [float(np.median(np.where(shaft_columns[:, x])[0])) for x in range(shaft_columns.shape[1])]
    assert max(centres) - min(centres) <= 1.0, centres
    return prop, float(np.median(centres))


def transform(prop, socket_y, x, y, angle, socket_x):
    """Rotate and translate in one inverse sample, about the hand's grip."""
    radians = math.radians(angle)
    c, s = math.cos(radians), math.sin(radians)
    image = prop.transform((SIZE, SIZE), Image.Transform.AFFINE,
                           (c, s, socket_x - c * x - s * y,
                            -s, c, socket_y + s * x - c * y),
                           Image.Resampling.NEAREST)
    # Test the forward mapping of every visible source pixel too, since
    # bounds from an already cropped image cannot prove there was no cut.
    ys, xs = np.where(np.asarray(prop)[:, :, 3] > 0)
    px = x + c * (xs - socket_x) - s * (ys - socket_y)
    py = y + s * (xs - socket_x) + c * (ys - socket_y)
    assert px.min() >= 1 and px.max() <= SIZE - 2, (x, y, angle, px.min(), px.max())
    assert py.min() >= 1 and py.max() <= SIZE - 2, (x, y, angle, py.min(), py.max())
    tip_length = LENGTH - 1 - socket_x
    tip = [round(x + c * tip_length), round(y + s * tip_length)]
    return image, tip


def attach(body, prop, axis, pose):
    x, y, angle, socket_x, held = pose
    spear, tip = transform(prop, axis, x, y, angle, socket_x)
    if not held:
        return Image.alpha_composite(spear, body), tip
    # Place the shaft over the sleeve and recover the exposed knuckles at
    # the hand socket. Bare fingers occlude the centre of the rigid shaft.
    actor = np.asarray(body)
    gy, gx = np.ogrid[:SIZE, :SIZE]
    grip = (np.abs(gx - x) <= 2) & (np.abs(gy - y) <= 2)
    if not np.any(actor[y-1:y+2, x-1:x+2, 3] == 255):
        raise ValueError(f"Grip at {(x, y)} is detached from actor")
    color = actor[:, :, :3].astype(np.int16)
    skin = (color[:, :, 0] >= 119) & (color[:, :, 0] - color[:, :, 2] > 9)
    occlusion = grip & skin & (actor[:, :, 3] > 0)
    if not occlusion.any():
        raise ValueError(f"No visible hand pixels near grip at {(x, y)}")
    combined = np.array(Image.alpha_composite(body, spear))
    combined[occlusion] = actor[occlusion]
    return Image.fromarray(combined), tip
