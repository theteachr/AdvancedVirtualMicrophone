from quart import Blueprint, render_template, redirect, url_for
from werkzeug.exceptions import abort

from factory import pulse, avm_devices
from icecream import ic

from . import requires_avm_device_id

app = Blueprint('main', __name__)


class TestDevice:
    def __init__(self, index, name):
        self.index = index
        self.name = name


@app.get("/")
async def root():
    return redirect(url_for('main.device', avm_device_id=next(iter(avm_devices.keys()))))


@app.get("/<avm_device_id>")
@requires_avm_device_id
async def device(avm_device_id: int):
    if avm_device_id not in avm_devices:
        return redirect(url_for('main.root'))
    return await render_template('index.html', current_device=avm_devices.get(avm_device_id),
                                 devices=filter(lambda _: _.info.owner_module != avm_device_id, avm_devices.values()))


@app.get('/<avm_device_id>/sink-inputs')
@requires_avm_device_id
async def sink_inputs_get(avm_device_id: int):
    objs = {}
    _avm_device = avm_devices.get(avm_device_id)

    for obj in await pulse.sink_input_list():
        if obj.index in _avm_device.loaded_sink_inputs:
            obj.avm_loaded = True
        else:
            obj.avm_loaded = False
        objs[obj.index] = obj

    return await render_template('sink_input_cards.html', objs=objs, current_device=_avm_device)


@app.get('/<avm_device_id>/sources')
@requires_avm_device_id
async def sources_get(avm_device_id: int):
    objs = {}
    _avm_device = avm_devices.get(avm_device_id)

    for obj in filter(lambda _: _.index != _avm_device.info.index, await pulse.source_list()):
        if obj.index in _avm_device.loaded_sources:
            obj.avm_loaded = True
        else:
            obj.avm_loaded = False
        objs[obj.index] = obj

    return await render_template('source_cards.html', objs=objs, current_device=_avm_device)
