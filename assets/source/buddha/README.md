# 释迦素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-22，交付包 `D:/TFM2-Workshop/buddha_packs/outputs/buddha_assets_done.zip`）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，图标、选人图和卡片；512 格的那组是精确两倍最近邻，没放）、
`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`checksums.json`、`audio/sources.json`、`reference/`
（造型参照）。

## 接入（Claude，2026-11-22）

- `tools/art/buddha_fix.py` 把 `runtime/sprites` 的图收色写到 `snapped/`：身体 64 色，特效每组 32 色。
- `tools/art/import_buddha.py` 出 1 倍帧和高清帧（PPU 3.3，站高 34 个游戏像素）：8 个动作原名，受击是未来视看穿以后的撤步。六道棍的
  棍风、枪刃的棍风、未来视的准星、观音盾的莲光、大圆寂刀·零蓄的气和斩出的刀光按 `cues.json` 的锚点画进他自己的帧、在身子后面（画在
  前面会盖住脸）；撤步的气流在脚下，画在前面。棍和枪刃的命中、莲光绽开打在人身上的挡击放在目标身上；被动的未来视准星、观音盾收起时的
  莲光放在他自己身上，按身子挪到眼镜和胸口。
- 技能数据 `tools/kit/build_buddha.py`，文本和音效 `tools/kit/setup_buddha.py`，配音 `addons/ragnarok/src/buddha.rs`。
- 音频：`python tools/kit/seed_buddha_audio.py`（默认从 `D:/TFM2-Workshop/buddha_packs/outputs/buddha_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：15 条音效里用到 14 条（撤步的落脚声没地方放：受击动作是引擎自己播的），六句配音（中村悠一）用
  五句，宣传片结尾那句只给试听，改名成 `ragnarok_buddha_sfx_*` / `ragnarok_buddha_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/` 那张；技能图标：枪刃 `staff`、观音盾 `shield`、大圆寂刀·零 `nirvana`，`sight` 那张是被动
  （未来视），不装（游戏只有三个技能图标位）。
