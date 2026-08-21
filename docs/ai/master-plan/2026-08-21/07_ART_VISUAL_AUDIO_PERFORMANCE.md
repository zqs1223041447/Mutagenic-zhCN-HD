# 美术、视觉、音频与性能

Halls of Torment 是视觉与战斗呈现参考：暗黑复古、低饱和、强轮廓、怪潮密度、击杀/死亡节奏、清晰 telegraph。

Product runtime 默认保持 2D。大规模正式美术阶段使用 Blender 5.2 LTS CLI/Python 生成/预渲染 sprites/atlases；Blender MCP 仅可选。

视觉优先级：Player > 致命 telegraph > Elite/Boss > 关键 projectile > Loot > Common Enemy > Cosmetic FX。

性能不提前发明绝对阈值；P1/P3 在实际参考硬件上建立 p50/p95/p99 frame time、enemy/projectile/event/audio/FX/loot/pool miss 基线。

高密度架构优先 pooling、共享 cadence、批量更新、事件预算，避免每个普通怪都运行重 AI。普通怪 FSM；Elite/Boss 需要时再用 HSM/BT。