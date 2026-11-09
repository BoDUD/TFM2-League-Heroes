# 泽丽：照英雄联盟原版重新设计，按 PPU 3 画设计图（给 Codex 的提示词）

> 泽丽现在游戏里的造型（附图 6）**用户不满意，这次不要照它画**，而是**照英雄联盟原版的泽丽重新设计**（附图 1–4；附图 5 是同一个英雄联盟模型换成本游戏 Q 版比例的样子）。她是**祖安的电火花**：头上**两个刺刺的发髻**（**黄绿色、发梢带深青色**，**发髻的尖是最高处**）、**绿色的眼睛**、脸颊上**一个小标记**；**深青色的外套**、**白色的毛领**；**黄色的上衣**、胸前**一道闪电图案**；**暗红色的紧身裤**和**护膝**；**棕色的靴子**；手里一把**黄绿色的电能步枪**。按 **PPU 3**，**每个游戏像素画成 3 格**，发髻的尖到脚底约 **111 格**，和本包其他英雄差不多的密度（附图 8–10）。
> - **长相、发型、衣服、颜色全部照英雄联盟原版**（附图 1–4），**头和身体的比例照附图 5**（本游戏的 Q 版比例：头大一些、腿短一些）：
>   - 头：**两个刺刺的发髻**（黄绿色、发梢深青色，最高处）、前面的**刘海**、**绿色的眼睛**、脸颊上的**小标记**、嘴。
>   - 上身：**深青色的外套**（敞开，袖子卷起）、**白色的毛领**、**黄色的上衣**和胸前的**闪电图案**、腰上的**皮带和挂件**。
>   - 腿：**暗红色的紧身裤**、膝盖上的**护膝**、**棕色的靴子**，两脚站稳。
>   - 步枪：**黄绿色的电能步枪**，样子照附图 1–4。
>   - **头的大小就是以后每个动作都要保持的大小**，照附图 5 的比例画。
> - **姿势和大小照附图 6**（**只看这两样，它的长相、发型、衣服、颜色都不要照**）：面朝右站着，两脚分开，**画面右边的手把步枪竖着举在身前**（枪口朝上），**画面左边的手放在身侧**。整个人的高度和站的位置照附图 7。
> - **朝向**：和附图 6 一样；近侧颜色亮，远侧稍暗。
> - **脚底碰到附图 7 的深灰线**（游戏里用这条线定位置），不画地面、不画影子。
> - **画布用 1024×1024**：**发髻的尖到脚底约 666 px（约 111 格）**，脚底在离画布底边约 64 px 的地方（附图 7 的深灰线），发髻的尖碰到附图 7 的浅灰线（附图 7 只看大小和位置）。整个人都在画面里。
> - **像素块**：大小一致的方块，**每块 6 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–5 档平涂，不要零散的单个杂色格。**眼睛、眉毛、嘴和脸颊的标记各自成块，不要糊成一团；发髻的尖刺、毛领、闪电图案和步枪都清楚。** 附图 8–10 是本包的其他英雄（8 倍放大，一格 = 一个像素），**只看风格**。
> - **透明背景要真透明**：每个像素的透明度只能是 0 或 255，**人物外面不要有任何柔光、光晕、半透明边**，也不要画黑色或彩色背景。两腿之间、手臂和身体之间、步枪和身体之间的空隙也是透明的。
> - 不画特效（没有电火花、电弧、光晕、残影，步枪不往外发光），不画地面、影子；**脚底以下什么都不能有**（游戏里血条在脚下）。
> - **不要自己缩放、裁剪或改成别的尺寸**：交付图就是 1024×1024 的原图。
>
> - 交付：`outputs/zeri-ppu/zeri-A.png`（1024×1024，**真透明背景**）；原始生成图原样放进 `outputs/zeri-ppu/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/zeri_ppu_done.zip`。

## 附图（在压缩包 `zeri_ppu_pack.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_zeri_idle.png` | 英雄联盟里的泽丽 | **长相、发型、衣服、颜色照它** |
| `refs/2_zeri_head.png` | 头部特写 | 脸、眼睛、发髻 |
| `refs/3_zeri_back.png` | 从身后看 | 背面、发髻后面 |
| `refs/4_zeri_splash.png` | 官方加载画面 | 气质和配色 |
| `refs/5_zeri_chibi.png` | 同一个英雄联盟模型换成本游戏的 Q 版比例（头 1.6 倍、腿 0.9 倍） | **头和身体的比例照它** |
| `refs/6_zeri_now.png` | 她现在的游戏造型（3 倍，**用户不满意**） | **只看姿势和大小**；长相、发型、衣服、颜色都不要照 |
| `refs/7_layout.png` | 布局示意：现在的造型放大到新尺寸的剪影 | 画布上的大小、脚底的线（深灰）、**发髻的尖要碰到的线（浅灰）** |
| `style/8_style_veigar.png` | 本包的维迦（8 倍，PPU 1.8） | **只看风格** |
| `style/9_style_seraphine.png` | 本包的萨勒芬妮（8 倍，PPU 2.2） | **只看风格** |
| `style/10_style_ezreal.png` | 本包的伊泽瑞尔（8 倍，PPU 2.19） | **只看风格** |

## 提示词：`zeri-A.png`

附图 1–10，顺序同上表（1 = 1_zeri_idle.png, 2 = 2_zeri_head.png, 3 = 3_zeri_back.png, 4 = 4_zeri_splash.png, 5 = 5_zeri_chibi.png, 6 = 6_zeri_now.png, 7 = 7_layout.png, 8 = 8_style_veigar.png, 9 = 9_style_seraphine.png, 10 = 10_style_ezreal.png）。

```text
10 attached images. Images 1-4 show THE CHARACTER TO DRAW: Zeri from League of Legends - image 1 a 3D render of her, image 2 her head close up, image 3 from behind, image 4 the official illustration. Copy her LOOK from them: the TWO SPIKY HAIR BUNS on top of her head, YELLOW-GREEN with DARK TEAL tips (THEIR TIPS her highest point), her bangs, GREEN EYES and the small mark on her cheek; the open TEAL JACKET with its sleeves pushed up and its WHITE FUR COLLAR; the YELLOW TOP with a LIGHTNING BOLT on it; the belt and its straps; the MAROON LEGGINGS with KNEE PADS; the BROWN BOOTS; her YELLOW-GREEN ELECTRIC RIFLE. Image 5 is the same 3D model in THIS GAME'S CHIBI PROPORTIONS (a bigger head, shorter legs): give her these proportions. Image 6 is her CURRENT game sprite, which the user REJECTED: take ONLY its POSE and its SIZE - standing turned to the viewer's right, legs apart, the rifle held UPRIGHT in front of her in the hand on the viewer's right (the muzzle up), the other hand at her side - and copy NOTHING of its looks (not its hair, face, clothes or colours). Image 7 is THIS picture's layout guide: the current sprite as a flat silhouette at the new size - how big the character is and where she stands; the dark grey line marks THE SOLES, the light grey line THE TIPS OF HER HAIR BUNS. Images 8-10 are STYLE ONLY, other characters from the same game shown 8x: copy their pixel-art look and their detail.
Create ONE pixel-art picture, a 1024x1024 PNG with a genuine transparent background (real alpha, every pixel either fully transparent or fully opaque - no black or coloured background, no glow). The tips of her hair buns are about 666 px (about 111 squares) above the soles, the soles about 64 px above the bottom edge; the whole figure inside the picture; nothing at all below the soles. Do not rescale, crop or resize the picture afterwards.
THE CHARACTER (League's Zeri, in image 5's proportions and image 6's pose): the two spiky hair buns and the bangs; the green eyes, the brows, the mouth and the cheek mark each a clear shape, never one muddy blob. The teal jacket with its white fur collar, the yellow top with its lightning bolt, the belt. The maroon leggings, the knee pads, the brown boots planted; both soles on one line. The yellow-green electric rifle held upright in the hand on the viewer's right.
The head the size image 5's proportions give it (it keeps this size in every later animation).
THE VIEW: as image 6; the near side in full tone, the far side a step darker.
THE PIXEL GRID: every square the SAME size, 6 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-5 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no halo, no blur, no anti-aliasing. The gaps in the figure are transparent.
No effects (no sparks, no electric arcs, no glow, no afterimages; the rifle does not glow outward), no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1024、真透明背景，**每个像素透明度只有 0 或 255，没有光晕、没有黑底**；没有被缩放或裁剪。
- **长相、发型、衣服、颜色是英雄联盟的泽丽**（附图 1–4），**比例照附图 5**，**只有姿势和大小照附图 6**（附图 6 的长相一点都不要）。
- 发髻的尖到脚底约 666 px（约 111 格）；脚底碰到深灰线，下面什么都没有。
- 脸上各部分清楚；**每块 6 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；没有特效。
- 画完后最后写 `outputs/zeri-ppu/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zeri_ppu_done.zip`。

## Claude 收到后（给 Claude 看）

- 这次是**照英雄联盟原版重新设计**（用户：「泽丽虽然是高清帧了 但是模型我不满意」，问了以后选「照英雄联盟原版重新设计」，不照现在的模型，也不照用户以前那张图 user_ref/zeri_user.png）。
- **读原图，不读导出图**：原画和 raw/ 放进 `assets/source/zeri/hd/`，照 `tools/art/design_khazix_hd.py`（按原图自己的格子读、每条线贴着最近的色边；脸照格子读，FACES 留空（平均色会把眼睛糊掉）；细线沿骨架铺（THIN）；几种 PPU 给用户选）读回；和本包其他英雄、现在的泽丽按游戏里的大小并排，给用户确认大小、脸、粗细。
- 她的 1 倍精灵现在是 37 行（hd.rs 里 PPU 3、SIZES 1.05）：新设计图按 37 行定 PPU，SIZES 先保留 1.05，给用户看大小时一起确认。
- **对齐点**：用设计图和旧 idle_base 的剪影重叠来定。
- 动作包照 `pack_khazix_actions.py`：跑步逐帧写明哪条腿撑地（第 1–4 帧近侧腿、第 5–8 帧远侧腿）；每帧缩放先按叠合法（`casts_*_hd.py --fits`），再按头（或别的不会变的部件）的大小校正到设计图那么大（第 6 批的 `b6_headzoom.py`；用户：「一定要注意模型不要变大变小」）；外描边 2 格（用户：「避免过度高清」）。
- 和这一批的另外几位在同一个 PR（claude/teemo-ppu）（用户：「最后重做提莫 菲兹 泽丽吧 泽丽虽然是高清帧了 但是模型我不满意」）。
