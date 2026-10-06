"""测试方案设计图生成器（图即代码）：输出 PNG 到 src/simulation/docs/diagrams/。

用法：PYTHONPATH=src /usr/local/anaconda3/envs/simulation-py312/bin/python scripts/make_diagrams.py
依赖：matplotlib（py312 环境）。中文以 macOS 自带字体渲染，输出可复现。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import fontManager  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "src/simulation/docs/diagrams"
OUT.mkdir(parents=True, exist_ok=True)

# ---- 中文字体（macOS 自带，按优先级） ----
for cand in ("PingFang SC", "Hiragino Sans GB", "Arial Unicode MS", "STHeiti"):
    if any(f.name == cand for f in fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [cand]
        break
plt.rcParams["axes.unicode_minus"] = False

# ---- 调色板 ----
NAVY = "#1F4E79"
TEAL = "#2E86AB"
ORANGE = "#E67E22"
RED = "#C0392B"
GREEN = "#1E8449"
GRAY = "#7F8C8D"
BG = "#F4F6F7"
LANES = ["#EBF0F5", "#FFFFFF"]


def box(ax, x, y, w, h, text, fc="white", ec=NAVY, fs=11, tc="#212121", lw=1.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.012",
                                fc=fc, ec=ec, lw=lw, mutation_aspect=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.5)


def arrow(ax, x1, y1, x2, y2, color=NAVY, lw=2.0, style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, color=color,
                                 lw=lw, linestyle=ls, mutation_scale=16,
                                 connectionstyle=f"arc3,rad={rad}"))


def label(ax, x, y, text, fs=9, color=GRAY, ha="center"):
    ax.text(x, y, text, ha=ha, va="center", fontsize=fs, color=color)


def new_fig(w, h, title):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.005, 0.005), 0.99, 0.99, boxstyle="round,pad=0.004",
                                fc=BG, ec="#BDC3C7", lw=1.0))
    ax.text(0.5, 0.965, title, ha="center", va="center", fontsize=17,
            color=NAVY, fontweight="bold")
    return fig, ax


def save(fig, name):
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved {path}")


# ================= 图 1：测试框架总体流程图 =================
def fig_framework():
    fig, ax = new_fig(14.5, 8.6, "图 1  传感器仿真测试框架——总体流程与数据流")

    layers = [
        (0.80, "① 配置层（唯一数值来源）", "#D6E4F0",
         [("sensor_params.yaml\n传感器标称参数", 0.06), ("test_thresholds.yaml\n46 条用例判定阈值", 0.29),
          ("sampling 采样计划\n200 帧 ×3 seed", 0.52), ("spec 0002\n需求与 AC（R2 pass）", 0.75)]),
        (0.60, "② 场景层（场景即代码）", "#D5EDE0",
         [("obstacles.py\n障碍物库 50 项\n五要素+距离档+门限", 0.06),
          ("scenarios.py\n46 条场景注册\nNAMED 条件表", 0.31),
          ("W0-W3 场景世界\nW0校准/W1高尔夫/W2足球/W3环境", 0.58)]),
        (0.40, "③ 执行层（可替换后端）", "#FDF0DC",
         [("backends.py\nSyntheticBackend（种子确定性）\n故障注入 / 7 降级组合\n→ 真实引擎后端同接口替换", 0.06),
          ("runner.py\nrun_tc / run_suite / run_all\n46 条判定逻辑", 0.47),
          ("GT 真值流\n≥100 Hz 全局快照\n（引擎接入后启用）", 0.76)]),
        (0.20, "④ 判定与输出层", "#FADBD8",
         [("verdict.py 判定器\n检出率 / Wilson 95% CI\n稳定窗(10帧≥8) / 误差统计", 0.06),
          ("verdict.json 归档\nreports/0002-*/<TC-ID>/", 0.42),
          ("CI 门禁\npytest 160 项全绿\nruff 无告警", 0.68)]),
    ]
    for y, title, color, items in layers:
        ax.add_patch(FancyBboxPatch((0.02, y - 0.015), 0.96, 0.135, boxstyle="round,pad=0.004",
                                    fc=color, ec="#BDC3C7", lw=1.0))
        ax.text(0.035, y + 0.104, title, fontsize=12, fontweight="bold", color=NAVY)
        for text, x in items:
            w = 0.20 if "backends" in text or "runner" in text else 0.185
            box(ax, x, y + 0.005, w, 0.088, text, fs=9.5, ec=TEAL, bold=False)

    for y in (0.60 + 0.12, 0.40 + 0.12, 0.20 + 0.12):
        for x in (0.15, 0.40, 0.63, 0.85):
            arrow(ax, x, y + 0.035, x, y - 0.005, lw=1.4)
    ax.text(0.5, 0.115, "自上而下：配置驱动 → 场景采样 → 判定门禁 → 证据归档 ｜ "
                        "左侧四层与 tests/ 一一对应，阈值变更须同步 spec 并过一致性测试",
            ha="center", fontsize=10, color=GRAY)
    save(fig, "01_framework_flow.png")


# ================= 图 2：测试步骤泳道图 =================
def fig_swimlane():
    fig, ax = new_fig(15.5, 8.6, "图 2  单条用例执行流程——泳道图（以 TC-L-05 旗杆检出为例）")

    lanes = ["场景与配置\nscenarios/\nthresholds", "传感器后端\nbackends", "执行器\nrunner",
             "判定器\nverdict", "报告与放行\nreport/CI/DoD"]
    lane_h, lane_y0 = 0.152, 0.075
    for i, name in enumerate(lanes):
        y = lane_y0 + (len(lanes) - 1 - i) * lane_h
        ax.add_patch(FancyBboxPatch((0.108, y), 0.882, lane_h - 0.014,
                                    boxstyle="round,pad=0.003", fc=LANES[i % 2],
                                    ec="#D5DBDB", lw=1.0))
        ax.add_patch(FancyBboxPatch((0.010, y), 0.094, lane_h - 0.014,
                                    boxstyle="round,pad=0.003", fc=NAVY, ec=NAVY))
        ax.text(0.057, y + (lane_h - 0.014) / 2, name, ha="center", va="center",
                fontsize=8.2, color="white", fontweight="bold")

    ly = {0: lane_y0 + 4 * lane_h, 1: lane_y0 + 3 * lane_h, 2: lane_y0 + 2 * lane_h,
          3: lane_y0 + lane_h, 4: lane_y0}
    cy = lambda ln: ly[ln] + (lane_h - 0.014) / 2  # noqa: E731

    steps = [
        (0.125, 0, "S1 装载配置\n读取判定线与\n障碍物规格", TEAL),
        (0.255, 0, "S2 构建场景\n旗杆 @0.5-5m\nseed 11/22/33", TEAL),
        (0.385, 1, "S3 采样观测\n≥200 帧/条件\n合成/真实引擎", ORANGE),
        (0.515, 2, "S4 汇总命中流\n多 seed 合并\n（600 帧）", ORANGE),
        (0.645, 3, "S5 统计判定\n稳定率(10帧≥8)\nWilson 95% CI", NAVY),
        (0.775, 3, "S6 rule 门禁\n率≥0.98@≤3m\n0.90@5m", NAVY),
        (0.905, 4, "S7 verdict 归档\nverdict.json\n+report.md", GREEN),
    ]
    coords = {}
    for x, ln, text, color in steps:
        w, h = 0.108, 0.100
        box(ax, x, cy(ln) - h / 2, w, h, text, fs=8.6, ec=color, fc="white", lw=1.8)
        coords[text[:2]] = (x, ln)

    seq = [("S1", "S2"), ("S2", "S3"), ("S3", "S4"), ("S4", "S5"), ("S5", "S6"), ("S6", "S7")]
    bw = 0.108  # 步骤框宽：箭头必须从框右缘出发、到下一框左缘结束
    for a, b in seq:
        (x1, l1), (x2, l2) = coords[a], coords[b]
        arrow(ax, x1 + bw + 0.004, cy(l1), x2 - 0.004, cy(l2), lw=1.8,
              rad=0.15 if l1 != l2 else 0.0)

    # 底部判定带：S8 分支 → 放行 / 整改回环
    ax.add_patch(FancyBboxPatch((0.012, 0.012), 0.978, 0.046, boxstyle="round,pad=0.003",
                                fc="#FBFCFC", ec="#D5DBDB", lw=1.0))
    arrow(ax, 0.958, cy(4) - 0.052, 0.72, 0.058, color=GREEN, lw=1.8, rad=0.18)
    box(ax, 0.565, 0.018, 0.155, 0.034, "S8 全部 46 条用例通过？", fs=9.5, ec=GREEN, lw=1.8)
    box(ax, 0.845, 0.018, 0.125, 0.034, "放行（DoD）", fs=10, fc=GREEN, ec=GREEN, tc="white", bold=True)
    box(ax, 0.255, 0.018, 0.185, 0.034, "fail → 落 Issue 整改", fs=10, fc=RED, ec=RED, tc="white", bold=True)
    arrow(ax, 0.563, 0.035, 0.443, 0.035, color=RED, lw=1.8)
    ax.text(0.503, 0.048, "否", fontsize=9, color=RED)
    arrow(ax, 0.722, 0.035, 0.843, 0.035, color=GREEN, lw=1.8)
    ax.text(0.782, 0.048, "是", fontsize=9, color=GREEN)
    arrow(ax, 0.253, 0.035, 0.30, 0.035, color=RED, lw=1.4)
    arrow(ax, 0.29, 0.030, 0.29, cy(0) - 0.055, color=RED, lw=1.4, ls=(0, (4, 2)), rad=0.0)
    ax.text(0.30, 0.115, "整改后回 S2（同分支 spec/NNNN，改场景/阈值/资产）", fontsize=8.4, color=RED)
    ax.text(0.55, 0.905, "泳道职责：配置只读 → 后端可替换 → 执行器不看数值 → 判定器不看来源 → 证据落盘",
            fontsize=10, color=GRAY)
    save(fig, "02_execution_swimlane.png")


# ================= 图 3：传感器数据流架构图 =================
def fig_architecture():
    fig, ax = new_fig(14.5, 8.0, "图 3  被测传感器套件与融合感知——数据流架构（含考核包络）")

    # 机器人本体
    ax.add_patch(FancyBboxPatch((0.30, 0.10), 0.40, 0.74, boxstyle="round,pad=0.006",
                                fc="#EAF2F8", ec=NAVY, lw=2.0))
    ax.text(0.50, 0.885, "割草机器人 DUT（800×600×350 mm）", ha="center", fontsize=11,
            color=NAVY, fontweight="bold")

    sensors = [
        (0.335, "主 LiDAR ×1\n顶置 H=350mm\n360°×59°\n10Hz / 0.1-40m", "近地覆盖线 0.67m\n(0.350-0.080)/tan22°", TEAL),
        (0.475, "超声波 ×12\n环形 30° 间隔\nH=120mm / ±15°\n0.05-1.5m", "近场兜底：0.67m 内\n低矮目标由超声负责", ORANGE),
        (0.615, "双目相机 ×2\n左右侧向 H=250mm\n基线 90mm / 30fps\n0.2-4m", "侧向视场\n交接带 0.7-1.5m", GREEN),
    ]
    for x, text, note, color in sensors:
        box(ax, x, 0.655, 0.115, 0.16, text, fs=8.6, ec=color, lw=2.0)
        label(ax, x + 0.0575, 0.592, note, fs=8.0)
        arrow(ax, x + 0.0575, 0.650, x + 0.0575, 0.545, color=color, lw=1.8)

    box(ax, 0.345, 0.44, 0.385, 0.095,
        "单传感器处理\nLiDAR 点云聚类 / 超声回波测距（温补 c=331.4+0.6T）/ 双目视差→深度",
        fs=9.5, ec=GRAY)
    arrow(ax, 0.5375, 0.435, 0.5375, 0.375, lw=2.0)
    box(ax, 0.345, 0.28, 0.385, 0.09,
        "融合感知（TC-F 被测）\n10Hz 目标级列表：位置/尺寸/类别/速度/置信度/主导传感器\nP95 ≤200ms；安全通路 P95 ≤250ms",
        fs=9.5, ec=RED, fc="#FDEDEC", lw=2.0)
    arrow(ax, 0.5375, 0.275, 0.5375, 0.215, color=RED, lw=2.0)
    box(ax, 0.395, 0.145, 0.285, 0.065,
        "避碰 / 安全停\n0 碰撞（TC-F-09/10 不可豁免）", fs=10, ec=RED, fc="#FADBD8", tc=RED, bold=True)

    # 测试侧
    box(ax, 0.045, 0.30, 0.215, 0.24,
        "仿真测试注入（本框架）\n场景世界 W0-W3\n50 项障碍物库\nENV-1~9 环境矩阵\nseed 确定性重放", fs=9.5, ec=NAVY, fc="white", lw=1.8)
    arrow(ax, 0.262, 0.47, 0.343, 0.47, lw=1.8)
    label(ax, 0.302, 0.49, "激励", fs=9)
    box(ax, 0.775, 0.30, 0.19, 0.24,
        "GT 真值对齐\n≥100Hz 全局快照\n障碍物 ID/位姿/材质\n机器人位姿/仿真时钟", fs=9.5, ec=GRAY, fc="white", lw=1.8)
    arrow(ax, 0.735, 0.47, 0.773, 0.47, lw=1.8, color=GRAY)
    label(ax, 0.755, 0.49, "比对", fs=9)
    arrow(ax, 0.872, 0.295, 0.872, 0.105, color=GRAY, lw=1.6, ls=(0, (4, 2)))
    arrow(ax, 0.872, 0.105, 0.66, 0.105, color=GRAY, lw=1.6, ls=(0, (4, 2)))
    arrow(ax, 0.5375, 0.105, 0.5375, 0.142, color=GRAY, lw=1.6, ls=(0, (4, 2)))
    ax.text(0.665, 0.082, "oracle 判定：观测 vs 真值 → rule 数值证据（禁截图）",
            fontsize=9, color=GRAY)
    save(fig, "03_sensor_architecture.png")


# ================= 图 4：障碍物库介绍图 =================
def fig_obstacles():
    fig, ax = new_fig(15.0, 8.8, "图 4  障碍物规格库（50 项）——四组分类与代表品类")

    cards = [
        (0.035, 0.50, "A 标准参照类（7 项）", TEAL,
         "Φ25/50/75 圆柱 ｜ 10%/50%/90% 反射率板\n标准纸箱 ｜ 标定球 ｜ 吸声软板\n平面镜/玻璃 ｜ 0-60° 倾角平台",
         "用途：计量基准与极限响应（低反/吸声/镜面/斜入射）"),
        (0.515, 0.50, "B 商用高尔夫球场类（21 项）", GREEN,
         "旗杆 Φ19×2100 ｜ 洞杯 ｜ 沙坑(唇沿150/陡壁1m)\n水塘 5×8m ｜ 喷头(凸出0/15/30mm) ｜ 缘石\n高尔夫球 Φ42.67 ｜ 球车 ｜ 雁群/犬 ｜ 长草簇\n码数桩 ｜ 球包 ｜ 沙耙 ｜ 软管 ｜ 维修沟 ｜ 兽穴\n练习网 ｜ 间隙护栏 ｜ 乔木 ｜ 灌木",
         "难点：极细长/负障碍/水面镜面/半透明网面/软硬混合"),
        (0.035, 0.075, "C 足球场类（14 项）", ORANGE,
         "门柱 Φ120 高光 ｜ 带网球门 7320×2440 ｜ 角旗\n足球 Φ220(静/滚10m/s/飞行) ｜ 锥筒 H320/500\n敏捷栏 ｜ 人墙模型 ｜ 广告围挡(高/低纹理)\n运动员 6-8m/s ｜ 绳梯 ｜ 球筐 ｜ 排水箅子\n划线机 ｜ 同型割草机器人",
         "难点：高光过曝/网面穿透/高速动态/自相似目标"),
        (0.515, 0.075, "D 交叉安全类（8 项）", RED,
         "人形假人(站 H1750/蹲 H900) ｜ 俯卧儿童 H300\n平铺衣物 ｜ 铁丝网(目50×50, 线Φ2) ｜ 反光警戒带\n石块 150/250 ｜ 场边长凳 ｜ 折叠椅/遮阳伞",
         "铁律：TC-F-09/10 零碰撞，不可豁免；误分为可碾压 =0"),
    ]
    for x, y, title, color, items, note in cards:
        ax.add_patch(FancyBboxPatch((x, y), 0.45, 0.40, boxstyle="round,pad=0.006",
                                    fc="white", ec=color, lw=2.2))
        ax.add_patch(FancyBboxPatch((x, y + 0.335), 0.45, 0.065, boxstyle="round,pad=0.006",
                                    fc=color, ec=color, lw=2.2))
        ax.text(x + 0.225, y + 0.367, title, ha="center", va="center", fontsize=12,
                color="white", fontweight="bold")
        ax.text(x + 0.022, y + 0.20, items, fontsize=9.3, va="center", linespacing=1.75)
        ax.text(x + 0.022, y + 0.035, note, fontsize=8.8, color=color, style="italic")

    ax.add_patch(FancyBboxPatch((0.035, 0.005), 0.93, 0.052, boxstyle="round,pad=0.004",
                                fc="#FDF2E9", ec=ORANGE, lw=1.4))
    ax.text(0.5, 0.031, "边角品类全覆盖：负障碍 ｜ 半透明网面 ｜ 吸声软目标 ｜ 镜面 ｜ 高反细线 ｜ 俯卧儿童 ｜ 动态 pop-out ｜ 夜场泛光 1800 lux",
            ha="center", va="center", fontsize=10.5, color="#9C640C", fontweight="bold")
    save(fig, "04_obstacle_library.png")


# ================= 图 5：执行顺序与回归策略 =================
def fig_strategy():
    fig, ax = new_fig(14.0, 5.6, "图 5  执行顺序与回归策略（门禁递进，安全最后且不可豁免）")

    stages = [
        (0.05, "阶段 1  计量基线（W0）", "TC-L-01~04\nTC-U-01/02 ｜ TC-C-01/02/07", "精度/盲区/反射率/同步标定", TEAL),
        (0.285, "阶段 2  单传感器功能", "其余 TC-L/U/C\n（含 3 条全库普查）", "检出/环境/覆盖/完整性", GREEN),
        (0.52, "阶段 3  融合感知", "TC-F-01~08、11~13", "完备性/互补/降级/延迟/决定论", ORANGE),
        (0.755, "阶段 4  安全专项", "TC-F-09/10", "静态+动态避碰\n碰撞 = 0 不可豁免", RED),
    ]
    for x, title, tcs, note, color in stages:
        ax.add_patch(FancyBboxPatch((x, 0.42), 0.21, 0.34, boxstyle="round,pad=0.006",
                                    fc="white", ec=color, lw=2.2))
        ax.add_patch(FancyBboxPatch((x, 0.66), 0.21, 0.10, boxstyle="round,pad=0.006",
                                    fc=color, ec=color, lw=2.2))
        ax.text(x + 0.105, 0.71, title, ha="center", va="center", fontsize=11,
                color="white", fontweight="bold")
        ax.text(x + 0.105, 0.585, tcs, ha="center", va="center", fontsize=9.3)
        ax.text(x + 0.105, 0.485, note, ha="center", va="center", fontsize=9.3, color=GRAY)
        if x < 0.75:
            arrow(ax, x + 0.213, 0.59, x + 0.232, 0.59, lw=2.4)

    ax.add_patch(FancyBboxPatch((0.05, 0.08), 0.915, 0.20, boxstyle="round,pad=0.006",
                                fc="#EBF5FB", ec=NAVY, lw=1.6))
    ax.text(0.507, 0.235, "回归策略", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(0.507, 0.155,
            "版本发布：全量 46 条重跑 ｜ 日常 CI 冒烟子集：TC-L-01 → TC-U-01 → TC-C-01 → TC-F-01（≤30 min）\n"
            "前置依赖：阶段 3 须在 TC-L/U/C 全通过后执行；阶段 4 最后执行，任一 rule 失败不得放行",
            ha="center", va="center", fontsize=10, linespacing=1.9)
    save(fig, "05_execution_strategy.png")


# ================= 图 6：数据流图（数据类） =================
def fig_dataflow():
    fig, ax = new_fig(15.0, 8.6, "图 6  测试数据流图——外部实体 / 处理过程 / 数据存储（字段级流向）")

    def entity(x, y, text, color):
        ax.add_patch(FancyBboxPatch((x, y), 0.16, 0.10, boxstyle="round,pad=0.004",
                                    fc="white", ec=color, lw=2.0))
        ax.text(x + 0.08, y + 0.05, text, ha="center", va="center",
                fontsize=9.2, color="#212121", linespacing=1.5)

    def store(y, text, color):
        ax.add_patch(FancyBboxPatch((0.60, y), 0.22, 0.08, boxstyle="round,pad=0.004",
                                    fc=color + "1E", ec=color, lw=1.8))
        ax.plot([0.60, 0.60], [y, y + 0.08], color=color, lw=5.0, solid_capstyle="butt")
        ax.text(0.715, y + 0.04, text, ha="center", va="center",
                fontsize=9.0, color="#212121", linespacing=1.5)

    def proc(y, text, color):
        ax.add_patch(FancyBboxPatch((0.30, y), 0.16, 0.075,
                                    boxstyle="round,pad=0.004,rounding_size=0.02",
                                    fc=color, ec=color, lw=1.6))
        ax.text(0.38, y + 0.0375, text, ha="center", va="center",
                fontsize=9.6, color="white", fontweight="bold", linespacing=1.45)

    def vflow(y1, y2, text):
        arrow(ax, 0.38, y1, 0.38, y2, lw=1.8)
        ax.text(0.395, (y1 + y2) / 2, text, ha="left", va="center", fontsize=8.2, color=NAVY)

    def hflow(y1, y2, text, color=NAVY, dashed=False, rad=0.0, label_dy=0.014):
        arrow(ax, 0.46, y1, 0.60, y2, color=color, lw=1.6,
              ls=(0, (3, 2)) if dashed else "-", rad=rad)
        ax.text(0.53, (y1 + y2) / 2 + label_dy, text, ha="center", va="center",
                fontsize=8.0, color=color,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.92))

    ax.text(0.115, 0.905, "外部实体", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(0.38, 0.905, "处理过程", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(0.71, 0.905, "数据存储", fontsize=11, color=NAVY, fontweight="bold")

    entity(0.035, 0.76, "spec 0002\n需求 / AC / 门禁", NAVY)
    entity(0.035, 0.60, "传感器选型\n规格书（冻结后）", TEAL)
    entity(0.035, 0.44, "真实仿真引擎\nIsaac / Gazebo（待接）", ORANGE)
    entity(0.035, 0.20, "测试工程师\n读 verdict / 改阈值", GREEN)

    proc(0.795, "P1 配置装载\nthresholds.py", NAVY)
    proc(0.665, "P2 场景构建\nscenarios.py", NAVY)
    proc(0.535, "P3 观测采样\nbackends.py", TEAL)
    proc(0.405, "P4 统计判定\nverdict.py", ORANGE)
    proc(0.275, "P5 编排执行\nrunner.py", GREEN)

    store(0.795, "D1 sensor_params.yaml\n量程 / 安装 / 帧率 / σ", TEAL)
    store(0.675, "D2 test_thresholds.yaml\n46 条 gates + 采样计划", NAVY)
    store(0.545, "D3 obstacles.py\n50 项 × 五要素 + 距离档", GREEN)
    store(0.415, "D4 scenarios.py\n46 条注册 + NAMED 条件表", ORANGE)
    store(0.275, "D5 reports/0002-*/<TC>/\nverdict.json（rule 证据）", RED)

    arrow(ax, 0.197, 0.81, 0.296, 0.828, color=NAVY, lw=1.6)
    ax.text(0.245, 0.838, "AC / 门禁数值", ha="center", fontsize=8.0, color=NAVY)
    hflow(0.835, 0.835, "yaml.safe_load → dict")
    hflow(0.818, 0.715, "tc_gates(id) → gates", rad=0.10)
    arrow(ax, 0.197, 0.665, 0.60, 0.822, color=TEAL, lw=1.4, ls=(0, (3, 2)), rad=0.22)
    ax.text(0.36, 0.706, "规格书标称收紧（选型冻结后）", ha="center", fontsize=8.0, color=TEAL,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.92))
    arrow(ax, 0.197, 0.505, 0.296, 0.565, color=ORANGE, lw=1.4, ls=(0, (3, 2)))
    ax.text(0.243, 0.545, "观测替换合成", ha="center", fontsize=8.0, color=ORANGE)
    hflow(0.70, 0.585, "census_items(L/U/C)", color=GREEN, rad=0.08)
    hflow(0.685, 0.455, "NAMED[tc] 条件", color=ORANGE, rad=-0.10)
    hflow(0.425, 0.315, "verdict {pass, checks[]}", color=RED, rad=-0.08)
    arrow(ax, 0.60, 0.24, 0.197, 0.24, color=GREEN, lw=1.4, ls=(0, (3, 2)))
    ax.text(0.398, 0.253, "读证据 → 发起整改（回 P1/P2）", ha="center", fontsize=8.0, color=GREEN)

    vflow(0.795, 0.740, "gates + 采样计划")
    vflow(0.665, 0.610, "条件 + seed")
    vflow(0.535, 0.480, "hits[bool] × 600（3 seed 合并）")
    vflow(0.405, 0.350, "verdict dict")

    ax.text(0.5, 0.115, "一致性闭环：D1↔D2 由 sensor_envelope 测试互锁 ｜ D2/D3/D4 与 spec.md 由 "
                        "test_config_consistency 强制对齐 ｜ 同 seed 重跑 D5 哈希一致（TC-F-13）",
            ha="center", fontsize=9.5, color=GRAY)
    save(fig, "06_data_flow.png")


# ================= 图 7：模块交互时序图（模块交互类） =================
def fig_sequence():
    fig, ax = new_fig(15.0, 8.4, "图 7  模块交互时序图——run_tc(\"TC-L-05\") 一次执行的调用链")

    actors = [
        (0.065, "pytest 用例\ntest_gates_l.py", "#5D6D7E"),
        (0.215, "runner\nrun_tc / run_suite", NAVY),
        (0.365, "thresholds\ntc_gates", TEAL),
        (0.505, "scenarios\nSCENARIOS / NAMED", GREEN),
        (0.655, "backends\nSyntheticBackend", ORANGE),
        (0.805, "verdict\n统计 + 门禁", "#8E44AD"),
        (0.935, "reports\nverdict.json", RED),
    ]
    top, bot = 0.845, 0.075
    for x, name, color in actors:
        ax.plot([x, x], [bot, top - 0.075], color="#BDC3C7", lw=1.2, ls=(0, (3, 3)), zorder=1)
        ax.add_patch(FancyBboxPatch((x - 0.068, top - 0.072), 0.136, 0.072,
                                    boxstyle="round,pad=0.004", fc=color, ec=color))
        ax.text(x, top - 0.036, name, ha="center", va="center", fontsize=8.6,
                color="white", fontweight="bold", linespacing=1.4)

    def msg(y, xa, xb, text, color=NAVY, ls="-", dashed=False):
        arrow(ax, xa, y, xb, y, color=color, lw=1.5, ls=(0, (3, 2)) if dashed else "-")
        ax.text((xa + xb) / 2, y + 0.013, text, ha="center", fontsize=8.0, color=color)

    y = top - 0.105
    msgs = [
        ("run_tc(\"TC-L-05\")", 0.065, 0.215, NAVY),
        ("tc_gates(\"TC-L-05\") → gates{archetype: detection}", 0.215, 0.365, TEAL),
        ("NAMED[\"TC-L-05\"] → 7 条件 (OB-B1/B7/D5 × 距离档)", 0.215, 0.505, GREEN),
        ("rng_for(\"TC-L-05|条件\", 11/22/33)", 0.215, 0.655, ORANGE),
        ("sample_hits(sensor, code, dist, 200) → hits[200]", 0.655, 0.215, ORANGE),
        ("stable_rate(hits) / wilson_interval(k, n)", 0.215, 0.805, "#8E44AD"),
        ("gate_check(率, \"ge\", 门限) → check{}", 0.215, 0.805, "#8E44AD"),
        ("make_verdict → {pass, failed, checks[]}", 0.805, 0.215, "#8E44AD"),
        ("json.dump → verdict.json（rule 数值证据）", 0.215, 0.935, RED),
    ]
    for text, xa, xb, color in msgs:
        msg(y, xa, xb, text, color)
        y -= 0.062

    # loop 框：多 seed 重复
    ly0, ly1 = y + 0.062 + 0.055, top - 0.155
    ax.add_patch(FancyBboxPatch((0.60, ly0), 0.335, (top - 0.155) - ly0 + 0.128,
                                boxstyle="round,pad=0.004", fc="none", ec=ORANGE, lw=1.4,
                                ls=(0, (4, 2)), zorder=0))
    ax.text(0.612, ly1 - 0.008, "loop × 3 seed", fontsize=8.4, color=ORANGE, fontweight="bold")

    # alt 框：fail 负向分支
    ay = 0.105
    ax.add_patch(FancyBboxPatch((0.13, ay), 0.72, 0.095, boxstyle="round,pad=0.004",
                                fc="#FDEDEC", ec=RED, lw=1.4, ls=(0, (4, 2))))
    ax.text(0.145, ay + 0.075, "alt 门禁 fail（如 faults.add(\"lidar_blind\")）", fontsize=8.6,
            color=RED, fontweight="bold")
    ax.text(0.50, ay + 0.032, "pass=false → failed 列表 → pytest 断言失败 → 落 Issue 整改（负向测试证明门禁真实生效）",
            ha="center", fontsize=8.4, color=RED)

    ax.text(0.5, 0.028, "设计约束：runner 不读 YAML 之外的数值 ｜ backends 可整体替换（同名接口） ｜ verdict 只做统计不做 I/O",
            ha="center", fontsize=9.5, color=GRAY)
    save(fig, "07_module_sequence.png")


if __name__ == "__main__":
    fig_framework()
    fig_swimlane()
    fig_architecture()
    fig_obstacles()
    fig_strategy()
    fig_dataflow()
    fig_sequence()
    print("all diagrams done")
