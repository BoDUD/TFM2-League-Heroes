# 蔚：新造型的动作（第 4 版，给 Codex 的提示词）

> 新造型已经定了：`master/vi_approved_master.png`（你上一轮画、用户认可的那张，3/4 侧面朝右、拳击架势）。它在游戏里会被我们读成 40 格高（`master/vi_ingame_40.png`）。
>
> **这一轮只需要像画主稿那样，一帧一张地生成动作**，别的都交给我们：
> 1. **每一帧单独一张 1254×1254 的图**，和主稿**完全同一个人、同一种大方块画风、同样大**：头和主稿一样大，站着时人和主稿一样高（约 719 px）；站着的帧脚底踩在主稿的地面线 y=1189 上，两脚中间对准 x=635（`master/vi_scale_guide.png` 里的红线）。跳起、弓步、蹲下就照这条地面线和这个站位点摆。
> 2. **不要读回网格、不要缩小、不要用代码拼、不要贴头**——生成出来的原图直接交，我们自己按主稿同样的格子读成 40 格。只要每张都和主稿一样大、一样的方块大小，读出来就一致。
> 3. 每张生成后自己对照主稿检查：人是不是同一个、头是不是一样大、两只拳套是不是一样大（每只都是主稿那么大）、脚底是不是在地面线上；不对就重画这一张。
> 4. 动作照英雄联盟（`pose/lol_pose_<动作>.png` 每帧一格，`lol_side/` 是侧面）：都从拳击架势出发、回到拳击架势。**死亡要整个人都在**：头、身体、两只手臂和拳套、两条腿每一帧都画全，只是越来越低、蜷起来，最后跪伏在拳套上（`ref_structure/oppi_vi_structure.png` 的 dead 3、dead 6 那种紧凑倒法，只看结构、不许照描）。
> 5. 不画任何特效（冲击波、拖尾、地裂、光芒都另外做好了）。
> 6. 待机不用画（我们用定稿做呼吸）。

## 交付

放在 **`outputs/vi-strips-v4/frames/`**：`vi_<动作>_<帧号>.png`（帧号从 1 开始，例如 `vi_attack_3.png`），每张 1254×1254、透明背景（做不到就纯绿 `#00FF00`）。附 `HANDOFF.md`（哪些帧重画过几次、有没有没做到的）和 `generation_prompts.json`。一共 50 张。

## 通用提示词

附图顺序：`master/vi_approved_master.png`（第一张，长相、画风、大小都照它）、`master/vi_scale_guide.png`（地面线和站位点）、这个动作的 `pose/lol_pose_<动作>.png`（姿势）。

```text
Pixel art game sprite of Vi from League of Legends, the SAME character as the FIRST image (the same design, costume, colours, face, hair and huge hextech gauntlets, the same chunky square pixels and the same size in the picture: the head as big as in the FIRST image, the figure as tall when standing), 3/4 view facing right, ONE pose: [pose]. Canvas 1254 x 1254, the figure placed like the FIRST image: when she stands, the soles on the same ground line and the point between her feet on the same column (see the guide). Hard edges, one dark outline, no anti-aliasing, no blur. Both gauntlets always the size of the FIRST image's. Transparent background (else pure green #00FF00, never magenta). No text, no shadow, no effects, no ground.
```

## 每个动作

| 动作 | 帧数 | 每帧毫秒 | 出手帧 |
|---|---|---|---|
| 移动 `run` | 8 | 105 / 105 / 105 / 105 / 105 / 105 / 105 / 105 | — |
| 普攻（直拳） `attack` | 6 | 60 / 60 / 70 / 70 / 70 / 70 | 3 |
| E 透体之劲（高举砸拳） `attack_e` | 6 | 60 / 60 / 50 / 80 / 80 / 70 | 4 |
| Q 强能冲拳·蓄力 `skill` | 4 | 125 / 125 / 125 / 125 | — |
| Q 强能冲拳·冲刺 `skill_dash` | 3 | 90 / 90 / 87 | 1 |
| R 天霸横空烈轰·起步 `ult` | 2 | 66 / 67 | 2 |
| R 天霸横空烈轰·冲锋 `ult_dash` | 6 | 125 / 125 / 125 / 125 / 125 / 125 | — |
| R 天霸横空烈轰·上勾拳砸地 `ult_slam` | 5 | 60 / 70 / 70 / 70 / 63 | 2 |
| 受击 `hit` | 2 | 100 / 100 | — |
| 死亡 `dead` | 8 | 100 / 100 / 110 / 120 / 130 / 150 / 200 / 500 | — |

### 移动：`vi_run_1.png` … `vi_run_8.png`

[pose] = `RUN, a seamless 8-frame loop (League's run, pose/lol_pose_run.png and lol_side/lol_run_side.png): she runs to the right in her guard - body upright, leaning a little forward, BOTH huge gauntlets held up in front of her chest like the master (never dropped, never swung behind); long strides, the legs ALTERNATE (frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames), the back foot kicked up behind to knee height; the head bobs at most one square.`

### 普攻（直拳）：`vi_attack_1.png` … `vi_attack_6.png`

[pose] = `BASIC ATTACK, a straight punch (League's attack, pose/lol_pose_attack.png): 1-2 from the guard she cocks the near (front) gauntlet back a little, the far fist stays up by her cheek; 3 THE PUNCH (the blow lands here): she steps in and drives the near gauntlet straight forward to the right at chest height, arm fully out, the far fist still guarding; 4 the fist still out; 5 pulling it back; 6 back in the guard.`

### E 透体之劲（高举砸拳）：`vi_attack_e_1.png` … `vi_attack_e_6.png`

[pose] = `RELENTLESS FORCE, an overhead hammer punch (League's E, pose/lol_pose_attack_e.png, lol_side/lol_e_side.png): 1 a jab-like wind-up from the guard; 2 the gauntlet raised high over her head; 3 she lunges forward; 4 THE SLAM (lands here): a deep lunge to the right, the body leaning low and forward, the front knee bent, the back leg straight, the gauntlet smashing down-forward at knee height in front of her, the other arm pulled back; 5 holding the lunge; 6 rising back into the guard. No shockwave (a separate effect).`

### Q 强能冲拳·蓄力：`vi_skill_1.png` … `vi_skill_4.png`

[pose] = `VAULT BREAKER, the charge (League's Q charge, pose/lol_pose_skill.png): she stays in place 0.5 s: 1 she drops a little lower in the guard; 2-4 the near gauntlet pulled back low beside her hip, the body coiled and leaning back, the far fist up in front guarding; 3-4 straining (the pulled gauntlet one square further back in 4). No glow effect (separate).`

### Q 强能冲拳·冲刺：`vi_skill_dash_1.png` … `vi_skill_dash_3.png`

[pose] = `VAULT BREAKER, the dash (League's Q dash, pose/lol_pose_skill_dash.png), held while she rockets forward: a low forward-leaning lunge to the right, the near gauntlet thrust straight out in front at chest height (it hits from frame 1), the other arm back behind her at shoulder height, the legs trailing; frames 1-3 nearly the same (the trailing leg moves a little). No trail (separate).`

### R 天霸横空烈轰·起步：`vi_ult_1.png` … `vi_ult_2.png`

[pose] = `CEASE AND DESIST, the launch (League's R start, pose/lol_pose_ult.png): 1 she plants her feet in a low guard, both gauntlets in front of her body; 2 crouched lower, leaning forward, about to spring (she launches after it).`

### R 天霸横空烈轰·冲锋：`vi_ult_dash_1.png` … `vi_ult_dash_6.png`

[pose] = `CEASE AND DESIST, the charge, a 6-frame loop (League's R run, pose/lol_pose_ult_dash.png), held while she rushes at the target: a fast sprint leaning hard to the right, the far gauntlet cocked back high over her shoulder, the near gauntlet low in front, long strides with the legs alternating. No trail (separate).`

### R 天霸横空烈轰·上勾拳砸地：`vi_ult_slam_1.png` … `vi_ult_slam_5.png`

[pose] = `CEASE AND DESIST, the slam (League's R hit, pose/lol_pose_ult_slam.png): 1 arriving low, both fists close in front; 2 THE UPPERCUT (the knock-up lands here): she drives the near gauntlet straight up high above her head, rising on her toes; 3 the fist coming down from above; 4 crouched low after the slam, both gauntlets near the ground in front; 5 rising back into the guard. No ground crack (separate).`

### 受击：`vi_hit_1.png` … `vi_hit_2.png`

[pose] = `HIT (League's hit, pose/lol_pose_hit.png): 1 jolted back by a blow in her guard - head and shoulders pushed back a little, eyes squeezed shut (two short dark lines), the gauntlets jolting with her; 2 recovering toward the guard, eyes open.`

### 死亡：`vi_dead_1.png` … `vi_dead_8.png`

[pose] = `DEATH (League's death, pose/lol_pose_dead.png; the compact fall of ref_structure/ is the target): 1-2 struck, she staggers back, the guard breaking, the gauntlets sagging; 3-4 she drops to one knee, then both knees; 5-6 kneeling and slumping forward, the gauntlets resting on the ground in front of her; 7-8 slumped over her gauntlets on the ground. THE WHOLE BODY IS DRAWN IN EVERY FRAME - head, torso, both arms and gauntlets, both legs - only lower and folded; never a part missing, never pieces scattered (the last strips lost the body here).`

