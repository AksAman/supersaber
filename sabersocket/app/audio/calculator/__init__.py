import queue
import threading
import time

import numpy as np
import pyaudio
import sounddevice as sd

from sabersocket.app.audio.rtaudio.stream_analyzer import StreamAnalyzer
from sabersocket.app.logger import logger
from sabersocket.app.settings import AUDIO_DEVICE, FPS, RMS_THRESHOLD, sleep_between_frames

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Queue to hold audio data
audio_queue = queue.Queue()

for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    logger.debug(f"Device {i}: {info['name']} - Input Channels: {info['maxInputChannels']}")


def list_devices():
    print("Available audio devices:")
    device_dict = sd.query_devices()
    print(device_dict)


def init_ear(device=AUDIO_DEVICE):
    return StreamAnalyzer(
        device=device,
        rate=None,  # Audio samplerate, None uses the default source settings
        FFT_window_size_ms=60,  # Window size used for the FFT transform
        updates_per_second=500,  # How often to read the audio stream for new data
        smoothing_length_ms=50,  # Apply some temporal smoothing to reduce noisy features
        reader_key="sounddevice",
    )


def audio_capture_thread(ear: StreamAnalyzer):
    """Thread function to continuously capture audio data."""

    def on_data(data):
        average_magnitude, max_magnitude, min_magnitude, rms, percentage = data
        logger.debug(
            f"last_max: {RMS_THRESHOLD}, rms: {rms}, average: {average_magnitude}, max: {max_magnitude}, min: {min_magnitude}, percentage: {percentage}"
        )
        audio_queue.put((average_magnitude, max_magnitude, min_magnitude, rms, percentage))

    ear.calculateFFT(fps=FPS, max_value=RMS_THRESHOLD, on_data=on_data, sleep_between_frames=sleep_between_frames)


# Start the audio capture thread
def start_audio_capture(ear: StreamAnalyzer):
    capture_thread = threading.Thread(target=audio_capture_thread, daemon=True, args=(ear,))
    capture_thread.start()
    return capture_thread


def stop_audio_capture(capture_thread: threading.Thread):
    if capture_thread:
        capture_thread.join()


def calculate_volume(data):
    """Calculates the volume of the audio data."""
    try:
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data**2))
        return dict(v=rms)
    except RuntimeWarning as e:
        logger.warning(f"Error in calculate_volume: {e}")
        return dict(v=0)
    except Exception as e:
        logger.exception(f"Error in calculate_volume: {e}")
        return dict(v=0)


def calculate_fft(audio_data):
    """Calculates FFT and returns the normalized magnitude."""
    # audio_data = np.frombuffer(data, dtype=np.int16)
    average_magnitude, max_magnitude, min_magnitude, rms, volume = audio_data
    return {
        # "audio_values": magnitude.tolist(),
        # "rms": rms,
        # "average": average_magnitude * 100,
        # "max": max_magnitude,
        # "min": min_magnitude,
        "v": volume,
    }
