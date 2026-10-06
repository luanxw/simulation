/* 传感器仿真测试方案演示 deck 生成器
 * 用法：NODE_PATH=$(npm root -g) node scripts/make_deck.js
 * 输出：src/simulation/docs/sensor_test_overview.pptx
 */
const pptxgen = require("pptxgenjs");

const W = 13.33, H = 7.5, M = 0.5;
const NAVY = "1F4E79", TEAL = "2E86AB", ORANGE = "E67E22", RED = "C0392B",
      GREEN = "1E8449", INK = "1A2733", MUTED = "5E6B7A", TINT = "F2F5F8",
      LIGHT = "FFFFFF";
const F = "PingFang SC";
const DIAG = "src/simulation/docs/diagrams/";

const RATIOS = {
  "01_framework_flow.png": 1.677, "02_execution_swimlane.png": 1.79,
  "03_sensor_architecture.png": 1.798, "04_obstacle_library.png": 1.695,
  "05_execution_strategy.png": 2.45, "06_data_flow.png": 1.734,
  "07_module_sequence.png": 1.774,
};

let p = new pptxgen();
p.layout = "LAYOUT_WIDE";
p.author = "传感器仿真测试组";
p.title = "割草机器人传感器套件仿真测试方案";

const bu = () => ({ code: "2022", indent: 12 });

function kicker(s, tag, num, dark = false) {
  s.addText([
    { text: tag, options: { color: dark ? "9EC9E8" : TEAL, bold: true } },
    { text: "   " + num, options: { color: dark ? "6B7C93" : "9AA7B4" } },
  ], { x: M, y: 0.32, w: 6, h: 0.3, fontSize: 12, fontFace: F, margin: 0 });
}
function title(s, text, dark = false) {
  s.addText(text, { x: M, y: 0.58, w: W - 2 * M, h: 0.62, fontSize: 27, bold: true,
    color: dark ? LIGHT : NAVY, fontFace: F, margin: 0 });
}
function imgSlide(tag, num, t, file) {
  const s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, tag, num); title(s, t);
  const r = RATIOS[file];
  let h = 5.72, w = h * r;
  if (w > W - 2 * M) { w = W - 2 * M; h = w / r; }
  const y = 1.32 + (5.9 - h) / 2;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: (W - w) / 2 - 0.06, y: y - 0.06,
    w: w + 0.12, h: h + 0.12, fill: { color: TINT }, line: { color: "D8E0E6", width: 1 },
    rectRadius: 0.08 });
  s.addImage({ path: DIAG + file, x: (W - w) / 2, y, w, h });
  return s;
}
function stat(s, x, y, w, num, label, color) {
  s.addText(num, { x, y, w, h: 0.85, fontSize: 54, bold: true, color, fontFace: F,
    align: "center", margin: 0 });
  s.addText(label, { x, y: y + 0.88, w, h: 0.62, fontSize: 13, color: MUTED,
    fontFace: F, align: "center", margin: 0, valign: "top" });
}

/* ---------- 1 封面 ---------- */
{
  const s = p.addSlide();
  s.background = { color: NAVY };
  s.addText("割草机器人 · 传感器仿真测试", { x: M, y: 1.55, w: 9, h: 0.4,
    fontSize: 16, color: "9EC9E8", fontFace: F, charSpacing: 4, margin: 0 });
  s.addText("传感器套件仿真测试方案", { x: M, y: 2.05, w: 12, h: 1.1,
    fontSize: 48, bold: true, color: LIGHT, fontFace: F, margin: 0 });
  s.addText("1×主 LiDAR ＋ 12×环形超声波 ＋ 2×侧向双目 ｜ 融合感知与安全避碰\n商用高尔夫球场 · 足球场场景全要素覆盖",
    { x: M, y: 3.35, w: 11.5, h: 0.95, fontSize: 18, color: "C9D8E6", fontFace: F,
      margin: 0, lineSpacingMultiple: 1.35 });
  const stats = [["46", "条测试用例"], ["50", "项障碍物库"], ["7", "张设计视图"], ["0", "碰撞门禁"]];
  stats.forEach(([n, l], i) => {
    s.addText(n, { x: M + i * 2.15, y: 4.85, w: 1.9, h: 0.75, fontSize: 40, bold: true,
      color: "E67E22", fontFace: F, margin: 0 });
    s.addText(l, { x: M + i * 2.15, y: 5.6, w: 1.9, h: 0.35, fontSize: 13,
      color: "9EC9E8", fontFace: F, margin: 0 });
  });
  s.addText("SIM-STD-0002 · V1.0 ｜ 依据规格 0002（独立评审 R2 pass）｜ 2026-10",
    { x: M, y: 6.75, w: 12, h: 0.35, fontSize: 12, color: "6B7C93", fontFace: F, margin: 0 });
}

/* ---------- 2 被测对象 ---------- */
{
  const s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "被测对象 DUT", "01"); title(s, "被测传感器套件与安全包络");
  const r = RATIOS["03_sensor_architecture.png"], h = 4.62, w = h * r;
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M - 0.05, y: 1.36, w: w + 0.1, h: h + 0.1,
    fill: { color: TINT }, line: { color: "D8E0E6", width: 1 }, rectRadius: 0.08 });
  s.addImage({ path: DIAG + "03_sensor_architecture.png", x: M, y: 1.41, w, h });
  const sx = 9.35, sw = 3.45;
  s.addText("覆盖预算（已复核口径）", { x: sx, y: 1.42, w: sw, h: 0.35, fontSize: 14,
    bold: true, color: NAVY, fontFace: F, margin: 0 });
  stat(s, sx, 1.85, sw, "0.67 m", "LiDAR 近地覆盖线\n更低矮目标由超声兜底", TEAL);
  stat(s, sx, 3.35, sw, "1.04 m", "1.6 m/s 急停距离\n< 超声 1.5 m 量程", ORANGE);
  stat(s, sx, 4.85, sw, "≤250 ms", "安全通路端到端 P95\n（融合输出 ≤200 ms）", RED);
}

/* ---------- 3 场景世界 ---------- */
{
  const s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "场景世界", "02"); title(s, "四类场景世界与环境矩阵");
  const rows = [
    ["W0 校准场", "50×50 m 哑光地面 · AprilTag 阵列 · 可编程漫射光", "计量基线", TEAL],
    ["W1 商用高尔夫球场", "球道 30×60 m · 果岭 Φ15 m · 沙坑×2 · 水塘 5×8 m · 球车道 · 喷头×8 · 旗杆洞杯 · 球车/行人/雁群动态", "高尔夫专项", GREEN],
    ["W2 足球场", "105×68 m 天然草 · 球门×2（柱+带网）· 角旗×4 · 广告围挡 · 训练器具 · 运动员 6–8 m/s · 夜场泛光 1800 lux", "足球专项", ORANGE],
    ["W3 环境注入场", "光照 5 档（100 klux→夜场）· 雨/喷灌/雾（至 50 m）/露水 · 风 3/6/9 m/s · 温度 5–35 °C · 草被 4–120 mm · 坡度至 15°", "环境鲁棒", RED],
  ];
  rows.forEach(([name, desc, tag, color], i) => {
    const y = 1.42 + i * 1.32;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y, w: 9.1, h: 1.14,
      fill: { color: TINT }, line: { color: "D8E0E6", width: 1 }, rectRadius: 0.06 });
    s.addShape(p.shapes.OVAL, { x: 0.72, y: y + 0.28, w: 0.58, h: 0.58, fill: { color } });
    s.addText(name.slice(0, 2), { x: 0.72, y: y + 0.28, w: 0.58, h: 0.58, fontSize: 15,
      bold: true, color: LIGHT, fontFace: F, align: "center", valign: "middle", margin: 0 });
    s.addText(name, { x: 1.5, y: y + 0.12, w: 6.4, h: 0.4, fontSize: 16, bold: true,
      color: INK, fontFace: F, margin: 0 });
    s.addText(desc, { x: 1.5, y: y + 0.52, w: 7.4, h: 0.56, fontSize: 11.5,
      color: MUTED, fontFace: F, margin: 0, valign: "top" });
    s.addText(tag, { x: 7.6, y: y + 0.14, w: 1.85, h: 0.34, fontSize: 11, bold: true,
      color, fontFace: F, align: "right", margin: 0 });
  });
  const ex = 9.95, ew = 2.9;
  s.addText("ENV 环境矩阵（9 项）", { x: ex, y: 1.42, w: ew, h: 0.35, fontSize: 14,
    bold: true, color: NAVY, fontFace: F, margin: 0 });
  s.addText([
    { text: "ENV-1 光照 5 档", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-2 降雨 2/20 mm/h", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-3 喷灌水雾", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-4 雾霾 至 50 m", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-5 露水凝露", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-6 风 3/6/9 m/s", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-7 温度 5–35 °C", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-8 草被 4–120 mm", options: { bullet: bu(), breakLine: true } },
    { text: "ENV-9 地形 0–15°", options: { bullet: bu() } },
  ], { x: ex, y: 1.85, w: ew, h: 3.9, fontSize: 12.5, color: INK, fontFace: F,
    paraSpaceAfter: 9, margin: 0 });
  s.addText("全部场景即代码：YAML + seed，同 seed 重跑结果完全一致（TC-F-13 强制）",
    { x: ex, y: 5.95, w: ew, h: 0.8, fontSize: 11, color: MUTED, fontFace: F, margin: 0 });
}

/* ---------- 4-8 图片页 ---------- */
imgSlide("障碍物介绍", "03", "障碍物规格库：50 项 · 四组分类 · 五要素规格", "04_obstacle_library.png");
imgSlide("架构设计类", "04", "测试框架分层架构：配置 → 场景 → 执行 → 判定输出", "01_framework_flow.png");
imgSlide("数据类", "05", "测试数据流：外部实体 / 处理过程 / 数据存储", "06_data_flow.png");
imgSlide("流程逻辑类", "06", "单条用例执行泳道：从装载配置到放行/整改回环", "02_execution_swimlane.png");
imgSlide("模块交互类", "07", "模块交互时序：run_tc 一次执行的完整调用链", "07_module_sequence.png");

/* ---------- 9 用例体系 ---------- */
{
  const s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "用例体系", "08"); title(s, "46 条测试用例与判定门禁");
  const cards = [
    ["11", "TC-L 主 LiDAR", "测距 ±30 mm · 角分辨 3°\n旗杆 ≥98%@≤3 m\n近地 0.67 m 内不考核", TEAL],
    ["12", "TC-U 超声波 ×12", "通道精度 ±15 mm\n串扰虚警 ≤1% · 环形 ≥71/72\n高尔夫球 @0.3 m ≥90%", GREEN],
    ["10", "TC-C 双目 ×2", "深度 ≤max(30mm, 2.5%Z)\n夜场泛光 ≥90%\n左右同步 ≤1 ms", ORANGE],
    ["13", "TC-F 融合感知", "完备性 ≥max(单传感器)−2pp\n延迟 P95 200/250 ms\n7 组合降级包线", NAVY],
  ];
  cards.forEach(([n, name, desc, color], i) => {
    const x = M + i * 3.21;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.96, h: 3.3,
      fill: { color: TINT }, line: { color: "D8E0E6", width: 1 }, rectRadius: 0.08 });
    s.addText(n, { x: x + 0.2, y: 1.68, w: 2.5, h: 0.9, fontSize: 52, bold: true,
      color, fontFace: F, margin: 0 });
    s.addText(name, { x: x + 0.2, y: 2.62, w: 2.6, h: 0.4, fontSize: 15, bold: true,
      color: INK, fontFace: F, margin: 0 });
    s.addText(desc, { x: x + 0.2, y: 3.06, w: 2.62, h: 1.6, fontSize: 11.5,
      color: MUTED, fontFace: F, margin: 0, valign: "top", lineSpacingMultiple: 1.3 });
  });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 5.15, w: W - 2 * M, h: 1.55,
    fill: { color: "FDEDEC" }, line: { color: RED, width: 1.4 }, rectRadius: 0.07 });
  s.addText("安全专项（TC-F-09/10）—— 放行铁律", { x: 0.85, y: 5.32, w: 11, h: 0.4,
    fontSize: 15, bold: true, color: RED, fontFace: F, margin: 0 });
  s.addText([
    { text: "静态 + 动态避碰碰撞次数 = 0，不可豁免 ｜ 安全品类（人形/俯卧儿童/动物/车辆/pop-out/深负障碍）误分为可碾压 = 0", options: { breakLine: true } },
    { text: "停止间隙 ≥50 mm @0.8 m/s、≥100 mm @1.6 m/s ｜ 触发距离一致性 σ ≤30 mm ｜ 每条件 ≥3 次重复 ×2 seed", options: {} },
  ], { x: 0.85, y: 5.74, w: 11.6, h: 0.85, fontSize: 12.5, color: INK, fontFace: F,
    margin: 0, lineSpacingMultiple: 1.4 });
}

/* ---------- 10 融合与降级 ---------- */
{
  const s = p.addSlide();
  s.background = { color: LIGHT };
  kicker(s, "融合感知", "09"); title(s, "融合专项：互补、仲裁与降级包线");
  const rows = [
    ["目标级精度", "位置 ≤50 mm · 分类 10 类混淆对角 ≥90% · 安全类误分 = 0"],
    ["检出完备性", "每项 ≥ max(单传感器) − 2 pp · 全库 ≥95% · 安全品类 ≥98%"],
    ["虚警抑制", "假障碍 ≤2 次/km · 假急停 ≤1 次/km（10 km 等效）"],
    ["冲突仲裁", "故障源 >3σ 注入 → 2 s 内降权隔离 · 双影目标 = 0"],
    ["动态跟踪", "ID 切换 ≤1/50 遭遇 · 稳定轨迹 ≤300 ms · pop-out ≤3 帧检出"],
    ["确定复现", "同 seed 重跑 5 次输出哈希完全一致（TC-F-13）"],
  ];
  rows.forEach(([k, v], i) => {
    const y = 1.5 + i * 0.86;
    s.addText(k, { x: M, y, w: 1.75, h: 0.75, fontSize: 15, bold: true, color: NAVY,
      fontFace: F, margin: 0, valign: "middle" });
    s.addText(v, { x: 2.35, y, w: 5.1, h: 0.75, fontSize: 11.5, color: INK,
      fontFace: F, margin: 0, valign: "middle" });
    if (i < 5) s.addShape(p.shapes.LINE, { x: M, y: y + 0.8, w: 6.95, h: 0,
      line: { color: "E1E7EC", width: 0.75 } });
  });
  const tx = 7.85, tw = 5.0;
  s.addText("7 组合降级包线（TC-F-08，摘选）", { x: tx, y: 1.5, w: tw, h: 0.35,
    fontSize: 14, bold: true, color: NAVY, fontFace: F, margin: 0 });
  const hdr = { fill: { color: NAVY }, color: "FFFFFF", bold: true, fontFace: F };
  const c = (t, o) => ({ text: t, options: o || {} });
  s.addTable([
    [c("禁用组合", hdr), c("全库", hdr), c("安全品类", hdr)],
    [c("仅超声在位"), c("—"), c("≥90% @≤0.8m")],
    [c("仅 LiDAR 在位"), c("≥85%"), c("≥90%")],
    [c("禁用 LiDAR"), c("≥75%"), c("≥90%")],
    [c("禁用超声"), c("≥92%"), c("≥95%")],
    [c("禁用双目"), c("≥92%"), c("≥95%")],
    [c("单侧双目"), c("同侧 −5pp"), c("对侧 −1pp")],
  ], { x: tx, y: 1.95, w: tw, rowH: 0.42, fontSize: 11, fontFace: F, color: INK,
    border: { pt: 0.75, color: "D8E0E6" }, valign: "middle",
    fill: { color: "FBFCFD" }, colW: [2.1, 1.25, 1.65] });
  s.addText("完整数值见 test_thresholds.yaml → degradation_envelope（7 组合逐项门禁，由测试强制对齐）",
    { x: tx, y: 5.35, w: tw, h: 0.7, fontSize: 10.5, color: MUTED, fontFace: F, margin: 0 });
}

/* ---------- 11 执行策略 ---------- */
imgSlide("执行策略", "10", "执行顺序与回归策略：四阶段门禁递进，安全最后且不可豁免", "05_execution_strategy.png");

/* ---------- 12 收尾 ---------- */
{
  const s = p.addSlide();
  s.background = { color: NAVY };
  kicker(s, "质量证据与下一步", "11", true);
  title(s, "评审闭环 · 代码基线 · 待办", true);
  const steps = [
    ["R1 独立评审", "fail：6 条 actionable\n（覆盖口径/矩阵断链/分类清单/降级包线/方法字段/计数）", "C0392B"],
    ["I-1~I-6 整改", "全部落账并闭合\n15 项自验 + Wilson/几何复算全过", "E67E22"],
    ["R2 独立复审", "pass：完备性 rubric 5 分\n仅余 2 条 advisory（不阻塞）", "1E8449"],
  ];
  steps.forEach(([k, v, color], i) => {
    const x = M + i * 4.2;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.55, w: 3.9, h: 1.7,
      fill: { color: "27547F" }, line: { color: color, width: 1.5 }, rectRadius: 0.08 });
    s.addText(k, { x: x + 0.25, y: 1.7, w: 3.4, h: 0.4, fontSize: 16, bold: true,
      color: LIGHT, fontFace: F, margin: 0 });
    s.addText(v, { x: x + 0.25, y: 2.12, w: 3.5, h: 1.0, fontSize: 11.5,
      color: "C9D8E6", fontFace: F, margin: 0, lineSpacingMultiple: 1.3 });
    if (i < 2) s.addText("→", { x: x + 3.92, y: 2.15, w: 0.35, h: 0.5, fontSize: 22,
      bold: true, color: "6B7C93", fontFace: F, margin: 0, align: "center" });
  });
  const evid = [
    ["160", "pytest 全绿：四套门禁\n+ 一致性 + 负向注入"],
    ["0", "ruff 告警：py3.12\nconda 独立环境"],
    ["46", "条 verdict 可归档\n数值证据 · 禁截图"],
  ];
  evid.forEach(([n, l], i) => {
    s.addText(n, { x: M + i * 4.2, y: 3.55, w: 1.5, h: 0.7, fontSize: 40, bold: true,
      color: "E67E22", fontFace: F, margin: 0 });
    s.addText(l, { x: M + i * 4.2 + 1.45, y: 3.58, w: 2.55, h: 0.8, fontSize: 11.5,
      color: "C9D8E6", fontFace: F, margin: 0, valign: "middle", lineSpacingMultiple: 1.25 });
  });
  s.addText("下一步", { x: M, y: 4.75, w: 3, h: 0.4, fontSize: 15, bold: true,
    color: LIGHT, fontFace: F, margin: 0 });
  const nexts = [
    ["① 方案批准", "确认 spec 0002 与 6 项待澄清问题"],
    ["② 引擎选型", "Task 1 PoC（候选 ≥2）→ ADR-0003"],
    ["③ 真实后端取证", "替换 SyntheticBackend → 全量 46 条 verdict"],
  ];
  nexts.forEach(([k, v], i) => {
    const x = M + i * 4.2;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 5.25, w: 3.9, h: 1.0,
      fill: { color: "1A3D61" }, line: { color: "2E86AB", width: 1.2 }, rectRadius: 0.08 });
    s.addText(k, { x: x + 0.22, y: 5.36, w: 3.4, h: 0.35, fontSize: 13.5, bold: true,
      color: "9EC9E8", fontFace: F, margin: 0 });
    s.addText(v, { x: x + 0.22, y: 5.72, w: 3.5, h: 0.42, fontSize: 11,
      color: "C9D8E6", fontFace: F, margin: 0 });
  });
  s.addText("配套交付：spec.md / tasks.md / review.md（.trae/specs/0002）· pytest 基线（src/simulation）· 标准指导书 + 使用说明 + 7 张设计图",
    { x: M, y: 6.7, w: 12.3, h: 0.4, fontSize: 11, color: "6B7C93", fontFace: F, margin: 0 });
}

p.writeFile({ fileName: "src/simulation/docs/sensor_test_overview.pptx" })
  .then(() => console.log("deck written"));
