# Varus VFX — 生图原稿交接

24 张均已通过原生图像生成工具逐张生成；根目录 PNG 就是未经裁剪、缩放或重绘的生图原稿。没有用代码绘制特效。代码仅用于原样复制、文件检查和预览。
本次完成的是特效原稿生成与交付。未导入游戏，未修改 mod，也未验证游戏内播放。

## 检查与限制

- 24 张文件可解码，均有透明像素及可见像素；所有预计帧区域非空。生成画面已逐张查看。
- 实际图片尺寸普遍没有遵循指定尺寸，部分帧格比例也有偏差。请按形状重新确定帧边界，再按 fx_list.json 的游戏像素大小处理；不要直接按原指定尺寸切图。
- manifest.json 的 frame_rectangles_estimate 是等分估计，不能视为最终导入矩形；宽度不能整除时，格宽差 1 像素。
- 存在半透明边缘、额外颜色和深色边；未验证严格色板、统一像素格、禁止光效描边或无缝循环。箭矢和锁链尚需严格上下对称校正。
- 部分效果在相邻帧中的位置和大小有变化；发射起点、人物空位、脚下环和 BIG 地面效果需要结合原包 design/varus_shots.png 校正锚点。
- p_rage_on 第 2 帧光柱较满，人物空位需在导入时清理；r_bind 的触须穿越中部，需检查人物遮挡。
- R chain 的原说明同时写 2688x384 与 672x288 单格，本次提示词按单格优先改为 2688x288。最终生图尺寸另见下表。
- 原包参考纹理 refs/lol_fx_ref.png 未随交付包分发。

## 文件与预览

prompts/ 保存每张实际使用的完整提示词。fx_list.json 原样保留绑定和目标游戏尺寸。
previews/overview.jpg 是全套总览；4 个 GIF 仅为等分裁切后每帧 120ms 的示意，背景为深色，不代表游戏时序或锚点。所有加工只影响预览，根目录 PNG 原稿保持原样。

## 逐张记录

|序号|文件|帧排列|要求尺寸|实际尺寸|生成记录|
|---|---|---|---|---|---|
|1|varus_fx_a_arrow.png|4列 × 1行|2048×256|2172×724|已生成，提示词见 prompts/01_varus_fx_a_arrow.txt|
|2|varus_fx_a_flash.png|3列 × 1行|720×200|2103×748|已生成，提示词见 prompts/02_varus_fx_a_flash.txt|
|3|varus_fx_a_hit.png|4列 × 1行|1024×256|1983×793|已生成，提示词见 prompts/03_varus_fx_a_hit.txt|
|4|varus_fx_b_mark.png|4列 × 3行|2048×576|1881×836|已生成，提示词见 prompts/04_varus_fx_b_mark.txt|
|5|varus_fx_b_pop.png|5列 × 1行|1280×256|1983×793|已生成，提示词见 prompts/05_varus_fx_b_pop.txt|
|6|varus_fx_w_pop.png|5列 × 1行|1280×256|1983×793|已生成，提示词见 prompts/06_varus_fx_w_pop.txt|
|7|varus_fx_w_glow.png|4列 × 1行|896×352|1999×786|已生成，提示词见 prompts/07_varus_fx_w_glow.txt|
|8|varus_fx_q_charge.png|6列 × 1行|1536×256|2172×724|已生成，提示词见 prompts/08_varus_fx_q_charge.txt|
|9|varus_fx_q_fire.png|4列 × 1行|1536×448|2172×724|已生成，提示词见 prompts/09_varus_fx_q_fire.txt|
|10|varus_fx_q_arrow.png|4列 × 1行|3072×256|2172×724|已生成，提示词见 prompts/10_varus_fx_q_arrow.txt|
|11|varus_fx_q_hit.png|5列 × 1行|1280×256|1983×793|已生成，提示词见 prompts/11_varus_fx_q_hit.txt|
|12|varus_fx_e_cast.png|4列 × 1行|1024×256|2172×724|已生成，提示词见 prompts/12_varus_fx_e_cast.txt|
|13|varus_fx_e_rain.png|7列 × 1行|3136×480|2194×717|已生成，提示词见 prompts/13_varus_fx_e_rain.txt|
|14|varus_fx_e_field.png|4列 × 1行|1856×240|2067×761|已生成，提示词见 prompts/14_varus_fx_e_field.txt|
|15|varus_fx_e_hit.png|4列 × 1行|1024×256|2172×724|已生成，提示词见 prompts/15_varus_fx_e_hit.txt|
|16|varus_fx_e_slow.png|4列 × 1行|2304×256|1881×836|已生成，提示词见 prompts/16_varus_fx_e_slow.txt|
|17|varus_fx_r_cast.png|4列 × 1行|1280×256|1983×793|已生成，提示词见 prompts/17_varus_fx_r_cast.txt|
|18|varus_fx_r_chain.png|4列 × 1行|2688×288|2032×774|已生成，提示词见 prompts/18_varus_fx_r_chain.txt|
|19|varus_fx_r_hit.png|5列 × 1行|1280×256|1983×793|已生成，提示词见 prompts/19_varus_fx_r_hit.txt|
|20|varus_fx_r_bind.png|4列 × 1行|1056×432|1958×803|已生成，提示词见 prompts/20_varus_fx_r_bind.txt|
|21|varus_fx_r_spread.png|6列 × 1行|2880×256|2103×748|已生成，提示词见 prompts/21_varus_fx_r_spread.txt|
|22|varus_fx_r_spread_hit.png|4列 × 1行|1024×256|2172×724|已生成，提示词见 prompts/22_varus_fx_r_spread_hit.txt|
|23|varus_fx_p_rage_on.png|5列 × 1行|1200×368|2172×724|已生成，提示词见 prompts/23_varus_fx_p_rage_on.txt|
|24|varus_fx_p_rage.png|4列 × 1行|2816×256|2079×756|已生成，提示词见 prompts/24_varus_fx_p_rage.txt|

## 导入时核对

b_mark 三行对应 b_v1/b_v2/b_v3；b_pop 按层数 70%/85%/100% 使用；q_charge_s 使用前 3 帧；q_arrow_s 使用缩小版。飞行物出生 tick 的空帧、施法效果跟随开关、人物上下绘制层级与循环播放须按原包绑定说明处理。
清理光与雾的深色边时保留实心箭头、荆棘、触须的轮廓；游戏内检查小尺寸辨识度、平均亮度、峰值亮度、动画衔接与遮挡。

## 失败和重做

生成调用失败：0；漏交文件：0。上述尺寸、像素格、锚点、对称和循环问题尚未修正，原稿阶段交付，不能宣称游戏可直接用。
