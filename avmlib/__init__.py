import os.path
import subprocess
import threading

from pulsectl import PulseError, PulseSinkInputInfo
from pulsectl_asyncio import PulseAsync


class AVMDevice:
    def __init__(self, pulse, info, fifo_path):
        self.pulse = pulse
        self.info = info
        self.fifo_file = open(fifo_path, 'wb')
        self.loaded_sources = {}
        self.loaded_sink_inputs = {}

    def load_sink_input(self, index):
        p = subprocess.Popen(['parec', '--monitor-stream', str(index)], stdout=self.fifo_file)
        self._register_pipe(p, index, self.loaded_sink_inputs)

    def load_source(self, index):
        p = subprocess.Popen(['parec', '-d', str(index)], stdout=self.fifo_file)
        self._register_pipe(p, index, self.loaded_sources)

    def unload_sink_input(self, index):
        p = self.loaded_sink_inputs.get(index)
        if p is None:
            return False
        p.terminate()
        return True

    def unload_source(self, index):
        p = self.loaded_sources.get(index)
        if p is None:
            return False
        p.terminate()
        return True

    @classmethod
    def _register_pipe(cls, process, index, storage):
        storage[index] = process
        _close_handler_thread = threading.Thread(target=cls._on_close_handler, args=(process, index, storage))
        _close_handler_thread.start()

    @staticmethod
    def _on_close_handler(process, index, storage):
        process.wait()
        del storage[index]

    def __dict__(self):
        return {'info': self.info, 'loaded_sources': self.loaded_sources,
                'loaded_sink_inputs': self.loaded_sink_inputs}

    def __repr__(self):
        return self.__dict__().__repr__()


class AVMDeviceInfo:
    def __init__(self, index, owner_module, input_name, fifo_path, pcm_sample_format, bitrate, channels, input_desc):
        self.index = index
        self.owner_module = owner_module
        self.name = input_name
        self.fifo_path = fifo_path
        self.pcm_sample_format = pcm_sample_format
        self.bitrate = bitrate
        self.channels = channels
        self.desc = input_desc

    def __dict__(self):
        return {'index': self.index, 'name': self.name, 'fifo_path': self.fifo_path,
                'pcm_sample_format': self.pcm_sample_format, 'bitrate': self.bitrate,
                'channels': self.channels, 'description': self.desc}

    def __repr__(self):
        return self.__dict__().__repr__()


class AVMUtils:
    @staticmethod
    async def create_avm_device(pulse: PulseAsync, input_name='VirtualMic', fifo_path=None, pcm_sample_format='s16le',
                                bitrate=44100, channels=2, input_desc=None) -> AVMDevice:
        if not input_name.isalnum():
            raise Exception('invalid `input_name` specified')
        if type(bitrate) != int:
            raise Exception('invalid bitrate specified')
        if type(channels) != int:
            raise Exception('invalid `channels` specified')
        if not pcm_sample_format.isalnum():
            raise Exception('invalid `pcm_sample_format` specified')
        if fifo_path is None:
            fifo_path = '/tmp/' + input_name
        if input_desc is None:
            input_desc = f'AVM_Device_{input_name}'
        if not os.path.exists(fifo_path):
            try:
                _created = await pulse.module_load('module-pipe-source',
                                                   f'source_name={input_name} file={fifo_path} '
                                                   f'format={pcm_sample_format} rate={bitrate} channels={channels} '
                                                   f'source_properties=node.description={input_desc}')
                _created = next(filter(lambda _: _.owner_module == _created, await pulse.source_list()))

            except (PulseError, StopIteration):

                _created = next(
                    filter(lambda _: _.name == input_name, await pulse.source_list()))  # TODO make these better
        else:
            _created = next(filter(lambda _: _.name == input_name, await pulse.source_list()))

        avm_info = AVMDeviceInfo(_created.index, _created.owner_module,
                                 input_name, fifo_path, pcm_sample_format, bitrate, channels, input_desc)

        return AVMDevice(pulse, avm_info, fifo_path)
