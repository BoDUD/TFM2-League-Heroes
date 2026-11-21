# 亚当素材交接

英雄资源 ID 为 `ragnarok_adam`。本次交付包含角色、四张技能图标、选人立绘、独立特效和日语音频。打开 `preview.html` 可以逐帧查看，切换深浅背景、镜像方向，并查看施放与命中的分层效果。

本地交付包为 `D:/TFM2-Workshop/adam_packs/outputs/adam_assets.zip`。和吕布、索尔一样，音频二进制随本地包交付。Git 分支包含美术、音频清单、生成脚本和试听界面。完整包里有 7 段日语语音和 16 条原创 Foley，各自附单声道 44.1 kHz PCM16 WAV 和运行用 MP3。

## 设定与技能

- 第二回合人类代表。造型取浅金乱发、向上弯的呆毛、蓝眼、绿色叶片腰饰和赤足。原作神器是女武神雷金蕾芙变成的右手指虎。 [人物设定](https://ragnarok-official.com/1st/character/)、[第 6 话](https://ragnarok-official.com/1st/story/ep06/)
- 神虚视读取和模仿神的动作。动画里亚当闪过宙斯的攻击并复刻反击，也复刻了「超越时间之拳」。 [第 6 话](https://ragnarok-official.com/1st/story/ep06/)、[第 7 话](https://ragnarok-official.com/1st/story/ep07/)
- 原作有持续使用后的失明和保护孩子的决意。可以把眼部负荷用于安排能力的发动间隔。 [第 8 话](https://ragnarok-official.com/1st/story/ep08/)

下面是游戏接入提案，数值、状态、判定、AI 与测试由 Claude 落地。

| 用法 | 动作和表现 |
| --- | --- |
| 普攻 | `attack`。拳风在出拳时播，命中回调独立播火花及音效。 |
| 神虚视 | `skill`。眼部亮点提示能力已启动，读到符合条件的攻击时进入闪避。 |
| 模仿反击 | `skill2`。读取到招式后显示镜像标记，用亚当自己的反击动画和近战判定。限制可模仿的招式类别，消费一次记录。 |
| 超越时间之拳 | `ult`。固定朝向蓄势、瞬发反击、恢复。蓄势和释放有独立特效，时间感由视觉与音效表达。 |

## 素材坐标

| 文件位置 | 内容 |
| --- | --- |
| `runtime/sprites/ragnarok_adam_native#sheet.png` 与 `#anim.fanim` | 8 个动作各 8 帧，128×128 逻辑格，向右。 `idle`、`run` 循环。 |
| `runtime/sprites/ragnarok_adam_fx_native#sheet.png` 与 `#anim.fanim` | 8 组独立特效各 8 帧。拳风、普攻命中、神虚视、闪避气流、模仿标记、反击命中、时间蓄势、时间释放。 |
| 同目录无 `_native` 的对应文件 | 精确 4 倍最近邻，512×512 每格。完整画面采样比例和玩法碰撞互相独立。 |
| `runtime/icons/` | 四张 256×256 图标。常规三个技能位映射到 `skill`、`skill2`、`ult`，`passive` 可供被动说明使用。 |
| `runtime/banpick_illustrations/ragnarok_adam.png` | 304×405 RGBA，头部 48 行透明。完整 1216×1428 立绘在 `art/illustration/`。 |
| `cues.json` | 逻辑格锚点、开始时间、特效与音效绑定。命中条目由确认命中的事件触发。 |
| `art_manifest.json` | 帧行、时长、坐标和源图 SHA-256。 |

角色脚底锚为 `(64,116)`，特效中心为 `(64,64)`。4 倍版锚点随格子乘 4。瞄准拳点或目标时，从脚底锚换算相对坐标。左侧角色的左右朝向与右侧角色保持对称，查看 `tools/art/import_lubu.py` 对非自动镜像特效的处理。可随角色翻转的定向出拳、闪避和时间释放适合按符号偏移或按现有导入法烘到相应的动作层。接触火花由目标坐标触发。

128 格图站立约 54 像素，按现有索尔 1.65 PPU 约为游戏 33 像素。接入时用现有 `tools/art/ragnarok_art.py` 和 `tools/art/ppu_hd.py` 管线验证 1 倍、`hd_` 和 `lo_`。本包的 4 倍图用于无损交付与预览。实机中用同一脚底坐标、相同世界高度检查各档画质，另外验证红蓝朝向、UI、回放和触发时序。

## 日语与音效

齐藤壮马为动画亚当配音。六段取自亚当的官方倒计时视频，一段来自第二回合官方 PV，后者保留背景音乐。切点、建议播放事件和源文件 SHA-256 在 `audio/voice_cuts.json` 和 `audio/manifest.json`。出拳嗖声与命中效果独立，普攻有三组变化。受击和倒地使用 Foley。 [官方倒计时](https://ragnarok-official.com/1st/news/127/)、[亚当倒计时原帖](https://twitter.com/ragnarok_PR/status/1404272382970368003)、[对决 PV 发布页](https://ragnarok-official.com/1st/news/185/)

解压后用 `python assets/source/adam/tools/seed_audio.py <解压后素材根目录>` 从完整本地包安装 MP3。脚本会先核对全部 MP3 的 SHA-256，再复制到仓库已忽略的 `ragnarok/sound/sfx/`。建议语音接在选人、入场、低频挑衅和大招蓄势，将长台词放在人声通道并设置间隔。

## 校验与重建

日常核对美术用 `python assets/source/adam/tools/verify_pack.py --art-only`，含本地 WAV/MP3 时去掉 `--art-only`。重建用 `tools/build_art.py` 和 `tools/build_audio.py <官方倒计时媒体> <对决 PV 媒体>`。在素材根目录使用这些相对路径。依赖 Pillow、NumPy、SciPy，音频另用 SoundFile 和 imageio-ffmpeg。

交付核对覆盖帧边界、逐帧差异、二值透明度、4 倍像素一致性、图标和立绘尺寸、音频解码、触发时序及打包文件完整性。当前为素材级验证，技能与 PPU 尚待实机接入和验证。

## 接入（Claude，2026-11-21）

- `tools/art/import_adam.py` 从 `runtime/sprites/ragnarok_adam_native` 和 `ragnarok_adam_fx_native` 出 1 倍帧和高清帧（PPU 1.65，和索尔一样，头顶 33 个游戏像素）。拳风、睁眼的光、闪避气流、模仿标记、反击火花、时间之拳的蓄势和释放按 `cues.json` 画进他自己的帧，跟着他左右翻；睁眼的光和模仿标记逐帧跟着头和身子挪。普攻的命中火花放在目标身上。
- 技能数据 `tools/kit/build_adam.py`，文本和音效 `tools/kit/setup_adam.py`，配音代码 `addons/ragnarok/src/adam.rs`。
- 音频：`python tools/kit/seed_adam_audio.py`（默认从 `D:/TFM2-Workshop/adam_packs/outputs/adam_assets` 拷，先核对 SHA-256）。用到 12 条音效（普攻只用第一组）和全部七句配音。
- 选人立绘 `ragnarok/banpick_illustrations/ragnarok_adam.png` 是 `tools/art/bp_illustrations.py` 从 `art/illustration/` 的原图裁的，和 `runtime/banpick_illustrations/` 那张逐像素一样。技能图标用 `runtime/icons/` 的 skill / skill2 / ult；被动图标不装，游戏只有三个技能图标位。
