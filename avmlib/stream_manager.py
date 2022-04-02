import subprocess
import threading
from abc import abstractmethod
from typing import Union

from pulsectl import PulseSinkInputInfo, PulseSourceInfo

from .constraints import Constraints


class StreamManager:
    def __init__(self):
        self.streams = {}
        self.fifo_file = open(Constraints.fifo_path, 'wb')

    def new_pipe(self, device_info: Union[PulseSinkInputInfo, PulseSourceInfo]):
        _si = StreamedInput(device_info, self.fifo_file, self)
        self.streams[device_info.index] = _si

    def kill_pipe(self, sink: StreamedInput):
        if sink.index not in self.streams: return
        try:
            _streamed_input = self.streams.pop(sink.index)
            _streamed_input.terminate()
        except KeyError:
            return


class StreamedInput:
    def __init__(self, device_info: Union[PulseSinkInputInfo, PulseSourceInfo], fifo_file,
                 parent_manager: StreamManager):
        self.process: subprocess.Popen = None
        self.device_info = device_info
        self.fifo_file = fifo_file
        self.parent_manager = parent_manager
        if isinstance(self.device_info, PulseSourceInfo):
            self._start_pipe()
        elif isinstance(self.device_info, PulseSinkInputInfo):
            self._start_pipe()
        else:
            raise Exception(f'Invalid device specified ({device_info})')
        self._close_handler_thread = threading.Thread(target=self._on_close_handler)
        self._close_handler_thread.start()

    @abstractmethod
    def _start_pipe(self):
        return

    def _on_close_handler(self):
        self.process.wait()
        self.parent_manager.kill_pipe(self.device_info)

    def terminate(self):
        self.process.terminate()


class _StreamedSinkInput(StreamedInput):
    def _start_pipe(self):
        self.process = subprocess.Popen(['parec', '--monitor-stream', str(self.device_info.index)],
                                        stdout=self.fifo_file)


class _StreamedSource(StreamedInput):
    def _start_pipe(self):
        self.process = subprocess.Popen(['parec', '-d', str(self.device_info.index)],
                                        stdout=self.fifo_file)
