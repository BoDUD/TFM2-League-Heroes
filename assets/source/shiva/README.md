# 湿婆素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-22，交付包 `D:/TFM2-Workshop/shiva_packs/outputs/shiva_assets_done.zip`）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：常态、轮回舞踊的燃烧形态、特效，图标、选人图和卡片；512 格的那组是
精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`checksums.json`、
`audio/sources.json`、`reference/`（常态和燃烧形态的造型参照）。

## 接入（Claude，2026-11-22）

- `tools/art/shiva_fix.py` 把 `runtime/sprites` 的图收色写到 `snapped/`：常态和燃烧形态两张身体图合起来 64 色（同一套调色板，变身时
  颜色不跳），特效每组 32 色。收完色再改一处：燃烧形态的跑步（`h_run`）Codex 画成了五条胳膊（身后垂着两条），贴着腰、颜色深的那条
  八帧都擦掉（`EXTRA_ARM`，每帧给手上一点和顶上几行的切法；腰带、裤子按颜色挡住不擦，露出来的皮肤边补描边），留下戴手镯的那条，
  和燃烧形态的待机一样四条胳膊。
- `tools/art/import_shiva.py` 出 1 倍帧和高清帧（PPU 3.3，站高 35 个游戏像素）：常态 8 个动作原名，燃烧形态 8 个动作 `h_*`，轮回舞踊
  时由 `addons/ragnarok/src/shiva.rs` 的显示钩子换上；燃烧形态的普攻、四臂连击按常态的节奏重排时长（RETIME）。拳风、交叉、点燃、
  火鞭按 `cues.json` 的锚点画进他自己的帧、在身子后面；舞步和火步在脚下，画在前面；四臂、燃烧形态的命中放在目标身上。
- 技能数据 `tools/kit/build_shiva.py`，文本和音效 `tools/kit/setup_shiva.py`，被动（节奏）、配音和显示钩子 `addons/ragnarok/src/shiva.rs`。
- 音频：`python tools/kit/seed_shiva_audio.py`（默认从 `D:/TFM2-Workshop/shiva_packs/outputs/shiva_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：14 条音效和六句配音（铃木达央），改名成 `ragnarok_shiva_sfx_*` / `ragnarok_shiva_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/` 那张；技能图标：四臂连击 `fourarms`、舞步 `dance`、轮回舞踊 `tandava`，`rhythm` 那张是被动，
  不装（游戏只有三个技能图标位）。
