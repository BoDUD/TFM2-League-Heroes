# 布隆：跑步改成交叉步（只重画腿，给 Codex 的提示词）

> 用户：「布隆走路没交叉步？」——上次画的 8 帧跑步里，**同一条腿一直在后面、另一条一直在前面**，像往前蹦，两条腿从来没有交替经过对方。这次**只重画腿**，其余都不动。
> - `now/braum_run_<n>.png` 是现在游戏里的这一帧（同一个 6 px 网格、同一个 1536×1024 画布）。**橙线（第 112 行）以上的所有东西——头、身体、两只手臂、毛皮披肩、腰带——逐格照抄，一格都不要改**；**盾也整块照抄不动**（它在腿前面、画面右边）。只重画橙线以下的**两条腿**（大腿、膝盖上的灰白毛皮、小腿、靴子），画在盾的后面。
> - `guide/` 是同一张加了线：橙线 = 腿从这里开始，红线 = 脚底线（第 163 行下边，鞋底踩在上面，跳起的那几帧可以离开 1–3 格），蓝十字 = 站位点。线不要画进图里。
> - **交叉步**照 `refs/caitlyn_run.png`（包里已经通过的凯特琳跑步，8 倍）：两条腿**轮流在前**，每半个循环换一次，中间在身体下面**交错经过**。英雄联盟里布隆的跑步见 `refs/league_run.png`（3D 渲染，只看节奏）。
> - 近侧的腿颜色亮、画在前面；远侧的腿暗一档、画在近侧腿后面（交错时被挡住一部分）。腿的粗细、颜色、膝盖毛皮、靴子都照造型 `design/braum_design.png`，**腿的长度每帧一样**（大腿 + 小腿伸直时从橙线到脚底约 50 格），不要缩短、不要变形。
> - 只用造型的颜色（`design/braum_palette.png`），每格一个纯色，1 格近黑描边，不要抖动、渐变、抗锯齿、半透明；不画特效、不画影子。

## 每帧两条腿的位置

（「前」= 画面右边，他朝右跑。近侧腿 = 画在前面、颜色亮的那条。）

| 帧 | 近侧腿（亮） | 远侧腿（暗） |
|---|---|---|
| 1 | 踩在身体正下方，膝盖微弯（承重） | 从后面往前摆，**正好经过近侧腿后面**（交错），脚离地 2–3 格 |
| 2 | 往后蹬，脚跟抬起 | 摆到前面，膝盖抬起 |
| 3 | 在后面，脚抬起离地 | 往前伸直，脚跟落向前方 |
| 4 | 最靠后，小腿往后踢起（步子最大） | 在前面踩地 |
| 5 | 从后面往前摆，**正好经过远侧腿前面**（交错），脚离地 2–3 格 | 踩在身体正下方，膝盖微弯（承重） |
| 6 | 摆到前面，膝盖抬起 | 往后蹬，脚跟抬起 |
| 7 | 往前伸直，脚跟落向前方 | 在后面，脚抬起离地 |
| 8 | 在前面踩地 | 最靠后，小腿往后踢起（步子最大） |

## 提示词

每帧一次，附图：`now/braum_run_<n>.png`（这一帧）、`design/braum_design.png`（造型）、`refs/caitlyn_run.png`（交叉步）、前一帧你刚交付的那张（第 1 帧不附）。

```text
Image 1 is a finished pixel-art frame of a running character (Braum, a huge bald strongman carrying a big door-like shield on the image right), drawn on a grid of 6x6-pixel squares on a 1536x1024 transparent canvas. Image 2 is the character's design (the same grid). Image 3 is another character's approved run, 8 frames: how the two legs take turns in front and cross under the body.
Redraw ONLY HIS LEGS in Image 1, as frame <n> of an 8-frame running loop facing right: <LEGS>. Copy everything above square row 112 (head, body, arms, fur, belt) and the whole shield square for square, unchanged. The legs: thighs and shins in the design's dark-brown trousers, the grey-white fur below the knees, dark blue-grey boots, exactly as thick and as long as in Image 2 (the same length in every frame), the near leg in full tone and drawn in front, the far leg one shade darker and behind it, both behind the shield. The soles on square row 163 (the planted foot), the lifted foot 2-3 squares above it. The same 6-pixel grid, only Image 2's colours, a 1-square near-black outline, no dithering, no gradients, no anti-aliasing, no semi-transparency, no effects, no shadow, no text, no grid lines. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<LEGS>` 按上表换成英文：

1. `the near leg planted right under the body, knee slightly bent; the far leg swinging forward and passing right behind the near leg, its foot 2-3 squares off the ground`
2. `the near leg pushing back, its heel lifting; the far leg swung to the front, knee raised`
3. `the near leg behind, its foot lifted off the ground; the far leg reaching forward straight, heel coming down ahead`
4. `the widest stride: the near leg farthest back, its shin kicked up behind; the far leg in front, planted`
5. `the far leg planted right under the body, knee slightly bent; the near leg swinging forward and passing right in front of the far leg, its foot 2-3 squares off the ground`
6. `the far leg pushing back, its heel lifting; the near leg swung to the front, knee raised`
7. `the far leg behind, its foot lifted off the ground; the near leg reaching forward straight, heel coming down ahead`
8. `the widest stride: the far leg farthest back, its shin kicked up behind; the near leg in front, planted`

## 交付

`outputs/braum-run-fix/`：`braum_run_1..8.png`（1536×1024、6 px 网格、透明）+ `braum_run_<n>_1x.png`（256×170，逐格一致），`raw/` 原稿，**最后**写 `HANDOFF.md`；打包 `braum_run_fix_done.zip`。交回前检查：橙线以上和盾逐格没变；两条腿每半个循环换一次前后、第 1、5 帧在身体下交错；腿长每帧一样；脚底在红线上。

## Claude 收到后（给 Claude 看）

- 按格子读回 `_1x`，橙线以上和盾用现在的帧逐格贴回（保证没变），只取腿；查腿长、交替、缝（gap-check）、脚底；再走 rig_braum.py；给用户看前后对比 GIF。
