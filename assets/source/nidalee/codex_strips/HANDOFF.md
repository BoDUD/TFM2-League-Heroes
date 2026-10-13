# Nidalee strips — 未完成交接

**状态：已生图并读回68/68帧（人形32，美洲狮36）。文件齐全；没有通过造型/动作严格验收。**

之前第59帧因 HTTP 429 暂停，本次继续后额度恢复，剩余10帧已全部补齐，并对6帧进行了针对性重画。

## 文件与生成方式

- 每个已生成帧：根目录1536×1024 PNG + 307×204 `_1x.png`，`raw/`保留模型原稿，未重采样。
- 68条实际英文提示词在 `prompts/`。第1帧用文档人形原提示词；之后在原提示词后追加了透明底和禁止放大等提醒。重画的6帧还追加了各自的动作纠正要求，完整记录见 `REPAIRS.json`。
- 工具：原生 image_gen，68次初次成功生图加6次针对性重画；同一动作初次生成时按顺序执行。引用顺序：骨架、造型、画布造型、前一帧（首帧不附）、原画。`MANIFEST.json`列出引用路径。前一帧为调用当时已读回的大图；后续重画不会追溯更新已经生成的下一帧。
- `raw/previous/`保留6张重画前原稿及当时提示词。原生生图原稿共74张；最终选择的68张位于 `raw/`根目录。
- 从原稿每个像素贴到给定56色，再对每个5×5格做多数投票（透明像素也参与），未取中心点。按同一原点逐块写入大图，不调用resize。半透明转为0/255；第197行起清空，所以没有红线以下内容，但原稿超出的轮廓可能被截断。
- 1536×1024不能被5整除：307×204个完整格覆盖1535×1020，右侧1px、底部4px保持透明，与cells.json规格一致。
- `PREVIEW_*.png`为1x帧总览；`VALIDATION.json`为实际技术检查；`cells.json`保留原帧顺序和时长。

## 已检查与未达到的条件

68组文件全部通过：尺寸、5px纯色块、只用原56色色板中的颜色、0/255透明度、大图与1x逐格一致、红线以下及边缘补白透明。每帧不一定用满56种颜色。

**以上只代表文件和网格合格，不代表美术合格。** 模型未实现逐格复制头/枪；人物和美洲狮的大小、骨架对位、脚底/爪底对位、1格外描边、近远腿色差及动作连续性都未完全达到要求。未做头/标枪模板刚体贴回、也未改成游戏资源。最终图已去掉半透明背景，但仍需检查局部残余杂像素。

## 逐帧提示词与问题

| 帧文件 | 用到的英文动作说明（完整提示词见同名txt） | 状态 / 未达到 |
|---|---|---|
| `nidalee_run_1.png` | running to the right, frame 1 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 |
| `nidalee_run_2.png` | running to the right, frame 2 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 可见内容最底为第194行（0起算），接地要求未验收。 |
| `nidalee_run_3.png` | running to the right, frame 3 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 可见内容最底为第195行（0起算），接地要求未验收。 |
| `nidalee_run_4.png` | running to the right, frame 4 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 |
| `nidalee_run_5.png` | running to the right, frame 5 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 可见内容最底为第192行（0起算），接地要求未验收。 |
| `nidalee_run_6.png` | running to the right, frame 6 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 可见内容最底为第193行（0起算），接地要求未验收。 |
| `nidalee_run_7.png` | running to the right, frame 7 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 可见内容最底为第193行（0起算），接地要求未验收。 |
| `nidalee_run_8.png` | running to the right, frame 8 of an 8-frame loop: legs crossing as in Image 1 (one forward, one back), the near arm swinging; the javelin upright in her far hand as in Image 2, bobbing with the stride | 跨步变化不足，多帧姿势近似；头未逐格复制；标枪长度、握持侧和人物尺寸漂移。 可见内容最底为第193行（0起算），接地要求未验收。 |
| `nidalee_attack_1.png` | basic attack, throwing her javelin, frame 1 of 5: the javelin turned a quarter turn to lie level, blade to the right, raised over her near shoulder (her near hand behind the shoulder grips it) | 头未逐格复制，人物/标枪尺寸漂移，身体与骨架不能逐格对位。 可见内容最底为第192行（0起算），接地要求未验收。 |
| `nidalee_attack_2.png` | basic attack, throwing her javelin, frame 2 of 5: drawn back to the full, leaning back, the far arm stretched forward to aim | 头未逐格复制，人物/标枪尺寸漂移，身体与骨架不能逐格对位。 可见内容最底为第192行（0起算），接地要求未验收。 |
| `nidalee_attack_3.png` | basic attack, throwing her javelin, frame 3 of 5: the release: the throwing arm swung forward, the javelin already gone - her hand is empty | 头未逐格复制，人物/标枪尺寸漂移，身体与骨架不能逐格对位。 可见内容最底为第193行（0起算），接地要求未验收。 |
| `nidalee_attack_4.png` | basic attack, throwing her javelin, frame 4 of 5: the follow-through, leaning forward, hands empty | 头未逐格复制，人物/标枪尺寸漂移，身体与骨架不能逐格对位。 可见内容最底为第186行（0起算），接地要求未验收。 |
| `nidalee_attack_5.png` | basic attack, throwing her javelin, frame 5 of 5: back to the standing pose of Image 2, the javelin upright in her far hand again | 头未逐格复制，人物/标枪尺寸漂移，身体与骨架不能逐格对位。 可见内容最底为第195行（0起算），接地要求未验收。 |
| `nidalee_skill_1.png` | Javelin Toss, a full-power throw, frame 1 of 6: crouching to gather power, the javelin level over her shoulder, blade to the right | 头未逐格复制，人物尺寸漂移；skill_2 已重画使枪接近水平，skill_3 仍略倾斜；未达到原枪刚体复制。 可见内容最底为第191行（0起算），接地要求未验收。 |
| `nidalee_skill_2.png` | Javelin Toss, a full-power throw, frame 2 of 6: leaning far back, the javelin drawn all the way back | 头未逐格复制，人物尺寸漂移；skill_2 已重画使枪接近水平，skill_3 仍略倾斜；未达到原枪刚体复制。 可见内容最底为第190行（0起算），接地要求未验收。 |
| `nidalee_skill_3.png` | Javelin Toss, a full-power throw, frame 3 of 6: stepping forward, the javelin starting forward | 头未逐格复制，人物尺寸漂移；skill_2 已重画使枪接近水平，skill_3 仍略倾斜；未达到原枪刚体复制。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_skill_4.png` | Javelin Toss, a full-power throw, frame 4 of 6: the release, the arm at its farthest forward, her hand empty | 头未逐格复制，人物尺寸漂移；skill_2 已重画使枪接近水平，skill_3 仍略倾斜；未达到原枪刚体复制。 可见内容最底为第190行（0起算），接地要求未验收。 |
| `nidalee_skill_5.png` | Javelin Toss, a full-power throw, frame 5 of 6: the follow-through, leaning forward, hands empty | 头未逐格复制，人物尺寸漂移；skill_2 已重画使枪接近水平，skill_3 仍略倾斜；未达到原枪刚体复制。 |
| `nidalee_skill_6.png` | Javelin Toss, a full-power throw, frame 6 of 6: back to the standing pose of Image 2, the javelin upright in her far hand | 头未逐格复制，人物尺寸漂移；skill_2 已重画使枪接近水平，skill_3 仍略倾斜；未达到原枪刚体复制。 可见内容最底为第194行（0起算），接地要求未验收。 |
| `nidalee_skill2_1.png` | casting a spell (a heal or a trap), frame 1 of 4: raising her near hand, the javelin still upright in her far hand | 头未逐格复制，人物尺寸漂移；skill2_2/3 已重画为竖直枪，但保持伸手的动作、握持侧和枪长度仍需严格对照。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_skill2_2.png` | casting a spell (a heal or a trap), frame 2 of 4: the near hand thrust forward, palm open | 头未逐格复制，人物尺寸漂移；skill2_2/3 已重画为竖直枪，但保持伸手的动作、握持侧和枪长度仍需严格对照。 可见内容最底为第195行（0起算），接地要求未验收。 |
| `nidalee_skill2_3.png` | casting a spell (a heal or a trap), frame 3 of 4: holding the cast | 头未逐格复制，人物尺寸漂移；skill2_2/3 已重画为竖直枪，但保持伸手的动作、握持侧和枪长度仍需严格对照。 可见内容最底为第191行（0起算），接地要求未验收。 |
| `nidalee_skill2_4.png` | casting a spell (a heal or a trap), frame 4 of 4: back to the standing pose | 头未逐格复制，人物尺寸漂移；skill2_2/3 已重画为竖直枪，但保持伸手的动作、握持侧和枪长度仍需严格对照。 可见内容最底为第194行（0起算），接地要求未验收。 |
| `nidalee_transform_1.png` | turning into a cougar, frame 1 of 3: bending her knees, crouching low, leaning forward, the javelin still upright in her hand | 头未逐格复制，人物尺寸漂移；3/4 正面胸部朝向及四肢支撑与表格要求仍需修正。 可见内容最底为第187行（0起算），接地要求未验收。 |
| `nidalee_transform_2.png` | turning into a cougar, frame 2 of 3: dropping her hands to the ground as if to pounce, the javelin let go (do not draw it) | 头未逐格复制，人物尺寸漂移；3/4 正面胸部朝向及四肢支撑与表格要求仍需修正。 可见内容最底为第190行（0起算），接地要求未验收。 |
| `nidalee_transform_3.png` | turning into a cougar, frame 3 of 3: lunging forward on all fours (a burst of light will cover her here - do not draw it) | 头未逐格复制，人物尺寸漂移；3/4 正面胸部朝向及四肢支撑与表格要求仍需修正。 |
| `nidalee_dead_1.png` | dying, frame 1 of 6: hit, staggering back, the javelin still in her hand | 未保持同一张逐格头，躺下帧头/身体方向偏离统一3/4正面；标枪尺寸/刚体方向需修正，dead_4 未画地上的枪，5/6 未严格静止一致。 可见内容最底为第194行（0起算），接地要求未验收。 |
| `nidalee_dead_2.png` | dying, frame 2 of 6: falling backward, the javelin slipping from her hand toward the image right | 未保持同一张逐格头，躺下帧头/身体方向偏离统一3/4正面；标枪尺寸/刚体方向需修正，dead_4 未画地上的枪，5/6 未严格静止一致。 可见内容最底为第195行（0起算），接地要求未验收。 |
| `nidalee_dead_3.png` | dying, frame 3 of 6: falling, almost on the ground | 未保持同一张逐格头，躺下帧头/身体方向偏离统一3/4正面；标枪尺寸/刚体方向需修正，dead_4 未画地上的枪，5/6 未严格静止一致。 可见内容最底为第193行（0起算），接地要求未验收。 |
| `nidalee_dead_4.png` | dying, frame 4 of 6: landing on the ground | 未保持同一张逐格头，躺下帧头/身体方向偏离统一3/4正面；标枪尺寸/刚体方向需修正，dead_4 未画地上的枪，5/6 未严格静止一致。 可见内容最底为第172行（0起算），接地要求未验收。 |
| `nidalee_dead_5.png` | dying, frame 5 of 6: lying on the ground, the javelin lying level beside her on the image right | 未保持同一张逐格头，躺下帧头/身体方向偏离统一3/4正面；标枪尺寸/刚体方向需修正，dead_4 未画地上的枪，5/6 未严格静止一致。 可见内容最底为第165行（0起算），接地要求未验收。 |
| `nidalee_dead_6.png` | dying, frame 6 of 6: the same, still (the last frame) | 未保持同一张逐格头，躺下帧头/身体方向偏离统一3/4正面；标枪尺寸/刚体方向需修正，dead_4 未画地上的枪，5/6 未严格静止一致。 可见内容最底为第160行（0起算），接地要求未验收。 |
| `nidalee_c_run_1.png` | running to the right, frame 1 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第179行（0起算），接地要求未验收。 |
| `nidalee_c_run_2.png` | running to the right, frame 2 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第175行（0起算），接地要求未验收。 |
| `nidalee_c_run_3.png` | running to the right, frame 3 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第166行（0起算），接地要求未验收。 |
| `nidalee_c_run_4.png` | running to the right, frame 4 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第164行（0起算），接地要求未验收。 |
| `nidalee_c_run_5.png` | running to the right, frame 5 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第167行（0起算），接地要求未验收。 |
| `nidalee_c_run_6.png` | running to the right, frame 6 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第175行（0起算），接地要求未验收。 |
| `nidalee_c_run_7.png` | running to the right, frame 7 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第164行（0起算），接地要求未验收。 |
| `nidalee_c_run_8.png` | running to the right, frame 8 of an 8-frame gallop loop as in Image 1: the front and hind legs gathering and stretching in turn, the body rising and falling, the tail streaming level behind | 头未逐格复制，鼻尖到屁股的尺寸和位置漂移，四足循环相位变化不足。 可见内容最底为第161行（0起算），接地要求未验收。 |
| `nidalee_c_attack_1.png` | a claw swipe, frame 1 of 4: lifting the near front paw | 头未逐格复制，身体尺寸/站位漂移，落地爪底未稳定对齐第196行。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_c_attack_2.png` | a claw swipe, frame 2 of 4: swiping the paw forward to the right | 头未逐格复制，身体尺寸/站位漂移，落地爪底未稳定对齐第196行。 可见内容最底为第190行（0起算），接地要求未验收。 |
| `nidalee_c_attack_3.png` | a claw swipe, frame 3 of 4: the paw at its farthest forward (the hit) | 头未逐格复制，身体尺寸/站位漂移，落地爪底未稳定对齐第196行。 可见内容最底为第185行（0起算），接地要求未验收。 |
| `nidalee_c_attack_4.png` | a claw swipe, frame 4 of 4: back to the standing pose of Image 2 | 头未逐格复制，身体尺寸/站位漂移，落地爪底未稳定对齐第196行。 |
| `nidalee_c_skill_1.png` | Takedown, a pouncing bite, frame 1 of 5: crouching on the hind legs to spring | 头未逐格复制，身体尺寸/站位漂移，咬住帧的下巴不符合仅打开原造型下巴的要求。 可见内容最底为第188行（0起算），接地要求未验收。 |
| `nidalee_c_skill_2.png` | Takedown, a pouncing bite, frame 2 of 5: the front half rearing up, jaws open | 头未逐格复制，身体尺寸/站位漂移，咬住帧的下巴不符合仅打开原造型下巴的要求。 可见内容最底为第181行（0起算），接地要求未验收。 |
| `nidalee_c_skill_3.png` | Takedown, a pouncing bite, frame 3 of 5: lunging down, biting, both front paws pressing down | 头未逐格复制，身体尺寸/站位漂移，咬住帧的下巴不符合仅打开原造型下巴的要求。 可见内容最底为第180行（0起算），接地要求未验收。 |
| `nidalee_c_skill_4.png` | Takedown, a pouncing bite, frame 4 of 5: holding the bite, low | 头未逐格复制，身体尺寸/站位漂移，咬住帧的下巴不符合仅打开原造型下巴的要求。 可见内容最底为第176行（0起算），接地要求未验收。 |
| `nidalee_c_skill_5.png` | Takedown, a pouncing bite, frame 5 of 5: back to the standing pose | 头未逐格复制，身体尺寸/站位漂移，咬住帧的下巴不符合仅打开原造型下巴的要求。 可见内容最底为第188行（0起算），接地要求未验收。 |
| `nidalee_c_pounce_1.png` | Pounce, a long leap, frame 1 of 6: crouching low, ready to spring | 头未逐格复制，身体尺寸/站位漂移，起落相位及落地爪底对位需修正。 可见内容最底为第176行（0起算），接地要求未验收。 |
| `nidalee_c_pounce_2.png` | Pounce, a long leap, frame 2 of 6: the hind legs pushing off, leaping forward and up to the right | 头未逐格复制，身体尺寸/站位漂移，起落相位及落地爪底对位需修正。 可见内容最底为第181行（0起算），接地要求未验收。 |
| `nidalee_c_pounce_3.png` | Pounce, a long leap, frame 3 of 6: in the air, the body fully stretched, front paws reaching forward | 头未逐格复制，身体尺寸/站位漂移，起落相位及落地爪底对位需修正。 可见内容最底为第163行（0起算），接地要求未验收。 |
| `nidalee_c_pounce_4.png` | Pounce, a long leap, frame 4 of 6: coming down, front paws reaching down | 头未逐格复制，身体尺寸/站位漂移，起落相位及落地爪底对位需修正。 可见内容最底为第168行（0起算），接地要求未验收。 |
| `nidalee_c_pounce_5.png` | Pounce, a long leap, frame 5 of 6: landing on the front paws, body low | 头未逐格复制，身体尺寸/站位漂移，起落相位及落地爪底对位需修正。 可见内容最底为第183行（0起算），接地要求未验收。 |
| `nidalee_c_pounce_6.png` | Pounce, a long leap, frame 6 of 6: standing again | 头未逐格复制，身体尺寸/站位漂移，起落相位及落地爪底对位需修正。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_c_swipe_1.png` | Swipe, both front paws, frame 1 of 4: the front half rising, both front paws raised | 头未逐格复制，身体尺寸/站位漂移，双爪动作和返回站姿仍需对照表格。 可见内容最底为第183行（0起算），接地要求未验收。 |
| `nidalee_c_swipe_2.png` | Swipe, both front paws, frame 2 of 4: both paws sweeping forward to the right | 头未逐格复制，身体尺寸/站位漂移，双爪动作和返回站姿仍需对照表格。 可见内容最底为第180行（0起算），接地要求未验收。 |
| `nidalee_c_swipe_3.png` | Swipe, both front paws, frame 3 of 4: the sweep at its farthest, body low | 头未逐格复制，身体尺寸/站位漂移，双爪动作和返回站姿仍需对照表格。 可见内容最底为第179行（0起算），接地要求未验收。 |
| `nidalee_c_swipe_4.png` | Swipe, both front paws, frame 4 of 4: back to the standing pose | 头未逐格复制，身体尺寸/站位漂移，双爪动作和返回站姿仍需对照表格。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_c_transform_1.png` | turning back into the huntress, frame 1 of 3: sitting back on the hind legs, the front half rising | 头未逐格复制，身体尺寸/站位漂移；后腿站起到回站的动作衔接需修正。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_c_transform_2.png` | turning back into the huntress, frame 2 of 3: sitting up tall, head raised | 头未逐格复制，身体尺寸/站位漂移；后腿站起到回站的动作衔接需修正。 可见内容最底为第190行（0起算），接地要求未验收。 |
| `nidalee_c_transform_3.png` | turning back into the huntress, frame 3 of 3: the front paws lifted off the ground (a burst of light will cover it here - do not draw it) | 头未逐格复制，身体尺寸/站位漂移；后腿站起到回站的动作衔接需修正。 可见内容最底为第189行（0起算），接地要求未验收。 |
| `nidalee_c_dead_1.png` | dying, frame 1 of 6: hit, flinching | 头未逐格复制，身体尺寸/站位漂移；第6帧已重画为朝右伏地，但与第5帧并非逐格静止一致。 可见内容最底为第185行（0起算），接地要求未验收。 |
| `nidalee_c_dead_2.png` | dying, frame 2 of 6: the legs giving way, sinking | 头未逐格复制，身体尺寸/站位漂移；第6帧已重画为朝右伏地，但与第5帧并非逐格静止一致。 可见内容最底为第179行（0起算），接地要求未验收。 |
| `nidalee_c_dead_3.png` | dying, frame 3 of 6: collapsing onto its side on the ground | 头未逐格复制，身体尺寸/站位漂移；第6帧已重画为朝右伏地，但与第5帧并非逐格静止一致。 可见内容最底为第177行（0起算），接地要求未验收。 |
| `nidalee_c_dead_4.png` | dying, frame 4 of 6: lying on the ground | 头未逐格复制，身体尺寸/站位漂移；第6帧已重画为朝右伏地，但与第5帧并非逐格静止一致。 可见内容最底为第180行（0起算），接地要求未验收。 |
| `nidalee_c_dead_5.png` | dying, frame 5 of 6: lying on its side, still | 头未逐格复制，身体尺寸/站位漂移；第6帧已重画为朝右伏地，但与第5帧并非逐格静止一致。 可见内容最底为第176行（0起算），接地要求未验收。 |
| `nidalee_c_dead_6.png` | dying, frame 6 of 6: the same, still (the last frame) | 头未逐格复制，身体尺寸/站位漂移；第6帧已重画为朝右伏地，但与第5帧并非逐格静止一致。 可见内容最底为第179行（0起算），接地要求未验收。 |

## 后续修正重点

全部帧均已生成。后续仍需逐帧对照造型与骨架修正头部、体型和站位，特别是跑步循环、躺下时的朝向、标枪原长度以及静止末帧。6帧重画解决了部分明显方向问题，未解决逐格模板一致性。

压缩包命名 `nidalee_strips_68_review.zip`。这是一份文件齐全的待修正批次，未使用done名称表示美术验收完成。
