class Constraints:
    input_name = 'VirtualMic'
    input_desc = input_name
    fifo_path = f'/tmp/{input_name}'
    pcm_sample_format = 's16le'
    bitrate = 44100
    channels = 2