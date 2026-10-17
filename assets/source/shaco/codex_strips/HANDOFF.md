# 萨科动作条带：眼部清理版 v1

使用用户选定的46格v4 A造型，保留用户认可的19格金色褶领修补。此版含10张条带、58帧；待机6帧使用原待机姿态，其余9个动作共52帧。

## 本轮修正

早先原生生成草稿出现了面部碎块、缩放不一致及部分缺帧，未作为成品打包。最终使用定稿的实际彩色像素部件组织姿势，重接袖子与膝部，最后贴入原头部。面部包括透明空隙均逐像素核对；掷刀第2帧脸旁的1格多余轮廓已清掉。死亡最后两帧连身体一起转90度，其余头部只平移。

## 文件

根目录的 shaco_<动作>.png 是严格8倍透明PNG；native/ 是对应的1倍像素源图。每格112×96格，即896×768像素。manifest.json 记录格子矩形、站位点、bbox、时长及参考出手帧。shaco_cells.json 保留输入站位与时长。design/ 是批准的领口修补版及原头部。preview/ 仅用于查看，含编号的接触表与GIF，不用作导入纹理。

## 提示词与结果

generation_prompts.json 中 actions.<动作>.prompt 是此前原生图像工具实际使用的完整提示词。每次参考图为修补版造型、now条、高清pose条；原始生成文件路径只用于追溯，坏稿没有装入此包。最终条带并非声称原生模型一次生成就满足严格网格。

| 动作 | 帧数 | 排版 | 提示词记录 |
|---|---:|---|---|
| idle | 6 | 3×2 | 输入待机 |
| run | 8 | 4×2 | actions.run.prompt |
| attack | 6 | 3×2 | actions.attack.prompt |
| attack_q | 6 | 3×2 | actions.attack_q.prompt |
| attack_e | 6 | 3×2 | actions.attack_e.prompt |
| skill | 5 | 3×2 | actions.skill.prompt |
| skill2 | 5 | 3×2 | actions.skill2.prompt |
| ult | 6 | 3×2 | actions.ult.prompt |
| hit | 2 | 2×1 | actions.hit.prompt |
| dead | 8 | 4×2 | actions.dead.prompt |

## 检查与尚未覆盖的部分

保存后的PNG重新读取核验：8×8纯色格、17色调色板、二值透明度、58帧头部原像素、眼周透明空隙、脚底线、帧数与原pivot/毫秒均通过。skill与skill2的第6格为空。每帧角色只有一个连通部分。详情见validation.json及saved_file_validation.json。

GIF时长受格式10毫秒精度限制，跑步139ms预览会取整；导入使用manifest或shaco_cells中的原毫秒数。待机6帧完全相同，因此GIF合成器合并为一帧。

动作以定稿像素部件的平移及旋转实现，袖子/膝部局部重接；3D参考中的扭转、帽子甩动、倒立和背面未逐形复刻，头部依要求固定，动作美术与流畅度仍以预览评审。没有额外特效。尚未导入游戏或进行游戏内测试，不能据文件检查声称游戏里已经通过。authoring/保存当前工作区的制作/核验脚本快照，脚本内路径依赖原工作区，并非独立安装器。
