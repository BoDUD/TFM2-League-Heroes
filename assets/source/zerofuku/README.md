# 零福／波旬素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-22，交付包 `D:/TFM2-Workshop/zerofuku_packs/outputs/zerofuku_assets_done.zip`；
打包后 Codex 又提交了一次 `e8ff128fd`「握柄那只空手露在斧柄上面」，这里放的是那次提交的）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：零福、波旬、特效，斧爻的道具图，图标、选人图和卡片；512 格的
那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`axe-registration.json`
（斧爻每帧的握点、角度、长度、斧刃倍数）、`checksums.json`、`audio/sources.json`、`reference/`（造型参照）。

`bare/` 不是交付里的：是零福没拿斧子的身体帧（`tools/art/zerofuku_bare.py` 用 Codex 工作目录里它自己的 `build.artwork(equip=False)`
取出来的，按原表重贴斧子 64 帧都和交付的一样），重贴斧子要用。

## 接入（Claude，2026-11-22）

- 斧爻（用户：「如果武器有歪的地方你可以帮忙修复一下」）：`tools/art/zerofuku_fix.py` 照 Codex 的做法（`rigid_axe.py`）把斧子重新贴到
  `bare/` 的身体上，改两处，再和波旬、特效一起收色写到 `snapped/`：
  - 斧子全长一律 107（待机的长度）。Codex 为了塞进 256 的格子，有几帧把整把斧子缩短了（Q 落斧 90、91，变身前蹲下 95，跑步 103，
    Q 别的帧 101-109），斧柄一会儿长一会儿短。零福的格子放宽到 272（只有 Q 落斧那两帧伸出 256）。
  - 待机第 4 帧的斧子按前后两帧的角度（-32.5 度）：原来平了 3 度多，一循环斧头往下点一下。
  - Q 里斧刃放大（1.18-1.35 倍）是 Codex 照原作画的（斧爻吸了不幸变大），不动。
  - 收色：两个形态合起来 64 色，特效每组 32 色。`--check` 先验一遍按原表贴回去和交付的一模一样。
- `tools/art/import_zerofuku.py` 出 1 倍帧和高清帧（PPU 3.3，零福 35、波旬 38 个游戏像素）：零福 8 个动作原名，波旬 8 个动作 `h_*`，
  大招 `ult` 是破茧（第 6 帧波旬现身）。波旬的普攻、Q 按零福的节奏重排时长，魔臂横断 `h_ult` 最后一帧多站一会儿凑满 0.93 秒。斧爻和
  臂刃的斩痕、Q 吸聚的不幸、魔钻的螺旋、破茧的碎壳按 `cues.json` 的锚点画进他自己的帧、在身子后面；怨气在脚下，画在前面。两种命中
  和被动挂上的不幸放在目标身上。
- 技能数据 `tools/kit/build_zerofuku.py`，文本和音效 `tools/kit/setup_zerofuku.py`，配音和波旬形态的显示 `addons/ragnarok/src/zerofuku.rs`。
- 音频：`python tools/kit/seed_zerofuku_audio.py`（默认从 `D:/TFM2-Workshop/zerofuku_packs/outputs/zerofuku_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：18 条音效和六句配音（零福四句，村瀬歩；波旬两句，稻田彻）都用上，改名成
  `ragnarok_zerofuku_sfx_*` / `ragnarok_zerofuku_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_zerofuku.png`（`ragnarok_hajun.png` 没用：一个英雄一张）；技能图标：斧爻
  `cleaver`、怨气冲击 `misfortune`、破茧 `cocoon`，`drill` 那张是波旬的 Q，不装（游戏只有三个技能图标位）。
