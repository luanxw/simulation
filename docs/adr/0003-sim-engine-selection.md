# 0003. 仿真引擎选型：Gazebo (gz-sim) 为主引擎 + 分层传感器建模，Isaac Sim 作保真度对标参考

- 状态：Proposed（PoC 验证通过后转 Accepted，见"后续行动"）
- 日期：2026-10-05
- 关联规格：`.trae/specs/0002-mower-sensor-sim-test-plan/`（Task 1，TR-1.1）

## 背景（Context）

规格 0002 要求对 1×主 LiDAR、12×环形超声波、2×侧向双目及融合输出做仿真测试，场景为商用高尔夫球场与足球场（W1/W2），并有四项硬约束（NFR-1~4 与 2.4 节）：

1. **确定性可复现**：同 seed 重跑输出哈希一致（TC-F-13 强制）；
2. **CI 可运行**：冒烟子集 ≤30 min；
3. **边角材质品类**：半透明网面（OB-B20/C2/D4）、镜面（OB-A6、水面 OB-B4、车窗）、吸声软目标、夜场泛光 1800 lux（ENV-1）都必须可建模；
4. **12×超声波**：两家主流引擎均无开箱即用的环形超声模型，必须自研建模层。

被考虑的候选：

- **A. NVIDIA Isaac Sim**（Omniverse RTX 渲染 + PhysX）：RTX LiDAR 光线追踪成熟，双目/深度相机为标准能力；但无官方超声模型；RTX LiDAR 在快速运动下存在几何不一致的已知问题（2026 年 GitHub 报告），透明/镜面材质交互有长期 quirk（NVIDIA 论坛）；安装重（需 RTX GPU、数十 GB），CI 成本高。
- **B. Gazebo (gz-sim Harmonic 8.x / Ionic 9.x)**：开源、轻量、headless 固定步长服务端模式（`-s -r`）适合 CI；GpuLidar 依赖 OGRE2 渲染（GPU 里程依赖）；传感器级 API 走 C++ 插件 + gz-transport（Python 可经 transport 绑定取数）；渲染线程时序会影响逐位确定性（需固定步长 + 关实时因子对拍验证）；无原生超声/声呐模型。
- **C. 自研光线追踪栈**（Blender/Blensor 离线渲染类）：材质保真度最高，但无实时闭环物理，不适合避碰/动态遭遇类用例，只适合离线数据集生成。
- **D. CARLA 等车载模拟器**：天气/光照系统强，但车辆语义过重、无超声，移植割草机器人成本高。

## 决策（Decision）

采用**混合分层架构**，而非单引擎押注：

1. **主引擎：Gazebo gz-sim（Harmonic 8.x 起，评估 Ionic 9.x）**——承载 W0~W3 世界、PhysX 物理、闭环避碰动态（TC-F-06/07/09/10）与 CI 冒烟子集；选择依据是确定性行进模式、开源可嵌入 CI、轻量可复制，匹配 NFR-1/NFR-2 两条硬约束。
2. **传感器建模分层**：
   - LiDAR/双目/深度：GpuLidar + 渲染相机直接取数；
   - **12×超声波：自研 gz 传感器插件**（射线锥束回波模型：-6dB 波束角、40 kHz 声速温补 c=331.4+0.6T、分时轮询时序），回波物理参数由本仓库 `sensor_params.yaml` 驱动——这是两家候选都绕不开的自研项，选择在开源栈上做以保 CI 与确定性；
   - 材质 BRDF/声学属性（吸声、半透明、镜面）录入资产元数据（D3 obstacles 库扩展），渲染侧用 gz 材质 + 插件侧用声学系数。
3. **保真度对标参考：Isaac Sim**——不进 CI，仅在 W1/W2 子集（夜场泛光、半透明网面、镜面三类边角品类）离线渲染对拍，标定 gz 渲染与 RTX 的偏差并写入能力边界报告；同时规避其 RTX LiDAR 快速运动几何不一致与镜面 quirk 对门禁判定的干扰。
4. **本仓库框架不动**：`verdict.py` 门禁、`runner.py` 判定逻辑、`test_thresholds.yaml` 全部保持引擎无关；按 `user_guide.md` §5.4 实现同名接口的 `GazeboBackend` 替换 `SyntheticBackend`。

## 被否方案的理由

- **Isaac Sim 为主**：CI 成本与确定性风险（快速运动点云不一致会直接威胁 TC-L-08/TC-F-13 的判定可信度）；且超声仍需自研，优势只剩渲染保真度——保留为对标参考即可，不必付全家桶成本。
- **纯自研栈**：失去闭环物理与生态，避碰/跟踪类用例（TC-F-06/07/09/10）无法可信执行。

## 后果（Consequences）

- 正面：CI 可运行（开源轻量）；确定性风险集中于单一已知的 GpuLidar 渲染线程问题，可用固定步长 + 禁实时因子 + 哈希对拍收敛；超声自研层直接由本仓库配置驱动，规格变更只改 YAML。
- 负面/代价：需投入自研超声插件（估计 2~3 周，含标定）；GpuLidar 渲染线程确定性需 PoC 专项验证，不通过则退路为"LiDAR 射线 CPU 插件"（性能换确定性）；Isaac Sim 对标需一张 RTX GPU 的离线工位。
- 后续行动（PoC 门禁，对应 TR-1.1）：
  1. gz-sim Harmonic headless 固定步长跑 LiDAR + 双目 + 1×超声（合成层）三流 ≥30 min 无崩溃，落盘时间戳偏差 ≤5 ms 证据；
  2. 同场景同 seed 重跑 5 次输出哈希一致（TC-F-13 预演）；
  3. 半透明网面 + 夜场泛光两个材质场景的 GpuLidar/相机渲染抽查；
  4. 三项全过 → 本 ADR 转 Accepted，`GazeboBackend` 立项（Task 7 前置）。

## 参考（调研快照，2026-10-05）

- Isaac Sim 文档与 RTX LiDAR（isaacsim.sensors.rtx）：docs.isaacsim.omniverse.nvidia.com；
- RTX LiDAR 快速运动几何不一致（2026-07 GitHub 报告）与透明/镜面材质 quirk：forums.developer.nvidia.com；
- gz-sim 传感器教程与 GpuLidar（gz-sensors）：gazebosim.org/docs、github.com/gazebosim/gz-sensors；
- GPU 依赖与渲染线程实时因子问题：robotics.stackexchange.com、discuss.ardupilot.org；
- Python 绑定形态（gz.sim / gz.transport13）：PX4 Gazebo 集成指南 docs.px4.io。
