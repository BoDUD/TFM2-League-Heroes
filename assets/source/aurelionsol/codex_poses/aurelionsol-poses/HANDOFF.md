# 索尔动作姿势交接（10张齐全）

用户提供的 aurelionsol_pose_pack.zip 对应10个动作，现已全部用内置 image_gen 生成：a_wind、a_throw、q_wind、q_breath、e_reach、e_hold、r_call、r_pull、d_rear、d_down。此前额度中断的 d_down 已补齐。

## 文件和方式

根目录10张 `aurelionsol-pose-<动作>.png` 为1254×1254 RGBA；`raw/` 是对应原始生成图，逐字节一致。实际提示词在 `generation-prompts.txt`，每张引用定稿、头部、该动作骨架、原版姿势和定稿骨架共5张参考。没有脚本拼身体或平滑缩小。`manifest.json` 记录尺寸、alpha层数、边界和哈希；`contact-sheet.png` 是缩略检查页，不作导入源。

## 视觉检查

头部均保持定稿配色和右前方视角，只有q_breath张嘴；角色帧未混入星弹、黑洞或龙息。普攻有扬爪与前甩，Q有吸气与张嘴，E有伸爪与捧合，R有高举与下拽，死亡有后仰与低位倒地。d_down保持尾巴横拖、手臂下垂，但上半身仍较直立，尚不完全等同参考中的斜躺。

## 严格规格尚未通过

文件齐全不等于游戏动作完成。原稿仍含半透明像素，未达到alpha只有0/255；不是严格从(0,0)对齐的11px网格。头部不是逐格复制，手臂23格、尾巴44格和地面y1188均未精确满足。r_call举臂偏长、r_pull握拳和尾巴弯曲需复核；d_rear后仰幅度不足；部分头框位置与骨架不一致。

本包用于后续按raw量格、统一头部及肢体尺度、调色板和锚点后导入rig。若要求完全照骨架，以上动作还要重画或校准。未写入运行模组，未进行游戏内验收。清单状态为 inventory_complete=true、strict_spec_complete=false，以免把原稿齐全误当作最终动作通过。
