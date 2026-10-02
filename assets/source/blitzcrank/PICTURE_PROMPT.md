# Blitzcrank — 设定图（第 0 步）

## 中文说明（给用户看）
请 Codex 按这份包画**一张高清像素风的布里茨（蒸汽机器人）设定图**，和之前的贾克斯、维嘉同一种画风（01、02 只看画风和金属的画法），出两张：
- **A**：英雄联盟里的待机姿势（参考 03）——两条巨大的手臂垂在身体两侧，大拳头垂到膝盖高度（近处那只略靠前），身子略微前倾，两只大扁脚分开踩稳。
- **B**：备战姿势（参考 06）——两条手臂弯起，两只大拳头举在胸前，像拳击手准备出拳。

两张都要：面朝右的 3/4 正面（看得到胸口的大圆形炉门和两只发光的圆眼睛，绝不画背影），整个人完整在画布里，透明背景，没有光晕、没有烟雾、没有地面阴影，**脚底以下什么都不能有**（游戏里血条在脚下，会挡住；垂下的拳头也不能低于脚底线）。
头（金色的圆顶小脑袋）比英雄联盟里**大约 1.5 倍**，让两只眼睛在游戏的小尺寸下也看得清；身体、手臂、脚的比例照英雄联盟。
输出：`outputs/blitzcrank-model-A.png`、`outputs/blitzcrank-model-B.png`，都是 1536x1024 横图，真透明 PNG。

参考图说明：01、02 只是**画风和金属画法**参考（之前采用的两张设定图），不要照抄他们的角色；03 是 A 的姿势和外形（权威）；04 是头和上半身特写（金色圆顶头、中间一道竖棱、两只粉白色发光圆眼、头陷在一圈钢制的领口里、脖子是一节节的弹簧管）；05 是正面（左右对称的样子：胸口大钢圈炉门、炉门中间的闪电纹、两根背后的烟囱、肩上的黑色软管和钢刺）；06 是 B 的姿势；07 侧面；08 背面；09 拳头特写（一块块金色方块拼成的大拳头、钢螺丝）。英雄联盟渲染图只做参考，不要照抄 3D 的光影。

## English prompt (for Codex)

Use case: stylized-concept character picture. Create TWO final character illustrations of **Blitzcrank, the Great
Steam Golem** (League of Legends), in his CLASSIC in-game look, as detailed crisp PIXEL ART in exactly the style of
the attached pictures 01-02 (dark stepped pixel contours, 3-5 flat tones per material, crisp highlights, bold readable
shapes, the way their steel parts are shaded). References 01-02 are ART STYLE ONLY: do NOT copy their characters,
weapons, backgrounds or glows. References 03-09 (renders of League's own model) are authoritative for Blitzcrank's
body, head, colours and fists; do not copy their 3D lighting, redraw them as pixel art.

**Picture A** (reference 03, his idle): full body, facing RIGHT in a three-quarter FRONT view: the big round chest
port and both glowing eyes visible, never a rear view. A huge top-heavy steam robot standing on two short legs with
his big flat feet apart on the SAME horizontal baseline, leaning slightly forward. His two ENORMOUS arms hang at his
sides with the giant fists down at about knee height, the near fist a little in front of his near leg, the far fist
beside his far side; both fists fully visible. 1536x1024 landscape PNG.

**Picture B** (reference 06): the same robot, same camera, in a ready-to-punch guard: both arms bent, the two giant
fists raised in front of his chest and belly like a boxer's guard, feet apart on one baseline. Chest port and both
eyes visible. 1536x1024 landscape PNG.

**Blitzcrank's look (both pictures):**
- Body: a huge round, egg-shaped GOLD-YELLOW steam-boiler torso (warm ochre gold, deeper brown-gold shading, small
  rust patches, rows of little rivets). On the chest/belly a LARGE ROUND PORT: a thick STEEL ring around a bronze-gold
  disc with a zigzag LIGHTNING-BOLT seam across it (references 04, 05).
- Head: a small rounded GOLD DOME with one raised ridge down its middle, sitting low and forward between the
  shoulders in a thick STEEL collar rim; under it a ribbed, spring-like dark neck. Two round GLOWING EYES side by side
  on the front of the dome (pale pink-white light with a hot white centre, set in dark sockets); no mouth, no nose,
  no hair. Draw the dome about 1.5 times League's size, so that the two eyes stay readable when the sprite is later
  drawn only 44 squares tall.
- Back and shoulders: two short STEEL SMOKESTACKS (exhaust pipes with gold-rimmed open tops) rising behind the head;
  big blocky GOLD SHOULDER PLATES with small steel pyramid SPIKES; thick BLACK ribbed rubber HOSES looping from the
  back over and around the shoulders into the arms.
- Arms: ENORMOUS, longer than his body is tall, built from chunky stacked GOLD BLOCKS (segmented plates) with steel
  SCREW HEADS and dark joints between the blocks; giant blocky FISTS whose fingers are square gold blocks with steel
  knuckle bolts (reference 09).
- Legs: short dark-steel piston legs; big flat GOLD FEET shaped like duck feet / plough plates with a riveted rim.
- Colour accents: gold-yellow and brown-gold body, gunmetal steel ring, collar, stacks and joints, black hoses,
  silver spikes and screws, the pale glowing eyes. The eye glow colour is used only by the eyes.

Keep the shapes bold and the silhouette readable (the later game sprite is 44 squares tall); a clean face: two eyes
only. Detailed PIXEL ART, not vector, not soft painting, not smooth 3D; crisp edges, no blur, no gradients, no noisy
texture. REAL transparent background (alpha 0 outside the silhouette), no backdrop colour, no steam clouds, no
electricity, no glow, halo or aura, no ground, no contact or cast shadow, no pedestal, no frame, no text, no labels.
Nothing below the soles (the hanging fists stay above the ground line). One character per picture, centred, top of
the smokestacks to the soles about 720 px, at least 80 px of empty transparent margin all round.

Deliver: `outputs/blitzcrank-model-A.png` and `outputs/blitzcrank-model-B.png` (both 1536x1024), true RGBA PNGs.
