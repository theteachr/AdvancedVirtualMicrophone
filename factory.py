from typing import Dict, Any

import pulsectl_asyncio
from pulsectl import PulseSinkInputInfo, PulseSourceInfo
from quart import Quart, render_template
from werkzeug.exceptions import UnprocessableEntity
from icecream import install

from avmlib import AVMUtils, AVMDevice

install()

app: Quart = None
pulse: pulsectl_asyncio.PulseAsync = None
avm_devices: dict[int, AVMDevice] = {}


async def _setup_error_handlers():
    @app.errorhandler(422)
    async def page_error(e: UnprocessableEntity):
        return await render_template('error.html', code=422, msg=e.description), 422


async def _setup_pa_session():
    global pulse
    pulse = pulsectl_asyncio.PulseAsync()
    await pulse.connect()


async def _setup_default_avm_device():
    global avm_devices
    _ = await AVMUtils.create_avm_device(pulse)
    avm_devices[_.info.owner_module] = _


async def _register_templates():
    from avm.api import app as bp_api
    from avm.main import app as bp_main
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_main)


def create_app():
    global app
    app = Quart(__name__)

    @app.context_processor
    async def context_processor():
        return dict(isinstance=isinstance, PulseSinkInputInfo=PulseSinkInputInfo, PulseSourceInfo=PulseSourceInfo)

    @app.before_serving
    async def startup():
        await _setup_pa_session()
        await _setup_default_avm_device()
        await _setup_error_handlers()
        await _register_templates()

    @app.after_serving
    async def shutdown():
        pulse.close()

    return app
