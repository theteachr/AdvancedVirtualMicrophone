import pulsectl_asyncio
from pulsectl import PulseSinkInputInfo, PulseSourceInfo
from quart import Quart, render_template
from werkzeug.exceptions import UnprocessableEntity
from avmlib.constraints import Constraints
from avmlib.stream_manager import StreamManager, StreamedInput

app: Quart = None
pulse: pulsectl_asyncio.PulseAsync = None
stream_manager: StreamManager = None


async def _setup_error_handlers():
    @app.errorhandler(422)
    async def page_error(e: UnprocessableEntity):
        return await render_template('error.html', code=422, msg=e.description), 422


async def _setup_pa_session():
    global pulse
    pulse = pulsectl_asyncio.PulseAsync()
    await pulse.connect()
    if not len(list(filter(lambda _: _.name == Constraints.input_name and _.description == Constraints.input_desc,
                           await pulse.source_list()))):
        await pulse.module_load('module-pipe-source',
                                f'source_name={Constraints.input_name} file={Constraints.fifo_path} '
                                f'format={Constraints.pcm_sample_format} rate={Constraints.bitrate} channels={Constraints.channels} '
                                f'source_properties=device.description="{Constraints.input_desc}"')


async def _setup_stream_manager():
    global stream_manager
    stream_manager = StreamManager()


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
        return dict(isinstance=isinstance, StreamedInput=StreamedInput, PulseSinkInputInfo=PulseSinkInputInfo, PulseSourceInfo=PulseSourceInfo)

    @app.before_serving
    async def startup():
        await _setup_pa_session()
        await _setup_stream_manager()
        await _setup_error_handlers()
        await _register_templates()

    @app.after_serving
    async def shutdown():
        pulse.close()

    return app
