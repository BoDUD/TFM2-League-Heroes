"""Register one straight blue trident to the authored closed-hand sockets."""
import math

import numpy as np
from PIL import Image


LENGTH = 79
THICKNESS = 21
SIZE = 128
EDGE = (151, 189, 221, 255)
CORE = (64, 97, 158, 255)
SHADOW = (17, 26, 57, 255)


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
    axis = int(math.floor(float(np.median(centres)) + .5))
    # Keep the painted fin and prongs. Carry the three-row profile through
    # both joins so the butt and front collar read as parts of the same rod.
    pixels = np.array(prop)
    pixels[axis - 1:axis + 2, 9:58] = np.array([EDGE, CORE, SHADOW])[:, None]
    pixels[axis + 1, 5:9] = SHADOW
    pixels[axis - 1:axis + 2, 58:60] = np.array([
        (221, 195, 110, 255), (155, 114, 50, 255), (54, 42, 21, 255),
    ])[:, None]
    pixels[axis + 1, 61] = SHADOW
    return Image.fromarray(pixels), axis


def transform(prop, socket_y, x, y, angle, socket_x):
    """Rotate and translate in one inverse sample, about the hand's grip."""
    radians = math.radians(angle)
    c, s = math.cos(radians), math.sin(radians)
    # Pillow samples pixel centres. Pivot about the centres of the authored
    # socket and hand pixels, including when the rod is turned steeply.
    hx, hy = x + .5, y + .5
    image = prop.transform(
        (SIZE, SIZE), Image.Transform.AFFINE,
        (c, s, socket_x + .5 - c * hx - s * hy,
         -s, c, socket_y + .5 + s * hx - c * hy),
        Image.Resampling.NEAREST,
    )
    # Test the forward mapping of every visible source pixel too, since
    # bounds from an already cropped image cannot prove there was no cut.
    ys, xs = np.where(np.asarray(prop)[:, :, 3] > 0)
    px = x + c * (xs - socket_x) - s * (ys - socket_y)
    py = y + s * (xs - socket_x) + c * (ys - socket_y)
    assert px.min() >= 1 and px.max() <= SIZE - 2, (x, y, angle, px.min(), px.max())
    assert py.min() >= 1 and py.max() <= SIZE - 2, (x, y, angle, py.min(), py.max())
    left, _, right, _ = prop.getbbox()
    pixels = np.array(image)
    # A one-pixel terminal can fall between nearest-neighbour samples.
    # Place the butt and tip explicitly on their projected axis points.
    tail_distance = left - socket_x
    tail = [round(x + c * tail_distance), round(y + s * tail_distance)]
    tip_distance = right - 1 - socket_x
    tip = [round(x + c * tip_distance), round(y + s * tip_distance)]
    pixels[tail[1], tail[0]] = prop.getpixel((left, socket_y))
    pixels[tip[1], tip[0]] = prop.getpixel((right - 1, socket_y))
    return Image.fromarray(pixels), tip


def attach(body, prop, axis, pose):
    x, y, angle, socket_x, held = pose
    spear, tip = transform(prop, axis, x, y, angle, socket_x)
    if not held:
        return Image.alpha_composite(spear, body), tip
    # Let the fingers wrap in front of the shaft at the exact hand socket.
    # A visible section on each side makes the grip readable at native size.
    actor = np.asarray(body)
    gy, gx = np.ogrid[:SIZE, :SIZE]
    dx, dy = gx - x, gy - y
    grip = (np.abs(dx) <= 2) & (np.abs(dy) <= 2)
    if not np.any(actor[y-1:y+2, x-1:x+2, 3] == 255):
        raise ValueError(f"Grip at {(x, y)} is detached from actor")
    color = actor[:, :, :3].astype(np.int16)
    skin = (color[:, :, 0] >= 119) & (color[:, :, 0] - color[:, :, 2] > 9)
    weapon_pixels = np.asarray(spear)
    weapon_mask = weapon_pixels[:, :, 3] > 0
    occlusion = grip & skin & (actor[:, :, 3] > 0) & weapon_mask
    if np.count_nonzero(occlusion) < 3:
        raise ValueError(f"Trident must pass under the knuckles at {(x, y)}")
    angle = math.radians(angle)
    along = math.cos(angle) * dx + math.sin(angle) * dy
    steel_edge = np.all(weapon_pixels == EDGE, axis=2) & ~occlusion
    for direction in (-1, 1):
        side = along * direction
        assert np.any(steel_edge & (side >= 2) & (side <= 8)), (pose, direction)
    combined = np.array(Image.alpha_composite(body, spear))
    combined[occlusion] = actor[occlusion]
    return Image.fromarray(combined), tip
