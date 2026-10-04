# 瑟提（Sett，腕豪）原图提示词包 · 第 0 步

**给用户（中文说明）**：瑟提还没有原图。请把整个 zip 交给 Codex，它按下面的英文提示词画**两张**高清像素风原图，
同一个人物、同一画风、同一镜头和比例，只差姿势：
- **A**：战斗待机（拳击架势）——略微下蹲的宽站姿，双拳握紧举在身前，远侧的拳在前、近侧的拳护在下巴旁。他的普攻是左右拳交替，这个姿势接动作最顺。
- **B**：「老大」站姿——站直挺胸、下巴微抬、嘴角带笑；近侧的拳垂在身侧，远侧的手握拳举到胸前（像在捏响指节）。

你挑一张，第 1 步再按它画游戏尺寸的精灵（约 40 行，和亚托克斯、德莱厄斯一样的大块头上单）。

**要你补的参考图**：这个会话在云端，连不上英雄联盟客户端，网络策略也挡住了英雄联盟的素材站（只放行 GitHub），
没法像以前那样把英雄联盟的模型渲染出来给 Codex 当参考。请把下表 3–5 号放进 zip 的 `refs/` 里再交给 Codex：
官方原画可以从客户端的英雄页或官网存，游戏内的样子可以在客户端「收藏 → 英雄 → 瑟提」里看模型截图。
补不了也能画（提示词里写了完整的外观描述，Codex 也认识这个英雄），只是衣服细节可能不准。
或者在云端环境的网络设置里放行 `raw.communitydragon.org`，我就能像以前一样渲染英雄联盟的模型和动作当参考。

- **长相照英雄联盟原版（经典皮肤）**：半瓦斯塔亚人的大块头拳手，宽肩厚胸、手臂粗壮、腰窄；**深酒红色长发**整体往后梳、
  在脑后蓬起垂到后颈；**金色的眼睛**，自信的坏笑，露一点尖牙。**赤裸上身**，外面披一件**敞开的长外套（毛领）**；
  **双手和前臂缠着绷带**，拳头是他的武器，要**画得大**（每只拳头差不多和头一样大）；宽松长裤配腰带，靴子。
  细节（外套的颜色和长短、毛领、项链、耳朵）**以 3–5 号参考图为准**，我的描述是凭记忆写的。
- **风格照 1、2 号**（你之前画的凯隐、蔚，用户都采用了）：清楚的大像素块、一圈近黑描边、每种材质 3–5 档平涂；
  头比英雄联盟模型大一些（头加头发约占身高 25–28%），这样缩到游戏尺寸还看得见脸。深色都用有颜色的深色
  （头发深酒红、外套和裤子各自的深色），黑色只用在描边。
- 不画任何特效（拳头的光、护盾、冲击波都等第 3 步单独画）；**脚底是最低点**，外套下摆、腰带不能低于脚底线（游戏在脚下画血条）。
- **背景**：真透明；做不到就用纯绿 `#00FF00`，**不要洋红色**（他的头发和外套是红色系，会被一起抠掉）。
- 交付：`outputs/sett-picture/` 里的 `sett-model-A.png`、`sett-model-B.png`（1024×1536，真透明，人物约 1100 px 高），
  附一个 `generation-prompts.txt` 写明实际用的提示词，**最后**写 `HANDOFF.md`（交付说明）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `style/1_style_kayn.png` | 你之前画的凯隐原图 A（用户采用） | **只看画风**：赤裸上身的男性英雄、肌肉的画法、深色的亮边 |
| `style/2_style_vi.png` | 你之前画的蔚原图 A（用户采用） | **只看画风**：拳手、超大的拳头怎么画清楚 |
| `refs/3_sett_splash.png` | **（要你补）**瑟提经典皮肤的官方原画 | 长相、服装、气质 |
| `refs/4_sett_ingame_front.png` | **（要你补）**游戏内模型，3/4 正面 | 服装和配色（以它为准） |
| `refs/5_sett_head.png` | **（要你补）**头部特写 | 发型、眼睛、表情 |

图像工具一次最多收 5 张参考：就是上面这 5 张，按顺序附上。没有 3–5 号时只附 1、2 号，提示词照用。

## 提示词 A：`sett-model-A.png`（战斗待机：拳击架势）

```text
Attached images, in order: 1 and 2 are STYLE ONLY - pixel-art pictures of OTHER characters from the same game that the user approved (1: a shirtless male fighter, 2: a woman brawler with huge fists); copy their pixel-art style and their way of drawing muscles and big fists, NOT their costumes, colours or poses. Images 3-5, if attached, are the character from League of Legends (3 the official illustration, 4 the in-game model 3/4 front, 5 the head): they are authoritative for his look - copy the costume, the hair and the colours from them, NOT their 3D shading or painted lighting. If images 3-5 are not attached, draw Sett, the Boss, from League of Legends in his classic (base) look as you know it.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha; if impossible, a flat pure green #00FF00 background - never magenta or pink), the character about 1100 px tall from the top of the hair to the soles, centred, with at least 60 px of transparent margin all round.
The character: Sett, the Boss - a towering half-vastayan pit fighter, the strongest brawler of the fighting pits. A very muscular build: broad shoulders, a huge chest, thick arms, a narrow waist, sturdy legs. HEAD: long DARK WINE-RED hair slicked back from his forehead and swept back into a thick mane down to the nape; GOLDEN eyes; a cocky, confident grin showing a hint of sharp fangs; a strong jaw. BODY: bare muscular chest and abs under an OPEN long coat with a shaggy fur collar (take its colours, length and trim from images 3-4). HANDS: both hands and forearms tightly WRAPPED like a boxer's, the FISTS big and solid - they are his weapons and must read clearly at small size, each fist about as big as his head. Loose trousers with a sash or belt, sturdy boots.
Proportions: game-sprite proportions like images 1 and 2 - a bigger head than the 3D model (the head with its hair about 25-28% of his height), the fists a little oversized; heroic and massive, not stocky or fat. 3/4 FRONT view facing image right: face and chest turned toward the viewer's right, BOTH eyes visible, level and the same size, nothing covering the face; never his back or a pure side view.
Pose: a boxer's fighting guard - a slightly crouched wide stance, knees bent, feet apart on one flat ground line, weight forward; the FAR fist held forward at chest height, the NEAR fist raised beside his chin; elbows in, shoulders hunched a little, the grin on his face. The soles are the lowest thing in the picture: the coat's tails and the sash end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 1 and 2 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep maroon for the hair, the coat's and the trousers' own dark tones - never black fill, black is only the outline); light rim lights and highlights on the muscles, the hair, the fists and the coat; warm tan skin with clear shading of the chest, abs and arms; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No glowing fists, no shockwave, no shield, no effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 提示词 B：`sett-model-B.png`（「老大」站姿）

附图同上。

```text
Attached images, in order: 1 and 2 are STYLE ONLY - pixel-art pictures of OTHER characters from the same game that the user approved (1: a shirtless male fighter, 2: a woman brawler with huge fists); copy their pixel-art style and their way of drawing muscles and big fists, NOT their costumes, colours or poses. Images 3-5, if attached, are the character from League of Legends (3 the official illustration, 4 the in-game model 3/4 front, 5 the head): they are authoritative for his look - copy the costume, the hair and the colours from them, NOT their 3D shading or painted lighting. If images 3-5 are not attached, draw Sett, the Boss, from League of Legends in his classic (base) look as you know it.
Create ONE full-body pixel-art picture of this character, 1024x1536 portrait PNG with a genuine transparent background (real alpha; if impossible, a flat pure green #00FF00 background - never magenta or pink), the character about 1100 px tall from the top of the hair to the soles, centred, with at least 60 px of transparent margin all round.
The character: Sett, the Boss - a towering half-vastayan pit fighter, the strongest brawler of the fighting pits. A very muscular build: broad shoulders, a huge chest, thick arms, a narrow waist, sturdy legs. HEAD: long DARK WINE-RED hair slicked back from his forehead and swept back into a thick mane down to the nape; GOLDEN eyes; a cocky, confident grin showing a hint of sharp fangs; a strong jaw. BODY: bare muscular chest and abs under an OPEN long coat with a shaggy fur collar (take its colours, length and trim from images 3-4). HANDS: both hands and forearms tightly WRAPPED like a boxer's, the FISTS big and solid - they are his weapons and must read clearly at small size, each fist about as big as his head. Loose trousers with a sash or belt, sturdy boots.
Proportions: game-sprite proportions like images 1 and 2 - a bigger head than the 3D model (the head with its hair about 25-28% of his height), the fists a little oversized; heroic and massive, not stocky or fat. 3/4 FRONT view facing image right: face and chest turned toward the viewer's right, BOTH eyes visible, level and the same size, nothing covering the face; never his back or a pure side view.
Pose: "the Boss" - he stands tall and relaxed, chest out, chin slightly raised, the grin on his face; feet apart on one flat ground line, weight on the back leg, the front foot a step ahead; the NEAR arm hangs by his side with the fist clenched; the FAR hand is raised to his chest, clenched into a fist as if cracking his knuckles (the fist in front of his far shoulder, not covering the face). The soles are the lowest thing in the picture: the coat's tails and the sash end AT OR ABOVE the soles line (the game draws the health bar under it).
Style: detailed crisp pixel art like images 1 and 2 - chunky square pixels about 8-10 output pixels each, a one-pixel near-black outline around the silhouette, inside it every material in its own 3-5 flat shades (coloured darks: deep maroon for the hair, the coat's and the trousers' own dark tones - never black fill, black is only the outline); light rim lights and highlights on the muscles, the hair, the fists and the coat; warm tan skin with clear shading of the chest, abs and arms; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No glowing fists, no shockwave, no shield, no effects, no background, no ground, no shadow, no text, no frame, no other characters.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格、不是黑底）；做不到就是纯绿 `#00FF00`，**不是洋红**；四周留边，人物完整，拳头没被切掉。
- 面朝右的 3/4 正面；两只眼睛都看得见、同一高度、一样大、金色；脸没被拳头挡住；深酒红的长发往后梳。
- 赤裸上身、敞开的毛领长外套、缠着绷带的大拳头都清楚；缩到 40 px 高还认得出「红色背头 + 大块头 + 两只大拳头」。
- 脚底是最低点，外套下摆、腰带都不低于它；没有光效、冲击波、护盾。
- 大像素块清楚，没有糊、没有柔光、没有渐变；深色部分有颜色（不是一片纯黑）。
- 如果模型不肯画有名字的角色，把提示词里的名字删掉，只留外观描述。
- 全部画完后最后写 `outputs/sett-picture/HANDOFF.md`（列出交付的文件），这样我这边知道已经交付完了。

## 之后的步骤（给用户看，Codex 这一轮不用管）

1. **第 1 步造型**：按选定的 A 或 B，直接画游戏尺寸（约 40 格，头发顶到脚底），8 倍方格；读回后给你看，选定再往下。
2. **第 2 步动作**：标签和出手时机已经在技能数据里定好（`tools/kit/sett_kit.py`）：
   | 标签 | 内容 | 时长 / 出手 |
   |---|---|---|
   | `idle` / `run` | 待机、移动（照英雄联盟的走路节奏） | — |
   | `attack` | 左拳刺拳 | 0.4 秒，第 12 tick 打中 |
   | `attack2` | 右拳重拳（更快） | 从第 3 tick 播 21 tick，第 9 tick 打中 |
   | `skill` | E 强手裂颅：双手往两侧一抓、拽回来对撞 | 0.5 秒，第 10 tick 抓住，第 18 tick 对撞 |
   | `skill2` | W 蓄意轰拳：拳头往后拉蓄力，一拳轰出 | 0.9 秒，第 29 tick 出拳 |
   | `ult` | R 抓起英雄、往前扔 | 前 8 tick |
   | `ult_dash` | R 跃起追上去（空中） | 循环，到落地为止 |
   | `ult_slam` | R 双拳砸地、起身 | 0.4 秒，第 4 tick 砸中 |
   | `hit` / `dead` | 受击、死亡 | — |
3. **第 3 步特效**：`league_sett_fx`（普攻左右拳命中、屈人之威的金色拳光和命中、E 抓中、W 护盾、W 真伤命中、R 抓取和命中、满豪意的热浪）
   和 `league_sett_big`（W 拳头冲击波和地面预警、E 对撞的爆点、R 砸地的大坑）。
