# Fizz — 设定图（第 0 步）

## 中文说明（给用户看）
请 Codex 按这份包画**一张高清像素风的菲兹（潮汐海灵）设定图**，和之前的崔丝塔娜、维嘉同一种画风（01、02），出两张：
- **A**：英雄联盟里的待机姿势（参考 03）——两手横握三叉戟，叉头朝右前方，杆尾朝左后方，叉子大约在腰的高度，两脚分开站稳。
- **B**：另一种待机（参考 06）——三叉戟竖着拄在身旁，叉头朝下点地、带鳍的杆尾朝上，一只手扶着杆。

两张都要：面朝右的 3/4 正面（看得到脸和浅色肚皮，**两只大眼睛都要看见**，远处那只窄一点，绝不画背影），约德尔人的大头小身子（头约占身高的 40%），整个人完整在画布里，透明背景，没有光晕、没有地面阴影，**鞋底（脚掌）以下什么都不能有**（游戏里血条在脚下，会挡住；B 的叉头只碰到地面线，不能低于脚掌）。
输出：`outputs/fizz-model-A.png`（1536x1024 横图，横着的三叉戟完整在画内）、`outputs/fizz-model-B.png`（1024x1536 竖图），真透明 PNG。

参考图说明：01、02 只是**画风和比例**参考（之前采用的两个约德尔人设定图），不要照抄他们的角色；03 是 A 的姿势和外形（权威）；04 是脸部（大绿眼睛、黑瞳孔、白高光，嘴是一条细细的弯线）；05 是头的侧面（两片下垂的长耳鳍、橙色内侧）；06 是 B 的姿势；07 侧面；08 背面（头后还垂着两片长鳍、鳍边是橙红色，短尾巴根上有一个小金环）；09 三叉戟特写（翠绿叉头、银色刃边、蓝色宝石、深红缠绳的杆、银色箍、杆尾的绿金色鳍穗）；10 是他 E 技能站在三叉戟顶上的样子（只看三叉戟和身体的比例，不用画这个姿势）。英雄联盟渲染图只做参考，不要照抄 3D 的光影。

## English prompt (for Codex)

Use case: stylized-concept character picture. Create TWO final character illustrations of **Fizz, the Tidal Trickster**
(League of Legends), in his CLASSIC in-game look, as detailed crisp PIXEL ART in exactly the style of the attached
pictures 01-02 (dark stepped pixel contours, 3-5 flat tones per material, crisp highlights, chibi yordle proportions).
References 01-02 are ART STYLE and PROPORTION ONLY: do NOT copy their characters, weapons, backgrounds or glows.
References 03-10 (renders of League's own model) are authoritative for Fizz's body, head, colours and trident; do not
copy their 3D lighting, redraw them as pixel art.

**Picture A** (reference 03, his idle): full body, facing RIGHT in a three-quarter FRONT view, face and pale belly
visible, BOTH big eyes visible (the far eye narrower, peeking past the snout), never a rear view. A small amphibious
yordle standing with his webbed feet apart on the SAME horizontal baseline, knees slightly bent, holding his long
TRIDENT horizontally across his body at waist height with both hands: the trident head points FORWARD to the RIGHT,
the finned butt end points back to the LEFT. The whole trident must fit in the canvas (it is longer than he is tall).
1536x1024 landscape PNG.

**Picture B** (reference 06): the same character, same camera, standing relaxed with the trident held UPRIGHT beside
him in his near hand: the trident head DOWN, its prongs just touching the ground line next to his feet, the shaft
rising past his head with the finned butt end on top. Face and belly visible, both eyes visible. Nothing below the
soles. 1024x1536 portrait PNG.

**Fizz's look (both pictures):**
- Body: slim, smooth, sky-blue/cyan skin with darker blue shading and a few pale-blue spots on the crown; a PALE
  CREAM-YELLOW belly and throat; long thin arms with small three-fingered hands; legs that darken to DEEP NAVY-BLUE
  from the knees down; big flat WEBBED FEET with long splayed toes.
- Head: big and rounded, about 40% of his height (a yordle), with a short rounded snout. Two long blue FIN-EARS hang
  from the top of the head down past his shoulders (like a rabbit's drooping ears), their inner sides and the frills
  at the back of the head bright ORANGE-RED (references 04, 05). Two BIG round eyes set wide on the sides of the head:
  white eyeball, large GREEN iris, black pupil, one white highlight each; heavy blue upper lids give a sly, mischievous
  look. A wide thin curved mouth line in a slight grin, no teeth. No nose, no hair.
- Fins: ORANGE-RED frills line the inner edges of the fin-ears; two more blue fin-lobes hang from the back of his
  head down his back (reference 08); small orange spines at his elbows; a small GOLD ring at the base of his short
  tail.
- The TRIDENT (reference 09): a long staff, about 1.3 times his height. JADE-GREEN trident head with three prongs
  (the middle one longest), pale steel/bone-white blade edges, small glowing BLUE gems where the prongs meet; a
  dark CRIMSON-RED wrapped shaft with a few bright steel bands; at the butt end a fan-shaped tuft of green and gold
  fins.
- Colour accents: cyan-blue body, cream belly, orange fins, crimson shaft, jade + steel trident, small blue gems; the
  green of the eyes is used only by the eyes.

Head large and readable (the later game sprite is a 34-px chibi, so keep the face clean and the shapes bold).
Detailed PIXEL ART, not vector, not soft painting, not smooth 3D; crisp edges, no blur, no gradients, no noisy
texture. REAL transparent background (alpha 0 outside the silhouette), no backdrop colour, no water, no glow, halo
or aura, no ground, no contact or cast shadow, no pedestal, no frame, no text, no labels. Nothing below the soles.
One character per picture, centred, top of the head (fin-ears included) to the soles about 750 px, at least 80 px of
empty transparent margin all round.

Deliver: `outputs/fizz-model-A.png` (1536x1024) and `outputs/fizz-model-B.png` (1024x1536), true RGBA PNGs.
