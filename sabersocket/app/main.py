from fastapi import FastAPI, WebSocket
import asyncio
from sabersocket.app.logger import logger
from contextlib import asynccontextmanager
from sabersocket.app.audio.calculator import (
    audio_queue,
    calculate_fft,
    start_audio_capture,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_audio_capture()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/audio-values")
async def get_audio_values():
    if not audio_queue.empty():
        data = audio_queue.get()
        return calculate_fft(data)
    else:
        return dict(v=0)


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
        logger.exception(f"Error in websocket_endpoint: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
