# 阿卡丽（Akali）重做 · 原画提示词包 · 第 0 步

**给用户（中文说明）**：阿卡丽重做，照崔丝塔娜的流程，先画原画，再画游戏尺寸的精灵图。上一版丑在两处：
1. 原画是写实比例，头只占身高约 1/7，缩到 40 格后脸就没了，面罩又挡住下半张脸，只剩两个小点；
2. 全身深黑、深绿，和游戏里橄榄绿的地面糊在一起（`00_problem_lineup.png` 最左边就是她）。

这次的原画直接按游戏尺寸设计：
- **Q 版比例**：头约占身高 1/3，眼睛大而清楚；
- **颜色和服装照英雄联盟的游戏内模型**（`05`–`09`）：亮黄绿的发带和镶边、肩膀和手臂上大片淡紫色纹身、腰间红棕色的大腰包配粗绳，这些亮色让她在地面上跳出来；旧原画把这些都画成了深绿和黑，这次不要。深色的头发和裤子都要有亮边。

请把整个 zip 交给 Codex。它按下面的英文提示词画两张原画，同一个姿势（英雄联盟的待机），只是镜头角度不同：
- A = 3/4 正面，脸最清楚；
- B = 转向侧面一些，两只眼睛仍然看得见，两把武器的轮廓更开。

你挑一张，我再按它写游戏尺寸（约 40 行，马尾算在内）的造型包（第 1 步）。
Codex 交付：`outputs/akali-model-A.png`、`outputs/akali-model-B.png`（1024x1536 竖图，透明背景）。

附图：
- `00_problem_lineup.png`：现在游戏里的阿卡丽（最左），和其他英雄一起站在竞技场地面上，4 倍。这是**要改掉的样子**：太暗、和地面糊在一起、脸太小。
- `00_old_akali.png`：上一版原画，**不要照它**：比例写实、配色太暗，服装也和英雄联盟模型不一样（这次服装和配色都以 `05`–`09` 为准）。
- `01_style_vayne.png`、`02_style_nami.png`、`03_style_veigar.png`、`04_style_tristana.png`：你认可过的原画，只当**画风**参照。
- `05_league_front.png`：英雄联盟经典皮肤的游戏内模型，待机姿势，3/4 正面朝右，就是原画 A 的角度和姿势。
- `06_league_head.png`：头部特写（马尾、发带、面罩、眼睛）。
- `07_league_pose_B.png`：同一个待机姿势转向侧面一些，就是原画 B 的角度。
- `08_league_side.png`：接近侧面，看马尾、镰刀和绑腿的轮廓。
- `09_league_back.png`：背面，看马尾、发带和上衣的背面。
- `10_league_splash.png`（如果有）：加载画面原画，只参照脸和气质（冷静、锐利），服装配色以游戏内模型为准。

---

## Prompt (English, for Codex image generation)

Draw **Akali, the Rogue Assassin** from League of Legends, in her **classic in-game model** (`05_league_front.png`),
as a full-body character picture for a pixel-art game. Make two pictures, A and B: **the same pose, the same costume,
only the camera angle differs.**

**Why this picture is being redone** - `00_problem_lineup.png` shows her current game sprite (far left) next to other
heroes on the game's olive-green ground: her realistic proportions left the head tiny, the mask hid the lower face,
and her near-black and dark olive-green body melted into the ground. `00_old_akali.png` is that old picture: do NOT
copy it - its proportions, its dark palette and its costume details are all replaced by the League model `05`-`09`.

**Style** - copy the attached pictures `01_style_vayne.png`, `02_style_nami.png`, `03_style_veigar.png` and
`04_style_tristana.png`: a detailed pixel-art illustration, a crisp dark outline around every shape, 3-5 flat shades per
material, bright highlights on metal and on the edges of dark areas, no blur, no soft gradients, no noise, no text, no
frame.

**View** - full body, **facing RIGHT**: we see her face and chest, never her back. She stands on one flat ground line
with both feet down. **Nothing below the soles**: no shadow, no ground, no base.

**Canvas** - **1024 x 1536 px (portrait)**, **transparent background**, the figure centred, about **1150 px from the
tip of the ponytail to the soles**; both blades inside the canvas.

**Proportions (most important)** - this picture will be redrawn at game size, about **40 pixels tall including the
ponytail**, so design it for that size with big clear shapes:
- a **chibi-leaning game figure**: the head (crown to chin) about **one third** of her height from the crown to the
  soles; a slim, short body; legs apart in a ready stance, knees slightly bent;
- the **spiky ponytail** tied high with a band: big and readable, but rising only about **one fifth** of her height
  above the crown and sweeping back (left);
- **the eyes carry the face** (the mask covers the nose and mouth): two **big almond eyes**, each with a clear white,
  a warm **hazel-brown iris** and a white highlight, dark upswept lashes; both eyes visible, the same shape and on the
  same line; strong dark brows; side locks frame the face but never cover the eyes.

**Colours - the League model's, which read on an olive-green ground** (`05`-`09`):
- **bright LIME / yellow-green**: the big hair ribbon, the trims of the mask and the top, the wrist wraps, small tassels;
- **deep TEAL-green** (blue-green, clearly bluer and darker than the ground) with a lighter teal edge: the mask, the
  sleeveless top, the loincloth panels, the shin wraps;
- **light LILAC / lavender** swirling tattoos covering her shoulders and arms (big bold swirls - a key bright shape);
- a big **RED-BROWN leather satchel** at her near hip tied with a thick tan **rope** - a key warm shape;
- **navy-black hair with strong blue highlights** and a lit rim along the top of the ponytail;
- **dark teal-black baggy trousers with a lit edge** on every fold (never a flat black shape);
- warm **tan skin** with bright highlights; black shoes with a lit edge;
- **steel blades with a green-tinted edge** and white highlights.
Black is only for the outline, the pupils and the lashes; every dark area shows its shape with lighter edges.

**Costume** (from `05`-`09`): a high spiky navy-black ponytail tied with a big bright lime ribbon, long side locks
framing the face; a teal cloth mask with a lime trim over the nose and mouth; a teal sleeveless wrap top with lime
edges, open at the sides; lilac swirl tattoos over both shoulders and arms (a few big bold shapes, not fine lines);
dark gloves with lime wrist wraps; the red-brown satchel on a thick rope at the near hip with a small lime tassel;
teal loincloth panels front and back with lime edges; baggy dark teal-black trousers; teal-green shin wraps; black
shoes.
**Weapons**: a steel **kunai** in her near hand (image left), held low and pointing forward-down; a steel **kama**
(sickle) with a dark wrapped handle in her far hand (image right), its curved blade out to the right. Each blade a big
clear shape.

**Picture A - League's idle, 3/4 front** (`05_league_front.png`): her face and chest turned toward the viewer about
as in `05`, both blades clear of the body.

**Picture B - the same idle, turned more to the side** (`07_league_pose_B.png`): the same pose and colours, the camera
a little further round to her front-right side; her face still in 3/4 view with **both eyes visible** (the far eye a
little narrower); the ponytail sweeping back to the left.

**Checks before you deliver**: facing right; the head about a third of her height, both big eyes visible and not
covered; the jade clearly different from an olive-green ground; no flat black areas; nothing below the soles;
transparent background; the silhouette (ponytail, head, the two blades) readable when the picture is shrunk to 40 px
tall.

Deliver: `outputs/akali-model-A.png` and `outputs/akali-model-B.png` (1024 x 1536, RGBA, transparent).
