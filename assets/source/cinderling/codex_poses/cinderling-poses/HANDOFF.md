# 绯红树怪动作原图交付
日期：2026-11-02（Asia/Tokyo）

## 交付内容
13 张独立动作原图，全部使用内置 image_gen 生成。所有交付图片均为 1254×1254 PNG，存在真实透明像素。没有对图片进行缩放、重采样、重绘、改色、透明阈值处理或程序化逐格绘制。

| 文件 | 动作 |
|---|---|
| `cinderling-pose-a_fling.png` | 普攻腾空甩叶 |
| `cinderling-pose-q_bristle.png` | 刃叶蓄力 |
| `cinderling-pose-q_throw.png` | 刃叶甩出 |
| `cinderling-pose-e_dig.png` | 钻地（已重画） |
| `cinderling-pose-e_pop.png` | 钻出 |
| `cinderling-pose-r_rear.png` | 后腿站立 |
| `cinderling-pose-r_roar.png` | 站立怒吼 |
| `cinderling-pose-run1.png` | 蹦跳1：蹲紧 |
| `cinderling-pose-run2.png` | 蹦跳2：蹬起 |
| `cinderling-pose-run3.png` | 蹦跳3：空中 |
| `cinderling-pose-run4.png` | 蹦跳4：落地 |
| `cinderling-pose-d_flip.png` | 死亡翻倒 |
| `cinderling-pose-d_down.png` | 死亡倒地 |

- `raw/`：13 张所选原始生成图，和交付图片 SHA-256 一致；另保留 `rejected-e_dig-generation-1.png`，仅作被拒绝首稿的记录。
- `generation-prompts.txt`：13 个实际生成提示词及每次参考图顺序。
- `correction-prompts.txt`：钻地重画提示词。
- `unexecuted-correction-prompt.txt`：出土姿势的后续修正提示词，调用返回额度限制，未生成新图片，不能算作已执行成功的修正。
- `validation.json`：只读检查结果，包含画布、透明度、可见包围盒、SHA-256、原图一致性。
- `preview.html`：浏览全部13张原图的索引页面，源图不变。

## 检查结果与制作限制
- 文件完整性：13/13；画布1254×1254：13/13；原图备份一致：13/13。
- 外观：所有动作保留紫褐树皮、木甲与青苔、浅绿叶鬃、木面具、尖爪。存活动作带橙眼和螺旋；d_down眼睛与螺旋已熄灭。
- e_dig首稿误画成完整蹲姿，已弃用并重画为下部被地面遮挡的残部。
- **e_pop仍有明显偏差**：身体伸展符合出土方向，但最低脚爪约y1195，没有达到参考图要求的腾空高度。针对这一问题的额外生成调用触发绘图额度限制，因此该帧是待修正原图。
- **严格像素制作要求未全部达标**：生成图仍有半透明边缘；未认证严格8px统一网格，面具无法保证逐格相同；各帧身体和面具大小、落脚线与参考骨架位置也有偏差。它们是原始绘图素材，不能当作已通过游戏动画像素一致性验收的最终帧。
- a_fling、run2、run3可见脚底高于1176地面；run4约y1174，接近落脚线。e_dig残部截断约y1191，仍需后续接入时对齐地面线。
- 按用户此前“保留生成原图即可”的选择及本包“不缩放或重新取样”的素材要求，所有上述偏差原样保留并明确记录。

本次仅完成动作原图制作与归档，未修改游戏或仓库；素材文档中面向另一助手的后续接入说明未作为本次操作指令执行。

