# 阿波罗素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-23，交付包 `D:/TFM2-Workshop/apollo_packs/outputs/apollo_assets_done.zip`；
这里放的是 Codex 的提交 `ab889d460`，以提交为准）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，三件独立的道具（光弓、光弦、阿尔忒弥斯的女神像），
图标、选人图和卡片；512 格的那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、
`manifest.json`、`checksums.json`、`bow-registration.json`（每帧弓和女神像的位置、大小、弓梢和弦）、`reflection.json`（和列奥尼达斯
举盾反弹的约定）、`audio/sources.json`、`reference/`（造型参照）。

## 接入（Claude，2026-11-23）

- 弓和女神像（「模型不要变大变小」）：Codex 的每一帧是空手的身体，光之矢第 3-6 帧贴上光弓、大招第 3-5 帧在身后贴女神像，大小是
  一帧一帧写死的：弓在拉弦、放箭两帧是 84×27，成形那帧只有 65×21、放完那帧 76×24；女神像显现那帧 95×141、之后 103×163。
  `tools/art/apollo_bare.py` 用 Codex 自己的代码（它的 build.py + bow.py）取出没拿弓的身体放进 `bare/`（按原表重贴 64 帧和交付
  一模一样才写），`tools/art/apollo_fix.py` 照它的贴法一律按满的大小重贴（握点不动，弓梢和弦跟着重算），女神像显现那帧用后两帧的
  大小和位置。再收色（身体 64 色，特效每组 32 色），写到 `snapped/`。
- `tools/art/import_apollo.py` 出 1 倍帧和高清帧（PPU 2.75，站直 42 个游戏像素）。日轮拳的拳光、光丝投出、离弦的光画进他自己
  的帧、在前面；光弓成形和女神像显现的光（一个大日轮）、银箭突进的箭影画在身后：画在前面会盖住他的脸（显现那次还盖住整个女神
  像），箭影的箭头对着出拳的手，手跟着身体走。日轮拳和光箭的命中、光丝的收束放在目标身上；飞出去的光箭是弹道画面（1 倍）。
- 和列奥尼达斯：`reflection.json` 想让光箭射在举着的盾上时停在碰撞点、交给列奥尼达斯按真的方向弹回去。引擎没有能让弹道转向的
  效果，列奥尼达斯举盾时身上挂反伤（光箭打上去一样弹回一部分伤害），反弹的光箭画在他举盾的帧里。两人对上时各有一句对方的台词。
- 位置是中路（用户 2026-11-23：「位置你看着定就行 选最合适的位置」）：普攻是拳（近战），下路要远程普攻；光丝定身、光箭消耗、
  银箭突进进场爆发，是中路刺客。技能数据 `tools/kit/build_apollo.py`，文本和音效 `tools/kit/setup_apollo.py`，配音
  `addons/ragnarok/src/apollo.rs`。
- 音频：`python tools/kit/seed_apollo_audio.py`（默认从 `D:/TFM2-Workshop/apollo_packs/outputs/apollo_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：用到 15 条音效和三句配音（鈴村健一），改名成 `ragnarok_apollo_sfx_*` / `ragnarok_apollo_vo_*`；
  出拳预备那条没用上（普攻的效果在打到那一拍才放）。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_apollo.png`；技能图标：阿尔忒弥斯之丝 `threads`、光之矢 `arrow`、银箭突进
  `artemis`，`strike` 那张是普攻，不装（游戏只有三个技能图标位）。
