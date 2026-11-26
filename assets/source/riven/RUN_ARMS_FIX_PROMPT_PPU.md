# 锐雯跑步：只改两只手臂（给 Codex 的提示词）

> 用户看了上一版：「锐雯拿剑的姿势有点怪 联盟里不是这样拿的吧」。

> **上一版的问题**（`refs/grip_right_vs_wrong.png`）：
> - 上一版把**前面那只手**（近侧）整条胳膊伸直，像拿着长枪往前戳。
> - 英雄联盟里是**后面那只手**（远侧）握剑：手肘弯着，**拳头收在下巴下面、锁骨前**，剑身从下巴底下往前平伸。前面那只手空着，跟着跑步前后摆。
> - 上一版把后面那只手画成在肩膀后面甩，没照模板上的蓝圈。

> 这次**只改两只手臂**：腿、身体、头、头发、肩甲、衣服、位置、大小都照上一版（`refs/previous_run_<k>.png`）一格不动。
> 交付格式和上次一样：`outputs/riven-run/run_1.png`、`run_2.png`、`run_3.png`，1536×1024，三格，同样的位置。

## 每帧的两只手

- **后面那只手（远侧，握剑的手）**
  - 每一帧都在胸前，**握紧的拳头正好在模板的蓝色小圆圈里**（就在下巴下面、锁骨前），拳头握的方向顺着红线（朝前）。
  - 手肘弯着、贴着身体，手臂大部分被身体挡住，只露出拳头和一点前臂。
  - 8 帧都一样稳，跑步时只跟着身体上下动。
- **前面那只手（近侧，空手）**
  - 握成空拳，像跑步一样前后摆，照 `refs/league_run_<k>.png` 同一帧的近侧手臂。
  - **不要伸直举在前面，不要拿任何东西。**
- **剑还是不要画**：只画握剑的空拳，我们之后按红线把剑贴上去。

## 附图（`riven_run_fix_pack.zip`）

| 文件 | 用在 |
|---|---|
| `refs/previous_run_<k>.png` | **第一张**：上一版（只改手臂，其余照它） |
| `templates/run_<k>.png` | **第二张**：蓝圈 = 后手拳头的位置，红线 = 剑的方向 |
| `refs/league_run_<k>.png` | **第三张**：英雄联盟同一帧（看两只手） |
| `refs/grip_right_vs_wrong.png` | **第四张**：对和错的对照 |
| `refs/design_no_sword.png`、`refs/design_palette.png` | 人物和颜色（和上次一样） |

## 提示词（每张模板一次，<k> = 1、2、3）

附图顺序：`refs/previous_run_<k>.png`、`templates/run_<k>.png`、`refs/league_run_<k>.png`、`refs/grip_right_vs_wrong.png`。

```text
Four attached images. Image 1 is YOUR PREVIOUS pixel-art sheet of this character's run (frames in three 512x1024 cells): keep EVERYTHING in it exactly - legs, body, head, hair, shoulder plate, clothes, colours, positions, sizes - and redraw ONLY HER TWO ARMS in every cell. Image 2 is the template of the same frames: the small BLUE circle marks where her FAR hand (the arm on the far side of her body) must be, and the RED line is the way the sword will point from it. Image 3 is the same frames from the game's 3D animation. Image 4 shows the problem: RIGHT (top) - in the game she grips the sword with her FAR hand, the elbow bent tight against her body and the CLOSED FIST tucked right under her chin at her collarbone, the blade sticking out forward; WRONG (bottom) - the last result held her NEAR arm straight out in front.
Redraw the arms so that in EVERY frame: her FAR arm is bent with its closed fist inside the blue circle under her chin, gripping along the red line (mostly hidden behind her body, only the fist and a bit of forearm showing); her NEAR arm is a runner's arm swinging forward and back as in image 3, with an empty closed fist, never held straight out, holding nothing. DO NOT DRAW THE SWORD - no blade, no hilt, only the empty fist.
Same rules as before: the SAME 8-px pixel grid and near-black outline as image 1, image 1's colours only, the arms the same length and thickness as in image 1 (bent, never stretched), a genuine transparent background (or flat pure white), no effects, no shadow, no text, no template marks. Output one 1536x1024 sheet with the same three-cell layout.
```
