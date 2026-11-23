# 列奥尼达斯素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-23，交付包 `D:/TFM2-Workshop/leonidas_packs/outputs/leonidas_assets_done.zip`；
这里放的是 Codex 的提交 `35546c8f5`，以提交为准）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效、链盾动作没拿盾的身体，三件独立的道具（圆盾、真理之盾、
钢链），图标、选人图和卡片；512 格的那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、
`manifest.json`、`checksums.json`、`shield-registration.json`（每帧盾的中心、角度、大小）、`audio/sources.json`、`reference/`（造型参照）。

## 接入（Claude，2026-11-23）

- 盾（「模型不要变大变小」）：Codex 的每一帧是空手的身体贴上一面盾，大小是一帧一帧写死的。圆盾平时 37×51，可举盾第 3-6 帧放大成
  42×55、甩出去的飞盘 44×24 / 51×31 / 43×29（长轴比直径短）、倒地时 37×36 和 55×17，盾一会儿大一会儿小。
  `tools/art/leonidas_bare.py` 用 Codex 自己的代码（它的 build.py + shield.py）取出没拿盾的身体放进 `bare/`（按原表重贴 64 帧和
  交付一模一样才写），`tools/art/leonidas_fix.py` 照它的贴法一律按同一面盾重贴：举盾 37×51，飞盘长轴都是 51，倒地第 4 帧
  37×51、躺在地上 51×17；大招换的真理之盾是另一面盾（53×67），不动。再收色（身体 64 色，特效每组 32 色），写到 `snapped/`。
- `tools/art/import_leonidas.py` 出 1 倍帧和高清帧（PPU 2.75，站直 42 个游戏像素）。盾击的钢弧、链盾飞盘的尾迹和钢链回卷、
  举盾的盾沿光和反弹的光箭画进他自己的帧、在前面（都在盾那一边，碰不到脸）；方阵冲锋脚下的尘土画在身后（画在前面一大团盖住
  两条腿）。盾击和链盾的命中、方阵冲锋的冲击放在目标身上。
- 反弹：Codex 想让举盾只在真挡下阿波罗的光箭时播反弹，方向按真的出射方向。引擎没有能让弹道转向的效果，这里举盾时身上挂反伤
  （打他的人挨一部分回去，阿波罗的光箭也一样），反弹的光箭每次举盾都在第 5 帧画出来。
- 位置是辅助（用户 2026-11-23 定的）。技能数据 `tools/kit/build_leonidas.py`，文本和音效 `tools/kit/setup_leonidas.py`，配音
  `addons/ragnarok/src/leonidas.rs`。
- 音频：`python tools/kit/seed_leonidas_audio.py`（默认从 `D:/TFM2-Workshop/leonidas_packs/outputs/leonidas_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：用到 15 条音效和六句配音（白熊寛嗣），改名成 `ragnarok_leonidas_sfx_*` / `ragnarok_leonidas_vo_*`；
  盾击蓄力那条没用上（普攻的效果在砸到那一拍才放）。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_leonidas.png`；技能图标：链盾 `chain`、举盾 `guard`、方阵冲锋 `phalanx`，
  `bash` 那张是普攻，不装（游戏只有三个技能图标位）。
