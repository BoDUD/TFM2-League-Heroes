# 加里奥（正义巨像）：先画一张像素风原图（第 0 步，给 Codex 的提示词）

> 加里奥还没有原图。这一步请 Codex 画一张全身像素风原图，A、B 两版只差**翅膀**，身体、脸、颜色、姿势完全一样：**A = 英雄联盟里的待机，两只金翅膀高高竖在背后**（附图 1）；**B = 同一个人，翅膀半收拢，翅尖只比头冠高一点**（游戏里格子小，B 更紧凑）。你挑一版，之后第 1 步再按它画正面 + 侧面的高清（PPU）造型。这一版走**高清（PPU）**：你画的原图会直接按格子读回成游戏里的高清造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–9）：加里奥，一座**会动的有翅膀的石像巨人**，全身是**淡青灰色的禁魔石**（亮部近白的浅青、中间灰青、暗部青灰），**所有边缘镶着土金色的金饰**。
> - **头**（附图 3 特写）：头比身体小很多（巨人比例）；一顶**金色的头冠头盔**，**正中一根高高的尖角，两边各一根矮一点的尖角**；头盔下是**一张严肃的石头脸**：方下巴、直鼻子、紧闭的嘴、深眼窝里两只浅色眼睛；脖子上一圈**金色领口**。
> - **身体**：**上身极宽、腰细**（倒三角）；两个**巨大的方块石肩甲**，边上有金边、肩甲正面一个金色尖角装饰；胸口正中一个**金色展翅徽章**；腹部是一层层石板；**两条胳膊又粗又长，前臂像石柱，两只巨大的石拳头**（拳头比头还大），垂在身体两边；腰下一圈金饰；**两条腿是反关节的兽腿**（大腿粗、小腿向后折，像石像鬼），膝盖上有**金色护膝**，**脚是有三根爪趾的石头兽爪**，脚踝一圈金环。
> - **翅膀**：背后两只**巨大的金色翅膀**，一片片**长长的金羽毛像刀片一样排开**（亮部明黄、暗部棕金），**A 翅膀高高竖起，翅尖远高于头冠**（附图 1、4）；**B 翅膀半收、向两边和后面张开，翅尖只比头冠高一点点**。翅膀在身体后面，**不能挡住脸、胸口徽章和两只拳头**。
> - **尾巴**：一条**石头尾巴**从身后垂到地上、拖在他身后（画面左边），**尾巴尖是一个金色的箭头**（附图 1）。
> - **姿势**：3/4 正面朝右（脸、胸口朝向看画的人），两腿分开站稳：**近侧的腿在画面左边、颜色亮；远侧的腿在画面右边、稍暗、稍高**；两只拳头垂在身体两侧，微微握着。
> - **比例**：他是巨人，**头只占身高（头冠到脚底）的七分之一左右，不要大头娃娃**；但脸要在小尺寸下还能看出是一张脸（可以比原版稍微大一点点）。整体收紧凑，风格照附图 10–12（你之前画的莫德凯撒、布隆、卡萨丁）。
> - **画布用竖版 1024×1536**：**头冠尖到脚底约 1000 px**（A、B 一样大）；A 的翅尖再往上，全部在画面里，不能出画；左右（翅膀、尾巴）不超过 960 px；脚底平平地落在一条地面线上（游戏在脚下画血条）。
> - **像素块**：大小一致的方块，**每块约 8 像素**，横平竖直对齐成网格（这张图会被按格子读回）；外轮廓一圈 1 块宽的近黑描边。
> - 不画任何特效（战争罡风的龙卷风、杜朗护盾的光、正义冲拳、英雄登场的落地冲击都在第 3 步单独画）；不画地面和影子。
> - 交付：`outputs/galio-picture/galio-model-A.png`、`outputs/galio-picture/galio-model-B.png`（都是 1024×1536 竖版、真透明背景）；附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明）。

## 附图（压缩包 `galio_pack0.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_galio_league_front.png` | 英雄联盟原版加里奥待机，3/4 朝右 | 颜色、形状、**角度**、A 的翅膀 |
| `refs/2_galio_league_frontal.png` | 同一帧，正面 | 胸口金徽章、肩甲、腰、腿 |
| `refs/3_galio_league_head.png` | 头的特写 | 金头冠的三根尖角、石头脸、金领口 |
| `refs/4_galio_league_back.png` | 同一帧的背后 | 翅膀怎么从背上长出来、尾巴 |
| `refs/5_galio_splash.png` | 官方加载画面 | 气质（威严的守护巨像） |
| `refs/6_galio_league_run.png` | 英雄联盟里他跑动的几个瞬间 | 沉重的兽腿 |
| `refs/7_galio_league_actions.png` | 普攻、战争罡风、正义冲拳、杜朗护盾的瞬间 | 拳头和翅膀怎么动 |
| `refs/8_galio_league_side_b.png` | 待机，3/4 和侧面之间 | 角度过渡参考（这一步不用） |
| `refs/9_galio_league_side.png` | 待机的侧面（朝右） | 反关节腿、翅膀的侧面（第 1 步用） |
| `style/10_style_mordekaiser.png` | 你之前的莫德凯撒像素图 | **只看风格**（最近通过的一张，同样走高清） |
| `style/11_style_braum.png` | 你之前的布隆像素图 | **只看风格**（大块头） |
| `style/12_style_kassadin.png` | 你之前的卡萨丁像素图 | **只看风格** |

## 提示词 A：`galio-model-A.png`（翅膀高高竖起）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look, the ANGLE and the WINGS of this picture; 2 the same from the front: the gold winged emblem on the chest, the huge shoulder blocks, the waist, the legs; 3 the head close-up: the gold crown-helm with three spikes, the stern stone face, the gold collar; 4 the same from behind: how the wings grow from the back, the tail; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells; 8 the idle between 3/4 and side - not used here; 9 the idle from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 another big heavy character, image 12 another approved picture).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 1000 px from the top of the crown spike to the soles, the wing tips higher still, no more than 960 px wide, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Galio, the Colossus, a LIVING WINGED STONE STATUE, a giant made of PALE GREEN-GREY PETRICITE STONE (near-white pale mint highlights, grey-green mid-tones, slate-green shadows) with EARTHY GOLD TRIM along every edge. THE HEAD: small for his huge body; a GOLD CROWN-HELM with ONE TALL CENTRAL SPIKE and a SHORTER SPIKE ON EACH SIDE; under it a STERN STONE FACE - square jaw, straight nose, closed mouth, two pale eyes in deep sockets; a GOLD COLLAR round the neck. THE BODY: an inverted triangle - VERY BROAD SHOULDERS, a narrow waist; two HUGE BLOCKY STONE PAULDRONS edged in gold with a pointed gold ornament on their front; a GOLD WINGED EMBLEM in the middle of the chest; layered stone plates on the belly; LONG THICK ARMS, forearms like stone pillars, two ENORMOUS STONE FISTS (bigger than his head) hanging at his sides; a gold band below the waist; DIGITIGRADE BEAST LEGS like a gargoyle (thick thighs, shins bending back), GOLD KNEE GUARDS, STONE CLAWED FEET with three toes and a gold anklet. THE WINGS: two HUGE GOLD WINGS behind him made of long BLADE-LIKE GOLD FEATHERS fanned in rows (bright yellow highlights, brown-gold shadows); here they RISE HIGH, their tips far above the crown, like image 1. THE TAIL: a stone tail hanging behind him down to the ground and trailing on the image left, ending in a GOLD ARROWHEAD tip.
Pose: League's own idle (image 1): standing firm, feet apart, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher; the fists hanging at his sides, loosely closed. The wings stay BEHIND him: they never cover the face, the chest emblem or the fists. 3/4 FRONT view facing image right, face and chest toward the viewer.
Proportions: a giant - the head about ONE SEVENTH of his height from crown to soles, NOT a chibi big head; the face may be a touch bigger than in the game model so it still reads as a face at a small size. Keep the whole figure COMPACT.
Style: crisp pixel art like images 10-12 - EVEN SQUARE PIXELS ABOUT 8 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a one-square near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the stone pale green-grey (near-white mint, grey-green, slate-green), the gold earthy yellow (bright yellow, ochre, brown-gold), the eyes pale; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no tornado, no wind, no shield glow, no impact), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`galio-model-B.png`（翅膀半收拢）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-9 are 3D renders and art of the character from the game (1 the full figure in 3/4 view facing right - the look and the ANGLE of this picture; 2 the same from the front: the gold winged emblem on the chest, the huge shoulder blocks, the waist, the legs; 3 the head close-up: the gold crown-helm with three spikes, the stern stone face, the gold collar; 4 the same from behind: how the wings grow from the back, the tail; 5 the official illustration: his mood; 6 moments of him running; 7 moments of his attack and spells - in some of them the wings are lower and spread; 8 the idle between 3/4 and side - not used here; 9 the idle from the side - not used here). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10, 11 and 12 are STYLE ONLY, other characters: copy their pixel-art style (image 10 the latest approved picture of this series, image 11 another big heavy character, image 12 another approved picture).
Create ONE full-body pixel-art picture of this character, a 1024x1536 PORTRAIT PNG with a genuine transparent background (real alpha), about 1000 px from the top of the crown spike to the soles, no more than 960 px wide, centred, comfortable transparent margins, nothing cut off, the soles level on one ground line.
The character: Galio, the Colossus, a LIVING WINGED STONE STATUE, a giant made of PALE GREEN-GREY PETRICITE STONE (near-white pale mint highlights, grey-green mid-tones, slate-green shadows) with EARTHY GOLD TRIM along every edge. THE HEAD: small for his huge body; a GOLD CROWN-HELM with ONE TALL CENTRAL SPIKE and a SHORTER SPIKE ON EACH SIDE; under it a STERN STONE FACE - square jaw, straight nose, closed mouth, two pale eyes in deep sockets; a GOLD COLLAR round the neck. THE BODY: an inverted triangle - VERY BROAD SHOULDERS, a narrow waist; two HUGE BLOCKY STONE PAULDRONS edged in gold with a pointed gold ornament on their front; a GOLD WINGED EMBLEM in the middle of the chest; layered stone plates on the belly; LONG THICK ARMS, forearms like stone pillars, two ENORMOUS STONE FISTS (bigger than his head) hanging at his sides; a gold band below the waist; DIGITIGRADE BEAST LEGS like a gargoyle (thick thighs, shins bending back), GOLD KNEE GUARDS, STONE CLAWED FEET with three toes and a gold anklet. THE WINGS: two HUGE GOLD WINGS behind him made of long BLADE-LIKE GOLD FEATHERS fanned in rows (bright yellow highlights, brown-gold shadows); here they are HALF FOLDED, spread out to both sides and back behind his shoulders, their tips ONLY A LITTLE ABOVE THE CROWN - a compact silhouette. THE TAIL: a stone tail hanging behind him down to the ground and trailing on the image left, ending in a GOLD ARROWHEAD tip.
Pose: League's own idle (image 1): standing firm, feet apart, the near leg on the image left in full tone, the far leg on the image right a shade darker and a little higher; the fists hanging at his sides, loosely closed. The wings stay BEHIND him: they never cover the face, the chest emblem or the fists. 3/4 FRONT view facing image right, face and chest toward the viewer.
Proportions: a giant - the head about ONE SEVENTH of his height from crown to soles, NOT a chibi big head; the face may be a touch bigger than in the game model so it still reads as a face at a small size. Keep the whole figure COMPACT.
Style: crisp pixel art like images 10-12 - EVEN SQUARE PIXELS ABOUT 8 OUTPUT PIXELS EACH, aligned on one straight grid (the picture will be read back square for square), a one-square near-black outline around the silhouette, inside it every material in its own 3-5 flat shades: the stone pale green-grey (near-white mint, grey-green, slate-green), the gold earthy yellow (bright yellow, ochre, brown-gold), the eyes pale; light and dark parts clearly separated, never one blob; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no tornado, no wind, no shield glow, no impact), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底），竖版 1024×1536，四周留边，翅膀、尾巴都完整，不出画。
- 淡青灰色石头身体 + 土金色金边；金头冠一高两矮三根尖角；严肃的石头脸、金领口；胸口金色展翅徽章。
- 倒三角：巨大方块肩甲、细腰；粗长的胳膊、比头还大的石拳头垂在两边；反关节兽腿、金护膝、三爪石脚、金脚环。
- 金色刀片羽毛的大翅膀在身后：A 高高竖起、翅尖远高于头冠；B 半收拢、翅尖只比头冠高一点；不挡脸、徽章和拳头。
- 石头尾巴拖在身后（画面左边）、尖端金箭头。
- 头冠尖到脚底约 1000 px（两版一样大）；头约占七分之一，不是大头娃娃；整体紧凑。
- 近侧腿在画面左边亮色、远侧腿在右边稍暗稍高；脚底落在同一条水平线上；没有任何特效。
- **每块约 8 像素、大小一致、对齐网格**；没有糊、没有柔光、没有渐变；全硬 alpha（不要半透明边）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/galio-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## Claude 收到后（给 Claude 看）

- 把两张原画（和 raw/）放进 `assets/source/galio/codex_picture/`，按格子读回，和包里的英雄（league/*#sheet.png）并排给用户挑 A / B 和大小。
- 选定后写第 1 步 `MODEL_PROMPTS.md`：**正面（3/4，待机 + 选人卡）+ 侧面（朝右，所有动作的底子）**两个视图，同一个高度、同一套格子、同样的细节（side-view-design）；高清 PPU，原稿 1:1 按格读回，绝不先画大再缩。在游戏里身高略大于布隆（约 40–42 行，用 hd.rs SIZES 调，不删躯干行）。
- 腿：待机两腿分开站稳（three-quarter-legs）；跑步按 Caitlyn 的交叉步方式（反关节兽腿也一样：大腿从髋部出发，不变形）；同一张脸贯穿所有帧；翅膀是刚体，只平移、不乱转。
