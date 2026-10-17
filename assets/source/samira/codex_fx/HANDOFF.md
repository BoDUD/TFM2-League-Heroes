# 莎米拉特效交接

23张独立特效生图原稿已齐，按输入包的原稿交付选项制作。所有图都由图像生成工具产生，没有用代码拼绘特效方块。交付保留原稿及实际提示词。这里的“完成”指特效源图交付，尚未进行游戏导入、烘焙、技能绑定或实战测试。

## 使用

根目录的 `samira_fx_*.png` 是交付原稿；`raw/` 保留24张实际生成原稿：23张选用原稿，加上已弃用的评分字母第1版。根目录评分字母选用第2版，其余22张采用第1版。`prompts/` 逐字记录实际提示词，按输入文档每项的英文提示词，并加上统一的等宽格子、只画特效、不带参考图文字、衰减帧保留亮火星等限制。原版灰度贴图只作形状参考，未包含在交付包。

`preview.html` 可逐张播放/暂停、拖动帧号、切换背景。预览100ms不是游戏时长。`manifest.json` 包含实际画布尺寸、期望尺寸、每帧等宽裁切矩形、实测不透明bbox、亮度、绑定描述及文件哈希。没有虚构游戏内时长或完成绑定的枪口锚点。

## 格式与导入限制

生图未稳定返回指定尺寸和严格16×16网格，部分边缘半透明，颜色不严格限定于请求色板。遵照本包允许交付这些原稿的条款，未对源图强行缩放、删行、重绘、强制对称或用代码补画。导入端应先逐格取回、调整到游戏尺寸、清除火光深色外缘、量亮度、设定时长和绑定起点，再做游戏内检查。评分字母保留深色描边。

子弹与挂身循环的精确对称性需要导入端处理：弹体大致上下对称，但随机火星/烟尾不是逐像素镜像；W/R与升级光的粒子也不是精确左右镜像。循环首尾仍需在最终尺寸/时长下检查。未把原稿交付称作像素格式或游戏运行验收通过。

## 逐张检查

| 特效 | 帧数 | 实际尺寸 | 提示词 | 检查及偏差 |
|---|---:|---|---|---|
| samira_fx_a_bullet.png | 4 | 2172×724 | prompts/samira_fx_a_bullet.txt | 朝右的弹头与尾巴，4帧循环；火星没有严格逐像素上下对称。 |
| samira_fx_a_flash.png | 3 | 2172×724 | prompts/samira_fx_a_flash.txt | 朝右的3帧枪火，逐帧衰减；原稿不是固定16px方块。 |
| samira_fx_a_hit.png | 4 | 2079×756 | prompts/samira_fx_a_hit.txt | 4帧白金闪光和橙火星；后两帧偏亮，导入端可调整透明衰减。 |
| samira_fx_a_slash.png | 3 | 2103×748 | prompts/samira_fx_a_slash.txt | 3帧右凸新月弧，后两帧碎成火星；半透明边和细碎像素需要导入端规范化。 |
| samira_fx_a_slash_hit.png | 4 | 2172×724 | prompts/samira_fx_a_slash_hit.txt | 4帧斜剑痕与火星；白芯和红火保留，非严格限定色板。 |
| samira_fx_j_up.png | 4 | 2149×732 | prompts/samira_fx_j_up.txt | 4帧上挑弧和脚下沙尘；弧顶和尘土锚点按原稿测量后再绑定。 |
| samira_fx_q_bullet.png | 4 | 2172×724 | prompts/samira_fx_q_bullet.txt | 4帧较大的右向弹头；主体近似上下对称，侧焰和火星不严格对称。 |
| samira_fx_q_flash.png | 3 | 2172×724 | prompts/samira_fx_q_flash.txt | 3帧更大的右向枪火；均有白亮芯，颜色和网格尚需规范化。 |
| samira_fx_q_hit.png | 4 | 2172×724 | prompts/samira_fx_q_hit.txt | 4帧爆闪、扩散火星；与普通命中相比体积更大。 |
| samira_fx_q_slash.png | 4 | 2080×756 | prompts/samira_fx_q_slash.txt | 4帧右凸大半月弧；中央角色空位不画人，实际站位须按导入目标重新定位。 |
| samira_fx_q_slash_hit.png | 4 | 2172×724 | prompts/samira_fx_q_slash_hit.txt | 4帧交叉剑痕；X形命中、火星衰减。 |
| samira_fx_e_dash.png | 4 | 2172×724 | prompts/samira_fx_e_dash.txt | 4帧红速度线、黄沙和碎屑；拖尾朝左，右端是移动人物的位置。 |
| samira_fx_e_hit.png | 4 | 2172×724 | prompts/samira_fx_e_hit.txt | 4帧水平剑痕和黄沙，末帧粒子衰减。 |
| samira_fx_e_reset.png | 4 | 2172×724 | prompts/samira_fx_e_reset.txt | 4帧金环和升起的星光；视觉近似左右对称，细小星点不完全一致。 |
| samira_fx_w_spin.png | 4 | 1983×793 | prompts/samira_fx_w_spin.txt | 4帧扁椭圆红剑火环，中央空；高亮变化用于循环，不能保证正好每帧推进四分之一圈或严格左右对称。 |
| samira_fx_w_hit.png | 4 | 2172×724 | prompts/samira_fx_w_hit.txt | 4帧弯剑痕和火星；亮芯清楚。 |
| samira_fx_r_on.png | 4 | 2172×724 | prompts/samira_fx_r_on.txt | 4帧红旋风、金枪火和玫瑰花瓣，中央空；各侧粒子不严格镜面对称，导入端应校对人物遮挡。 |
| samira_fx_r_flash.png | 2 | 1942×809 | prompts/samira_fx_r_flash.txt | 2帧右向小枪火；用于两枪时由导入端镜像左侧实例。 |
| samira_fx_r_bullet.png | 3 | 1995×788 | prompts/samira_fx_r_bullet.txt | 3帧右向红橙曳光弹；核心近似对称，烟尾与火星不严格上下对称。 |
| samira_fx_r_hit.png | 4 | 2172×724 | prompts/samira_fx_r_hit.txt | 4帧火光与玫瑰花瓣衰减；花瓣轮廓应在游戏大小再检查。 |
| samira_fx_g_letters.png | 6 | 2172×724 | prompts/samira_fx_g_letters_attempt2.txt | 第2版：6格按E、D、C、B、A、S排列；直立粗方块字，深色轮廓，仅S带火焰。第1版倾斜且火焰过多，已弃用但保留raw。仍需最终游戏尺寸检查。 |
| samira_fx_g_up.png | 3 | 2172×724 | prompts/samira_fx_g_up.txt | 3帧金色星闪、扩散圆环和小星；视觉近似左右对称，细节不完全一致。 |
| samira_fx_g_s.png | 4 | 1983×793 | prompts/samira_fx_g_s.txt | 4帧金红爆闪、扩散环和火星；视觉近似左右对称，细节不完全一致。 |

## 导入对应关系

`fx_list.json` 保留输入包的绑定与游戏目标大小。原文末尾的 Claude 导入说明是下一阶段的交接要求，本轮未执行那些仓库修改。需要烘进角色帧的 a_flash/q_flash/r_flash/a_slash 交给导入端处理；r_flash左枪实例用镜像；评分字母保持正常阅读方向。循环/跟随、Delayed事件、Q近身140ms延迟及枪口出弹偏移，须在导入后与已定稿动作共同验证。

最终核对：23/23文件齐全，全部帧均有可见内容，全部原稿有透明背景像素；最亮一成的不透明像素亮度范围208.2–253.9（0–255）。预览JavaScript语法检查通过；未做游戏内验收。
