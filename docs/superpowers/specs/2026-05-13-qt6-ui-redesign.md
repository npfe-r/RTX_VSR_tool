# PyQt6 UI 重设计规格文档

**项目**: RTX 视频超分辨率工具  
**日期**: 2026-05-13  
**状态**: 设计定稿

---

## 1. 整体布局

### 1.1 窗口规格

- 默认尺寸: 1200×800，居中显示
- 最小尺寸: 960×600
- 窗口标题: "RTX 视频超分辨率工具"
- 窗口图标: 应用自定义图标
- 主窗口继承 `QMainWindow`，中心部件使用 `QWidget` + `QVBoxLayout`

### 1.2 区域划分

```
┌──────────────────────────────────────────────────────────────┐
│  TitleBar (QMenuBar + 标题 + 窗口控制)                       │
├──────────────────────────────────────────────────────────────┤
│  FileBar (输入/输出路径 + 浏览按钮 + 拖拽)   固定高度 80px     │
├─────────────────────────────┬────────────────────────────────┤
│                             │                                │
│   VideoPanel                │   ParamPanel                   │
│   ┌───────────────────┐    │   ┌────────────────────────┐   │
│   │   视频预览 (QLabel) │    │   │ 📐 输出尺寸  (可折叠)    │   │
│   │   QPixmap 缩放显示  │    │   ├────────────────────────┤   │
│   └───────────────────┘    │   │ 🧠 AI 处理     (可折叠)    │   │
│   ┌───────────────────┐    │   ├────────────────────────┤   │
│   │   视频信息卡片       │    │   │ 🎞 编码设置    (可折叠)    │   │
│   └───────────────────┘    │   └────────────────────────┘   │
│                             │                                │
├─────────────────────────────┴────────────────────────────────┤
│  BottomBar (开始/暂停/停止 + 进度 + 统计)    固定高度 80px     │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 分割器

- 视频面板与参数面板之间使用 `QSplitter(Horizontal)`
- 初始比例: 视频面板 55% / 参数面板 45%
- 分割线样式与 Blender 风格一致（细线 #555555）

---

## 2. 文件顶栏 (FileBar)

### 2.1 布局

水平布局，两行路径输入，每行一个 `QLabel` + `QLineEdit` + `QPushButton`

### 2.2 交互

- **拖拽支持**: `QLineEdit` 启用 `setAcceptDrops(True)`，拖入时高亮边框绿色
- **点击浏览**: 使用 `QFileDialog.getOpenFileName`（输入）和 `QFileDialog.getExistingDirectory`（输出）
- **自动检测**: 输入路径变更后立即触发视频信息检测（使用 QTimer 防抖 300ms）
- **清空按钮**: 输入框右侧绘制"×"清除按钮
- **输出默认**: 输出目录为空时自动跟随输入文件所在目录

### 2.3 控件

| 控件 | 类型 | 说明 |
|------|------|------|
| 输入标签 | `QLabel` | "📁 输入:" |
| 输入路径 | `DropLineEdit` | 继承 QLineEdit，重写 dragEnter/dragDrop |
| 浏览按钮 | `QPushButton` | "选择文件" |
| 输出标签 | `QLabel` | "📁 输出:" |
| 输出路径 | `QLineEdit` | 只读模式，显示输出目录 |
| 浏览按钮 | `QPushButton` | "选择目录" |

---

## 3. 视频面板 (VideoPanel)

### 3.1 布局

`QVBoxLayout`，上方预览占大部分空间，下方视频信息卡片

### 3.2 视频预览

- 使用 `QLabel` + `QPixmap` 显示首帧缩略图
- 图片等比缩放适应宽度，最大高度 400px
- 无视频时显示拖拽占位提示（虚线边框 + "拖拽视频文件到此处"）
- 未来可扩展为实时帧预览（处理中显示当前帧）

### 3.3 视频信息卡片

使用 `QGroupBox` 或 `QFrame` 包裹：

```
格式: MP4     编码: avc1
分辨率: 1920 × 1080    帧率: 23.976 FPS
时长: 00:00:23    总帧数: 1243
文件大小: 245.3 MB
```

每个信息项用 `QLabel` 网格布局排列。

---

## 4. 参数面板 (ParamPanel)

### 4.1 通用规则

- 使用可折叠 `QGroupBox` 分组（点击标题栏展开/折叠），默认全部展开
- 每个分组内使用 `QFormLayout` 或 `QGridLayout`
- 所有控件 hover 时显示 tooltip 说明
- 参数变更即时生效，不阻塞 UI

### 4.2 📐 输出尺寸分组

| 标签 | 控件 | 选项/范围 | 说明 |
|------|------|-----------|------|
| 放大模式 | `QComboBox` | "2x 放大", "4x 放大", "固定分辨率", "保持原尺寸" | 选中"固定分辨率"时启用宽高输入 |
| 宽度 | `QSpinBox` | 320-7680, step 16 | 仅在"固定分辨率"时可用 |
| 高度 | `QSpinBox` | 240-4320, step 16 | 同上 |
| 封装格式 | `QComboBox` | "mp4", "mov", "mkv" | |
| 输出 FPS | `QSpinBox` | 0-120, 0=跟随原片 | 0 显示为"自动" |

**响应联动**: `QComboBox` 切换至"固定分辨率"时，自动启用宽高输入；切换至其他选项时自动禁用并将宽高置灰。

### 4.3 🧠 AI 处理分组

| 标签 | 控件 | 选项/范围 | 说明 |
|------|------|-----------|------|
| 质量/模式 | `QComboBox` | 12 个模式（BICUBIC~HIGHBITRATE_HIGH） | 显示中文描述 |
| GPU | `QLabel` 或 `QComboBox` | 自动检测 GPU 名称 | 单卡显示 `QLabel`，多卡显示 `QComboBox` |

**GPU 检测逻辑**:
- 使用 `torch.cuda.is_available()` 检测
- 遍历 `torch.cuda.device_count()` 获取设备列表
- 显示设备名称而非 ID（如 "NVIDIA GeForce RTX 4090"）
- 单卡 → 只读 label；多卡 → 下拉选择框

### 4.4 🎞 编码设置分组

| 标签 | 控件 | 选项/范围 | 说明 |
|------|------|-----------|------|
| 视频编码器 | `QComboBox` | "H.264 (libx264)", "H.265 (libx265)", "AV1 (libaom-av1)" | |
| CRF | `QSlider` + `QSpinBox` | 0-51 | 滑块拖动与输入框双向同步 |
| 编码速度 | `QComboBox` | ultrafast ~ veryslow | |

**CRF 联动细节**:
- `QSlider` 水平放置，`QSpinBox` 紧贴右侧
- 拖动滑块时输入框实时更新
- 输入框手动输入数值时滑块同步移动
- tooltip: "0=无损, 18=视觉无损, 23=默认, 28=有损, 51=最差"

---

## 5. 底部栏 (BottomBar)

### 5.1 三种状态

**闲置状态**:
- 仅一个大按钮 `QPushButton` "🚀 开始处理"
- 按钮水平居中，使用强调色背景，宽度 240px
- 按钮 disabled 条件: 输入路径为空/文件不存在

**处理中状态**:
```
[⏸ 暂停] [■ 停止]    ████████████████░░░░ 45%
帧: 560/1243  |  12.3 FPS  |  剩余 1m 20s
显存: 4.2/24 GB  |  平均 81ms/帧
```
- 暂停按钮切换为"▶ 继续"
- 停止按钮点击弹出确认对话框
- 进度条使用 `QProgressBar` 自定义样式（强调色填充）

**完成状态**:
```
✅ 处理完成！1243 帧 | 耗时 1m 45s | 平均 84ms/帧
[📂 打开输出目录]  [▶ 播放预览]  [🔄 继续处理下一个]
```
- "打开输出目录" → `QDesktopServices.openUrl`
- "播放预览" → 内嵌视频播放（文件 < 500MB）或提示
- "继续处理下一个" → 清空状态回到初始

### 5.2 进度更新

- 使用 `QThread` 在后台运行 GPU 处理
- 通过 `signal/slot` 将进度数据发送回主线程
- 更新频率控制: 每处理 N 帧或每 200ms 更新一次 UI
- 信号包含: 当前帧数、总帧数、FPS、单帧耗时、显存占用

---

## 6. 配色方案 (Blender 风格)

### 6.1 色板

| 用途 | 色值 | 说明 |
|------|------|------|
| 窗口背景 | `#3D3D3D` | 主窗口底色 |
| 面板背景 | `#4A4A4A` | QGroupBox、QFrame 底色 |
| 控件背景 | `#575757` | QPushButton、QLineEdit、QComboBox 默认底色 |
| 控件悬停 | `#636363` | 鼠标悬停时 |
| 控件按下 | `#4E4E4E` | 鼠标按下时 |
| 输入框背景 | `#464646` | QLineEdit/QSpinBox 编辑区域 |
| 边框/分割线 | `#555555` | QGroupBox 边框、QSplitter 分割线 |
| 文字主色 | `#D3D3D3` | 正文 |
| 文字弱化 | `#888888` | 辅助说明 |
| 强调色 | `#5C9BD5` | 进度条填充、选中态、按钮主色 |
| 成功 | `#6BAF6D` | 完成状态文字 |
| 警告 | `#B5A36A` | 警告信息 |
| 错误 | `#B56A6A` | 错误信息 |

### 6.2 QSS 样式要点

- 所有按钮: 扁平风格，无渐变，无外发光
- 圆角: 4px
- 字体: Microsoft YaHei / Noto Sans SC, 12px
- QSlider: 细轨道 4px 高，滑块圆形 14px 直径
- QProgressBar: 纯色填充，无条纹动画
- QGroupBox: 标题栏点击可折叠，展开/收缩箭头

---

## 7. 线程模型

### 7.1 处理流程

```
主线程 (UI)  ─── 启动 ──→  WorkerThread
    ↑                          │
    │    signal: progress      │
    ├── slot: update_progress  │
    │    signal: finished      │
    ├── slot: on_finished      │
    │    signal: error         │
    └── slot: on_error         │
```

### 7.2 WorkerThread 接口

```python
class WorkerThread(QThread):
    progress_updated = pyqtSignal(int, int, float, float, float)  # frame, total, fps, ms, mem
    status_message = pyqtSignal(str)
    finished = pyqtSignal(int, float)  # total_frames, elapsed
    error_occurred = pyqtSignal(str)

    def __init__(self, input_path, output_path, params):
        super().__init__()
        self._is_paused = False
        self._is_cancelled = False

    def run(self): ...
    def pause(self): ...
    def resume(self): ...
    def cancel(self): ...
```

### 7.3 控件状态与线程状态映射

| 线程状态 | 开始按钮 | 暂停按钮 | 停止按钮 | 参数控件 |
|---------|---------|---------|---------|---------|
| 空闲 | Enabled | Hidden | Hidden | Enabled |
| 运行中 | Hidden | Enabled("⏸") | Enabled | Disabled |
| 暂停中 | Hidden | Enabled("▶") | Enabled | Disabled |
| 完成 | Enabled("🔄") | Hidden | Hidden | Enabled |

---

## 8. 打包配置

### 8.1 PyInstaller

```bash
pyinstaller --onefile --windowed \
  --name "RTX_VSR_Tool" \
  --icon icon.ico \
  --add-data "styles/*.qss;styles" \
  app.py
```

### 8.2 依赖

- PyQt6 >= 6.5
- PyTorch (现有)
- opencv-python-headless (现有)
- numpy (现有)

---

## 9. 文件结构

```
RTX_VSR_tool/
├── app.py              → 程序入口（精简）
├── main_window.py      → 主窗口 + 布局构建
├── video_panel.py      → 视频预览 + 信息面板
├── param_panel.py      → 参数面板（三个分组）
├── bottom_bar.py       → 底部控制栏 + 进度
├── worker.py           → QThread 后台处理
├── file_bar.py         → 文件顶栏 + 拖拽
├── theme.py            → 配色方案 + QSS 加载
├── utils.py            → 工具函数
├── resources/
│   └── icon.ico        → 应用图标
├── styles/
│   └── blender.qss     → QSS 样式表
├── requirements.txt
└── start.bat
```
