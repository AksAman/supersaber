import pyaudio
import numpy as np
import threading
import queue
from sabersocket.app.audio.rtaudio.stream_analyzer import Stream_Analyzer
from sabersocket.app.settings import sleep_between_frames, RMS_THRESHOLD
from sabersocket.app.logger import logger
import time


# Initialize PyAudio
audio = pyaudio.PyAudio()

# Queue to hold audio data
audio_queue = queue.Queue()

for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    logger.debug(
        f"Device {i}: {info['name']} - Input Channels: {info['maxInputChannels']}"
    )


ear = Stream_Analyzer(
    rate=None,  # Audio samplerate, None uses the default source settings
    FFT_window_size_ms=60,  # Window size used for the FFT transform
    updates_per_second=500,  # How often to read the audio stream for new data
    smoothing_length_ms=50,  # Apply some temporal smoothing to reduce noisy features
)


def audio_capture_thread():
    """Thread function to continuously capture audio data."""
    fps = 60  # How often to update the FFT features + display
    last_update = time.time()
    logger.debug("All ready, starting audio measurements now...")
    fft_samples = 0
    last_max = RMS_THRESHOLD
    while True:
        if (time.time() - last_update) > (1.0 / fps):
            last_update = time.time()
            _, raw_fft, _, binned_fft = ear.get_audio_features()

            average_magnitude = np.mean(binned_fft)
            max_magnitude = np.max(binned_fft)
            min_magnitude = np.min(binned_fft)
            rms = np.sqrt(np.mean(binned_fft**2))
            percentage = rms / last_max
            # if rms > last_max:
            #     last_max = rms
            # if rms < RMS_THRESHOLD:
            #     last_max = RMS_THRESHOLD
            fft_samples += 1
            if fft_samples % 20 == 0:
                # logger.debug(f"Got fft_features #{fft_samples} of shape {raw_fft}")

                logger.debug(
                    f"last_max: {last_max}, rms: {rms}, average: {average_magnitude}, max: {max_magnitude}, min: {min_magnitude}, percentage: {percentage}"
                )
                audio_queue.put(
                    (average_magnitude, max_magnitude, min_magnitude, rms, percentage)
                )

        elif sleep_between_frames:
            time.sleep(((1.0 / fps) - (time.time() - last_update)) * 0.99)


# Start the audio capture thread
def start_audio_capture():
    capture_thread = threading.Thread(target=audio_capture_thread, daemon=True)
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
