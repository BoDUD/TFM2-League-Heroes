# 希尔科特效包交付

18 张特效动画表，共 95 帧；另附 3 个 64×64 技能图标。所有视觉原稿由内置 image_gen 生成，没有用代码拼出替代特效。

## 使用方式

- pixel_1x/：18 张导入用横向帧表，严格采用清单的每帧游戏像素尺寸；按 manifest.json 的 frames、cell_1x 切格。
- 顶层 silco_fx_*.png：对应的精确 8 倍最近邻预览，与 pixel_1x/ 逐像素一致。
- 顶层 silco_icon_*.png：64×64 图标，32×32 逻辑格放大两倍。
- raw/：18 张特效及 3 张图标的原始生图，未重采样。q_burst 原稿4列2行，r_burst原稿5列2行，其余按原稿横排；以 manifest 中 raw_layout 为准。
- fx-overview.png、previews/：深色背景视觉预览，仅供检查，不作导入源。
- generation-prompts.txt、manifest.json、QA.json、SHA256SUMS.json：实际提示词、切格与绑定信息、检查结果和校验值。

## 清单
- silco_fx_a_vial.png：4 帧，cell_1x=12×6，top-bottom
- silco_fx_a_hit.png：4 帧，cell_1x=16×16，left-right
- silco_fx_q_can.png：4 帧，cell_1x=12×10，top-bottom
- silco_fx_q_warn.png：4 帧，cell_1x=26×10，left-right
- silco_fx_q_burst.png：7 帧，cell_1x=40×34，left-right
- silco_fx_m_leap.png：5 帧，cell_1x=22×46，left-right
- silco_fx_m_bite.png：4 帧，cell_1x=24×38，none
- silco_fx_m_die.png：5 帧，cell_1x=18×12，left-right
- silco_fx_e_dose.png：5 帧，cell_1x=20×44，left-right
- silco_fx_e_shimmer.png：6 帧，cell_1x=26×42，left-right
- silco_fx_e_crash.png：5 帧，cell_1x=22×30，left-right
- silco_fx_r_can.png：4 帧，cell_1x=22×18，top-bottom
- silco_fx_r_warn.png：6 帧，cell_1x=60×22，left-right
- silco_fx_r_burst.png：10 帧，cell_1x=72×60，left-right
- silco_fx_r_fog.png：6 帧，cell_1x=84×32，left-right
- silco_fx_r_slow.png：4 帧，cell_1x=20×14，left-right
- silco_fx_p_shield.png：6 帧，cell_1x=28×46，left-right
- silco_fx_p_dom.png：6 帧，cell_1x=16×48，left-right
- silco_icon_skill.png：1 帧，cell_1x=64×64，none
- silco_icon_skill2.png：1 帧，cell_1x=64×64，none
- silco_icon_ult.png：1 帧，cell_1x=64×64，none

## 处理与检查

按输入包要求对生成素材做取格后处理：alpha>=180保留，去除极小孤立残留和原稿误画的细分隔线；色值映射到该项指定色板，每格覆盖率至少8%时取覆盖色的多数色，较低覆盖率留透明。8%阈值用于保留细警示圈和护盾边线，区别于包含透明票的绝对多数。不是凭空绘制形状。

原稿未稳定遵守所需画布比例，因此先分帧、按全组最大内容框将生成图映射到该特效的目标占幅，再按地面或头顶/左侧锚点排版。m_leap置于顶部，m_bite置于左侧，p_dom限定顶部10格；围身特效清空身体占位区。每帧取左半或上半镜像为严格对称，m_bite保留不对称。p_dom补入橙红眼色板以保留眼印身份。所有这些转换会改变原稿中的局部比例，raw/可供重新提取。

已独立检查：18张帧表尺寸和帧数、每帧非空、alpha只有0/255、指定对称逐像素一致、8倍图精确对应、3图标尺寸和2px格一致，全部通过。连续动画视觉仍需在游戏中确认；低分辨率畸变体的金牙、眼印及围身细线有细节损失，不应将文件检查等同于游戏内技能验收。未导入或绑定运行时。
