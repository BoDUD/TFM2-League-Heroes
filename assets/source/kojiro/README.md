# 佐佐木小次郎素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-21，交付包 `D:/TFM2-Workshop/kojiro_packs/outputs/kojiro_assets_done.zip`）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集、图标、选人图和 1216×1428 的立绘；512 格的那组是精确两倍最近邻，没放）、
`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`art_manifest.json`、`checksums.json`、`audio/sources.json`、
`model_reference.png` / `weapon_reference.png`（造型参照）。

## 接入（Claude，2026-11-21）

- `tools/art/kojiro_fix.py` 把 `runtime/sprites` 的图收色写到 `snapped/`：身体和双刀待机合起来 64 色（同一套调色板，换双刀时颜色不跳），
  特效每组 32 色。Codex 的图有十几万种颜色，`ppu_hd.py` 出 lo_（选人、百科）和 `ragnarok_art.py` 出 1 倍帧挑调色板会挑歪。
- `tools/art/import_kojiro.py` 出 1 倍帧和高清帧（PPU 3.3，站高 34 个游戏像素）：单刀 8 个动作原名，双刀待机改名 `niten_idle`，
  大招再放一份叫 `niten_attack`（按普攻的节奏重排时长），二天岩流之后由 `addons/ragnarok/src/kojiro.rs` 的显示钩子换上。
  燕返刀光、预判涟漪、双刀交错按 `cues.json` 的锚点画进他自己的帧，在身子后面（画在前面会盖住头和脸）；命中的金属火花放在目标身上。
- 技能数据 `tools/kit/build_kojiro.py`，文本和音效 `tools/kit/setup_kojiro.py`，被动、配音和显示钩子 `addons/ragnarok/src/kojiro.rs`。
- 音频：`python tools/kit/seed_kojiro_audio.py`（默认从 `D:/TFM2-Workshop/kojiro_packs/outputs/kojiro_assets` 拷，先核对 `audio/sources.json`
  里的 SHA-256）：12 条音效和全部八句配音，改名成 `ragnarok_kojiro_sfx_*` / `ragnarok_kojiro_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/` 那张；技能图标：燕返 `swallow`、千手无双 `senju`、二天岩流 `niten`，`prediction` 那张是被动，
  不装（游戏只有三个技能图标位）。
