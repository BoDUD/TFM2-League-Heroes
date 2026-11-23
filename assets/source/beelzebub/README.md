# 别西卜素材

Codex 的交接说明见 [HANDOFF.md](HANDOFF.md)（2026-11-23，交付包 `D:/TFM2-Workshop/beelzebub_packs/outputs/beelzebub_assets_done.zip`；
这里放的是 Codex 的提交 `ce16a3f54`，比交付包晚一分钟，以提交为准）。
这里放了交付里除 WAV / MP3 以外的东西：`runtime/`（256 格的图集：身体、特效，骸骨杖阿波弥俄斯的道具图，图标、选人图和卡片；512 格的
那组是精确两倍最近邻，没放）、`review/`（可播放的预览页、逐格核对和接触图）、`cues.json`、`manifest.json`、`staff-registration.json`
（骸骨杖每帧的握点、角度、握在杖身的哪里和像素校验）、`checksums.json`、`audio/sources.json`、`reference/`（造型参照）。

## 接入（Claude，2026-11-23）

- 骸骨杖照零福、哈迪斯那两次查过：每帧同一根直杖、长度一样（103 格），待机的角度跟着呼吸慢慢摆（-115° 到 -118°，不是来回跳），
  掉杖以后四帧锁住。不用改。`tools/art/beelzebub_fix.py` 只收色（身体 64 色，特效每组 32 色），写到 `snapped/`。
- `tools/art/import_beelzebub.py` 出 1 倍帧和高清帧（PPU 2.75，站直 42 个游戏像素）。振动掌的掌风、振动波和扩散的波纹画进他自己的帧、
  在身子后面；地狱之门的屏障和格挡涟漪、混沌的黑核在前面；混沌的爆发一开始是个比他还大的黑球，画在前面会把人连脸整个盖住，
  放在身后。振动掌的命中放在目标身上。
- 位置是中路法师（用户 2026-11-23 定的：「中路法师」），包里第一个打魔法伤害的。技能数据 `tools/kit/build_beelzebub.py`，文本和音效
  `tools/kit/setup_beelzebub.py`，配音 `addons/ragnarok/src/beelzebub.rs`。
- 音频：`python tools/kit/seed_beelzebub_audio.py`（默认从 `D:/TFM2-Workshop/beelzebub_packs/outputs/beelzebub_assets` 拷，先核对
  `audio/sources.json` 里的 SHA-256）：用到 14 条音效和五句配音（浪川大辅），改名成 `ragnarok_beelzebub_sfx_*` / `ragnarok_beelzebub_vo_*`。
- 选人立绘用 `runtime/banpick_illustrations/ragnarok_beelzebub.png`；技能图标：暴食的堕天使 `wave`、地狱之门 `guard`、虚神〈混沌〉
  `chaos`，`palm` 那张是普攻，不装（游戏只有三个技能图标位）。
