import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from sabersocket.app.audio.calculator import (
    audio_queue,
    calculate_fft,
    init_ear,
    list_devices,
    start_audio_capture_thread,
)
from sabersocket.app.logger import logger

data_lock = asyncio.Lock()
clients: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    list_devices()
    # device = int(input("Enter the audio device: "))
    ear = init_ear()
    start_audio_capture_thread(ear=ear)
    asyncio.create_task(broadcast_data())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/audio-values")
# async def get_audio_values():
#     async with data_lock:
#         if not audio_queue.empty():
#             data = audio_queue.get()
#             return calculate_fft(data)
#         else:
#             return dict(v=0)


async def broadcast_data():
    while True:
        async with data_lock:
            if not audio_queue.empty():
                data = audio_queue.get()
                fft_data = calculate_fft(data)
                for client in clients:
                    print(f"sending data to client:{client}: {fft_data}")
                    await client.send_json(fft_data)
        await asyncio.sleep(0.04)


# @app.websocket("/audio-values")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             if not audio_queue.empty():
#                 data = audio_queue.get()
#                 await websocket.send_json(calculate_fft(data))
#             await asyncio.sleep(0.01)
#     except Exception as e:
#         logger.exception(f"Error in websocket_endpoint: {e}")
#     finally:
#         await websocket.close()


@app.websocket("/audio-values")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        clients.remove(websocket)
    except Exception as e:
        logger.exception(f"Error in websocket_endpoint: {e}")
        clients.remove(websocket)
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
