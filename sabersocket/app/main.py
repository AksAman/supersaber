from fastapi import FastAPI, WebSocket
import pyaudio
import numpy as np
import asyncio
import threading
import queue
import logging

app = FastAPI()


# Logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Queue to hold audio data
audio_queue = queue.Queue()

for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']} - Input Channels: {info['maxInputChannels']}")


def audio_capture_thread():
    """Thread function to continuously capture audio data."""
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=0,
    )
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_queue.put(data)
        except Exception as e:
            print(f"Error in audio capture: {e}")


# Start the audio capture thread
capture_thread = threading.Thread(target=audio_capture_thread, daemon=True)
capture_thread.start()


def calculate_volume(data):
    """Calculates the volume of the audio data."""
    try:
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_data**2))
        return dict(rms=rms)
    except RuntimeWarning as e:
        logger.warning(f"Error in calculate_volume: {e}")
        return dict(rms=0)
    except Exception as e:
        logger.exception(f"Error in calculate_volume: {e}")
        return dict(rms=0)


def calculate_fft(data):
    """Calculates FFT and returns the normalized magnitude."""
    audio_data = np.frombuffer(data, dtype=np.int16)
    fft_data = np.fft.fft(audio_data)
    magnitude = np.abs(fft_data)[: CHUNK // 2]
    magnitude = magnitude / np.max(magnitude)
    average_magnitude = np.mean(magnitude)
    max_magnitude = np.max(magnitude)
    min_magnitude = np.min(magnitude)
    rms = np.sqrt(np.mean(audio_data**2))
    print(rms)
    return {
        # "audio_values": magnitude.tolist(),
        "rms": rms,
        "average": average_magnitude * 100,
        "max": max_magnitude,
        "min": min_magnitude,
    }


@app.get("/audio-values")
async def get_audio_values():
    if not audio_queue.empty():
        data = audio_queue.get()
        return calculate_fft(data)
    else:
        return dict(rms=0)


@app.websocket("/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if not audio_queue.empty():
                data = audio_queue.get()
                await websocket.send_json(calculate_fft(data))
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
