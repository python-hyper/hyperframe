import pytest

from hyperframe.exceptions import InvalidFrameError, UnknownFrameError
from hyperframe.frame import DataFrame, ExtensionFrame, Frame


@pytest.mark.parametrize('length', [0, 0xFF, 0x100, 0xFFFF, 0x10000, 0xFFFFFF])
def test_frame_header_length_boundaries(length):
    header = length.to_bytes(3, 'big') + b'\x00\x00\x00\x00\x00\x01'
    frame, parsed_length = Frame.parse_frame_header(memoryview(header))

    assert isinstance(frame, DataFrame)
    assert parsed_length == length
    assert frame.stream_id == 1


@pytest.mark.parametrize('stream_id', [1, 0xFF, 0x100, 0xFFFF, 0x10000, 0x7FFFFFFF])
@pytest.mark.parametrize('reserved', [0, 0x80000000])
def test_frame_header_preserves_stream_id_bits(stream_id, reserved):
    header = b'\x00' * 5 + (stream_id | reserved).to_bytes(4, 'big')
    frame, length = Frame.parse_frame_header(memoryview(header))

    assert frame.stream_id == stream_id
    assert length == 0


@pytest.mark.parametrize('strict', [False, True])
@pytest.mark.parametrize('frame_type,length,flags', [
    (0x0B, 0, 0x80),
    (0x80, 0x10000, 0xFF),
    (0xFF, 0xFFFFFF, 0x7F),
])
def test_unknown_frame_header_boundaries(frame_type, length, flags, strict):
    header = length.to_bytes(3, 'big') + bytes([frame_type, flags]) + b'\x00\x00\x00\x01'

    if strict:
        with pytest.raises(UnknownFrameError) as excinfo:
            Frame.parse_frame_header(memoryview(header), strict=True)
        assert excinfo.value.frame_type == frame_type
        assert excinfo.value.length == length
        return

    frame, parsed_length = Frame.parse_frame_header(memoryview(header))
    assert isinstance(frame, ExtensionFrame)
    assert frame.type == frame_type
    assert frame.flag_byte == flags
    assert parsed_length == length
    assert frame.stream_id == 1


@pytest.mark.parametrize('header_length', [*range(9), 10, 18])
def test_frame_header_requires_exactly_nine_bytes(header_length):
    header = b'\x00' * 8 + b'\x01' + b'\x00' * 9
    with pytest.raises(InvalidFrameError):
        Frame.parse_frame_header(memoryview(header)[:header_length])
