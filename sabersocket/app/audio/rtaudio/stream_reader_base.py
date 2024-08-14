from abc import ABC, abstractmethod
from typing import Any

from sabersocket.app.audio.rtaudio.utils import numpy_data_buffer


class IStreamReader(ABC):
    stream_start_time: float
    data_buffer: numpy_data_buffer
    update_window_n_frames: int
    new_data: bool
    num_data_captures: int
    data_capture_delays: Any

    @abstractmethod
    def __init__(
        self,
        device=None,
        rate=None,
        updates_per_second=1000,
        FFT_window_size=None,
        verbose=False,
    ):
        pass

    @abstractmethod
    def stream_start(self, data_windows_to_buffer=None):
        pass

    @abstractmethod
    def terminate(self):
        pass

    @abstractmethod
    def non_blocking_stream_read(self, indata, frames, time_info, status):
        pass

    @abstractmethod
    def test_stream_read(self, indata, frames, time_info, status):
        pass

    @abstractmethod
    def get_rate(self) -> int:
        pass

    @abstractmethod
    def get_device(self):
        pass
