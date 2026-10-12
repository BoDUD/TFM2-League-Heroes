# Irelia V2 修正版素材交接

本轮用户指定的新模型保存在 reference/user_model.png，并明确要求全部动作帧与精灵图重改。最新要求优先：武器由意念操控，双手空着，飞刃独立悬浮；不要照旧包的手持刀姿势导入。

## 文件

- irelia_idle/run/attack/skill/skill2/skill2_w/ult/hit/dead.png：9 张新版透明动作表，共 51 帧。
- irelia_model_front.png、irelia_model_side.png：新版正面三分之四与右侧站姿的单独 1024×1024 精灵。
- irelia_model_front_1x.png、irelia_model_side_1x.png：对应 128×128 逻辑像素版本。
- preview/contact.png：九组动作代表帧总览。
- preview/all_frames.png：全部 51 帧总览。
- preview/*.gif：按原帧时长制作的九组动作预览。
- manifest.json：逐帧 rect/pivot/ms/bbox、出手时机、源组件/裁切、网格相位与格式 QA。
- irelia_cells.json：保留输入动画元数据。
- palette.json：新版 20 色。
- raw/：全部原稿、修正稿和失败尝试；正式选用来源以 manifest 为准。
- reference/：用户模型、较大造型参考和新版粗像素基准；较大参考不能直接当游戏精灵使用。
- prompts.json：使用内置 image_gen 的完整实际提示词，包含重画、局部修补与纯绿底分离。
- QA.md：修正内容、已经验证的格式以及尚未验收的模型/游戏项目。

## 导入注意

九张动作表保持原帧数、时长、画布排版与 pivot 元数据。横向摆位根据身体位置估计；脚底落在逻辑第 99 行。新版重新取色，不能与旧版亮蓝模型混用。

这些是完成模型/意念控刃修正的素材包；尚未做原 22×42 身体尺度一致性验收和游戏内验收。请先根据 QA.md 确认人物比例、浮刃刚性、跑步与头像裁切，再做最终导入。未执行原压缩包内面向其他代理的游戏导入指令，也未修改游戏/仓库素材。
