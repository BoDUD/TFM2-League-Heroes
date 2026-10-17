# 内瑟斯（沙漠死神）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 内瑟斯是一个**高大、肌肉结实的豺狼头战士**（恕瑞玛的飞升者）：**黑褐色的毛**，豺狼的长嘴、尖牙，**两只高高竖起的长耳朵**（耳朵里面是暗红色）；头上戴着**金色的豺狼头冠**，把头顶、后脑和脖子包住，额前一颗**青绿色的宝石**；**两只眼睛发青绿色的光**。身上是**金色铠甲**：巨大的金色肩甲、胸前的金色领甲、金色护臂和金色长靴，铠甲上镶着**青绿色的宝石和花纹**；腰上一条**深蓝色的编织腰带**，下面是**青绿色的围裙（长腰布）**和浅灰色的布条；手臂和小腿上缠着**灰白相间的布条**。他手里拿着一根**很长的法杖**：**棕色的木杆**，两端是青绿色的金属，**一端是金色的大月牙形斧刃**（带青绿色的宝石），另一端是一个小一点的金色尖刃。请 Codex 画**两张全身像**（同一个内瑟斯，长相、颜色、**格子大小**都一样；两张**都要用**，不是二选一）：
> - **A：平时的样子**（英雄联盟里的待机，附图 1）。他微微弓背站着，法杖横握在身前偏下：**月牙斧刃在前面（画面右边）靠近地面**，杖尾斜着伸向身后（画面左边）。脸朝右前方。
> - **B：死神降临（大招变身）**。还是他本人、**同样的格子大小、同样的站姿**，但**整个人大约高 1.35 倍**（英雄联盟里大招时他会变大 30–40%）：从耳尖到鞋底约 97 格（附图 8b）。**眼睛和铠甲上所有青绿色的宝石、花纹都发出亮青白色的光**（平涂的亮色，不要柔光），法杖的斧刃也更亮。英雄联盟里这个形态是同一个模型放大、外面套一圈沙暴特效，没有单独的模型，所以 B 照这段文字画（附图 5 的加载画面是他发怒发光的样子）。沙暴是特效，不画。B 用来做附加包里变身后的整个身体和大招期间的动作。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.2）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的塔姆、厄加特、斯维因和雷克顿，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：高大健壮的豺狼战士，**头（连耳朵）约占身高的四分之一**（约 18 格），不要大头娃娃，也不要写实的细长比例。肩膀很宽（金色大肩甲），腰比肩窄，腿结实。
> - **头**（附图 3 特写）：金色豺狼头冠（几档金：亮金、金、暗金、棕金，不要一片黄），头冠上的青绿宝石；**长嘴向前伸、黑褐色的毛，嘴边露出白色尖牙**；两只长耳朵竖起，**近侧的耳朵里面暗红色**；**两只眼睛一样大、一样高、发青绿光**。
> - **铠甲**：金色肩甲很大、带青绿镶边；胸口是金色领甲，露出黑褐色的毛和肌肉；金色护臂、金色长靴，都镶青绿宝石。
> - **布料**：腰上深蓝色编织腰带；青绿色的长腰布垂到膝盖，下面一条浅灰色的布；手臂和小腿缠着灰白条纹的布条。
> - **法杖**：长度约等于他的身高；棕色木杆（有缠绕的纹路），两端青绿色金属；**金色月牙形大斧刃**，上面镶青绿宝石；另一端一个小的金色尖刃。斧刃和杖身**必须完整地画出来**、形状清楚，不要只剩一根细线。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**。**A：从耳尖到鞋底约 792 px，也就是约 72 格**，鞋底在离画布底边约 146 px 的地方（附图 8a 的灰线）。**B：同样每格 11 像素，从耳尖到鞋底约 1070 px（约 97 格）**，鞋底在同一条线上（附图 8b）。法杖、耳朵全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。金色铠甲、青绿宝石、黑褐色的毛、深蓝腰带、青绿腰布、灰白布条、棕色木杆要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**黑褐色的毛很暗，一定要有偏暖的亮边**，不然在深色背景上会糊成一团。
> - 不画任何特效（沙暴、灵魂火、Q 的发光、吸取的光都放到第 3 步单独画；B 发光的眼睛和宝石是身体的一部分，用平涂的亮色画，不要柔光）；不画地面，不画影子。
> - 交付：`outputs/nasus-picture/nasus-A.png`、`nasus-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/nasus-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/nasus_picture_done.zip`。

## 附图（在压缩包 `nasus_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_nasus_idle.png` | 英雄联盟原版内瑟斯的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和法杖的拿法 |
| `refs/2_nasus_frontal.png` | 同一帧，正面 | 肩甲、领甲、腰带、腰布、布条怎么排 |
| `refs/3_nasus_head.png` | 头部特写 | 金色豺狼头冠、长耳朵（暗红内耳）、长嘴尖牙、发光的眼睛 |
| `refs/4_nasus_back.png` | 同一帧的背后 | 肩甲背面、腰布、法杖的另一端 |
| `refs/5_nasus_splash.png` | 官方加载画面 | 气质、**B 的发光**（眼睛和宝石的亮青白色） |
| `refs/6_nasus_r_cast.png` | 大招的一帧：举杖怒吼 | 法杖竖起来时的全长、斧刃的形状 |
| `refs/7_nasus_q_strike.png` | Q 汲魂痛击的一帧 | 斧刃的正面形状、弓身的样子 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同样的格子，整个人大 1.35 倍） | 他的位置和大小、地面线（灰） |
| `style/11_style_tahmkench.png` | 本包的塔姆，8 倍放大，一格 = 一个像素（PPU 1.2，和内瑟斯一样） | **只看风格**：大个子怎么分档、怎么留亮边 |
| `style/12_style_urgot.png` | 本包的厄加特（8 倍，PPU 1.2） | **只看风格**：金属铠甲、暗色身体的亮边 |
| `style/13_style_swain.png` | 本包的斯维因（8 倍，PPU 1.5） | **只看风格**：脸、眼睛、暗色衣服的亮边 |
| `style/14_style_renekton.png` | 本包的雷克顿（8 倍，1 倍密度），恕瑞玛的兽头战士 | **只看风格**：兽头、金饰和长柄武器在格子上怎么画 |

## 提示词：`nasus-A.png` / `nasus-B.png`（同一段提示词，只换最后一句）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 are 3D renders and art of a character from the game: a TALL MUSCULAR JACKAL-HEADED WARRIOR - dark brown fur, a long jackal snout with white fangs, TWO TALL UPRIGHT EARS (the inner ear dark red), a GOLD JACKAL HEADDRESS covering the top and back of his head and his neck with a TEAL GEM on the brow, TWO EYES GLOWING TEAL; GOLD ARMOUR - huge gold pauldrons, a gold collar plate over a dark-furred chest, gold bracers and tall gold boots, all inlaid with TEAL gems and teal lines; a DARK-BLUE BRAIDED BELT, a long TEAL LOINCLOTH down to the knees with a light-grey cloth under it, GREY-AND-WHITE STRIPED WRAPS on his forearms and shins; he holds a VERY LONG STAFF: a brown wooden shaft with a wound pattern, teal metal at both ends, a big GOLD CRESCENT AXE BLADE with teal gems at one end and a small gold spike at the other (1 his idle, 3/4 view facing right - the look, the ANGLE, pose A and how he holds the staff; 2 the same from the front: the pauldrons, the collar, the belt, the loincloth, the wraps; 3 the head close-up: the gold headdress, the ears, the snout and fangs, the glowing eyes; 4 the same from behind: the pauldrons' back, the loincloth, the staff's other end; 5 the official illustration: his mood and how his eyes and gems blaze; 6 his ultimate: the staff raised upright, its full length and the blade's shape; 7 his Q strike: the blade's face, the hunched body). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how a huge body is split into clear shades with lit edges (11), metal armour and a dark body with lit edges (12), a face with two clear eyes and dark clothes with light edges (13), a beast head, gold ornaments and a long polearm on the grid (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the ears, the staff and its blade whole); both soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b).
PROPORTIONS: a big strong jackal warrior - the head with the ears about a quarter of his height (about 18 squares in A), NOT a big-headed doll and NOT realistic slim proportions; very broad shoulders (the gold pauldrons), the waist narrower, strong legs.
THE HEAD: the gold headdress in bright gold / gold / dark gold / brown-gold (never one flat yellow), its teal brow gem; the snout reaching forward, dark brown fur, white fangs at the mouth; both ears upright, the near one dark red inside; TWO EYES of the SAME size at the SAME height, glowing teal.
THE ARMOUR: huge gold pauldrons with teal trims; a gold collar plate, the dark-furred muscular chest showing; gold bracers and tall gold boots with teal gems.
THE CLOTH: a dark-blue braided belt; a long teal loincloth to the knees with a light-grey cloth under it; grey-and-white striped wraps on the forearms and shins.
THE STAFF: about as long as he is tall; a brown wound wooden shaft, teal metal at both ends; the GOLD CRESCENT AXE BLADE with teal gems drawn whole with a clear shape (never just a thin line); a small gold spike at the other end.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark brown fur with WARM LIT EDGES so it never turns into one dark mass, the gold armour, the teal gems, the dark-blue belt, the teal loincloth, the grey-white wraps, the brown shaft clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no sandstorm, no spirit fire, no glowing trails), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (nasus-A.png): his idle (image 1) - standing slightly hunched, the staff held low across in front of him: the CRESCENT BLADE IN FRONT (image right) near the ground, the shaft slanting back behind him (image left); the face to the front-right. He is about 792 px (about 72 squares) from the ear tips to his soles.
POSE B (nasus-B.png): FURY OF THE SANDS - the SAME warrior with the SAME 11-px squares and the same pose and staff grip as A, but the WHOLE FIGURE 1.35 TIMES TALLER: about 1070 px (about 97 squares) from the ear tips to his soles, the soles on the same ground line (image 8b); his EYES and EVERY TEAL GEM AND TEAL LINE on the armour BLAZE bright cyan-white (flat bright squares, no glow halo), the staff's blade brighter too. No sandstorm (that is an effect, drawn later).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，耳朵、法杖和斧刃完整，不出画。
- 比例：高大健壮的豺狼战士，头（连耳朵）约占身高四分之一（A 约 18 格），不是大头娃娃；两只眼睛一样大、一样高、发青绿光。
- 头：金色豺狼头冠分几档金色、额前青绿宝石；长嘴、黑褐色毛、白色尖牙；两只长耳朵竖起，近侧耳朵里面暗红。
- 铠甲：金色大肩甲、金色领甲、护臂、长靴，镶青绿宝石；胸口露出黑褐色的毛。
- 布料：深蓝编织腰带、青绿长腰布、浅灰布、灰白条纹布条。
- 法杖：约和身高一样长，棕色木杆，金色月牙斧刃完整清楚，另一端小尖刃。
- A：待机姿势，斧刃在前（画面右边）靠近地面、杖尾斜向身后；从耳尖到鞋底约 792 px（约 72 格），鞋底在同一条地面线上。
- B：**同样每格 11 像素、同样的姿势**，整个人大 1.35 倍（耳尖到鞋底约 1070 px，约 97 格），鞋底在同一条线上；眼睛和所有青绿宝石、花纹发亮青白色（平涂）。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/nasus-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nasus_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/nasus/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_swain_hd.py` 的做法），和已合并的上单（德莱厄斯、塔姆、厄加特、斯维因、雷克顿）按游戏里的大小并排，给用户定大小；PPU 1.2（用户选的），A 显示高度约和德莱厄斯一样，B 约大 1.35 倍。
- 定下后第 1 步按游戏格子重画 A 和 B，再自己做动作帧（塔姆 / 斯维因的方式，无损：只平移、整块直角转、整行移；法杖只能整根平移或直角转）：走路用换皮法（oppi 的雷克顿 cf_renekton 当动作骨架、我们的设计当皮肤，`tools/art/pack_swain_run.py` 的做法）；普攻 nasus_attack1 / Nasus_Attack2；Q 汲魂痛击 Nasus_Spell1；W 枯萎 Nasus_Base_Spell2_Full（伸手）；E 灵魂烈焰 Nasus_Base_Spell3_Full；R 死神降临 Nasus_Base_Spell4_Full（举杖怒吼）；死亡 Nasus_Base_Death。B 形态（附加包整身换图）：b_idle / b_run / b_attack / b_skill / b_skill2 / b_hit，主包里 R 期间的普攻和技能也用 B 的动作。
