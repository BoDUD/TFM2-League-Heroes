# 巴德：真正的侧面（给 Codex 的提示词）

> 上一轮的两张侧面其实是正面的头和号角平移了 3 格，身体没有转过去；而且你把细稿缩到 12 像素格子时糊了。这一轮**只要细稿，不要缩**：
> - 照你自己的正面细稿（附图 1：`raw/front-01.png`，约 **8 像素一格**的干净像素画）**同样的画法、同样的格子大小、同样的身高**，画巴德的**正侧面朝右**——所有动作都会从这张侧面画出来。
> - **大小和位置**（附图 6）：1024×1536 竖版、真透明背景；**鬃毛顶在 y≈340（绿线）**，**脚底在 y≈1392（红线）**，**两脚中间在 x≈600（蓝线）**；天线、乐器可以高出鬃毛顶，号角往后（画面左边）伸。附图 6 里淡淡的影子是正面细稿，侧面要和它一样高。
> - **身体是正侧面**：胸口、圆肚子、红色挂布朝右（侧过来只看到挂布的侧边一窄条），近侧（离看画的人近的一侧）肩膀和胳膊在身体前面，远侧胳膊大部分被挡住；**两条柱子腿一前一后**（近侧腿在前、颜色亮；远侧腿在后、暗一档），脚尖朝右；腰侧的金铃铛、深蓝灰腰布、紫流苏、深酒红灯笼裤照正面。参考附图 3（英雄联盟模型的侧面）。
> - **乐器还扛在近侧肩上**（附图 3、5）：近侧的大手握着金色喇叭口举在头旁边（青绿圆球朝前/朝右），**象牙号角从肩膀上往后弯、顺着背在画面左边垂下来**，几道棕色皮带，下面挂两三个小金铃。
> - **头不变成侧脸**：还是那团圆圆的浅绿白鬃毛 + **同一个青铜面具**（附图 1、2 的面具：两个金色眼孔 + 一个嘴孔），面具往鬃毛团的右边挪一点表示他朝右看，**两个眼孔和嘴孔都看得到**；天线 + 金珠。不要画鼻子、不要画侧脸轮廓。
> - **风格完全照附图 1**：约 8 像素一格、一格一色、外轮廓 1 格近黑描边、每种材质 3–4 档平涂、干净清楚；不要糊、不要柔光、不要渐变。附图 2 是附图 1 缩成游戏里的样子（8 倍），侧面缩下来要和它一样的比例（鬃毛团大、腿短、敦实）。
> - **不要自己缩小、不要再按 12 像素格子整理**——我这边会按格子读回再缩到游戏大小。只去掉背景（真透明），别的不动。
> - 不画特效（米普、星光、传送门、金色穹顶），不画地面和影子。
> - 交付：`outputs/bard-side/bard-side-draft.png`（就是生成的细稿，背景透明）；如果画了两版，再交一张 `bard-side-draft-2.png`；所有原始生成稿放 `outputs/bard-side/raw/`；`generation-prompts.txt` 写实际用的提示词；**最后**写 `outputs/bard-side/HANDOFF.md`。

## 附图（压缩包 `bard_side_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_front_draft.png` | 你自己的正面细稿（约 8 像素一格） | **画法、格子大小、颜色、所有细节** |
| `2_front_in_game.png` | 这张细稿缩成游戏造型的样子（8 倍放大，一格 = 游戏里的一个高清像素） | 缩下来的比例（侧面要一样敦实） |
| `3_league_side.png` | 英雄联盟模型转到侧面朝右（待机 + 两帧跑步） | **侧面的身体怎么转、乐器在侧面怎么扛** |
| `4_league_head.png` | 头的特写 | 鬃毛、面具、天线 |
| `5_league_instrument.png` | 乐器扛在肩上的特写 | 号角、皮带、铃铛、喇叭口 |
| `6_size_guide.png` | 画布：绿线 = 鬃毛顶 y≈340，红线 = 脚底 y≈1392，蓝线 = 两脚中间 x≈600；淡影是正面细稿 | **大小和位置** |

## 提示词

六张图都附上（工具一次最多 5 张时：1、3、6 必附，再附 2 和 5）。

```text
Attached: image 1 is YOUR OWN detailed pixel-art front view of this character (about 8 x 8 output pixels per square, a one-square near-black outline, flat 3-4 step shading) - copy its drawing style, square size, colours and every detail exactly; image 2 is that drawing brought down to the game's size (8x) - keep those stocky proportions; image 3 is the game's 3D model seen side-on facing right (idle and two running frames): how the body turns and how the instrument sits on the shoulder from the side; images 4 and 5 are close-ups of the head and of the instrument; image 6 is the canvas with guide lines (green: top of the mane, red: soles, blue: the point between the feet) and the front drawing faint behind them for the size.
Draw ONE full-body picture of the SAME character - Bard: a big fluffy pale green-white mane round a small round bronze mask with two glowing golden eye holes and one golden mouth hole, a short antenna with a golden bead, sage-green skin, big olive-brown hands, red-and-dark-purple striped bracers, a red tabard with orange swirls, a brown belt, a dark blue-grey waist cloth with purple tassels, a golden bell at the hip, loose dark wine-red trousers, two thick dark iron peg feet, the instrument on his near shoulder - but SIDE-ON FACING IMAGE RIGHT: the body in full profile, chest and round belly facing right (only a narrow strip of the red tabard showing at the front), the near shoulder and near arm in front of the body, the far arm mostly hidden, the two peg legs one ahead of the other (the near leg in front in full tone, the far leg behind a shade darker), the feet pointing right. The near hand holds the golden bell-mouth up beside his head (the teal orb facing forward), the ivory horn arching back over the shoulder and hanging down his back on the image left with a few brown leather bands and two or three small golden bells under it.
THE HEAD IS NOT A PROFILE: the same round fluffy mane and the SAME bronze mask as image 1, the mask moved a little toward the right side of the mane as if he looks right, both golden eye holes and the mouth hole still visible; no nose, no side face.
Size and place exactly as image 6: a 1024x1536 portrait PNG with a genuine transparent background, the top of the mane at y 340, the soles at y 1392, the point between the feet at x 600; the antenna and the instrument may go higher, the horn reaches back to the left; nothing cut off.
Style exactly like image 1: crisp clean pixel art on even squares of about 8 x 8 output pixels, every square one flat colour, a one-square near-black outline, each material in 3-4 flat shades, no dithering, no gradients, no soft glow, no blur, no anti-aliasing. Do NOT reduce or re-grid it to bigger squares afterwards. No effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 1024×1536、真透明背景；鬃毛顶 y≈340、脚底 y≈1392、两脚中间 x≈600；和正面细稿一样高。
- **身体真的是正侧面**：胸口肚子朝右、挂布只露一窄条、两条柱子腿一前一后、脚尖朝右。
- 乐器在近侧肩上：大手握着金喇叭口在头旁边，象牙号角往后弯、顺背垂在画面左边，小金铃挂在下面。
- 头：同一团圆鬃毛 + 同一个青铜面具，两个眼孔和嘴孔都看得到；不是侧脸。
- 画法和附图 1 一样（约 8 像素一格、1 格近黑描边、平涂、干净）；**没有缩小、没有按 12 像素格子整理**。
- 没有特效、地面、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述。
- 最后写 `outputs/bard-side/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/bard/codex_side/`（含 raw/），用 `tools/art/design_bard_hd.py` 同样的流程缩到 51 行：regrid 读回 → 正面的调色板 → 多数投票 → 贴正面的面具（同一张脸，只平移）、喇叭口 → 号角 / 铃铛按需要补 → 补缝 → 外描边加 1 格 → 两遍平整；和正面在游戏大小下并排给用户看。
- 定了以后写第 2 步 MODEL_STRIPS.md：所有动作从侧面画，头用正面的面具，跑步按 Caitlyn 的交叉步，乐器是刚体；同样让 Codex 交细稿、由我缩。
