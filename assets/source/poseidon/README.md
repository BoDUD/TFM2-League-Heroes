# 波塞冬素材交接

资源 ID 为 `ragnarok_poseidon`。打开 `preview.html` 可以看角色动作、独立特效、两侧朝向和命中条件，也可以在完整交付包中听语音。交付包在 `D:/TFM2-Workshop/poseidon_packs/outputs/poseidon_assets.zip`。WAV 和 MP3 随本地包提供，沿用亚当、吕布和索尔的音频交付方式。

## 原作与接入提案

波塞冬是第三回合的神方选手，对阵佐佐木小次郎。角色参考动画的金色卷发、冷峻蓝眼、蓝金开襟与白色分片裙甲。三叉戟保留深蓝直杆、金蓝鳍形护手和三枚银色刃尖。[官方角色设定](https://ragnarok-official.com/1st/character/)、[对决 PV](https://www.youtube.com/watch?v=Yrlpp7fW6II)

动画第三回合以持戟猛攻和大量高速刺击推进。游戏里建议把出手节奏、判定范围与多段命中做出区分。下表是资源对应关系，玩法参数由 Claude 接入时确定。[官方第 10 话](https://ragnarok-official.com/1st/story/ep10/)、[官方第 12 话](https://ragnarok-official.com/1st/story/ep12/)

| 动作 | 资源用法 |
| --- | --- |
| 普攻 `attack` | 单次水平突刺。出手播戟风，命中再播火花和冲击音。 |
| 怒涛连刺 `skill` | 地面进身后快速重复突刺。终点的扇形戟风与命中水花可分开使用。 |
| 暴雨斜刺 `skill2` | 抬高戟刃，然后斜向压落。升势、坠刺与落点冲击有独立触发点。 |
| 四十昼夜的大洪水 `ult` | 起手、戟影合围、收势。以目标或区域中心为戟影锚点，压迫密度由环形戟影表现。 |

## 图档及坐标

| 文件位置 | 内容 |
| --- | --- |
| `runtime/sprites/ragnarok_poseidon_native#sheet.png` 与 `#anim.fanim` | 待机、跑步、普攻、连刺、斜刺、大招、受击、倒地各 8 帧。每格 128×128，默认朝右。 |
| `runtime/sprites/ragnarok_poseidon_fx_native#sheet.png` 与 `#anim.fanim` | 8 组 × 8 帧。普通戟风及命中、连刺及命中、斜刺升势及坠刺、洪流蓄势及环绕戟影。 |
| 同目录无 `_native` 的对应文件 | 精确 4 倍最近邻，512×512 每格。 |
| `runtime/icons/` | 4 张 256×256 技能图标，含被动预留图。 |
| `runtime/banpick_illustrations/ragnarok_poseidon.png` | 选人图 304×405 RGBA，上方 48 行透明。1216×1428 立绘在 `art/illustration/`。 |
| `art/trident_native.png` 和 `grips.json` | 统一的 79 像素三叉戟模板。逐帧坐标依次为逻辑 X、Y、顺时针角度、杆上握点、是否在手。角色图已完成三叉戟合成。 |
| `cues.json` 和 `art_manifest.json` | 精确帧时长、脚底、特效锚点、接触提示和逐帧戟尖。 |

逻辑图脚底固定在 `(64,116)`，跑步腾空两格各抬 1 像素。特效各格以 `(64,64)` 为中心。左向偏移以 X=64 镜像，靠角色的定向特效可按现有 `tools/art/import_lubu.py` 的导入方法合成。命中火花接实际命中事件，局部合成用的目标位置可从 `cues.json` 换算。倒地第 4–8 帧共享同一个落地戟位置。

人物站直约 58 逻辑像素，按 PPU 1.65 约为 35 游戏像素，初次接入可用这个值与索尔在实机对照。以 128 格图进入仓库现有 `tools/art/ragnarok_art.py` 与 `tools/art/ppu_hd.py` 管线，检查 1 倍、`hd_` 和 `lo_` 三档。接入后需用实际红蓝朝向、技能时序和回放确认效果。

## 音频

樱井孝宏的波塞冬官方日语原声有 9 段。6 段来自单人倒计时，3 段来自对决 PV 的波塞冬独白，PV 片段保留背景音乐。17 条原创战斗 Foley 分别覆盖戟风、确认命中、升势、坠刺、蓄势、连刺、落戟和身体落地。每条均有 44.1 kHz 单声道 PCM16 WAV 和 160 kbps MP3。台词意译、切点及建议事件见 `audio/voice_cuts.json`，文件哈希及音源见 `audio/manifest.json`。[官方声源公告](https://ragnarok-official.com/1st/news/127/)、[波塞冬倒计时原帖](https://twitter.com/ragnarok_PR/status/1402823584263905283)、[对决 PV](https://www.youtube.com/watch?v=Yrlpp7fW6II)

在仓库运行 `python assets/source/poseidon/tools/seed_audio.py <解压后的素材根目录>`。脚本校验所有 MP3 后导入仓库本地的 `ragnarok/sound/sfx/`。建议长台词用于入场和展示，攻击用短音效。

## 校验

`python assets/source/poseidon/tools/verify_pack.py --art-only` 验证无音频的分支。用完整解压包检查时省略 `--art-only`。重建可运行 `tools/build_art.py`、`tools/build_audio.py <官方倒计时媒体> <官方对决 PV 媒体>`，需要 Pillow、NumPy、SciPy，音频另用 SoundFile 与 imageio-ffmpeg。

校验覆盖角色与特效边界、二值透明、精确 4 倍采样、同一把戟的逐帧合成、三叉戟未裁切、平刺角度、立绘尺寸、音频解码和触发时序。Claude 负责技能代码、实际判定、AI、注册和 PPU 实机接入。
