# 蔚：新造型（第 2 版，照 oppi 的做法；给 Codex 的提示词）

> **为什么重画**：用户看了现在的蔚（A40：正面站、拳套垂在两边）说：「头不连接身体」「死亡的时候大规模模型丢失」「身体看起来很奇怪」，要求参考隔壁 oppi 模组（LoL Reborn）的蔚的做法重画。见 `ours_now/ours_vs_oppi.png`：
> - 红框：我们的头像浮在一条细围巾上，下巴两边是空的，看着头和身体是分开的；
> - 橙框：身体上满是零散的金色碎点，看不出是什么材质。
>
> **`ref_structure/oppi_vi_structure.png` 只看结构，不许照着描、不许复制像素**（那是 oppi 团队的作品，我们要画我们自己的蔚）。要学的是这几点：
> 1. **3/4 侧面朝右**，**拳击架势**：近处（画面左边）的大拳套横在胸前像一块盾，远处的拳头举在脸颊旁边；两脚分开踩稳，膝盖微弯。
> 2. **头和身体连成一体**：头发往下盖住后颈、披到肩上，下巴直接接在衣领/肩甲上，**没有空隙**。
> 3. **身体干净**：大块的深色衣服 + 钢色肩甲 + 腰带，每种材质 4–5 个色阶、一道深色外描边，**不要零散的金色碎点**（金色只用在拳套外壳和少数镶边）。
> 4. 这一版只画待机造型；之后的所有动作都会从这个架势出发（死亡是蹲跪下去缩成一团，不会散架）。
>
> **服装和配色照我们自己的 `picture/vi-model-A.png`**（这张就是我们之前生成的拳击架势图）：粉色短发、护目镜推在头上、蓝眼睛、红围巾、钢蓝胸甲、深蓝紫腿甲和黑靴、两只巨大的海克斯拳套（金色外壳、仪表盘、钢灰指节、蓝水晶）。脸用我们的：蓝眼睛、粉发，见 `ours_now/` 里的头。

## 要交的东西

放在 **`outputs/vi-model-v2/`**：
- `vi_design_A.png`、`vi_design_B.png`、`vi_design_C.png`：三个可选造型，每张 **1024×1024、8 倍（每个方块 8×8 px）**，人站在画布中间偏下（脚底在第 99 行方块、站位点在第 64 列），透明背景；
- `logical/vi_design_<A|B|C>_1x.png`（128×128，1 像素 1 格）；`HANDOFF.md`（每张怎么画的、方块大小、人多高）。
- 三张的差别：A 最贴近 `picture/vi-model-A.png` 的架势；B 头小一点、身体比例更接近 oppi 的；C 拳套更大、架势更低（更像英雄联盟的待机）。

## 规则

- **尺寸**：人从头发顶到鞋底 **38–40 格高**，宽度随架势（oppi 的是 35 格宽 37 格高）。
- **做法**：生图直接出大方块像素画（方块大小不限，生图给多大就多大），然后按方块读回 1 格 1 像素，读回后人 38–40 格高、读回的图和生图一样干净就合格；不合格就重新生成。**不许把细节比方块还小的大图压缩下来**（会变成金色碎点），也**不要用代码一块一块拼**（上一版就是代码画的，身体像方块机器人）。
- 一道深色外描边（`#2C1E3F` 或 `#1F1E2F`），里面用材质自己的暗色；不要半透明；不要抗锯齿。
- 颜色：沿用 `palette/vi_palette_a40.png` 的 32 色为主，可以再加同色系的过渡色（总数 60 以内）。眼睛的蓝只在眼睛里，水晶用饱和蓝。
- 头约占身高的 1/3（我们一贯的 Q 版比例），眼睛在小尺寸下看得清。

## 提示词（生图用）

```text
Pixel art game sprite of Vi from League of Legends for a small tactics game, ONE character, full body, 3/4 view facing
right, in a boxer's guard: the near huge hextech gauntlet held across the chest like a shield, the far gauntlet raised
beside the cheek; feet planted wide, knees slightly bent. Chunky square pixels on a strict grid, the standing figure
about 40 squares tall, hard edges, no anti-aliasing, one dark outline, 4-5 shades per material, a clean dark body:
steel-blue breastplate, dark navy-violet leg armour, black boots, steel shoulder plates, a brown belt; gold only on the
gauntlet housings (with a gauge dial, steel-grey knuckle blocks and a glowing blue crystal on each). Short hot-pink
hair with dark goggles pushed up, falling over the back of the neck onto the shoulders - the head sits right on the
collar and shoulders with no gap; a fair face with blue eyes; a red scarf at the collar. Costume and colours as the
FIRST image. Transparent background (else pure green #00FF00, never magenta). No text, no grid lines, no border.
```
附图顺序：`picture/vi-model-A.png`（服装、配色、架势）、`ref_structure/oppi_vi_structure.png`（只看结构：比例、头和肩怎么连、身体怎么干净）。
