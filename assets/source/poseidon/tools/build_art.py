"""Build Poseidon's native and exact 4× presentation assets from reviewed art."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import trident


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "art"
DIST = ROOT / "runtime"
QA = ROOT / "qa"
HERO = "ragnarok_poseidon"
CELL = 128
FOOT = 116
HD = 4
STANDING = 58
TIMES = {
    "idle": [140] * 8,
    "run": [76, 72, 68, 72, 76, 72, 68, 72],
    "attack": [95, 75, 55, 50, 60, 70, 75, 105],
    "skill": [95, 75, 55, 55, 65, 70, 80, 100],
    "skill2": [100, 80, 55, 50, 60, 70, 85, 110],
    "ult": [150, 130, 100, 50, 60, 75, 90, 125],
    "hit": [65, 55, 65, 70, 75, 80, 85, 100],
    "dead": [85, 115, 130, 145, 145, 165, 220, 620],
}
ACTORS = {
    "idle": ("idle", 2, 0, ()), "run": ("run", 2, 0, ()),
    "attack": ("fight", 4, 0, (0, 1, 6, 7)), "hit": ("fight", 4, 8, (0, 1, 6, 7)),
    "skill": ("power", 4, 0, (0, 1, 6, 7)), "skill2": ("power", 4, 8, (0, 1, 6, 7)),
    "ult": ("finish", 4, 0, (0, 1, 6, 7)), "dead": ("finish", 4, 8, (0, 1)),
}
FX = {
    "fxa": (("thrust_wind", 43, 34), ("thrust_hit", 27, 39)),
    "fxb": (("flurry_wind", 66, 43), ("flurry_hit", 43, 45)),
    "fxc": (("rain_rise", 43, 54), ("rain_fall", 57, 42)),
    "fxd": (("flood_charge", 69, 46), ("flood_barrage", 104, 50)),
}
ICONS = ("passive", "skill", "skill2", "ult")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def grid(im, columns, rows):
    for y in range(rows):
        for x in range(columns):
            yield im.crop((round(x * im.width / columns), round(y * im.height / rows),
                           round((x + 1) * im.width / columns), round((y + 1) * im.height / rows)))


def dominant(tile, matte):
    pixels = np.array(tile)
    alpha = pixels[:, :, 3]
    color = pixels[:, :, :3].max(axis=2)
    if matte:
        # Recover color clusters from a desaturated source matte if present.
        # The pale tabard and dark contour lie adjacent to these clusters.
        red, green, blue = pixels[:, :, :3].astype(np.int16).transpose(2, 0, 1)
        chroma = pixels[:, :, :3].max(axis=2).astype(np.int16) - pixels[:, :, :3].min(axis=2)
        colored = (chroma >= 34) & (alpha >= 105)
        near = ndimage.distance_transform_edt(~colored)
        mask = colored | ((near <= 11) & ((color < 85) | ((color > 172) & (red > blue))) & (alpha >= 105))
    else:
        mask = alpha >= 125
    mask &= ~((ndimage.distance_transform_edt(mask) <= 4) & (color < 38) & (alpha < 224))
    labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
    assert count, "Missing sprite"
    area = np.bincount(labels.ravel())
    area[0] = 0
    main = labels == area.argmax()
    mask = main | ((ndimage.distance_transform_edt(~main) <= 5) & (labels > 0) & (area[labels] >= 24))
    mask |= ndimage.binary_fill_holes(mask) & (alpha > 110)
    pixels[:, :, 3] = mask.astype(np.uint8) * 255
    pixels[~mask] = 0
    return Image.fromarray(pixels)


def body_x(tile, standing):
    box = tile.getbbox()
    mask = np.asarray(tile)[:, :, 3] > 0
    hip_row = round(box[3] - standing * .43)
    _, xs = np.where(mask[max(0, hip_row - 6):hip_row + 7])
    return float(np.median(xs)) if xs.size else (box[0] + box[2]) / 2


def actor_frames(action, tiles, samples):
    boxes = [tile.getbbox() for tile in tiles]
    heights = [box[3] - box[1] for box in boxes]
    standing = statistics.median(heights[i] for i in (samples or range(len(tiles))))
    scale = STANDING / standing
    hips = [body_x(tile, standing) for tile in tiles]
    center = statistics.median(hips[i] for i in (samples or range(len(tiles))))
    frames = []
    for i, (tile, box, hip) in enumerate(zip(tiles, boxes, hips)):
        ground = FOOT - (1 if action == "run" and i in (3, 7) else 0)
        if action in ("idle", "run"):
            pivot = hip
        elif action == "dead" and i >= 3:
            pivot = (box[0] + box[2]) / 2
        else:
            pivot = hip + np.clip(center - hip, -2 / scale, 2 / scale)
        frame = tile.transform(
            (CELL, CELL), Image.Transform.AFFINE,
            (1 / scale, 0, pivot - CELL / 2 / scale, 0, 1 / scale, box[3] - ground / scale),
            Image.Resampling.NEAREST,
        )
        bound = frame.getbbox()
        assert bound and bound[0] > 2 and bound[2] < CELL - 2 and bound[1] > 2 and bound[3] <= FOOT, (action, i, bound)
        frames.append(frame)
    return frames


def palette(frames, count):
    pixels = [np.asarray(frame) for frame in frames]
    scene = np.concatenate([arr[arr[:, :, 3] > 0, :3] for arr in pixels])
    swatch = Image.fromarray(scene.reshape(1, -1, 3)).quantize(colors=count)
    result = []
    for frame in frames:
        visible = frame.getchannel("A")
        mapped = frame.convert("RGB").quantize(palette=swatch, dither=Image.Dither.NONE).convert("RGBA")
        mapped.putalpha(visible)
        mapped.paste((0, 0, 0, 0), mask=visible.point(lambda a: 255 - a))
        result.append(mapped)
    return result


def effect_frames(tiles, size, matte):
    bitmaps = []
    for tile in tiles:
        data = np.array(tile)
        a = data[:, :, 3]
        if matte:
            rgb = data[:, :, :3].astype(np.int16)
            mask = np.ptp(rgb, axis=2) >= 43
        else:
            cutoff = max(104, round(float(a.max()) * .63))
            mask = a >= cutoff
        edge = max(4, round(min(tile.size) * .041))
        mask[:edge] = mask[-edge:] = False
        mask[:, :edge] = mask[:, -edge:] = False
        data[:, :, 3] = mask.astype(np.uint8) * 255
        data[~mask] = 0
        bitmaps.append(Image.fromarray(data))
    bounds = [im.getbbox() for im in bitmaps]
    assert all(bounds), bounds
    extent = max(max(b[2] - b[0], b[3] - b[1]) for b in bounds)
    result = []
    for im, box in zip(bitmaps, bounds):
        # One scale per effect keeps the authored expansion and contraction.
        ratio = size / extent
        cut = im.crop(box)
        cut = cut.resize(tuple(max(1, round(s * ratio)) for s in cut.size), Image.Resampling.NEAREST)
        frame = Image.new("RGBA", (CELL, CELL))
        if not cut.getbbox():
            # A single source fleck can fall between sample centres.
            cut = Image.new("RGBA", (1, 1), im.getpixel(tuple(np.argwhere(np.asarray(im)[:, :, 3] > 0)[0][::-1])))
        frame.paste(cut, ((CELL - cut.width) // 2, (CELL - cut.height) // 2))
        result.append(frame)
    return palette(result, 32)


def export_atlas(bank, groups, times):
    atlas = Image.new("RGBA", (CELL * 8, CELL * len(groups)))
    groups_info = {}
    for row, (action, frames) in enumerate(groups.items()):
        assert len(frames) == len(times[action]) == 8
        assert len(set(frame.tobytes() for frame in frames)) == 8, (action, "duplicate pose")
        groups_info[action] = {"row": row, "frames": len(frames), "ms": times[action],
                               "bounds": [frame.getbbox() for frame in frames]}
        for col, frame in enumerate(frames):
            atlas.paste(frame, (col * CELL, row * CELL))
    directory = DIST / "sprites"
    directory.mkdir(parents=True, exist_ok=True)
    for scale, tag in ((1, "_native"), (HD, "")):
        stem = f"{HERO}{bank}{tag}"
        tile = scale * CELL
        enlarged = atlas.resize((atlas.width * scale, atlas.height * scale), Image.Resampling.NEAREST)
        enlarged.save(directory / f"{stem}#sheet.png", optimize=True)
        write_json(directory / f"{stem}#anim.fanim", {"anims": {
            action: {"frames": [
                {"duration": ms / 1000, "data": {"x": col * tile, "y": info["row"] * tile, "w": tile, "h": tile}}
                for col, ms in enumerate(times[action])
            ]} for action, info in groups_info.items()
        }})
    return groups_info


def board(name, groups):
    # Show silhouettes against both the dark arena and a light inspection ground.
    QA.mkdir(parents=True, exist_ok=True)
    row_height = 128
    out = Image.new("RGB", (1024, row_height * len(groups)), "#283341")
    draw = ImageDraw.Draw(out)
    for y, (action, frames) in enumerate(groups.items()):
        for x, im in enumerate(frames):
            px, py = x * 128, y * row_height
            bg = "#a6b2ac" if x >= 4 else "#283341"
            draw.rectangle((px, py, px + 127, py + row_height - 1), fill=bg)
            out.paste(im, (px, py + (0 if name == "actor" else 10)), im)
            draw.text((px + 5, py + 4), f"{action} {x + 1}", fill="#ffffff" if x < 4 else "#101820")
            if name == "actor":
                draw.line((px, py + FOOT, px + 127, py + FOOT), fill="#5e7880")
    out.save(QA / f"{name}_contact.png")


def stills():
    d = DIST / "icons"
    d.mkdir(parents=True, exist_ok=True)
    icons = Image.open(SOURCE / "icons.png").convert("RGB")
    for name, tile in zip(ICONS, grid(icons, 2, 2)):
        tile.resize((256, 256), Image.Resampling.LANCZOS).save(d / f"{HERO}_{name}.png")
    d = DIST / "banpick_illustrations"
    d.mkdir(parents=True, exist_ok=True)
    card = np.asarray(Image.open(SOURCE / "card.png").convert("RGB"))
    h, w, _ = card.shape
    assert w <= 1216 and h <= 1428, (w, h)
    left, top = (1216 - w) // 2, 1428 - h
    right = 1216 - w - left
    # Reflect only narrow edge strips. All original art is copied 1:1.
    x = np.r_[19 - np.abs(np.arange(-left, 0) % 38 - 19), np.arange(w),
              w - 1 - (19 - np.abs(np.arange(1, right + 1) % 38 - 19))]
    y = np.r_[14 - np.abs(np.arange(-top, 0) % 28 - 14), np.arange(h)]
    padded = card[:, x][y]
    assert np.array_equal(padded[top:top + h, left:left + w], card)
    img = Image.fromarray(padded)
    hd_directory = SOURCE / "illustration"
    hd_directory.mkdir(exist_ok=True)
    img.save(hd_directory / f"{HERO}_1216x1428.png")
    # The active repository reserves 48 clear rows for the ban/pick overlay.
    card_ui = Image.new("RGBA", (304, 405))
    card_ui.paste(img.resize((304, 357), Image.Resampling.LANCZOS).convert("RGBA"), (0, 48))
    card_ui.save(d / f"{HERO}.png")
    card_ui.thumbnail((140, 187), Image.Resampling.LANCZOS)
    card_ui.save(QA / "card_140.png")
    return {"original": [w, h], "offset": [left, top], "master": [1216, 1428],
            "runtime": [304, 405], "clear_top_rows": 48}


def make_bodies():
    actors = {}
    for action, (file, rows, start, samples) in ACTORS.items():
        source = Image.open(SOURCE / f"{file}.png").convert("RGBA")
        matte = np.median(np.asarray(source)[:, :, 3]) > 160
        tiles = list(grid(source, 4, rows))
        actors[action] = actor_frames(action, [dominant(tile, matte) for tile in tiles[start:start + 8]], samples)
    colors = palette([frame for frames in actors.values() for frame in frames], 48)
    return {action: colors[i * 8:(i + 1) * 8] for i, action in enumerate(actors)}


def grip_board(actors, directory):
    directory.mkdir(parents=True, exist_ok=True)
    box = (29, 53, 105, 117)
    for action, frames in actors.items():
        out = Image.new("RGB", (1024, 470), "#27353f")
        draw = ImageDraw.Draw(out)
        for i, frame in enumerate(frames):
            x, y = i % 4 * 256 + 16, i // 4 * 235 + 23
            for nx in range(30, 105, 5):
                dx = x + (nx - box[0]) * 3
                draw.line((dx, y, dx, y + 193), fill="#3f5463")
                draw.text((dx - 4, y + 194), str(nx), fill="white")
            for ny in range(55, 117, 5):
                dy = y + (ny - box[1]) * 3
                draw.line((x, dy, x + 228, dy), fill="#3f5463")
                draw.text((x - 15, dy - 5), str(ny), fill="white")
            sprite = frame.crop(box).resize((228, 192), Image.Resampling.NEAREST)
            out.paste(sprite, (x, y), sprite)
            draw.text((x + 6, y - 17), f"{action} {i + 1}", fill="white")
        out.save(directory / f"{action}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grip-board", type=Path)
    opts = parser.parse_args()
    actors = make_bodies()
    if opts.grip_board:
        grip_board(actors, opts.grip_board)
        return
    QA.mkdir(parents=True, exist_ok=True)
    raw_prop = Image.open(SOURCE / "trident.png").convert("RGBA")
    weapon, axis = trident.template(dominant(raw_prop, False))
    weapon_path = SOURCE / "trident_native.png"
    weapon.save(weapon_path)
    grips = json.loads((ROOT / "grips.json").read_text(encoding="utf-8"))
    assert actors.keys() == grips.keys()
    tips = {}
    for action, poses in grips.items():
        assert len(poses) == 8
        equipped = [trident.attach(body, weapon, axis, pose) for body, pose in zip(actors[action], poses)]
        actors[action] = [one[0] for one in equipped]
        tips[action] = [one[1] for one in equipped]
    effects, effect_times = {}, {}
    for file, specs in FX.items():
        source = Image.open(SOURCE / f"{file}.png").convert("RGBA")
        matte = np.median(np.asarray(source)[:, :, 3]) > 155
        tiles = list(grid(source, 4, 4))
        for i, (effect, size, ms) in enumerate(specs):
            effects[effect] = effect_frames(tiles[i * 8:(i + 1) * 8], size, matte)
            effect_times[effect] = [ms] * 8
    write_json(ROOT / "art_manifest.json", {
        "hero": HERO, "facing": "right", "native_cell": [CELL, CELL], "hd_cell": [CELL * HD, CELL * HD],
        "foot_anchor": [64, FOOT], "effect_anchor": [64, 64], "hd_multiplier": HD, "loop": ["idle", "run"],
        "actor": export_atlas("", actors, TIMES), "fx": export_atlas("_fx", effects, effect_times),
        "card": stills(),
        "weapon": {"span_px": trident.LENGTH, "source": "art/trident_native.png", "tip_by_frame": tips,
                   "grips_sha256": sha(ROOT / "grips.json")},
        "source_sha256": {p.name: sha(p) for p in sorted(SOURCE.glob("*.png"))},
        "runtime_registration_tested": False,
    })
    board("actor", actors)
    board("effects", effects)


if __name__ == "__main__":
    main()
