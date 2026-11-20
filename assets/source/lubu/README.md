# 吕布奉先的素材（Codex 交付）

来源：Codex 2026-11-20 的交付，本地仓库 `D:\steam\steamapps\common\Teamfight Manager2\TeamFightMange2-mod-ragnarok-lubu`
（BoDUD/TeamFightMange2-mod 的旧检出，远端已不在）分支 `codex/ragnarok-lubu-assets-v02` 的提交 `00d78f3`
（素材 0.2.1，修过黑边重影），也在 `<游戏>\outputs\ragnarok_lubu_assets_v02.zip`。

`codex_v02/`：

- `ragnarok_lubu_native#sheet.png` / `#anim.fanim`：角色 8 个动作 x 8 帧，每格 128 x 128，脚底点 (64, 116)。就是游戏里的高清帧，
  `tools/art/import_lubu.py` 把挥砍特效画进去、缩出 1 倍帧，`tools/art/ppu_hd.py --hero lubu` 写 hd_ / lo_。
- `ragnarok_lubu_fx_native#sheet.png` / `#anim.fanim`：8 种特效 x 8 帧，同样的格子。挥痕、横扫、突刺、天喰蓄力和斩击画进他自己的帧，
  火花、天喰冲击、碎盾放进 `ragnarok/effects/ragnarok_lubu_fx`。
- `asset_manifest_v02.json`：帧时长、特效锚点（从脚底量）、触发时刻、四张图标的 SHA256。
- `ragnarok_lubu_passive.png`：被动图标（用户确认的那张）。游戏只有三个技能图标位，被动写在普攻说明里，这张不装进游戏。

Codex 做的 4 倍高清图集（4096 x 4096）是原画逐像素放大 4 倍，像素一样，没有收进来。

技能图标三张（`ragnarok/icons/`）是用户确认的高清版，原样 256 x 256，哈希和清单一致。

音频（15 条原创音效、10 条官方日语原声）不进仓库：`python tools/kit/seed_lubu_audio.py` 从交付里复制到 `ragnarok/sound/sfx/`。
