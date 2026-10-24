# 阿狸：按 PPU 1.5 重画设计图（给 Codex 的提示词）

> 阿狸现在游戏里的造型是 1 倍的：从狐耳尖到脚底只有 40 格，脸、头发、衣服的细节都挤在一起（附图 7）。这次和凯特琳、锐雯、拉克丝一样按 **PPU 1.5** 重画：**每个游戏像素画成 1.5 格**，从狐耳尖到脚底约 **60 格**。这次只画**一张**全身设计图；动作之后再做。
> - **比例照现在的游戏精灵（附图 7）**：Q 版大头，头（连头发、不算狐耳）约占身高的三分之一，身材纤细；不要更高更瘦，也不要更矮。
> - **衣服、颜色照附图 6**（之前定下的阿狸造型）：
>   - 头：**深蓝黑色长发**（长度照附图 6，垂到腰），带深蓝紫的高光；头顶一对**黑色狐耳**，耳朵里面粉色；**金黄色的眼睛**，两只眼睛一样高、都看得见；脸颊上三道细细的胡须纹；表情妩媚、微笑。
>   - 上身：**红白配色的和风短上衣**：白色衣身、红色的宽袖和衣襟，金色镶边；腰间红色的腰带，前面垂下金色的挂饰。
>   - 下身：红色短裙；**红色长靴 / 长袜到大腿**，金色的镶边和靴口。
>   - **九条尾巴**：**蓬松的大毛尾，白色为主，尾尖淡紫**，阴影在下沿；从后腰（屁股上方）长出来，尾根藏在身体后面。
> - **尾巴是阿狸最重要的特征，一定要大、一定要看得见**（用户以前说过：「尾巴又太小 导致比赛内的尾巴特征不明显 尤其是比赛的时候 尾巴几乎被身体完全遮挡」）：
>   - 照附图 6 的样子，**在她身后往后上方张开成半扇形**，看得见 5–6 条，互相叠着，每条都有体积。
>   - 整束约 **36–40 格宽、38–42 格高**（附图 8 的剪影里尾巴的位置和大小）。
>   - 范围：尾尖在腰和狐耳尖之间（最多高出狐耳尖 3 格）；**膝盖以下不要有尾巴**，绝不碰脚底线；身前（她朝右，右边）不要有尾巴；头顶正上方不要有。
>   - 英雄联盟的待机（附图 1）尾巴是拖在地上的，**这次不要照它**，照附图 6 往后上方张开。
> - **姿势照附图 1**（英雄联盟里的待机）：站着，近侧的手抬到脸旁边（照附图 1），另一只手垂在身侧；两只脚底在同一条地面线上。手里不拿法球。
> - **朝向**：四分之三侧身，**脸和胸口朝右前方**（附图 1、3）。近侧（画面左边）的手臂和腿颜色亮，远侧稍暗。
> - **画布用方形 1024×1024**：**狐耳尖到脚底约 660 px，也就是约 60 格**，脚底在离画布底边约 64 px 的地方（附图 8 的深灰线），狐耳尖碰到附图 8 的浅灰线（附图 8 只看大小和位置，姿势照附图 1）。整个人和整束尾巴都在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。头发要有深蓝紫的明暗层次，不要一片死黑；尾巴的白要有淡紫灰的阴影，不要一片死白，每条尾巴之间有描边分开；金黄眼睛、粉色耳内、红衣服要清楚。附图 9–11 是本包同样密度（PPU 1.45–2.2）的英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。
> - 不画特效（不画法球、不画狐火）、地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
>
> - 交付：`outputs/ahri-ppu/ahri-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/ahri-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ahri_ppu_done.zip`。

## 附图（在压缩包 `ahri_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ahri_idle.png` | 英雄联盟里的阿狸待机，四分之三朝右（头放大到接近游戏精灵的比例） | **朝向、姿势**（尾巴不照它） |
| `refs/2_ahri_side.png` | 同一帧，转得更侧 | 手的位置、衣服 |
| `refs/3_ahri_head.png` | 头部特写 | 脸、头发、狐耳 |
| `refs/4_ahri_tails.png` | 同一帧，从身后看 | **尾巴的形状**、尾根在后腰 |
| `refs/5_ahri_splash.png` | 官方加载画面 | 看气质和配色 |
| `refs/6_ahri_picture.png` | 之前定下的阿狸造型 | **衣服、颜色、尾巴的摆法照它** |
| `refs/7_ahri_now.png` | 她现在的游戏精灵（8 倍，1 倍密度，40 格高） | **比例、身材** |
| `refs/8_layout.png` | 布局示意：现在的精灵放大到新尺寸的剪影 | 画布上的大小、脚底线（深灰）、**狐耳尖要碰到的线（浅灰）**、尾巴的范围 |
| `style/9_style_caitlyn.png` | 本包的凯特琳（8 倍，PPU 1.45） | **只看风格** |
| `style/10_style_riven.png` | 本包的锐雯（8 倍，PPU 1.5） | **只看风格** |
| `style/11_style_lux.png` | 本包的拉克丝（8 倍，PPU 2.2） | **只看风格**：女法师、身材 |

## 提示词：`ahri-A.png`

附图 1–11，顺序同上表。

```text
Eleven attached images. Images 1-4 are 3D renders of a character from the game (her head enlarged toward a game sprite's proportions): a fox-girl mage with fox ears and nine white tails (1 her idle in 3/4 view facing right - the ANGLE and the POSE for this picture, but NOT her tails; 2 the same turned more to the side: her arms and clothes; 3 her head: the face, the hair, the fox ears; 4 the same frame seen from behind: the tails' shape and where they grow from). Image 5 is the official illustration: the mood and the colours. Image 6 is the approved pixel picture of her: copy its COSTUME, COLOURS and the way its TAILS fan out behind her. Image 7 is her small game sprite now, shown 8x: copy its PROPORTIONS (a chibi: the head with the hair, not counting the ears, about a THIRD of her height, a slender build) - not its pose. Image 8 is THIS picture's layout guide: her sprite now as a flat silhouette at the new size - how big she and her tails are and where she stands (not the pose); the dark grey line is the ground where her soles stand, the light grey line is where THE TIPS OF HER FOX EARS go. Images 9-11 are STYLE ONLY, other characters from the same game shown 8x (every square one pixel) at a similar square density: copy their pixel-art look and their 3/4 front-right view.
Create ONE pixel-art picture of her, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). She is about 660 px (about 60 squares) from the tips of her fox ears to her soles, the soles about 64 px above the bottom edge; the whole figure and all the tails inside the picture with margins, nothing cut off; both soles on one ground line; nothing at all below her soles.
THE CHARACTER (image 6): a charming fox-girl mage. HEAD: long DARK NAVY-BLACK hair down to her waist (as in image 6), shaded with deep blue-violet highlights; a pair of BLACK FOX EARS on top with PINK insides; GOLDEN-YELLOW eyes, the two eyes at the same height, both visible; three thin whisker marks on each cheek; a charming smile. BODY: a short Korean-style robe in RED AND WHITE - a white body, red wide sleeves and red collar, gold trim; a red sash at the waist with a gold tassel hanging in front. LEGS: a short red skirt; long RED boots / stockings up to the thighs with gold trim.
THE NINE TAILS (her most important feature - they must be BIG and clearly VISIBLE): big fluffy fox tails, mostly WHITE with PALE VIOLET tips, shaded along their lower edges, each tail outlined apart from the next; they grow from her lower back above her hips (their roots hidden behind her body) and FAN OUT BEHIND HER, UP AND BACK, in a half fan like image 6 - NOT trailing along the ground like image 1; 5-6 of the tails visible, overlapping, each with volume; the whole fan about 36-40 squares wide and 38-42 squares tall (the tails' area in image 8); the tips between her waist and the tips of her ears (at most 3 squares above the ear tips); NO tail below her knees, none touching the ground line, none in front of her (she faces right: nothing to her right), none straight above her head.
PROPORTIONS (image 7): a chibi, the head with the hair about a THIRD of her height, slender - NOT taller or thinner, NOT shorter.
THE VIEW: 3/4 view FACING RIGHT like images 1 and 3: the face and the chest turned to the front-right; the NEAR arm and leg on the image LEFT in full tone, the far ones a step darker.
THE POSE (image 1): standing, the near hand raised beside her face as in image 1, the other arm down at her side; both soles on one ground line. No orb in her hands.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark hair with blue-violet light and shade (never one flat black mass), the white tails with pale violet-grey shading (never flat white), the golden eyes, the pink ear insides and the red clothes clear; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing.
No effects, no orb, no fox-fire, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**。
- **姿势照附图 1**：站着，近侧的手抬到脸旁；狐耳尖到脚底约 660 px（约 60 格），两只脚底在同一条线上，脚底以下什么都没有。
- **尾巴大、看得见**：在身后往后上方张开成半扇形（照附图 6），看得见 5–6 条，白色带淡紫尾尖；从后腰长出来；膝盖以下、身前、头顶正上方都没有尾巴。
- 衣服、颜色和附图 6 一样：深蓝黑长发、黑色狐耳（粉色耳内）、金黄眼睛、胡须纹、红白和风短上衣、红腰带和金挂饰、红色短裙和长靴。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格。
- 画完后最后写 `outputs/ahri-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ahri_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- **读原图，不读导出图**（拉克丝的教训：Codex 的导出按大格子采样，脸都没了）：原画和 raw/ 放进 `assets/source/ahri/hd/`，照 `tools/art/design_lux_hd.py` 按原图自己的格子读回；和拉克丝、凯特琳、锐雯、现在的阿狸按游戏里的大小并排，给用户确认大小和 PPU。
- 动作开工前先定**手臂要不要动**（拉克丝的教训：施法时手和武器不动，用户：「手和法杖一点动作都没有的 不奇怪？」）；阿狸的普攻、Q、E、R 都要抬手放球 / 冲刺，大概率要 Codex 整帧重画再由 Claude 修（`tools/art/casts_lux_hd.py` 的做法）。
- 每一帧都要看得见尾巴；查塞拉斯、佛耶戈 / 妮蔻灵魂表、待机和选人卡轮播、Q / E 的出手高度等适配。
