from functools import wraps
from quart import abort

from factory import avm_devices, pulse


def requires_avm_device_id(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        _id: str = kwargs.get('avm_device_id')
        if not _id.isdigit() or ((_id := int(_id)) not in avm_devices):
            abort(422, 'invalid_avm_id')
        kwargs['avm_device_id'] = _id
        return await func(*args, **kwargs)

    return wrapper


def requires_sink_index(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        _id: str = kwargs.get('sink_input_index')
        if not _id.isdigit():
            abort(422, 'invalid_sink_input_index')
        _id = int(_id)
        try:
            next(filter(lambda _: _.index == _id, await pulse.sink_input_list()))
        except StopIteration:
            abort(422, 'invalid_sink_input_index')

        kwargs['sink_input_index'] = _id
        return await func(*args, **kwargs)

    return wrapper


def requires_source_index(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        _id: str = kwargs.get('source_index')
        if not _id.isdigit():
            abort(422, 'invalid_source_index')
        _id = int(_id)
        try:
            next(filter(lambda _: _.index == _id, await pulse.source_list()))
        except StopIteration:
            abort(422, 'invalid_source_index')

        kwargs['source_index'] = _id
        return await func(*args, **kwargs)

    return wrapper
