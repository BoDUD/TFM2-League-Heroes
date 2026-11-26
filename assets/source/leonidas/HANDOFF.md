# 列奥尼达斯 · 美术与音频交接

角色资源 ID 为 `ragnarok_leonidas`。造型采用动画第三季第九回合的黑色战术上衣、白发束、银白胡须、脸部旧疤和蓝迷彩裤。圆盾以钢蓝色呈现，方阵冲锋时换为带 Λ 的红铜真理之盾。

## 图集和锚点

- 角色和独立特效各 8 组，每组 8 帧。逻辑格 256×256，HD 格 512×512，最近邻整数倍 2×。同一分辨率的 `#sheet.png` 和 `#anim.fanim` 配套使用。
- 默认朝右，逻辑脚底锚点 (128, 232)，特效中心 (128, 128)。HD 坐标乘 2，游戏内显示比例由 Claude 通过 PPU 对齐。
- `runtime/props/` 保存常态圆盾、真理之盾和钢链三件独立原图。主图集已合成对应武器。`shield-registration.json` 给出每帧握点、盾中心、角度和投影尺寸，均为右朝向逻辑坐标。水平翻转时对盾、钢链及锚点做同一镜像。倒地第 5～8 帧共用同一个落盾位置。
- `runtime/sprites/ragnarok_leonidas_throw_body_native#sheet.png` 是链盾动作的无武器身体动画，另含 HD 版。若投射距离动态变化，链盾动作加载这组无武器帧，并按实际弹体与手部位置挂接独立盾和钢链。
- 选人立绘 1216×1428，运行选人图 304×405。盾击、链盾、举盾反弹和方阵冲锋图标各 256×256。

## 动作时点

| 动作 | 关键帧 |
| --- | --- |
| `attack` | 第 4 帧盾击，第 5 帧预览命中。实战命中按回调触发。 |
| `skill` | 第 4 帧放出链盾，第 6 帧收链，第 7 帧接回圆盾。 |
| `skill2` | 第 3 帧举盾。预览第 5 帧反弹光箭。实战只在确认可反弹弹体被挡下时播放反射，方向使用实际出射方向。 |
| `ult` | 第 3 帧切换真理之盾，第 4 帧开始方阵冲锋，第 5 帧预览冲击，第 8 帧恢复常态盾。 |
| `dead` | 第 5 帧盾落地，第 7 帧身体接地。 |

`cues.json` 的帧从 1 开始，毫秒数为动作起点到该帧的累计时间。对接阿波罗时，将他的光箭拦截回调接到 `confirmed_reflect`，两人使用同一个实际碰撞点。伤害、位移、反弹条件和 AI 由 Claude 接入。

## 预览和音频

- `review/review.html` 支持播放、逐帧、深浅底、左右朝向、独立和叠加特效与音频试听。
- WAV 与 MP3 均为 44.1 kHz 单声道。白熊寛嗣的日语动画原声来自官方公开片段，部分保留原片背景声。`audio/sources.json` 记录配音演员、来源、剪辑时间及 SHA-256。另做 16 条原创战斗音效。
- 已做素材和浏览器预览校验。Claude 对接游戏注册、PPU、技能和 AI，并进行游戏内验证。

[官方角色与声优](https://ragnarok-official.com/chara/kingleonidas.html) · [盾的设定](https://ragnarok-official.com/chara/geirolul.html) · [方阵与光箭反弹](https://ragnarok-official.com/story/15.html) · [Netflix Japan 对战片段](https://www.youtube.com/watch?v=5xCVIiyC99M)
