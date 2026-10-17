# Smolder 第2步细稿交接
日期：2026-10-15（Asia/Tokyo）

## 交付状态
42个指定帧已全部生成并交付，另保留6张针对姿势的补稿，共48张原始生成稿。**本包是带明确验收问题的细稿，不能标为全部检查通过。** 全部图片都是生成稿原样副本，未缩小、未按粗网格整理，未抠图、阈值化alpha、减色、重描或重排格子。

使用内置 image_gen.imagegen；每次设置 transparent_background=true，每帧单独生成。第一帧依次附骨架、选定造型、造型在画布上的参考、辅助线骨架，后一帧加上同动作前一帧作为第4张，再附辅助线骨架为第5张。没有组合参考板，也没有丢弃指定参考。

文末“Claude收到后”是下游代理说明，没有在本轮执行游戏大小读回、调色板映射、贴脸、游戏仓库导入、技能数据修改或SDK操作。

## 文件清单
- 本目录42张 smolder_<动作>_<n>.png：逐帧表列出全部文件。
- raw/：42张首稿（同指定帧名），以及6张 -attempt-02.png 补稿；全部原样保存。
- generation-prompts.txt：P001–P048每次实际完整提示词和附件顺序。
- generation-records.json：48次生成记录，来源路径、提示词、参考顺序；W4记录标明工具报错后恢复。
- selected-frames.json：42张选定稿与提示词编号、raw文件映射。
- cells.json：从输入包原样复制的帧清单和时长。
- validation.json、validation.tsv：42张选定稿逐帧尺寸、alpha、包围框、越线像素、SHA-256及raw一致性实测。
- HANDOFF.md：本文件，所有图像、提示词和检查数据写完后最后写入。
- 打包文件：上一级 outputs/smolder_strips_done.zip，包含整个 smolder-strips/ 目录。

## 末帧静止与补稿选择
选用第二次生成的 R2、R4、dead3、dead4、dead5。dead6独立两次生成均有大小变化，因此最终dead6原样保持选定dead5，确保静止，两文件逐字节一致。独立dead6首稿和补稿均保留在raw/。这不是把图片缩小或重描。

死亡表格描述要求坐下后摇晃、侧倒、侧躺，但部分 now 骨架仍立着或腹部朝下；补稿优先执行该帧表格要求，同时保持造型的前右朝向。姿势与骨架不完全重合处已在下表注明。

## “交回前请检查”逐条核对

| 原检查项 | 结论 |
|---|---|
| 42帧、正确文件名、每张1536×1024、透明底、原样细稿 | 数量、命名、尺寸和原样保存通过；42张均与选定raw逐字节一致。**透明质量未通过**：42帧都含半透明及柔光，有真实alpha=0背景区域但不是纯净透明精灵。 |
| 与画布造型一样大、圆滚大头短腿、一直3/4朝右、同一张头 | Q版造型、主要脸部构件大体保持；精确比例、头部尺寸与位置逐帧有漂移，不能声明一致性通过。R2已补画前右朝向；W2/W3和R3有额外闭眼。 |
| 尾巴每帧上卷不碰线；翅膀仅按指定帧展开并完整 | 尾巴目视全部向上卷，尾尖离地，未见拖地长尾；没有翼尖裁切。展开翼的轮廓与翼膜配色有偏差，尤其E1–E3/E7残留额外斗篷状翅片。未用自动分割宣称精确尾尖检查通过。 |
| 脚底y990，空中/倒下帧按骨架，无红线以下内容；无特效地面文字辅助线 | 没有喷火、火球、喷嚏火花、风、妈妈、地面、文字或辅助线；**火苗与身体柔光违反无特效要求**。脚底未精确对位。按alpha>128检测，有7帧在y990以下出现像素：run3、run4、skill5、skill2_2、skill2_3、skill2_4、skill2_e_8；详细计数见validation。其它帧也不能因未越线就称脚底对齐通过。死亡补稿侧躺位置偏高。 |
| 全部画完后最后写HANDOFF | 通过；本文件在42帧、48个raw、提示词和验证记录之后写入，随后只打包到目录外。 |

共同问题（适用于下表所有帧）：生成器仍画出柔光与半透明，细节像素块大小及6–7px对齐未达严格一致，材质色阶受柔光影响，头部和主体尺寸与参考有漂移。下表只列各帧额外的动作差异；“可见”表示目视可辨，不等于整帧通过全部验收。

## 每帧提示词与问题记录
提示词P编号对应 generation-prompts.txt 的完整实际文本。

| 交付帧 | 所选提示词 | 对应原稿 | 动作观察与未做到之处 |
|---|---|---|---|
| smolder_run_1.png | P001 | raw/smolder_run_1.png | 迈步、收翼、卷尾；四足对角节奏未严格验证。 |
| smolder_run_2.png | P002 | raw/smolder_run_2.png | 迈步变化可见；头部及整体尺寸与前帧有漂移。 |
| smolder_run_3.png | P003 | raw/smolder_run_3.png | 四腿较易分辨；有像素越过y990。 |
| smolder_run_4.png | P004 | raw/smolder_run_4.png | 迈步可见；有像素越过y990。 |
| smolder_run_5.png | P005 | raw/smolder_run_5.png | 抬前爪变化可见；头高与基准有偏差。 |
| smolder_run_6.png | P006 | raw/smolder_run_6.png | 远侧腿暗色可见；循环节奏未严格验证。 |
| smolder_run_7.png | P007 | raw/smolder_run_7.png | 保持收翼卷尾；首尾衔接未达精确一致。 |
| smolder_run_8.png | P008 | raw/smolder_run_8.png | 循环末帧已画；与第1帧的大小和步幅并非精确闭环。 |
| smolder_attack_1.png | P009 | raw/smolder_attack_1.png | 压身、收头可见。 |
| smolder_attack_2.png | P010 | raw/smolder_attack_2.png | 鼓腮蓄力可见。 |
| smolder_attack_3.png | P011 | raw/smolder_attack_3.png | 向右伸头张嘴，无火球。 |
| smolder_attack_4.png | P012 | raw/smolder_attack_4.png | 前爪离地的小跳可见。 |
| smolder_attack_5.png | P013 | raw/smolder_attack_5.png | 恢复站姿收翼；与造型的精确尺寸仍有偏差。 |
| smolder_skill_1.png | P014 | raw/smolder_skill_1.png | 半张翼、抬头吸气；张嘴比吸气要求更明显。 |
| smolder_skill_2.png | P015 | raw/smolder_skill_2.png | 低伏撑地、张翼；翼幅偏大。 |
| smolder_skill_3.png | P016 | raw/smolder_skill_3.png | 大张嘴出手、张翼，无龙息；与第2帧区分有限。 |
| smolder_skill_4.png | P017 | raw/smolder_skill_4.png | 继续张嘴，双翼开始下降；收拢幅度有限。 |
| smolder_skill_5.png | P018 | raw/smolder_skill_5.png | 恢复收翼站姿；有像素越过y990。 |
| smolder_skill2_1.png | P019 | raw/smolder_skill2_1.png | 皱鼻抬头；眼睛已近全闭，强于眯眼。 |
| smolder_skill2_2.png | P020 | raw/smolder_skill2_2.png | 立起、后仰、张翼；非指定帧闭眼，翼膜偏粉；越过y990。 |
| smolder_skill2_3.png | P021 | raw/smolder_skill2_3.png | 后仰张翼；与第2帧高度差不够明显，仍闭眼、翼膜偏粉；越过y990。 |
| smolder_skill2_4.png | P022 | raw/smolder_skill2_4.png | 闭眼向右下甩头、落前爪；工具报错后恢复落盘稿；越过y990。 |
| smolder_skill2_5.png | P023 | raw/smolder_skill2_5.png | 恢复收翼站姿；摇头幅度不明显。 |
| smolder_skill2_e_1.png | P024 | raw/smolder_skill2_e_1.png | 下蹲张翼；展开翼下有斗篷状翅片残留，结构未通过。 |
| smolder_skill2_e_2.png | P025 | raw/smolder_skill2_e_2.png | 四脚离地、双翼上举；仍有斗篷状翅片残留。 |
| smolder_skill2_e_3.png | P026 | raw/smolder_skill2_e_3.png | 上扇、腿收于身下；仍有斗篷状翅片残留。 |
| smolder_skill2_e_4.png | P027 | raw/smolder_skill2_e_4.png | 水平张翼、悬空；翼膜内侧杏色不足。 |
| smolder_skill2_e_5.png | P028 | raw/smolder_skill2_e_5.png | 下扇、身体抬高可见；翼膜偏深色。 |
| smolder_skill2_e_6.png | P029 | raw/smolder_skill2_e_6.png | 回升翼抬得偏高，非严格水平。 |
| smolder_skill2_e_7.png | P030 | raw/smolder_skill2_e_7.png | 张翼减速、脚向下；仍有斗篷状翅片残留。 |
| smolder_skill2_e_8.png | P031 | raw/smolder_skill2_e_8.png | 回位收翼；有像素越过y990。 |
| smolder_ult_1.png | P032 | raw/smolder_ult_1.png | 向前裹头的披风轮廓可见。 |
| smolder_ult_2.png | P043 | raw/smolder_ult_2-attempt-02.png | 补稿：紧裹缩团、恢复3/4朝右；未完全匹配骨架低头幅度。 |
| smolder_ult_3.png | P034 | raw/smolder_ult_3.png | 立起大张嘴呼喊；眼睛闭合，未保持青绿双眼可见。 |
| smolder_ult_4.png | P044 | raw/smolder_ult_4-attempt-02.png | 补稿：保持后腿立姿、双前爪张开、睁眼大喊；精确后仰角度未通过。 |
| smolder_ult_5.png | P036 | raw/smolder_ult_5.png | 恢复站姿收翼；精确基准尺寸有偏差。 |
| smolder_dead_1.png | P037 | raw/smolder_dead_1.png | 闭眼受击缩身可见。 |
| smolder_dead_2.png | P038 | raw/smolder_dead_2.png | 坐落、四爪上抬可见。 |
| smolder_dead_3.png | P045 | raw/smolder_dead_3-attempt-02.png | 补稿：坐姿摇晃衔接；倾斜幅度及与骨架高度存在差异。 |
| smolder_dead_4.png | P046 | raw/smolder_dead_4-attempt-02.png | 补稿：四脚失去支撑并翻向一侧；方向不完全等同骨架。 |
| smolder_dead_5.png | P047 | raw/smolder_dead_5-attempt-02.png | 补稿：真正侧躺、闭眼、四爪放松；脸与身体尺寸偏大，着地位置高于y990。 |
| smolder_dead_6.png | P047 | raw/smolder_dead_5-attempt-02.png | 静止保持第5帧的原样文件；两次独立生成第6帧在raw保留但未选用。 |

## 使用建议
先检查raw和逐帧备注再进入后续制作，尤其透明柔光、比例漂移、飞行翅片结构及红线对位。目录中的细稿未被本代理缩放处理；后续按格子读回和游戏导入仍由下游步骤承担。zip中的“done”仅是用户指定包名，不代表全部视觉验收通过。

