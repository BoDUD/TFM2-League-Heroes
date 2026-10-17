# 凯尔：按游戏原尺寸重画角色图（给 Codex 的提示词）

玩家反映凯尔的模型"太抽象"。现在的角色图是英雄联盟的 3D 模型按游戏尺寸投色、再贴上手画的头：身体是一团金色和灰绿色的碎块，翅膀是几条淡色的线，看不出盔甲、手臂和剑。这次请 Codex 按游戏原尺寸重画全部 63 帧：姿势和位置照现在的每一帧，造型照英雄联盟原版，画法照原版英雄。特效不变（`PROMPTS.md` 那一套），只重画角色。

这和拉克丝、艾希那次按原尺寸重画（[`../NATIVE_REDRAW.md`](../NATIVE_REDRAW.md)）是同一个做法，区别是凯尔的动作帧大（带翅膀、R 把剑举过头顶），每帧一张画布，不画整张格子图。

## 步骤

1. **先只画造型图** `kayle_native.png`（第 1 条提示词），交给用户看。不通过就重画这一张，不带着错的造型往下做。
   **已完成（2026-09-29）**：Codex 第二轮的造型，用户通过。原图 948×1659、像素块宽 14–16 px 不等，Claude 按它自己的边缘逐格取色、整理到游戏网格：`design/kayle_native.png`（512×896，21 色，眼睛 1×2 格深棕加琥珀、红唇 1 格，去掉串色杂点），头顶到脚底 40 格（比现在的 32 格高），脚底放在第 94 行，脸的中心对准现在头部关节的位置。
2. 造型图通过后，**按动作逐个画** 9 个动作、63 帧（第 2 条提示词，每个动作换最后一段）。**现在从这一步开始。**
3. 交回一个文件夹：63 张 `kayle_<动作>_<帧号>.png`（文件名和 `now/` 里的一一对应）、`HANDOFF.md`（做法和自查结果）。
4. Claude 用 `python tools/art/native_frames.py join --hero kayle --src <文件夹>` 把每帧按锚点放回格子，再 `python tools/art/import_native.py --hero kayle` 导入游戏；每一帧站在现在那一帧的位置上，头的轨迹、前冲、死亡倒地都不用重调。

## 压缩包里的附图（`kayle_model_pack.zip`，含英雄联盟模型渲染，只在本地用，不提交）

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/kayle_native.png` | **通过的造型**（整理到游戏网格，8 倍，512×896），`design/kayle_native_12x.png` 是它的 12 倍特写 | 每一帧的颜色、头、盔甲、翅膀、剑都照它 |
| `design/kayle_now_design.png` | 现在游戏里的待机第 1 帧，放大 8 倍，在 64×112 格的画布上 | 造型图的大小和位置 |
| `design/kayle_league_views.png` | 英雄联盟原版凯尔（用户选的造型 C：11 级的脸和白发、最上面一对翅膀、合体的剑），四个角度 | 服装、配色、剑和翅膀的形状 |
| `design/kayle_league_chibi.png` | 同一个模型换成我们的比例（头 3 倍、腿 0.7 倍），放大 8 倍 | 比例 |
| `design/kayle_now_head_12x.png` | 现在的头（用户选的 K5：浅肤色、发光的琥珀色眼睛、红唇、白发），放大 12 倍 | 脸 |
| `style/tfm2_style_ref_*.png`、`style/pack_native_ref.png` | 原版英雄和本包按原尺寸画的英雄（拉克丝、艾希、蕾欧娜、迦娜），上排待机、下排攻击，放大 8 倍 | 画法 |
| `now/kayle_<动作>_<帧号>.png` | 现在游戏里的每一帧，放大 8 倍，每帧一张 512×896 的画布 | 每帧的姿势、大小、位置（在它上面重画） |
| `pose/kayle_<动作>_<帧号>.png` | 同一帧英雄联盟原版的姿势（我们比例的 3D 模型），同一张画布 | 看清哪只手拿剑、剑和翅膀朝哪 |
| `strips/kayle_now_<动作>.png` | 每个动作的全部帧排成一行，放大 4 倍 | 同一动作前后一致 |
| `kayle_frames.json` | 画布 64×112 格、锚点 (32, 86)，每个动作的帧数和每帧时长 | 核对文件 |

## 所有图的规则

- **像素尺寸（最重要）**：角色是游戏里的小精灵，按真正的低分辨率像素画来画，整体放大 8 倍输出：每个像素是一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光。
- **画布**：512×896（64×112 个方块），和 `now/` 里对应的那张一样大；每一帧最低的那一行、横向位置和 `now/` 那张一样。通过的造型比 `now/` 高约 8 格（头顶到脚底 40 格对 32 格），所以头和身体比 `now/` 靠上，这是对的。背景透明，做不到时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号、影子。
- **看得清（这次的重点）**：大块造型、少颜色、1 个方块宽的近黑描边 `#1E1624`、内部深色线越少越好。动作图只用通过的造型那 21 种颜色（见第 2 节的表），每种材质 2–4 个平涂色阶，不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **只画角色**：剑上的火、弹道、光圈、治疗光这些都是单独的特效，不要画进角色图。
- 3/4 正面朝右，看得到脸和胸口，不画背影（死亡最后趴下的两帧除外）。

---

## 1. `kayle_native.png`：造型图

附：`design/kayle_now_design.png`、`design/kayle_league_views.png`、`design/kayle_league_chibi.png`、`design/kayle_now_head_12x.png`、`style/pack_native_ref.png`、`style/tfm2_style_ref_mage.png`

```text
Attached: (1) kayle_now_design.png - our game's current sprite of Kayle at 8x (every game pixel an 8x8 block) on a 512x896 canvas: her size, pose and place are right, but at game size players find her "too abstract": the body is a mush of gold and grey-green specks, the wings a few pale lines, the arms, the armour and the sword do not read. (2) kayle_league_views.png - Kayle from League of Legends (the look we use: her level-11 form with the face and white hair showing, only the upper pair of wings, the one-piece sword), four angles: her costume, colours and shapes. (3) kayle_league_chibi.png - the same 3D model in our chibi proportions at 8x. (4) kayle_now_head_12x.png - her approved face at 12x. (5) pack_native_ref.png and tfm2_style_ref_mage.png - heroes of the game Teamfight Manager 2 drawn at their real pixel size, at 8x: the pixel size and the cleanliness to match.

Task: redraw image (1) as clean hand-made pixel art at EXACTLY the same pixel size and place: a chibi Kayle about 32 squares from the top of her hair to her soles (the wings above that), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow. Output 512x896, transparent background (if impossible: solid #FF00FF), no grid, text, border or shadow.

Kayle (League of Legends, default skin, level-11 look), chibi, 3/4 FRONT view facing right, floating in the air, calm:
- Head about one third of her height (without the wings). Face as in image (4): fair warm skin, glowing amber-gold eyes (each about 2x2 squares: a dark lid square on top, amber below, a pale-gold highlight), a 1-square red mouth, a small pointed ear. White hair with a pale icy-cyan tint, swept up and back like a white flame (3-4 flat shades, a few big highlight squares), a few long strands falling behind her shoulders.
- Gold armour, clearly separate plates: a golden breastplate with a light-gold highlight on top; big angular golden pauldrons (2-3 squares tall) on both shoulders; golden bracers on the forearms and golden gauntlet hands; big curved golden plates on the hips (like a split skirt); golden knee guards and golden boot tips. Gold in 4-5 flat shades from dark bronze to pale gold.
- Under the gold: a light sage grey-green bodysuit on the arms, the waist and the legs (3 shades). Arms and legs must read as limbs: at least 2 squares thick, outlined.
- One pair of large wings from her upper back, rising behind her shoulders and head: 3-4 big feather tiers, lilac-purple at the root shading to pale blue and ice-cyan at the tips, each tier a flat shape with a 1-square outline; the wings stay BEHIND her body and head and never cover her face or chest.
- The sword in her right hand (the hand toward the right side of the image), pointing down diagonally to the lower right as in image (1): a long straight crystal blade in glowing teal-cyan (2 squares wide near the guard, 1 at the tip, 3-4 shades from dark teal to near-white), a golden star-shaped guard (3x3 squares).
Pixel rules: at most 32 colours in total; every material 2-5 flat shades; big solid areas; no dithering, gradients or noise, no lone square of a different colour inside an area; a 1-square near-black outline (#1E1624) around the whole silhouette and around the wings and the sword, very few inner dark lines. Keep only details that read at this size.
Size and place: exactly as in image (1) - the same height, her lowest pixel on the same row, her head in the same place, the sword ending where it ends there.
Before finishing, check: every square is 8x8 on one grid; at most 32 colours; both eyes and the red mouth clearly visible; breastplate, pauldrons, arms, hip plates and legs each readable as separate shapes; the wings do not hide her body; the sword is one clean straight blade with a gold guard.
```

## 2. 动作图（每个动作一次，63 帧）

每个动作附：`design/kayle_native.png`（通过的造型）、这个动作 `now/` 里的全部帧、`pose/` 里的全部帧、`strips/kayle_now_<动作>.png`。提示词前面一段通用，最后的 `ANIMATION:` 一段按下表换。

通过的造型只用这 21 种颜色（每一帧都只能用它们）：

| 部位 | 颜色 |
|---|---|
| 描边 | `#1E1624` |
| 白发（亮、中、暗） | `#F6F8FA` `#E4EDF3` `#ADBAC7` |
| 皮肤（亮、耳朵和暗部） | `#FBDCC4` `#F2B48E` |
| 眼睛（上格深棕、下格琥珀）、嘴 | `#5A2E08` `#E28A08`、`#D0203A` |
| 金甲（亮到暗） | `#FBD764` `#F2BE4C` `#D99A34` `#A86E23` |
| 灰绿内衬（亮、暗） | `#CED3BC` `#A3AA97` |
| 翅膀（冰蓝、浅蓝、长春花蓝、淡紫） | `#B6E8F5` `#96B4F9` `#8C90E0` `#B296F5` |
| 剑（亮、暗） | `#6DF9F1` `#43E6DE` |

```text
Attached: (A) design/kayle_native.png - the APPROVED design of Kayle at 8x (every game pixel an 8x8 block) on a 512x896 canvas: copy her colours (exactly the 21 listed below, no others), her head and face, her gold plates, sage limbs, wings and teal sword, and her pixel style exactly. She is about 40 squares from the top of her hair to her soles. (B) now/kayle_<anim>_<NN>.png - our current in-game frames of this animation at 8x, one 512x896 canvas per frame: take from each frame its POSE, its lowest row and its horizontal place, NOT its size or its muddy pixels - (B) is only 32 squares tall, so draw her at the size of (A), taller than (B) by about 8 squares, standing on the same lowest row. (C) pose/kayle_<anim>_<NN>.png - League of Legends' own pose for the same frames (the 3D model, same canvas): use it to understand the pose - which hand holds the sword, where the blade, the arms, the legs and the wings point. (D) strips/kayle_now_<anim>.png - all frames of the animation side by side.

Task: redraw every frame of (B) as clean pixel art of the character in (A), one output per frame, same file name as the frame in (B) (kayle_<anim>_<NN>.png), 512x896, at EXACTLY the same pixel size as (A): every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur. Transparent background (if impossible: solid #FF00FF). No grid, text, border or shadow.
Colours: ONLY these 21 - outline #1E1624; hair #F6F8FA #E4EDF3 #ADBAC7; skin #FBDCC4 #F2B48E; eyes #5A2E08 (upper square) #E28A08 (lower square); mouth #D0203A; gold #FBD764 #F2BE4C #D99A34 #A86E23; sage #CED3BC #A3AA97; wings #B6E8F5 #96B4F9 #8C90E0 #B296F5; sword #6DF9F1 #43E6DE. Big flat areas; no dithering, no noise, no lone odd square; a 1-square #1E1624 outline around her, the wings and the sword.
Head: paste the head of (A) - white flame hair, each eye 1 square wide and 2 tall (dark brown over amber), the 1-square red mouth - unchanged in every frame, turned only where the pose turns it (lying on the ground). Keep the gold pauldrons, breastplate, bracers, hip plates and boots, the sage arms and legs (2 squares thick), the two-tier wings and the straight teal sword as readable separate shapes in every frame. 3/4 FRONT view facing right, never her back (except where the frame in (B) lies face down). Do not draw effects (fire, projectiles, glows, halos) - only Kayle.
Place: on every canvas her lowest row is the lowest row of the matching (B) frame, her body and head over the same columns, the sword and the wings reaching the same way; frames that are the same drawing in (B) stay the same drawing.
Before finishing each animation, check: all squares 8x8 on one grid, only the 21 colours, the head identical in every frame, every frame's lowest row equal to its (B) frame's.
ANIMATION: <from the table>
```

| 动作 | 帧数 × 时长 | `ANIMATION:` 这一段 |
|---|---|---|
| `idle` | 6 × 200 ms | `IDLE, 6 frames: all 6 frames are exactly (A) itself, unchanged (the game adds the breathing).` |
| `run` | 16 × 267 ms | `MOVE, 16 frames, one loop of League's glide: she flies forward leaning into the move, legs trailing behind; the wings beat - folded up in some frames, spread back and level in others, exactly as in (B)/(C); the sword trails BEHIND her, pointing down and back to the lower left (never in front of her); her height rises and falls exactly as in (B). Keep the loop smooth: frame 16 flows into frame 1.` |
| `attack` | 6 × 50–77 ms | `RANGED ATTACK, 6 frames: the sword swings back behind her to the lower left (frames 2-3), then she slashes forward to the right while the wings sweep back (4-5), and settles (6). The fireball it throws is a separate effect.` |
| `attack_melee` | 6 × 50–77 ms | `MELEE ATTACK, 6 frames: a straight thrust forward to the right, the blade level (frame 1); she gathers upright (2-3); a low lunging cut forward, the blade level again (4); the wings spread as she settles (5-6).` |
| `skill` | 6 × 60–80 ms | `RADIANT BLAST, 6 frames: she leans back with her arm drawn in and the wings swept back low (frames 1-3), then straightens up (4-6). The celestial sword she launches is a separate effect; her own sword stays as in (B).` |
| `skill2` | 6 × 50–90 ms | `STARFIRE SPELLBLADE, 6 frames: the sword drawn back behind her to the left (frames 2-3), then swept forward and down to the lower right in a long arc, the blade reaching far out as in (B), the wings raised (4-6).` |
| `ult` | 8 × 70–120 ms | `DIVINE JUDGMENT, 8 frames: the wings spread (frames 1-2); she gathers (3) and raises the sword straight up above her head (4-5); in frame 6 she has thrown it: the sword flies high above her head, apart from her hand, exactly where it is in (B); in frame 7 she has no sword, arms spread, one hand raised; in frame 8 the sword is back in her hand as she returns toward idle.` |
| `hit` | 2 × 120 ms | `HIT, 2 frames: 1 she flinches from a blow, upper body jolted back, eyes squeezed shut (two short dark lines); 2 recovering toward idle.` |
| `dead` | 7 × 100–500 ms | `DEATH, 7 frames: struck (the sword still in hand in frame 1), knocked back, kneeling, rising a little, falling forward, then lying face down on the ground (frames 6-7, her head turned sideways). The sword has left her hand from frame 2 on and is not drawn; the wings fold and lie flat behind her as in (B).` |

## 自查（交回前每条都要过）

- 63 个文件都在：`kayle_idle_01..06`、`kayle_run_01..16`、`kayle_attack_01..06`、`kayle_attack_melee_01..06`、`kayle_skill_01..06`、`kayle_skill2_01..06`、`kayle_ult_01..08`、`kayle_hit_01..02`、`kayle_dead_01..07`，每张 512×896。
- 每个 8×8 方块只有一种颜色，透明度只有全透明和不透明（或品红背景）。
- 只用上表的 21 种颜色。
- 每一帧最低的那一行和 `now/` 里同名那张一样（±1 格），横向位置对得上；待机 6 帧就是造型图本身。
- 每一帧的头都是造型图那个头；剑是一条干净的直刃，移动时在身后。

## 导入（已完成）

Codex 交回 63 帧（交接说明在 [`codex_model/`](codex_model/)）：待机 6 帧是造型图本身，另外 57 帧是生图原稿（948×1659、半透明边缘、每张两三万种颜色、像素块 11–16 px 宽且各帧不同，头和位置每帧不一样），它自己说明还没有规整。Claude 用 [`tools/art/tidy_kayle.py`](../../../tools/art/tidy_kayle.py) 整理：

1. 每个游戏像素取原稿里它中心的颜色，映射到 21 色（整格合并会在块宽对不上时重复出一列描边）。
2. 受击和倒地以外的 48 帧擦掉画的头，贴上造型图的头：两只眼睛对上画的眼睛，找不到时按头顶和脸的位置。每帧同一张脸，循环时头不"沸腾"。
3. 琥珀色只留在眼睛上；竖直方向按身体最低一行对齐原来那一帧（移动恢复原版的上下浮动）；横向保持 Codex 画的位置，待机和移动在导入时按眼睛对齐（`import_native.py` 的 `EYES`）。
4. 清掉孤立的杂点。

```bash
python tools/art/tidy_kayle.py <Codex 的交付文件夹> --out <文件夹>
python tools/art/native_frames.py join --hero kayle --src <文件夹>
python tools/art/import_native.py --hero kayle
```

每帧对齐用的目标（原来那一帧的身体最低行）第一次运行时从被替换的动作条量出，存在 `codex_model/kayle_targets.json`，之后重跑读它。结果：21 色，和右边像素同色的比例 37%，头像截取点 (−2, −40)。
