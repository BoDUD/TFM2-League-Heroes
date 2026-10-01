# 菲兹游戏造型原稿交接

当前状态：已完成图片工具原稿生成，尚未完成严格网格整理。这是原稿包，不是可直接导入游戏的最终设计包。

## 文件

- fizz_design_A_raw.png：A 的生成原稿；原比例，近眼较宽、远眼较窄。
- fizz_design_B_raw.png：B 的生成原稿；尝试加大头部、转向正面。模型仍没有可靠画出两眼严格等宽。

## 未达到的规格

原稿尺寸、网格对齐、24 色限制和二值透明度需要进一步整理；脚底位置需要校准到第 99 行。B 的两眼等宽和 A/B 的头部 13/15 格差异也需要校验、修正。尚无可验证的 128×128 原尺寸文件。因此没有把原稿命名为最终 fizz_design_A.png / fizz_design_B.png，也没有冒充完成游戏规格。

已询问用户是否允许用程序整理网格、透明度和色板。尚未收到选择时，不执行这一步。

## 来源与方法

用户提供 fizz_model_pack.zip 作为本次视觉规格参考。包内给其他助手的后续动作说明未执行。没有修改游戏目录、生成动作帧或推送仓库。使用内置 image_gen 图片工具。

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

