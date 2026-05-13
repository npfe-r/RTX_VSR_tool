import os
import time
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

from utils import calc_output_size

# Map software preset names to NVENC-compatible p1-p7 presets
NVENC_PRESET_MAP = {
    "ultrafast": "p1",
    "superfast": "p2",
    "veryfast": "p3",
    "faster": "p3",
    "fast": "p4",
    "medium": "p4",
    "slow": "p5",
    "slower": "p6",
    "veryslow": "p7",
}


class WorkerThread(QThread):
    progress_updated = pyqtSignal(int, int, float, float, float)
    # frame, total, fps, avg_ms, gpu_mem_gb
    status_message = pyqtSignal(str)
    finished = pyqtSignal(int, float)  # total_frames, elapsed_seconds
    error_occurred = pyqtSignal(str)

    def __init__(self, input_path, output_path, params):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.params = params
        self._paused = False
        self._cancelled = False

    def run(self):
        import cv2
        import torch
        from nvvfx import VideoSuperRes
        from nvvfx.effects.video_super_res import QualityLevel

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

        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            self.error_occurred.emit("无法打开视频文件")
            return

        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        out_fps = self.params.get("fps_override", 0) or orig_fps

        out_w, out_h = calc_output_size(
            self.params["output_mode"],
            orig_w, orig_h,
            self.params.get("custom_w", 3840),
            self.params.get("custom_h", 2160),
        )
        out_w += out_w % 2
        out_h += out_h % 2

        tmp_path = self.output_path.rsplit(".", 1)[0] + "_tmp.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(tmp_path, fourcc, out_fps, (out_w, out_h))
        if not writer.isOpened():
            self.error_occurred.emit("无法创建临时视频文件")
            cap.release()
            return

        quality = quality_map.get(self.params["quality_label"], QualityLevel.HIGH)
        device_id = self.params.get("device_id", 0)
        wall_start = time.time()

        self.status_message.emit("预热 CUDA ...")

        try:
            with VideoSuperRes(quality=quality, device=device_id) as sr:
                sr.output_width = out_w
                sr.output_height = out_h
                sr.load()

                dummy = torch.zeros(3, orig_h, orig_w, device=f"cuda:{device_id}")
                torch.from_dlpack(sr.run(dummy).image).clone()
                torch.cuda.empty_cache()

                frame_count = 0
                total_time = 0.0

                while True:
                    if self._cancelled:
                        break

                    if self._paused:
                        self.status_message.emit("已暂停")
                        while self._paused:
                            if self._cancelled:
                                break
                            self.msleep(100)
                        continue

                    ret, frame_bgr = cap.read()
                    if not ret:
                        break

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
                        fps = frame_count / (now - wall_start + 1e-9)
                        avg_ms = (total_time / frame_count) * 1000
                        mem = 0
                        if torch.cuda.is_available():
                            mem = torch.cuda.memory_allocated(device_id) / 1024**3
                        self.progress_updated.emit(frame_count, total_frames, fps, avg_ms, mem)

        except Exception as e:
            self.error_occurred.emit(str(e))
            cap.release()
            writer.release()
            return

        cap.release()
        writer.release()

        if self._cancelled:
            Path(tmp_path).unlink(missing_ok=True)
            return

        if frame_count == 0:
            self.error_occurred.emit("未能读取到任何帧")
            return

        # ffmpeg final encode
        self.status_message.emit("正在编码输出 ...")
        try:
            import subprocess
            has_audio = False
            try:
                prob = subprocess.run(
                    ["ffprobe", "-i", self.input_path, "-show_streams",
                     "-select_streams", "a", "-loglevel", "error"],
                    capture_output=True, text=True, timeout=30,
                )
                has_audio = bool(prob.stdout.strip())
            except Exception:
                pass

            enc_codec = self.params.get("enc_codec", "libx264")
            is_nvenc = enc_codec.endswith("_nvenc")

            cmd = ["ffmpeg", "-y", "-i", tmp_path]
            if has_audio:
                cmd += ["-i", self.input_path]
            cmd += ["-map", "0:v:0"]
            if has_audio:
                cmd += ["-map", "1:a:0"]
            cmd += ["-c:v", enc_codec]
            preset = self.params.get("preset", "medium")
            if is_nvenc:
                preset = NVENC_PRESET_MAP.get(preset, "p4")
                cmd += ["-rc", "vbr", "-b:v", "0",
                        "-cq", str(self.params.get("crf", 18))]
            else:
                cmd += ["-crf", str(self.params.get("crf", 18))]
            cmd += ["-preset", preset]
            if has_audio:
                cmd += ["-c:a", "aac"]
            cmd += ["-loglevel", "error", self.output_path]

            result = subprocess.run(cmd, timeout=600)
            if result.returncode != 0:
                self.error_occurred.emit(f"FFmpeg 编码失败 (exit code {result.returncode})")
                Path(tmp_path).unlink(missing_ok=True)
                cap.release()
                writer.release()
                return

        except subprocess.TimeoutExpired:
            self.error_occurred.emit("FFmpeg 编码超时 (超过600s)")
            Path(tmp_path).unlink(missing_ok=True)
            cap.release()
            writer.release()
            return
        except FileNotFoundError:
            self.error_occurred.emit("未找到 FFmpeg，请检查系统 PATH")
            Path(tmp_path).unlink(missing_ok=True)
            cap.release()
            writer.release()
            return
        except Exception:
            # Fallback: keep the OpenCV tmp file as output
            os.replace(tmp_path, self.output_path)

        Path(tmp_path).unlink(missing_ok=True)
        elapsed = time.time() - wall_start
        self.finished.emit(frame_count, elapsed)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self.status_message.emit("继续处理 ...")

    @property
    def is_paused(self):
        return self._paused

    def cancel(self):
        self._cancelled = True
        self._paused = False
