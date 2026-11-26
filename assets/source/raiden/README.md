# 雷电为右卫门素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-22，交付包 `D:/TFM2-Workshop/raiden_packs/outputs/raiden_assets_done.zip`）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、肌肉解放的过渡、特效，图标、选人图和卡片；512 格的那组是精确
两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`checksums.json`、`audio/sources.json`、
`reference/`（造型参照）。

## 接入（Claude，2026-11-22）

- `tools/art/raiden_fix.py` 把 `runtime/sprites` 的图收色写到 `snapped/`：身体和肌肉解放的过渡合起来 64 色（同一套调色板），特效每组
  32 色（`tools/art/ragnarok_repixel.py` 的 `snap_delivery`，小次郎那次的做法）。
- `tools/art/import_raiden.py` 出 1 倍帧和高清帧（PPU 3.3，站高 37 个游戏像素，和赫拉克勒斯一样高）：8 个动作原名，肌肉解放的过渡
  `muscle_release`（每条命第一次放八咫乌之前，数据用 CasterAnimation 放）。掌风、八咫乌蓄劲的气和冲击波、肌肉解放的红纹按 `cues.json`
  的锚点画进他自己的帧、在身子后面（画在前面会盖住脸）；四股的尘土和地面震环在脚下，画在前面；掌、八咫乌的命中放在目标身上。
- 技能数据 `tools/kit/build_raiden.py`，文本和音效 `tools/kit/setup_raiden.py`，配音 `addons/ragnarok/src/raiden.rs`。
- 音频：`python tools/kit/seed_raiden_audio.py`（默认从 `D:/TFM2-Workshop/raiden_packs/outputs/raiden_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：13 条音效和六句配音（木村昴），改名成 `ragnarok_raiden_sfx_*` / `ragnarok_raiden_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/` 那张；技能图标：连掌 `palm`、四股 `shiko`、八咫乌 `yatagarasu`，`volund` 那张是被动，
  不装（游戏只有三个技能图标位）。
