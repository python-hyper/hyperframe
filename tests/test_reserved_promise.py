import struct

import pytest

from hyperframe.exceptions import InvalidDataError
from hyperframe.frame import PushPromiseFrame


@pytest.mark.parametrize("stream_id", [2, 0x7FFFFFFE])
@pytest.mark.parametrize("padded", [False, True])
def test_parse_promised_stream_reserved_bit(stream_id, padded):
    frame = PushPromiseFrame(1)
    body = struct.pack("!L", stream_id | 0x80000000) + b"headers"
    if padded:
        frame.flags.add("PADDED")
        body = b"\x01" + body + b"\x00"
    frame.parse_body(memoryview(body))
    assert frame.promised_stream_id == stream_id
    assert frame.data == b"headers"


def test_reserved_bit_does_not_make_zero_stream_valid():
    frame = PushPromiseFrame(1)
    with pytest.raises(InvalidDataError):
        frame.parse_body(memoryview(b"\x80\x00\x00\x00"))


@pytest.mark.parametrize("stream_id", [2, 0x7FFFFFFE])
def test_serialize_promised_stream_reserved_bit(stream_id):
    frame = PushPromiseFrame(1, promised_stream_id=stream_id | 0x80000000)
    assert frame.serialize_body() == struct.pack("!L", stream_id)
