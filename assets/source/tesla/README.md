# 尼古拉·特斯拉素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-23，交付包 `D:/TFM2-Workshop/tesla_packs/outputs/tesla_assets_done.zip`；
这里放的是 Codex 的提交 `7e3a2e0db`，比交付包晚一分钟，以提交为准）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，图标、选人图和卡片；512 格的那组是精确两倍最近邻，
没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`checksums.json`、`audio/sources.json`、
`reference/`（造型参照）。

## 接入（Claude，2026-11-23）

- 机甲双拳，没有另贴的道具，不用修。`tools/art/tesla_fix.py` 只收色（身体 64 色，特效每组 32 色），写到 `snapped/`。
- `tools/art/import_tesla.py` 出 1 倍帧和高清帧（PPU 2.75，站直 42 个游戏像素）。普攻和双拳的拳风画进他自己的帧、在身子后面；
  特斯拉步脚下的拖痕和到达的闪光在前面。离场的闪光数据在起跳那一拍放在他当时站的地方（不跟着走）；拳击和双拳的命中放在目标身上。
- 神之监狱：Codex 画的是一个金色的立方体牢笼，展开一次（`zone_deploy`）、再循环（`zone_idle`）。区域的画面会跟着施放方向转，
  方块一转就歪，所以做成套在被关的人身上的牢笼：展开一次，再每 40 拍（循环一圈 0.675 秒）在他身上接着放一次循环，都是跟着人的
  特效画面，不转方向、走高清。一开始挂成 buff 的画面，游戏只画 1 倍，用户：「这个弄高清点」，就改成这样。牢笼的底边对着脚底
  （原点放在格子里 182 那一行）。
- 位置是打野（用户 2026-11-23 定的）。技能数据 `tools/kit/build_tesla.py`，文本和音效 `tools/kit/setup_tesla.py`，配音
  `addons/ragnarok/src/tesla.rs`。
- 音频：`python tools/kit/seed_tesla_audio.py`（默认从 `D:/TFM2-Workshop/tesla_packs/outputs/tesla_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：用到 15 条音效和八句配音（古川慎），改名成 `ragnarok_tesla_sfx_*` / `ragnarok_tesla_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_tesla.png`；技能图标：特斯拉步 `warp`、神之监狱 `zone`、双向电光拳 `punch`，
  `plasma` 那张是普攻，不装（游戏只有三个技能图标位）。
