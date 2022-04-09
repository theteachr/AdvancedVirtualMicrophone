from quart import Blueprint, abort, redirect, url_for

from . import requires_avm_device_id, requires_sink_index, requires_source_index
from factory import pulse, avm_devices
from avmlib import AVMDevice

app = Blueprint('api', __name__, url_prefix='/api')


@app.get('')
@app.get('/')
async def root():
    return avm_devices.__repr__()


@app.put("/<avm_device_id>/sink-inputs/<sink_input_index>")
@app.post("/<avm_device_id>/sink-inputs/<sink_input_index>/load")
@requires_avm_device_id
@requires_sink_index
async def sink_inputs_put(avm_device_id: int, sink_input_index: str):
    avm_device: AVMDevice = avm_devices.get(avm_device_id)
    if sink_input_index in avm_device.loaded_sink_inputs:
        return redirect(url_for(f'main.sink_inputs_get', avm_device_id=avm_device_id))

    avm_device.load_sink_input(sink_input_index)
    return redirect(url_for(f'main.sink_inputs_get', avm_device_id=avm_device_id))


@app.put("/<avm_device_id>/sink-inputs/<sink_input_index>")
@app.post("/<avm_device_id>/sink-inputs/<sink_input_index>/unload")
@requires_avm_device_id
@requires_sink_index
async def sink_inputs_delete(avm_device_id: int, sink_input_index: str):
    avm_device = avm_devices.get(avm_device_id)
    avm_device.unload_sink_input(sink_input_index)
    return redirect(url_for(f'main.sink_inputs_get', avm_device_id=avm_device_id))


@app.put("/<avm_device_id>/sources/<source_index>")
@app.post("/<avm_device_id>/sources/<source_index>/load")
@requires_avm_device_id
@requires_source_index
async def sources_put(avm_device_id: int, source_index: str):
    avm_device = avm_devices.get(avm_device_id)
    if source_index in avm_device.loaded_sources:
        return redirect(url_for(f'main.sources_get', avm_device_id=avm_device_id))

    avm_device.load_source(source_index)
    return redirect(url_for(f'main.sources_get', avm_device_id=avm_device_id))


@app.put("/<avm_device_id>/sources/<source_index>")
@app.post("/<avm_device_id>/sources/<source_index>/unload")
@requires_avm_device_id
@requires_source_index
async def sources_delete(avm_device_id: int, source_index: str):
    avm_device = avm_devices.get(avm_device_id)
    avm_device.unload_source(source_index)
    return redirect(url_for(f'main.sources_get', avm_device_id=avm_device_id))
