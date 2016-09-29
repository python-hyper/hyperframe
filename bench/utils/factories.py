from bench.utils import get_bytes, get_int, get_bool
from hyperframe.frame import *


MAX_STREAM_ID = 0x7FFFFFFF
MAX_ERROR_CODE = 0x7FFFFFFF
MAX_PAYLOAD_LENGTH = 0xFFFF
MAX_PADDING_LENGTH = 0xFF
MAX_STREAM_WEIGHT = 0xFF


def data_frame_factory():
    frame = DataFrame(get_int(1, MAX_STREAM_ID))
    frame.data = get_bytes(get_int(0, MAX_PAYLOAD_LENGTH))

    if get_bool():
        frame.flags.add("END_STREAM")

    frame.flags.add("PADDED")
    frame.pad_length = get_int(0, MAX_PADDING_LENGTH)

    return frame


def priority_frame_factory():
    frame = PriorityFrame(get_int(1, MAX_STREAM_ID))
    frame.exclusive = get_bool()
    frame.depends_on = get_int(0, MAX_STREAM_ID)
    frame.stream_weight = get_int(0, MAX_STREAM_WEIGHT)

    return frame


def rst_stream_frame_factory():
    frame = RstStreamFrame(get_int(1, MAX_STREAM_ID))
    frame.error_code = get_int(1, MAX_ERROR_CODE)

    return frame


def settings_frame_factory():
    frame = SettingsFrame()
    for _ in range(get_int(0, 16)):
        frame.settings[get_int(1, 0xFF)] = get_int(0, 0xFFFFFFFF)

    return frame


def settings_frame_ack_factory():
    frame = SettingsFrame()
    frame.flags.add("ACK")
    return frame


def push_promise_frame_factory():
    frame = PushPromiseFrame(get_int(1, MAX_STREAM_ID))
    frame.data = get_bytes(get_int(0, MAX_PAYLOAD_LENGTH))

    if get_bool():
        frame.flags.add("END_HEADERS")

    if get_int(0, 10) != 0:
        frame.flags.add("PADDED")
        frame.pad_length = get_int(0, MAX_PADDING_LENGTH)

    return frame


def ping_frame_factory():
    frame = PingFrame()
    frame.data = get_bytes(8)

    if get_bool():
        frame.flags.add("ACK")

    return frame


def go_away_frame_factory():
    frame = GoAwayFrame()
    frame.last_stream_id = get_int(1, MAX_STREAM_ID)
    frame.error_code = get_int(1, MAX_ERROR_CODE)

    return frame


def window_update_frame_factory():
    frame = WindowUpdateFrame(get_int(0, MAX_STREAM_ID))
    frame.window_increment = get_int(1, 0x7FFFFFFF)

    return frame


def headers_frame_factory():
    frame = HeadersFrame(get_int(1, MAX_STREAM_ID))
    frame.data = get_bytes(get_int(0, MAX_PAYLOAD_LENGTH))

    if get_bool():
        frame.flags.add("END_HEADERS")
        if get_bool():
            frame.flags.add("END_STREAM")

    if get_bool():
        frame.flags.add("PRIORITY")
        frame.depends_on = get_int(0, MAX_STREAM_ID)
        frame.exclusive = get_bool()
        frame.stream_weight = get_int(0, MAX_STREAM_WEIGHT)

    frame.flags.add("PADDED")
    frame.pad_length = get_int(0, MAX_PADDING_LENGTH)

    return frame


FRAME_FACTORIES = {
    "data": data_frame_factory,
    "priority": priority_frame_factory,
    "rst_stream": rst_stream_frame_factory,
    "settings": settings_frame_factory,
    "settings_ack": settings_frame_ack_factory,
    "push_promise": push_promise_frame_factory,
    "ping": ping_frame_factory,
    "go_away": go_away_frame_factory,
    "window_update": window_update_frame_factory,
    "headers": headers_frame_factory
}