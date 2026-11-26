# 开膛手杰克素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-21，交付包 `D:/TFM2-Workshop/jack_packs/outputs/jack_assets_done.zip`；伞前护弧换成
轻的那一版也在包里）。这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，飞刀和雨伞的道具图、图标、选人图和
1216×1428 的立绘；512 格的那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、
`checksums.json`、`audio/sources.json`、`reference/`（造型参照）。

## 接入（Claude，2026-11-21）

- `tools/art/jack_fix.py` 把 `runtime/sprites` 的图收色写到 `snapped/`：身体 64 色，特效每组 32 色（`tools/art/ragnarok_repixel.py` 的
  `snap_delivery`，小次郎那次的做法）。
- `tools/art/import_jack.py` 出 1 倍帧和高清帧（PPU 3.3，站高 35 个游戏像素，连帽上的羽毛）：8 个动作原名。扇形飞刀、伞前的护弧、
  手套触物按 `cues.json` 的锚点画进他自己的帧、在身子后面（护弧画在前面会横过他的脸）；后撤时的雾画在前面（他是躲进雾里）。
  飞刀命中、收招 `dear_god` 放在目标身上，大招起手单片镜那道异色的光 `emotion_glint` 也放在被他看穿的人身上（Codex 画在他眼睛上，
  一圈比他的头还大）。飞出去的刀是 `ragnarok/effects/ragnarok_jack_proj`（1 倍，跟着飞行方向转）。
- 技能数据 `tools/kit/build_jack.py`，文本和音效 `tools/kit/setup_jack.py`，被动和配音 `addons/ragnarok/src/jack.rs`。
- 音频：`python tools/kit/seed_jack_audio.py`（默认从 `D:/TFM2-Workshop/jack_packs/outputs/jack_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：12 条音效和六句配音，改名成 `ragnarok_jack_sfx_*` / `ragnarok_jack_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/` 那张；技能图标：飞刀扇 `fan`、伦敦之雾 `artifact`（手套碰过的东西变成神器，伞也是）、
  亲爱的神 `dear_god`，`emotion` 那张单片镜是被动，不装（游戏只有三个技能图标位）。
