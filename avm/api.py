from quart import Blueprint, abort, redirect, url_for

from factory import pulse, stream_manager

app = Blueprint('api', __name__, url_prefix='/api')


@app.put("/sink-inputs/<sink_input_id>")
@app.post("/sink-inputs/<sink_input_id>/load")
async def sink_inputs_put(sink_input_id: str):
    if not isinstance(sink_input_id, str) or not sink_input_id.isdigit():
        return abort(422, f"invalid_id: {sink_input_id}")
    sink_input_id = int(sink_input_id)
    if sink_input_id in stream_manager.streams:
        return redirect(url_for(f'main.sink_inputs_get'))
    try:
        sink = filter(lambda _: _.index == sink_input_id, await pulse.sink_input_list()).__next__()
    except StopIteration:
        return abort(422, f"unknown_id: {sink_input_id}")
    stream_manager.new_pipe(sink)
    return redirect(url_for(f'main.sink_inputs_get'))


@app.delete("/sink-inputs/<sink_input_id>")
@app.post("/sink-inputs/<sink_input_id>/unload")
async def sink_inputs_delete(sink_input_id: str):
    if not isinstance(sink_input_id, str) or not sink_input_id.isdigit():
        return abort(422, f"invalid_id: {sink_input_id}")
    sink_input_id = int(sink_input_id)
    if sink_input_id not in stream_manager.streams:
        return redirect(url_for(f'main.sink_inputs_get'))
    try:
        streamed_input = stream_manager.streams[sink_input_id]
    except IndexError:
        return abort(422, f"unknown_id: {sink_input_id}")
    stream_manager.kill_pipe(streamed_input.device_info)
    return redirect(url_for(f'main.sink_inputs_get'))


@app.put("/sources/<source_id>")
@app.post("/sources/<source_id>/load")
async def sources_put(source_id: str):
    if not isinstance(source_id, str) or not source_id.isdigit():
        return abort(422, f"invalid_id: {source_id}")
    source_id = int(source_id)
    if source_id in stream_manager.streams:
        return redirect(url_for(f'main.sources_get'))
    try:
        sink = filter(lambda _: _.index == source_id, await pulse.source_list()).__next__()
    except StopIteration:
        return abort(422, f"unknown_id: {source_id}")
    stream_manager.new_pipe(sink)
    return redirect(url_for(f'main.sources_get'))


@app.delete("/sources/<source_id>")
@app.post("/sources/<source_id>/unload")
async def sources_delete(source_id: str):
    if not isinstance(source_id, str) or not source_id.isdigit():
        return abort(422, f"invalid_id: {source_id}")
    source_id = int(source_id)
    if source_id not in stream_manager.streams:
        return redirect(url_for(f'main.sources_get'))
    try:
        streamed_input = stream_manager.streams[source_id]
    except IndexError:
        return abort(422, f"unknown_id: {source_id}")
    stream_manager.kill_pipe(streamed_input.device_info)
    return redirect(url_for(f'main.sources_get'))
