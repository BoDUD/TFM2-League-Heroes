# 哈迪斯素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-22，交付包 `D:/TFM2-Workshop/hades_packs/outputs/hades_assets_done.zip`；
这里放的是 Codex 的提交 `6adc388f9`，内容和交付包一样）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，双叉枪和德斯莫斯的道具图，图标、选人图和卡片；512 格的
那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`spear-registration.json`
（双叉枪每帧的握点、角度、握在枪杆的哪里）、`checksums.json`、`audio/sources.json`、`reference/`（造型参照）。

`bare/` 不是交付里的：是哈迪斯没拿枪的身体帧（`tools/art/hades_bare.py` 用 Codex 工作目录里它自己的 `build.art_action(tag, equip=False)`
取出来的，按原表重贴枪 64 帧都和交付的一样），重贴枪要用。

## 接入（Claude，2026-11-22）

- 双叉枪（用户说过「如果武器有歪的地方你可以帮忙修复一下」，这次照样查）：枪长每帧都是 154，不用改；待机 8 帧 Codex 给的角度
  -83、-81、-85、-82、-85、-83、-82、-83，一会儿左一会儿右，枪尖跟着来回跳 2–3 个像素。`tools/art/hades_fix.py` 照 Codex 的做法
  （`spear.py`）把枪重新贴到 `bare/` 的身体上，待机一律 -83°，再和特效一起收色写到 `snapped/`（身体 64 色，特效每组 32 色）。
  改到待机第 2–5、7 帧，改动都在枪上。
- `tools/art/import_hades.py` 出 1 倍帧和高清帧（PPU 2.75，一开始就是放大到联盟个子以后的大小：站直 42 个游戏像素，枪尖 58）。
  枪风、风压斩、伊科尔觉醒、德斯莫斯的突刺按 `cues.json` 的锚点画进他自己的帧、在身子后面；重砸砸开的地面和碎石在脚下，画在
  前面。两种命中放在目标身上。
- 技能数据 `tools/kit/build_hades.py`，文本和音效 `tools/kit/setup_hades.py`，配音 `addons/ragnarok/src/hades.rs`。
- 音频：`python tools/kit/seed_hades_audio.py`（默认从 `D:/TFM2-Workshop/hades_packs/outputs/hades_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：14 条音效和七句配音（置鮎龍太郎）都用上，改名成 `ragnarok_hades_sfx_*` / `ragnarok_hades_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_hades.png`；技能图标：风压斩 `wind`、冥府重砸 `earth`、德斯莫斯 `desmos`，
  `bident` 那张是普攻，不装（游戏只有三个技能图标位）。
