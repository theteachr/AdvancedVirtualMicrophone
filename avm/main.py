from quart import Blueprint, render_template

from factory import pulse
from .api import stream_manager
from icecream import ic

app = Blueprint('main', __name__)


@app.get("/")
async def root():
    return await render_template('index.html')


@app.get('/sink-inputs')
async def sink_inputs_get():
    objs = {}
    objs.update({obj.index: obj for obj in await pulse.sink_input_list()})
    objs.update(stream_manager.streams)
    return await render_template('button.html', objs=objs)


@app.get('/sources')
async def sources_get():
    objs = {}
    # objs.update({obj.index: obj for obj in filter(lambda _: not (_.description==Constraints.input_desc and _.name==Constraints.input_name), await pulse.source_list())})
    # objs.update({index: obj for index, obj in stream_manager.streams.items() if index in objs})
    return await render_template('button.html', objs=objs)
