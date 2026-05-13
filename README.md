# RTX 视频超分辨率工具 (RTX Video Super Res Tool)

利用 NVIDIA RTX VSR AI 模型，对视频进行 AI 驱动的超分辨率放大、降噪和去模糊处理。

## 功能特性

- **AI 超分辨率** — 基于 NVIDIA VFX SDK 的 VideoSuperRes 模型，支持 2x / 4x 放大
- **降噪 / 去模糊** — 内置多种降噪和去模糊模式，提升视频清晰度
- **固定分辨率输出** — 自定义输出宽高（最高 7680×4320）
- **硬件加速编码** — 支持 NVIDIA NVENC（H.264 / H.265 / AV1），编码速度远超软件方案
- **软件编码** — 同时提供 libx264 / libx265 / libaom-av1 软件编码器
- **原音频保留** — 自动保留原始视频的音频流（AAC 编码）
- **GPU 选择** — 多 GPU 环境下可指定使用哪张显卡
- **GPU 加速** — 基于 CUDA 的实时逐帧处理
- **实时进度监控** — 显示处理进度、帧率（FPS）、每帧耗时、剩余时间和 GPU 显存占用
- **视频预览** — 拖拽视频文件后自动显示缩略图和元信息
- **设置持久化** — 自动保存并恢复窗口位置和参数设置
- **暂停 / 停止** — 处理过程中可暂停或取消任务

## 系统要求

| 组件 | 要求 |
|------|------|
| **GPU** | NVIDIA 显卡，支持 CUDA 12.8+（RTX 20 系列及以上推荐） |
| **驱动** | NVIDIA 显卡驱动 ≥ 550.0 |
| **Python** | 3.10 |
| **操作系统** | Windows 10/11 |
| **其他** | FFmpeg（需添加到系统 PATH）|

### 已知兼容 GPU

- NVIDIA RTX 20 系列及更新架构的显卡
- 不支持非 NVIDIA 显卡（AMD、Intel 等）
- NVENC AV1 编码需要 RTX 40 系列及以上

## 安装

### 1. 安装 FFmpeg

本项目依赖 FFmpeg 进行最终编码和音频处理。

- 从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载 Windows 构建版本
- 解压后将 `bin` 目录添加到系统 PATH 环境变量
- 验证安装：在终端运行 `ffmpeg -version`

### 2. 配置 Python 虚拟环境

```bash
cd H:\Project\RTX_VSR_tool
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 启动应用

**方式一：双击 `start.bat`**

**方式二：手动运行**

```bash
cd H:\Project\RTX_VSR_tool
venv\Scripts\activate
python app.py
```

启动后将打开 PyQt6 桌面窗口，即可在图形界面中操作。

## 使用指南

### 基本流程

1. **选择输入文件** — 拖拽视频文件到输入框，或点击"选择文件"按钮（支持 mp4、mov、avi、mkv、webm、flv、wmv）
2. **选择输出目录** — 可自定义输出位置，留空则使用输入文件所在目录
3. **配置处理参数** — 在右侧面板中设置输出尺寸、AI 模式和编码参数
4. **点击"开始处理"** — 等待处理完成，进度条和状态栏会实时更新

### 参数说明

#### 输出尺寸

| 参数 | 说明 |
|------|------|
| **2x 放大** | 宽高各放大至 2 倍 |
| **4x 放大** | 宽高各放大至 4 倍 |
| **固定分辨率** | 自定义输出宽高（步进 16px） |
| **保持原尺寸** | 不放大，仅降噪/去模糊 |
| **封装格式** | mp4 / mov / mkv |
| **输出 FPS** | 0 = 跟随原始帧率 |

#### AI 处理

| 模式 | 说明 |
|------|------|
| **BICUBIC** | 无 AI，标准双三次插值放大 |
| **LOW** | AI 速度优先，质量较低 |
| **MEDIUM** | AI 均衡模式 |
| **HIGH** | AI 质量优先（默认，推荐大多数视频使用） |
| **ULTRA** | AI 极致细节，追求最佳画质 |
| **DENOISE_LOW / MEDIUM / HIGH** | AI 降噪，由低到高，用于噪点较多的视频 |
| **DEBLUR_LOW / MEDIUM / HIGH** | AI 去模糊，由低到高，用于模糊的视频 |
| **HIGHBITRATE_HIGH** | 适用于高码率源素材 |

#### 编码设置

| 参数 | 说明 |
|------|------|
| **视频编码器** | H.264 / H.265 / AV1，每个编码器可选软件或 NVENC 硬件加速版本 |
| **CRF** | 0（无损）– 51（最差），建议 17–20。18 = 视觉无损 |
| **编码速度** | ultrafast → veryslow，越慢压缩率越高文件越小。NVENC 模式下自动映射到 p1-p7 |

### NVENC 硬件编码

支持以下硬件加速编码器（需要相应 GPU 支持）：

| 编码器 | GPU 要求 |
|--------|----------|
| H.264 (NVENC) | 所有 Kepler+ 架构 |
| H.265 (NVENC) | 所有 Maxwell 2nd+ 架构 |
| AV1 (NVENC) | RTX 40 系列及以上 |

硬件编码速度远快于软件编码，适合大多数场景。软件编码在同码率下画质略好。

### 处理流程

```
输入视频 → OpenCV 解码 → CUDA 逐帧 AI 处理 → 临时文件 → FFmpeg 编码（含音频）→ 输出文件
```

## 构建（打包为独立可执行文件）

项目提供 PyInstaller 构建配置，可打包为无 Pythton 环境也可运行的 exe：

```bash
pip install pyinstaller
```

**一键构建所有版本：**
```bash
build_all.bat
```

**或单独构建：**

```bash
python -m PyInstaller --clean build_light.spec    # 轻量包 (~200 MB)
python -m PyInstaller --clean build_full.spec      # 全量包 (~2.7 GB)
```

- **轻量包** — 仅打包 PyQt6 + numpy，其余依赖（torch、nvvfx、opencv、ffmpeg）从系统已安装环境中加载
- **全量包** — 包含全部依赖，开箱即用，但体积较大

## 性能参考

处理速度取决于 GPU 型号、视频分辨率和 AI 模式选择：

- **RTX 4090** — 1080p → 4K HIGH 模式下约 30-50 FPS
- **RTX 3080** — 1080p → 4K HIGH 模式下约 15-25 FPS
- **RTX 2060** — 1080p → 4K HIGH 模式下约 5-10 FPS

ULTRA 模式约比 HIGH 模式慢 2-3 倍。降噪/去模糊模式速度接近 HIGH。

## 常见问题

### Q: 提示 "FFmpeg 编码失败"？
A: 检查 FFmpeg 是否正确安装并添加到 PATH。程序会保留 OpenCV 编码的临时文件作为保底输出。

### Q: CUDA 显存不足？
A: 尝试选择较低的分辨率输出模式，或关闭其他占用 GPU 显存的程序。

### Q: 输出文件很大？
A: 提高 CRF 值（如 23-28）或选择 H.265/AV1 编码器可减小文件体积。

### Q: 程序启动报错？
A: 确认显卡驱动已更新到最新版本，且支持 CUDA 12.8+。启动时程序会自动检查关键依赖并弹窗提示。

## 技术栈

- **NVIDIA VFX SDK 1.2.0** — VideoSuperRes AI 模型
- **PyTorch 2.11** — 深度学习框架（CUDA 12.8）
- **PyQt6** — 桌面图形界面
- **OpenCV 4.13** — 视频解码与帧处理
- **FFmpeg** — 最终编码与音频混合

## 项目结构

```
RTX_VSR_tool/
├── app.py                  # 程序入口
├── main_window.py          # 主窗口（布局、信号连接、设置持久化）
├── worker.py               # 后台处理线程（AI 推理 + FFmpeg 编码）
├── utils.py                # 工具函数（GPU 检测、视频信息、尺寸计算）
├── check_deps.py           # 启动依赖检查
├── requirements.txt        # Python 依赖
├── start.bat               # Windows 启动脚本
├── build_all.bat           # 一键打包脚本
├── build_light.spec        # PyInstaller 轻量包配置
├── build_full.spec         # PyInstaller 全量包配置
├── build.spec              # PyInstaller 标准包配置
├── rthook_find_packages.py # PyInstaller 运行时钩子
├── widgets/
│   ├── __init__.py
│   ├── file_bar.py         # 文件选择栏（输入/输出路径，拖拽支持）
│   ├── video_panel.py      # 视频信息面板（缩略图预览 + 元数据显示）
│   └── param_panel.py      # 参数控制面板（所有配置控件）
├── input/                  # 输入视频目录
├── output/                 # 输出视频目录
└── venv/                   # Python 虚拟环境
```

## License

仅供个人和学习用途。使用 NVIDIA VFX SDK 需遵守 NVIDIA 的许可协议。
