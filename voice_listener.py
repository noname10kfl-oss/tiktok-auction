"""Voice listener: đo volume + lọc nhiễu + nhép miệng VTuber."""
import queue
import threading
import time
from typing import Callable, Optional


class VoiceListener:
    """
    Nghe mic, lọc nhiễu, đo volume, gửi tín hiệu.
    Có 2 bộ lọc:
    - High-pass filter (cắt tần số thấp < 80Hz)
    - Noise gate (chặn âm thanh dưới ngưỡng)
    """

    def __init__(self,
                 on_volume: Callable[[float], None],
                 on_status: Callable[[str], None],
                 on_speak_audio: Optional[Callable[[bytes, int], None]] = None):
        self.on_volume = on_volume
        self.on_status = on_status
        self.on_speak_audio = on_speak_audio

        self.enabled = False
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = False

        # === Cấu hình volume ===
        self.threshold = 12          # Ngưỡng mở miệng
        self.sensitivity = 2.5       # Hệ số nhân
        self.noise_floor = 300       # Nền tối thiểu
        self.volume_scale = 3000

        # === Cấu hình lọc nhiễu ===
        self.noise_gate_enabled = True
        self.noise_gate_threshold = 200   # RMS tối thiểu để qua
        self.highpass_enabled = True
        self.highpass_cutoff = 80         # Hz — cắt dưới tần số này
        self.smoothing_enabled = True
        self.smoothing_factor = 0.3       # Làm mượt volume (0-1, cao hơn = mượt hơn)

        # State cho smoothing
        self._smoothed_volume = 0.0

        # State cho high-pass filter (stateful filter)
        self._hp_prev_in = 0.0
        self._hp_prev_out = 0.0

    def start(self):
        if self.enabled:
            return
        self.enabled = True
        self._stop_flag = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.enabled = False
        self._stop_flag = True

    @property
    def is_running(self):
        return self.enabled

    def _run(self):
        try:
            import sounddevice as sd
            import numpy as np
        except ImportError as e:
            self.on_status(
                f"❌ Chưa cài sounddevice/numpy: {e}\n"
                f"Chạy: uv add sounddevice numpy"
            )
            self.enabled = False
            return

        self.on_status("🎤 Đang khởi động mic...")

        # Tính hệ số high-pass filter (RC filter 1st order)
        # alpha = RC / (RC + dt)
        # RC = 1 / (2 * pi * cutoff)
        sr = 16000
        dt = 1.0 / sr
        rc = 1.0 / (2 * 3.14159265 * self.highpass_cutoff)
        hp_alpha = rc / (rc + dt)

        q = queue.Queue()

        def callback(indata, frames, time_info, status):
            try:
                q.put_nowait(indata.copy())
            except queue.Full:
                pass

        try:
            with sd.InputStream(
                samplerate=sr,
                blocksize=800,
                dtype='int16',
                channels=1,
                callback=callback
            ):
                self.on_status("🎤 Mic đã bật — lọc nhiễu đang chạy!")

                while not self._stop_flag and self.enabled:
                    try:
                        data = q.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    # Chuyển int16 → float32
                    audio = data.flatten().astype(np.float32)

                    # ============ HIGH-PASS FILTER ============
                    if self.highpass_enabled:
                        filtered = np.zeros_like(audio)
                        prev_in = self._hp_prev_in
                        prev_out = self._hp_prev_out
                        for i in range(len(audio)):
                            x = audio[i]
                            y = hp_alpha * (prev_out + x - prev_in)
                            filtered[i] = y
                            prev_in = x
                            prev_out = y
                        self._hp_prev_in = prev_in
                        self._hp_prev_out = prev_out
                        audio = filtered

                    # Tính RMS sau khi lọc
                    rms = float(np.sqrt(np.mean(audio ** 2)))

                    # ============ NOISE GATE ============
                    if self.noise_gate_enabled:
                        if rms < self.noise_gate_threshold:
                            rms = 0.0

                    # Chuẩn hóa volume
                    level = max(0, rms - self.noise_floor)
                    raw_volume = min(100,
                        (level / self.volume_scale) * 100 * self.sensitivity
                    )

                    # ============ SMOOTHING ============
                    if self.smoothing_enabled:
                        self._smoothed_volume = (
                            self._smoothed_volume * (1 - self.smoothing_factor)
                            + raw_volume * self.smoothing_factor
                        )
                        volume = self._smoothed_volume
                    else:
                        volume = raw_volume

                    # Gửi volume
                    try:
                        self.on_volume(volume)
                    except Exception:
                        pass

                    # Gửi audio cho voice changer nếu vượt ngưỡng
                    if volume >= self.threshold and self.on_speak_audio:
                        try:
                            # Chuyển về int16 để gửi đi
                            audio_int16 = np.clip(
                                audio, -32768, 32767
                            ).astype(np.int16)
                            self.on_speak_audio(
                                audio_int16.tobytes(), sr
                            )
                        except Exception:
                            pass

        except Exception as e:
            self.on_status(f"❌ Lỗi mic: {e}")
        finally:
            self.enabled = False
            self.on_status("⏹ Đã dừng mic")