# 赫拉克勒斯素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-21，交付包 `D:/TFM2-Workshop/heracles_packs/outputs/heracles_assets_done.zip`）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：常态、刻耳柏洛斯形态、特效，图标、选人图和 1216×1428 的立绘；512 格的
那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`checksums.json`、
`audio/sources.json`、`reference/`（造型、狮头巨棒、觉醒形态的参照）。

## 接入（Claude，2026-11-21）

- `tools/art/heracles_fix.py` 把 `runtime/sprites` 的图收色写到 `snapped/`：常态和刻耳柏洛斯形态两张身体图合起来 64 色（同一套调色板，
  变身时颜色不跳），特效每组 32 色（`tools/art/ragnarok_repixel.py` 的 `snap_delivery`，小次郎那次的做法）。
- `tools/art/import_heracles.py` 出 1 倍帧和高清帧（PPU 3.3，站高 37 个游戏像素）：常态 8 个动作原名，刻耳柏洛斯形态 8 个动作 `c_*`，
  第十二御业以后由 `addons/ragnarok/src/heracles.rs` 的显示钩子换上；形态的普攻 `c_attack` 按常态普攻的节奏重排时长。
  巨棒的弧光、狮头、变身的光环和觉醒、拳风、护势的光环按 `cues.json` 的锚点画进他自己的帧、在身子后面（画在前面会盖住头和脸）；
  砸在他身前地上的冲击画在前面；巨棒、拳头的命中放在目标身上。
- 技能数据 `tools/kit/build_heracles.py`，文本和音效 `tools/kit/setup_heracles.py`，被动、配音和显示钩子 `addons/ragnarok/src/heracles.rs`。
- 音频：`python tools/kit/seed_heracles_audio.py`（默认从 `D:/TFM2-Workshop/heracles_packs/outputs/heracles_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：12 条音效和六句配音，改名成 `ragnarok_heracles_sfx_*` / `ragnarok_heracles_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/` 那张；技能图标：涅墨亚之狮 `lion`、克里特公牛 `slam`、刻耳柏洛斯 `cerberus`，`justice` 那张
  是被动，不装（游戏只有三个技能图标位）。
