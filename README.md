# RTX 视频超分辨率工具 (RTX Video Super Res Tool)

利用 NVIDIA RTX VSR AI 模型，对视频进行 AI 驱动的超分辨率放大、降噪和去模糊处理。

## 功能特性

- **AI 超分辨率** — 基于 NVIDIA VFX SDK 的 VideoSuperRes 模型，支持 2x / 4x 放大
- **降噪 / 去模糊** — 内置多种降噪和去模糊模式，提升视频清晰度
- **固定分辨率输出** — 自定义输出宽高（最高 7680×4320）
- **灵活的编码选项** — 支持 H.264、H.265、AV1 编码器，可调节 CRF 和编码速度预设
- **原音频保留** — 自动保留原始视频的音频流（AAC 编码）
- **GPU 加速** — 基于 CUDA 的实时逐帧处理，支持多 GPU 选择
- **实时进度监控** — 显示处理进度、帧率（FPS）、每帧耗时、剩余时间和 GPU 显存占用
- **视频预览** — 处理完成后直接在浏览器中预览结果（< 500MB）

## 系统要求

| 组件 | 要求 |
|------|------|
| **GPU** | NVIDIA 显卡，支持 CUDA 12.8+（RTX 20 系列及以上推荐） |
| **驱动** | NVIDIA 显卡驱动 ≥ 550.0 |
| **Python** | 3.10 |
| **操作系统** | Windows 10/11 |
| **其他** | FFmpeg（需添加到系统 PATH） |

### 已知兼容 GPU

- NVIDIA RTX 20 系列及更新架构的显卡
- 不支持非 NVIDIA 显卡（AMD、Intel 等）

## 安装

### 1. 安装 FFmpeg

本项目依赖 FFmpeg 进行最终编码和音频处理。

- 从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载 Windows 构建版本
- 解压后将 `bin` 目录添加到系统 PATH 环境变量
- 验证安装：在终端运行 `ffmpeg -version`

### 2. 配置 Python 虚拟环境

项目已包含预配置的虚拟环境（`venv/`），如要重新创建：

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
streamlit run app.py --server.port 8501 --server.headless true
```

启动后浏览器打开 `http://localhost:8501` 即可使用。

## 使用指南

### 基本流程

1. **选择输入文件** — 点击"选择文件"按钮选取视频文件（支持 mp4、mov、avi、mkv、webm、flv、wmv）
2. **选择输出目录** — 可自定义输出位置，留空则使用输入文件所在目录
3. **配置处理参数** — 在侧边栏三个标签页中设置
4. **点击"开始处理"** — 等待处理完成，自动预览结果

### 参数说明

#### 📦 输出设置

| 参数 | 说明 |
|------|------|
| **输出尺寸** | 2x 放大 / 4x 放大 / 固定分辨率 / 保持原尺寸（仅降噪/去模糊） |
| **封装格式** | mp4 / mov / mkv |
| **输出 FPS** | 0 = 跟随原始帧率 |

#### 🧠 AI 处理

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

#### 🎞 编码设置

| 参数 | 说明 |
|------|------|
| **视频编码器** | H.264（兼容性最佳）、H.265（同质量体积更小）、AV1（压缩率最高但编码极慢） |
| **CRF** | 0（无损）– 51（最差），建议 17–20。18 = 视觉无损 |
| **编码速度** | ultrafast → veryslow，越慢压缩率越高文件越小 |

### 处理流程

```
输入视频 → OpenCV 解码 → CUDA 逐帧 AI 处理 → 临时文件 → FFmpeg 编码（含音频）→ 输出文件
```

## 性能参考

处理速度取决于 GPU 型号、视频分辨率和 AI 模式选择：

- **RTX 4090** — 1080p → 4K HIGH 模式下约 30-50 FPS
- **RTX 3080** — 1080p → 4K HIGH 模式下约 15-25 FPS
- **RTX 2060** — 1080p → 4K HIGH 模式下约 5-10 FPS

ULTRA 模式约比 HIGH 模式慢 2-3 倍。降噪/去模糊模式速度接近 HIGH。

## 常见问题

### Q: 提示 "FFmpeg 编码失败"？
A: 检查 FFmpeg 是否正确安装并添加到 PATH。处理会回退到 OpenCV 编码的输出文件。

### Q: CUDA 显存不足？
A: 尝试选择较低的分辨率输出模式，或关闭其他占用 GPU 显存的程序。

### Q: 输出文件很大？
A: 提高 CRF 值（如 23-28）或选择 H.265/AV1 编码器可减小文件体积。

### Q: 程序启动报错？
A: 确认显卡驱动已更新到最新版本，且支持 CUDA 12.8+。

## 技术栈

- **NVIDIA VFX SDK 1.2.0** — VideoSuperRes AI 模型
- **PyTorch 2.11** — 深度学习框架（CUDA 12.8）
- **Streamlit 1.57** — Web UI 框架
- **OpenCV 4.13** — 视频解码与帧处理
- **FFmpeg** — 最终编码与音频混合

## 项目结构

```
RTX_VSR_tool/
├── app.py              # 主程序（单文件）
├── requirements.txt    # Python 依赖
├── start.bat           # Windows 启动脚本
├── input/              # 输入视频目录
├── output/             # 输出视频目录
└── venv/               # Python 虚拟环境
```

## License

仅供个人和学习用途。使用 NVIDIA VFX SDK 需遵守 NVIDIA 的许可协议。
