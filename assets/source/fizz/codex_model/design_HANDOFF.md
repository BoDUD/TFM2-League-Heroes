# 菲兹游戏造型设计交接

## 最终文件

- fizz_design_A.png / fizz_design_B.png：1024×1024，RGBA，严格 8 倍像素展示图。
- fizz_design_A_1x.png / fizz_design_B_1x.png：128×128，RGBA，游戏逻辑像素原尺寸图，包含定位用透明画布。
- fizz_design_comparison.png：与素材包崔丝塔娜质量参考并排，附暗底 1× 预览；背景和文字只在对比图中。
- palette.json / palette.gpl / palette.png：共用 24 色色板及预览。
- validation.json：从最终 PNG 读取并校验的规格结果。

## 两版差异

A：耳鳍顶至下巴 13 格；近眼 3 格宽，远眼 2 格宽，眼睛同位于第 73、74 行。
B：耳鳍顶至下巴 15 格；两眼均 3 格宽，眼睛同位于第 75、76 行；脸更正面，头部覆盖更多上躯干，露出的身体相应缩短。
两版的下身、手、武器、站位及色板共用同一模板。仅头部、脸及其覆盖的上躯干有差异。

## 已验证的数值

- 8× 图逐像素等于 1× 图的最近邻 8 倍展开；没有混色或小于一格的细节。
- 每张仅 24 个不透明 RGB 颜色，透明度只有 0 和 255；透明像素为 RGBA(0,0,0,0)。
- 最上方像素在第 66 行，脚底最低为第 99 行，因此全身高度 34 格；放大脚底下沿为 y=800，最低色块是 y=792–799。
- 第 100–127 行完全透明，脚下没有阴影、光晕或其他残留。
- 两脚中心的中点为逻辑坐标 x=64，即放大图 x=512。
- 三叉戟包括描边宽 57 格，叉头朝右，中央叉齿最长；整根位于脚底以上。
- 杆中间是 1 格深红，上下各 1 格描边。双手内部各为 2×2 色块，起始列 x=60、66，间距 6 格，均连着手臂。
- 亮绿及眼睛暗绿只出现在眼睛区域，武器翠绿为独立的偏蓝色组。

## 使用的方法与改动

先用内置 image_gen 生成游戏尺寸原稿，使用的两段提示词附后。生成器未稳定遵守网格、尺寸、眼睛宽度和色数。
用户明确回复“允许”程序整理后，先恢复原稿已有粗像素网格，供形状和配色比较，再直接在 128×128 逻辑画布逐格重绘头部、耳鳍、双手、躯干、蹼足与三叉戟，统一 24 色，输出严格最近邻 8 倍图。
这次修正范围较大，最终图是经过逐格调整的游戏造型方案，并非仅给生成原稿做自动色彩量化。没有把上一轮高清插画滤波缩小来充当游戏像素图。

## 视觉上的取舍 / 后续确认

数值规格已通过。34 格分辨率下，橙色耳鳍褶边、背后鳍叶、脚趾和三叉戟纹样被合并成清晰色簇，未逐项复刻高清设定图的小纹饰。小手保留握杆轮廓，未单独画出三个手指。眼睛用两行、单格瞳孔和高光，因此不会呈现高清原画的圆形虹膜细节。
画风和神态是否完全达到用户偏好仍需结合对比图选择；当前交付是这一步的两版造型候选。没有制作动作帧、安装游戏素材或修改仓库。

## A 最终原稿提示词

Make a SQUARE 1024x1024 transparent PNG of ONE tiny pixel-art videogame sprite.
FIRST image: replace ONLY the gray silhouette with a colored Fizz game sprite, preserve EXACT silhouette size and position. Remove guides and background. MOST of canvas stays empty. Sprite from top to soles exactly34 chunky pixels high, at8x =272screen pixels. Its feet y792–799. Center between feet x512.
SECOND image: match Tristana's ACTUAL 34-pixel sprite scale, color shading and drawing style. Do not use detailed illustration styling.
Fizz is a cyan small amphibian with a round13-pixel-high head, two drooping long blue fin ears with orange inner frills, pale crown spots, cream belly, navy webbed feet, short blue tail gold ring. Three-quarter FRONT facing RIGHT. Two green eyes SAME height: near3pixels wide, far2pixels wide, pupils right, tiny dark grin. Each hand2x2pixels connected to thick arm. Both hands horizontally hold a LONG crimson trident waist-high, head RIGHT, green/gold butt LEFT. Total weapon56pixels long. Three jade-teal prongs, white steel edges, blue gem. ONE-pixel navy-black outline,24colors maximum, hard flat blocks. Every cell EXACT8x8 with no smaller details. No blur, antialiasing, glow, gradients, shadows, text, grid, black background, magenta background. One isolated TINY 34-pixel sprite on alpha transparency; no giant character. VERSION A ONLY.

## B 原稿提示词

Draw ONE SQUARE 1024x1024 PNG of Fizz game-size pixel-art design B, alpha transparent.
FIRST reference ONLY SIZE/PLACE: replace tiny gray silhouette exactly there, erase all lines/background. Body top to feet34 logical pixels at8x=272px, crown logical row66, feet lowest row99 y792–799, feet midpoint x512. Entire tiny sprite around lower center of a mostly empty canvas. Long trident56 logical pixels wide.
SECOND reference is mandatory style and coarse pixel scale: match Tristana's34pixel sprite, not illustration art.
THIRD reference is version A character. Keep SAME body colors, long floppy orange-lined blue fin-ears, cream belly, navy webbed feet, short tail/gold ring, and waist-high horizontal crimson trident held in BOTH hands, jade/steel three-prong head RIGHT, green/gold buttLEFT, blue gem/silver bands. Same silhouette and weapon, SAME total34pixel bodyheight.
VERSION B change ONLY head and eyes: head15logical pixels high instead of13, body slightly shorter; face turned more FRONT while still looking RIGHT. BOTH eyes EXACTLY3logical pixels wide and2pixels high, on SAME rows, equally sized. White + lime iris + rightward black pupil, heavy blue lids, 1–2 blue cells between eyes, dark3cell sly grin. No nose/hair/teeth. Eyes remain readable and unoccluded. Long ear fins must not cover eyes.
Strict ONE8x8 flat screen block per gamepixel, ONE1cell near-black silhouette outline, at most24colors, clean intentional colored2–3tone material shading like reference2. No subpixel detail, gradients, blur, noise, halo, glow, shadow, grid, labels or extra sprites. Everything below y799 fully transparent. Only this tiny34pixel-high sprite, no enlarged illustration.

