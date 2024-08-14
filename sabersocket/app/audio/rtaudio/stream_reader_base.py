from abc import ABC, abstractmethod


class IStreamReader(ABC):

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
