# 秦始皇素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-22，交付包 `D:/TFM2-Workshop/qin_packs/outputs/qin_assets_done.zip`；
这里放的是 Codex 的提交 `969382a77`，内容和交付包一样）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，勾践剑的道具图，图标、选人图和卡片；512 格的那组是
精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`sword-registration.json`
（大招持剑那几帧的握点、角度、长度）、`checksums.json`、`audio/sources.json`、`reference/`（造型参照）。

## 接入（Claude，2026-11-22）

- 勾践剑只在大招第 3–7 帧出现，Codex 每帧贴的是同一把剑、同一个长度（87），只转角度，不用改。`tools/art/qin_fix.py` 收色
  （身体 64 色，特效每组 32 色），写到 `snapped/`。
- `tools/art/import_qin.py` 出 1 倍帧和高清帧（PPU 2.75，站直 42 个游戏像素）。爪痕、天凤回推、勾践剑的剑光和剑痕按 `cues.json`
  的锚点画进他自己的帧、在身子后面；神罗铠袖的护势是两条袖子上的光，画在前面。指爪命中和气弹炸开的星放在目标身上；飞出去的
  气弹是弹道画面（`ragnarok/effects/ragnarok_qin_proj`，1 倍）。
- 位置是辅助（用户问过理由以后定的「辅助」）。技能数据 `tools/kit/build_qin.py`，文本和音效 `tools/kit/setup_qin.py`，配音
  `addons/ragnarok/src/qin.rs`。
- 音频：`python tools/kit/seed_qin_audio.py`（默认从 `D:/TFM2-Workshop/qin_packs/outputs/qin_assets` 拷，先核对 `audio/sources.json`
  里的 SHA-256）：13 条音效和七句配音（石川界人）都用上，改名成 `ragnarok_qin_sfx_*` / `ragnarok_qin_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_qin.png`；技能图标：波流龟气弹 `tortoise`、神罗铠袖·承力天凤 `phoenix`、
  勾践剑 `jian`，`claw` 那张是普攻，不装（游戏只有三个技能图标位）。
