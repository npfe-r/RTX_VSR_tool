import os
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import cv2
import numpy as np
import streamlit as st
import torch
from nvvfx import VideoSuperRes
from nvvfx.effects.video_super_res import QualityLevel

# ---------- Page config ----------
st.set_page_config(
    page_title="RTX Video Super Res Tool",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 RTX 视频超分辨率工具")
st.markdown(
    "利用 NVIDIA RTX VSR AI 模型提升 3D 渲染视频的分辨率和清晰度。"
)


# ---------- Native dialogs ----------
def _pick_file() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="选择视频文件",
        filetypes=[
            ("视频文件", "*.mp4 *.mov *.avi *.mkv *.webm *.flv *.wmv"),
            ("所有文件", "*.*"),
        ],
    )
    root.destroy()
    return path


def _pick_folder() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askdirectory(title="选择输出目录")
    root.destroy()
    return path


# ---------- Helpers ----------
def auto_gpu_name() -> str:
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(0)
    return "未检测到 GPU"


def calc_output_size(mode: str, w: int, h: int, cw: int, ch: int):
    if mode == "2x 放大 (最常用)":
        return w * 2, h * 2
    elif mode == "4x 放大":
        return w * 4, h * 4
    elif mode == "固定分辨率":
        return cw, ch
    return w, h


def fmt_time(s: float) -> str:
    return f"{s:.0f}s" if s < 60 else f"{int(s // 60)}m {int(s % 60)}s"


# ---------- Init session state ----------
if "input_path" not in st.session_state:
    st.session_state.input_path = ""
if "output_dir" not in st.session_state:
    st.session_state.output_dir = ""

# ---------- Globals ----------
quality_map = {
    "BICUBIC (无AI 插值)": QualityLevel.BICUBIC,
    "LOW (AI 速度优先)": QualityLevel.LOW,
    "MEDIUM (AI 均衡)": QualityLevel.MEDIUM,
    "HIGH (AI 质量优先)": QualityLevel.HIGH,
    "ULTRA (AI 极致细节)": QualityLevel.ULTRA,
    "DENOISE_LOW (轻度降噪)": QualityLevel.DENOISE_LOW,
    "DENOISE_MEDIUM (中度降噪)": QualityLevel.DENOISE_MEDIUM,
    "DENOISE_HIGH (强力降噪)": QualityLevel.DENOISE_HIGH,
    "DEBLUR_LOW (轻度去模糊)": QualityLevel.DEBLUR_LOW,
    "DEBLUR_MEDIUM (中度去模糊)": QualityLevel.DEBLUR_MEDIUM,
    "DEBLUR_HIGH (强力去模糊)": QualityLevel.DEBLUR_HIGH,
    "HIGHBITRATE_HIGH (高码率源)": QualityLevel.HIGHBITRATE_HIGH,
}
codec_map = {
    "H.264 (libx264)": "libx264",
    "H.265 (libx265)": "libx265",
    "AV1 (libaom-av1)": "libaom-av1",
}

# ---------- Sidebar ----------
st.sidebar.header("⚙️ 处理参数")
st.sidebar.caption(f"GPU: {auto_gpu_name()}")

tab = st.sidebar.radio(
    "分类",
    ["📦 输出设置", "🧠 AI 处理", "🎞 编码设置"],
    horizontal=True,
    label_visibility="collapsed",
)

# Defaults (in case a tab hasn't been visited yet)
output_mode = st.session_state.get("output_mode", "2x 放大 (最常用)")
custom_w = st.session_state.get("custom_w", 3840)
custom_h = st.session_state.get("custom_h", 2160)
container_fmt = st.session_state.get("container_fmt", "mp4")
fps_override = st.session_state.get("fps_override", 0)
quality_label = st.session_state.get("quality_label", "HIGH (AI 质量优先)")
quality = quality_map.get(quality_label, QualityLevel.HIGH)
device_id = st.session_state.get("device_id", 0)
enc_codec = st.session_state.get("enc_codec", "libx264")
crf = st.session_state.get("crf", 18)
preset = st.session_state.get("preset", "medium")

# ---- Tab: 输出设置 ----
if tab == "📦 输出设置":
    output_mode = st.sidebar.radio(
        "输出尺寸",
        options=["2x 放大 (最常用)", "4x 放大", "固定分辨率", "保持原尺寸 (降噪/去模糊)"],
        index=0,
        key="output_mode",
    )
    custom_w = st.sidebar.number_input(
        "宽度", 320, 7680, 3840, 16, key="custom_w",
        disabled=(output_mode != "固定分辨率"),
    )
    custom_h = st.sidebar.number_input(
        "高度", 240, 4320, 2160, 16, key="custom_h",
        disabled=(output_mode != "固定分辨率"),
    )
    container_fmt = st.sidebar.selectbox(
        "封装格式", ["mp4", "mov", "mkv"], index=0, key="container_fmt",
        help="输出文件容器格式，建议保持 mp4",
    )
    fps_override = st.sidebar.number_input("输出 FPS (0=跟随原片)", 0, 120, 0, key="fps_override")

# ---- Tab: AI 处理 ----
elif tab == "🧠 AI 处理":
    quality_label = st.sidebar.selectbox(
        "质量 / 模式", list(quality_map.keys()), index=3, key="quality_label",
        help="选择 AI 模型。普通视频选 HIGH 或 ULTRA，高码率源选 HIGHBITRATE",
    )
    quality = quality_map[quality_label]
    device_id = st.sidebar.number_input("CUDA 设备 ID", 0, 7, 0, key="device_id")

# ---- Tab: 编码设置 ----
else:
    codec_label = st.sidebar.selectbox(
        "视频编码器",
        ["H.264 (libx264)", "H.265 (libx265)", "AV1 (libaom-av1)"],
        index=0, key="codec_label",
        help="H.264 兼容性最好，H.265 同质量体积更小，AV1 压缩率最高但编码极慢",
    )
    enc_codec = codec_map[codec_label]
    st.session_state["enc_codec"] = enc_codec
    crf = st.sidebar.slider(
        "编码质量 (CRF)", 0, 51, 18, key="crf",
        help="0=无损, 18=视觉无损, 23=默认, 28=有损, 51=最差。建议 17-20",
    )
    preset = st.sidebar.selectbox(
        "编码速度",
        ["ultrafast", "superfast", "veryfast", "faster", "fast",
         "medium", "slow", "slower", "veryslow"],
        index=5, key="preset",
        help="越慢压缩率越高文件越小",
    )

# ---------- File paths ----------
st.subheader("📂 文件路径")

def _on_pick_file():
    p = _pick_file()
    if p:
        st.session_state.input_path = p

def _on_pick_folder():
    p = _pick_folder()
    if p:
        st.session_state.output_dir = p

# Input file row
ic1, ic2 = st.columns([5, 1])
with ic1:
    st.text_input("输入视频文件", key="input_path", placeholder="点击右侧按钮选择文件")
with ic2:
    st.write("")
    st.write("")
    st.button("📁 选择文件", on_click=_on_pick_file, use_container_width=True)

# Output dir row
oc1, oc2 = st.columns([5, 1])
with oc1:
    st.text_input("输出目录", key="output_dir", placeholder="留空则使用视频所在目录")
with oc2:
    st.write("")
    st.write("")
    st.button("📂 选择目录", on_click=_on_pick_folder, use_container_width=True)

input_path = st.session_state.input_path
output_dir = st.session_state.output_dir

# ---------- Validate ----------
path_ok = True
if input_path:
    p = Path(input_path)
    if not p.exists():
        st.warning(f"⚠️ 文件不存在: {input_path}")
        path_ok = False
    elif p.suffix.lower() not in (".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"):
        st.warning(f"⚠️ 不支持的文件格式: {p.suffix}")
        path_ok = False

if not output_dir and input_path:
    output_dir = str(Path(input_path).parent)

if output_dir and not Path(output_dir).exists():
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        st.warning(f"⚠️ 无法创建输出目录: {e}")
        path_ok = False

if not input_path or not path_ok:
    st.info("请选择要处理的视频文件。")
    st.stop()

# ---------- Thumbnail + info ----------
cap_info = cv2.VideoCapture(input_path)
if cap_info.isOpened():
    v_w = int(cap_info.get(cv2.CAP_PROP_FRAME_WIDTH))
    v_h = int(cap_info.get(cv2.CAP_PROP_FRAME_HEIGHT))
    v_fps = cap_info.get(cv2.CAP_PROP_FPS)
    v_frames = int(cap_info.get(cv2.CAP_PROP_FRAME_COUNT))
    v_dur = v_frames / v_fps if v_fps > 0 else 0
    v_codec = int(cap_info.get(cv2.CAP_PROP_FOURCC))
    v_codec_str = "".join(chr((v_codec >> 8 * i) & 0xFF) for i in range(4))

    # read first frame for thumbnail
    ret_th, frame_th = cap_info.read()
    cap_info.release()

    if ret_th:
        # RGB for display
        rgb_th = cv2.cvtColor(frame_th, cv2.COLOR_BGR2RGB)

        # compute display height (max 360px)
        disp_h = 360
        scale = disp_h / v_h
        disp_w = int(v_w * scale)
        thumb = cv2.resize(rgb_th, (disp_w, disp_h))

        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.image(thumb, caption="首帧预览", use_container_width=True)
        with col_b:
            st.markdown(
                f"**{Path(input_path).name}**  \n"
                f"分辨率: `{v_w} × {v_h}`  \n"
                f"时长: `{v_dur:.1f}s`  ({v_frames} 帧 @ {v_fps:.1f} FPS)  \n"
                f"编码: `{v_codec_str}`  \n"
                f"文件大小: `{Path(input_path).stat().st_size / 1024 / 1024:.1f} MB`"
            )
    else:
        st.video(input_path)
else:
    st.warning("无法读取视频信息")
    st.video(input_path)

# Output path
in_name = Path(input_path).stem
out_filename = f"{in_name}_enhanced.{container_fmt}"
out_path = str(Path(output_dir) / out_filename)

st.caption(f"输出文件: `{out_path}`")
if Path(out_path).exists():
    st.warning("⚠️ 输出文件已存在，处理后将覆盖。")

# ---------- Process ----------
if st.button("🚀 开始处理", type="primary", use_container_width=True):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        st.error("无法打开视频，文件可能已损坏。")
        st.stop()

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    out_fps = fps_override or orig_fps

    out_w, out_h = calc_output_size(output_mode, orig_w, orig_h, custom_w, custom_h)
    out_w += out_w % 2
    out_h += out_h % 2

    st.markdown(
        f"**{orig_w}×{orig_h}** → **{out_w}×{out_h}**"
        f" | {total_frames} 帧 | {orig_fps:.1f} FPS | **{quality_label}**"
        f" | {enc_codec} CRF {crf}"
    )

    # Write to a temp file first, then ffmpeg encodes final output
    tmp_path = out_path.rsplit(".", 1)[0] + "_tmp.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(tmp_path, fourcc, out_fps, (out_w, out_h))

    if not writer.isOpened():
        st.error("无法创建临时视频文件。")
        cap.release()
        st.stop()

    # ---------- Processing ----------
    prog = st.progress(0, text="预热 CUDA ...")
    stat = st.empty()

    with VideoSuperRes(quality=quality, device=device_id) as sr:
        sr.output_width = out_w
        sr.output_height = out_h
        sr.load()

        # warmup
        dummy = torch.zeros(3, orig_h, orig_w, device=f"cuda:{device_id}")
        torch.from_dlpack(sr.run(dummy).image).clone()
        torch.cuda.empty_cache()

        frame_count = 0
        total_time = 0.0
        prev_time = time.time()
        wall_start = prev_time

        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                break

            # BGR HWC uint8 -> RGB CHW float32 on CUDA
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            tensor = (
                torch.from_numpy(rgb)
                .permute(2, 0, 1)
                .float()
                .div_(255.0)
                .contiguous()
                .to(f"cuda:{device_id}", non_blocking=True)
            )

            t0 = time.perf_counter()
            result = sr.run(tensor)
            torch.cuda.synchronize(f"cuda:{device_id}")
            t1 = time.perf_counter()

            out_t = torch.from_dlpack(result.image).clone()
            out_np = out_t.mul_(255.0).byte().permute(1, 2, 0).cpu().numpy()
            out_bgr = cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)
            writer.write(out_bgr)

            frame_count += 1
            total_time += t1 - t0

            if frame_count % max(1, total_frames // 100) == 0 or frame_count == total_frames:
                now = time.time()
                fps_disp = frame_count / (now - prev_time + 1e-9)
                avg_ms = (total_time / frame_count) * 1000
                eta = (total_frames - frame_count) / max(fps_disp, 0.01)
                pct = min(frame_count / total_frames, 1.0)

                prog.progress(
                    pct,
                    text=f"{frame_count}/{total_frames}  "
                    f"| {avg_ms:.0f} ms/帧 | {fps_disp:.1f} FPS | 剩余 {eta:.0f}s",
                )

                if torch.cuda.is_available():
                    mem = torch.cuda.memory_allocated(device_id) / 1024**3
                    stat.text(f"GPU 显存: {mem:.1f} GB")

    cap.release()
    writer.release()

    if frame_count == 0:
        st.error("未能读取到任何帧。")
        st.stop()

    # ---------- ffmpeg final encode ----------
    has_audio = False
    try:
        prob = subprocess.run(
            ["ffprobe", "-i", input_path, "-show_streams", "-select_streams", "a",
             "-loglevel", "error"],
            capture_output=True, text=True, timeout=30,
        )
        has_audio = bool(prob.stdout.strip())
    except Exception:
        pass

    prog.progress(0.95, text="正在编码输出 ...")

    cmd = [
        "ffmpeg", "-y",
        "-i", tmp_path,              # 0: processed video
    ]
    if has_audio:
        cmd += ["-i", input_path]    # 1: original (audio only later)

    cmd += ["-map", "0:v:0"]         # video from processed
    if has_audio:
        cmd += ["-map", "1:a:0"]     # audio from original
    cmd += [
        "-c:v", enc_codec,
        "-crf", str(crf),
        "-preset", preset,
    ]
    if has_audio:
        cmd += ["-c:a", "aac"]
    cmd += ["-loglevel", "error", out_path]

    try:
        subprocess.run(cmd, timeout=600)
    except Exception as e:
        st.error(f"ffmpeg 编码失败: {e}")
        # fallback: keep the OpenCV tmp file as output
        os.replace(tmp_path, out_path)

    Path(tmp_path).unlink(missing_ok=True)
    elapsed = time.time() - wall_start
    prog.progress(1.0, text="✅ 全部完成!")
    stat.empty()

    avg_fps = frame_count / total_time
    elapsed_str = (
        f"{elapsed:.0f}s" if elapsed < 60
        else f"{int(elapsed // 60)}m {int(elapsed % 60)}s"
    )
    st.success(
        f"**处理完成！** {frame_count} 帧 | 耗时 {elapsed_str}"
        f" | 平均 {total_time / frame_count * 1000:.0f} ms/帧 ({avg_fps:.1f} FPS)"
    )
    st.markdown(f"**输出:** `{out_path}`")

    # preview (skip very large files)
    fsize = Path(out_path).stat().st_size
    if fsize < 500 * 1024 * 1024:
        st.video(out_path)
    else:
        st.info(f"输出文件较大 ({fsize / 1024 / 1024:.0f} MB)，请在资源管理器中播放。")

st.sidebar.markdown("---")
st.sidebar.caption("NVIDIA VFX SDK 1.2.0 · PyTorch · Streamlit")
