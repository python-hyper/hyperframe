# -*- coding: utf-8 -*-
from hyperframe.frame import (
    Frame, Flags, DataFrame, PriorityFrame, RstStreamFrame, SettingsFrame,
    PushPromiseFrame, PingFrame, GoAwayFrame, WindowUpdateFrame, HeadersFrame,
    ContinuationFrame, AltSvcFrame, Origin, BlockedFrame,
)
import pytest


def decode_frame(frame_data):
    f, length = Frame.parse_frame_header(frame_data[:9])
    f.parse_body(memoryview(frame_data[9:9 + length]))
    assert 9 + length == len(frame_data)
    return f


class TestGeneralFrameBehaviour(object):
    def test_base_frame_ignores_flags(self):
        f = Frame(stream_id=0)
        flags = f.parse_flags(0xFF)
        assert not flags
        assert isinstance(flags, Flags)

    def test_base_frame_cant_serialize(self):
        f = Frame(stream_id=0)
        with pytest.raises(NotImplementedError):
            f.serialize()

    def test_base_frame_cant_parse_body(self):
        data = b''
        f = Frame(stream_id=0)
        with pytest.raises(NotImplementedError):
            f.parse_body(data)

    def test_parse_frame_header_unknown_type(self):
        with pytest.raises(ValueError):
            Frame.parse_frame_header(b'\x00\x00\x00\xFF\x00\x00\x00\x00\x01')

    def test_repr(self, monkeypatch):
        f = Frame(stream_id=0)
        monkeypatch.setattr(Frame, "serialize_body", lambda _: "body")
        assert repr(f) == "Frame(Stream: 0; Flags: None): body"

        monkeypatch.setattr(Frame, "serialize_body", lambda _: "A"*105)
        assert repr(f) == "Frame(Stream: 0; Flags: None): {}...".format("A"*100)


class TestDataFrame(object):
    payload = b'\x00\x00\x08\x00\x01\x00\x00\x00\x01testdata'
    payload_with_padding = b'\x00\x00\x13\x00\x09\x00\x00\x00\x01\x0Atestdata' + b'\0' * 10

    def test_data_frame_has_correct_flags(self):
        f = DataFrame(1)
        flags = f.parse_flags(0xFF)
        assert flags == set([
            'END_STREAM', 'PADDED'
        ])

    def test_data_frame_serializes_properly(self):
        f = DataFrame(1)
        f.flags = set(['END_STREAM'])
        f.data = b'testdata'

        s = f.serialize()
        assert s == self.payload

    def test_data_frame_with_padding_serializes_properly(self):
        f = DataFrame(1)
        f.flags = set(['END_STREAM', 'PADDED'])
        f.data = b'testdata'
        f.pad_length = 10

        s = f.serialize()
        assert s == self.payload_with_padding

    def test_data_frame_parses_properly(self):
        f = decode_frame(self.payload)

        assert isinstance(f, DataFrame)
        assert f.flags == set(['END_STREAM'])
        assert f.pad_length == 0
        assert f.data == b'testdata'
        assert f.body_len == 8

    def test_data_frame_with_padding_parses_properly(self):
        f = decode_frame(self.payload_with_padding)

        assert isinstance(f, DataFrame)
        assert f.flags == set(['END_STREAM', 'PADDED'])
        assert f.pad_length == 10
        assert f.data == b'testdata'
        assert f.body_len == 19

    def test_data_frame_with_padding_calculates_flow_control_len(self):
        f = DataFrame(1)
        f.flags = set(['PADDED'])
        f.data = b'testdata'
        f.pad_length = 10

        assert f.flow_controlled_length == 19

    def test_data_frame_without_padding_calculates_flow_control_len(self):
        f = DataFrame(1)
        f.data = b'testdata'

        assert f.flow_controlled_length == 8

    def test_data_frame_comes_on_a_stream(self):
        with pytest.raises(ValueError):
            DataFrame(0)

    def test_long_data_frame(self):
        f = DataFrame(1)

        # Use more than 256 bytes of data to force setting higher bits.
        f.data = b'\x01' * 300
        data = f.serialize()

        # The top three bytes should be numerically equal to 300. That means
        # they should read 00 01 2C.
        # The weird double index trick is to ensure this test behaves equally
        # on Python 2 and Python 3.
        assert data[0] == b'\x00'[0]
        assert data[1] == b'\x01'[0]
        assert data[2] == b'\x2C'[0]

    def test_body_length_behaves_correctly(self):
        f = DataFrame(1)

        f.data = b'\x01' * 300

        # Initially the body length is zero. For now this is incidental, but
        # I'm going to test it to ensure that the behaviour is codified. We
        # should change this test if we change that.
        assert f.body_len == 0

        data = f.serialize()
        assert f.body_len == 300


class TestPriorityFrame(object):
    payload = b'\x00\x00\x05\x02\x00\x00\x00\x00\x01\x80\x00\x00\x04\x40'

    def test_priority_frame_has_no_flags(self):
        f = PriorityFrame(1)
        flags = f.parse_flags(0xFF)
        assert flags == set()
        assert isinstance(flags, Flags)

    def test_priority_frame_with_all_data_serializes_properly(self):
        f = PriorityFrame(1)
        f.depends_on = 0x04
        f.stream_weight = 64
        f.exclusive = True

        assert f.serialize() == self.payload

    def test_priority_frame_with_all_data_parses_properly(self):
        f = decode_frame(self.payload)

        assert isinstance(f, PriorityFrame)
        assert f.flags == set()
        assert f.depends_on == 4
        assert f.stream_weight == 64
        assert f.exclusive == True
        assert f.body_len == 5

    def test_priority_frame_comes_on_a_stream(self):
        with pytest.raises(ValueError):
            PriorityFrame(0)


class TestRstStreamFrame(object):
    def test_rst_stream_frame_has_no_flags(self):
        f = RstStreamFrame(1)
        flags = f.parse_flags(0xFF)
        assert not flags
        assert isinstance(flags, Flags)

    def test_rst_stream_frame_serializes_properly(self):
        f = RstStreamFrame(1)
        f.error_code = 420

        s = f.serialize()
        assert s == b'\x00\x00\x04\x03\x00\x00\x00\x00\x01\x00\x00\x01\xa4'

    def test_rst_stream_frame_parses_properly(self):
        s = b'\x00\x00\x04\x03\x00\x00\x00\x00\x01\x00\x00\x01\xa4'
        f = decode_frame(s)

        assert isinstance(f, RstStreamFrame)
        assert f.flags == set()
        assert f.error_code == 420
        assert f.body_len == 4

    def test_rst_stream_frame_comes_on_a_stream(self):
        with pytest.raises(ValueError):
            RstStreamFrame(0)

    def test_rst_stream_frame_must_have_body_length_four(self):
        f = RstStreamFrame(1)
        with pytest.raises(ValueError):
            f.parse_body(b'\x01')


class TestSettingsFrame(object):
    serialized = (
        b'\x00\x00\x24\x04\x01\x00\x00\x00\x00' +  # Frame header
        b'\x00\x01\x00\x00\x10\x00'             +  # HEADER_TABLE_SIZE
        b'\x00\x02\x00\x00\x00\x00'             +  # ENABLE_PUSH
        b'\x00\x03\x00\x00\x00\x64'             +  # MAX_CONCURRENT_STREAMS
        b'\x00\x04\x00\x00\xFF\xFF'             +  # INITIAL_WINDOW_SIZE
        b'\x00\x05\x00\x00\x40\x00'             +  # SETTINGS_MAX_FRAME_SIZE
        b'\x00\x06\x00\x00\xFF\xFF'                # SETTINGS_MAX_HEADER_LIST_SIZE
    )

    settings = {
        SettingsFrame.HEADER_TABLE_SIZE: 4096,
        SettingsFrame.ENABLE_PUSH: 0,
        SettingsFrame.MAX_CONCURRENT_STREAMS: 100,
        SettingsFrame.INITIAL_WINDOW_SIZE: 65535,
        SettingsFrame.SETTINGS_MAX_FRAME_SIZE: 16384,
        SettingsFrame.SETTINGS_MAX_HEADER_LIST_SIZE: 65535,
    }

    def test_settings_frame_has_only_one_flag(self):
        f = SettingsFrame()
        flags = f.parse_flags(0xFF)
        assert flags == set(['ACK'])

    def test_settings_frame_serializes_properly(self):
        f = SettingsFrame()
        f.parse_flags(0xFF)
        f.settings = self.settings

        s = f.serialize()
        assert s == self.serialized

    def test_settings_frame_with_settings(self):
        f = SettingsFrame(settings=self.settings)
        assert f.settings == self.settings

    def test_settings_frame_without_settings(self):
        f = SettingsFrame()
        assert f.settings == {}

    def test_settings_frame_with_ack(self):
        f = SettingsFrame(flags=('ACK',))
        assert 'ACK' in f.flags

    def test_settings_frame_ack_and_settings(self):
        with pytest.raises(ValueError):
            SettingsFrame(settings=self.settings, flags=('ACK',))

    def test_settings_frame_parses_properly(self):
        f = decode_frame(self.serialized)

        assert isinstance(f, SettingsFrame)
        assert f.flags == set(['ACK'])
        assert f.settings == self.settings
        assert f.body_len == 36

    def test_settings_frames_never_have_streams(self):
        with pytest.raises(ValueError):
            SettingsFrame(stream_id=1)


class TestPushPromiseFrame(object):
    def test_push_promise_frame_flags(self):
        f = PushPromiseFrame(1)
        flags = f.parse_flags(0xFF)

        assert flags == set(['END_HEADERS', 'PADDED'])

    def test_push_promise_frame_serializes_properly(self):
        f = PushPromiseFrame(1)
        f.flags = set(['END_HEADERS'])
        f.promised_stream_id = 4
        f.data = b'hello world'

        s = f.serialize()
        assert s == (
            b'\x00\x00\x0F\x05\x04\x00\x00\x00\x01' +
            b'\x00\x00\x00\x04' +
            b'hello world'
        )

    def test_push_promise_frame_parses_properly(self):
        s = (
            b'\x00\x00\x0F\x05\x04\x00\x00\x00\x01' +
            b'\x00\x00\x00\x04' +
            b'hello world'
        )
        f = decode_frame(s)

        assert isinstance(f, PushPromiseFrame)
        assert f.flags == set(['END_HEADERS'])
        assert f.promised_stream_id == 4
        assert f.data == b'hello world'
        assert f.body_len == 15


class TestPingFrame(object):
    def test_ping_frame_has_only_one_flag(self):
        f = PingFrame()
        flags = f.parse_flags(0xFF)

        assert flags == set(['ACK'])

    def test_ping_frame_serializes_properly(self):
        f = PingFrame()
        f.parse_flags(0xFF)
        f.opaque_data = b'\x01\x02'

        s = f.serialize()
        assert s == (
            b'\x00\x00\x08\x06\x01\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00'
        )

    def test_no_more_than_8_octets(self):
        f = PingFrame()
        f.opaque_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09'

        with pytest.raises(ValueError):
            f.serialize()

    def test_ping_frame_parses_properly(self):
        s = b'\x00\x00\x08\x06\x01\x00\x00\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00'
        f = decode_frame(s)

        assert isinstance(f, PingFrame)
        assert f.flags == set(['ACK'])
        assert f.opaque_data == b'\x01\x02\x00\x00\x00\x00\x00\x00'
        assert f.body_len == 8

    def test_ping_frame_never_has_a_stream(self):
        with pytest.raises(ValueError):
            PingFrame(stream_id=1)

    def test_ping_frame_has_no_more_than_body_length_8(self):
        f = PingFrame()
        with pytest.raises(ValueError):
            f.parse_body(b'\x01\x02\x03\x04\x05\x06\x07\x08\x09')


class TestGoAwayFrame(object):
    def test_go_away_has_no_flags(self):
        f = GoAwayFrame()
        flags = f.parse_flags(0xFF)

        assert not flags
        assert isinstance(flags, Flags)

    def test_goaway_serializes_properly(self):
        f = GoAwayFrame()
        f.last_stream_id = 64
        f.error_code = 32
        f.additional_data = b'hello'

        s = f.serialize()
        assert s == (
            b'\x00\x00\x0D\x07\x00\x00\x00\x00\x00' +  # Frame header
            b'\x00\x00\x00\x40'                     +  # Last Stream ID
            b'\x00\x00\x00\x20'                     +  # Error Code
            b'hello'                                   # Additional data
        )

    def test_goaway_frame_parses_properly(self):
        s = (
            b'\x00\x00\x0D\x07\x00\x00\x00\x00\x00' +  # Frame header
            b'\x00\x00\x00\x40'                     +  # Last Stream ID
            b'\x00\x00\x00\x20'                     +  # Error Code
            b'hello'                                   # Additional data
        )
        f = decode_frame(s)

        assert isinstance(f, GoAwayFrame)
        assert f.flags == set()
        assert f.additional_data == b'hello'
        assert f.body_len == 13

    def test_goaway_frame_never_has_a_stream(self):
        with pytest.raises(ValueError):
            GoAwayFrame(stream_id=1)


class TestWindowUpdateFrame(object):
    def test_window_update_has_no_flags(self):
        f = WindowUpdateFrame(0)
        flags = f.parse_flags(0xFF)

        assert not flags
        assert isinstance(flags, Flags)

    def test_window_update_serializes_properly(self):
        f = WindowUpdateFrame(0)
        f.window_increment = 512

        s = f.serialize()
        assert s == b'\x00\x00\x04\x08\x00\x00\x00\x00\x00\x00\x00\x02\x00'

    def test_windowupdate_frame_parses_properly(self):
        s = b'\x00\x00\x04\x08\x00\x00\x00\x00\x00\x00\x00\x02\x00'
        f = decode_frame(s)

        assert isinstance(f, WindowUpdateFrame)
        assert f.flags == set()
        assert f.window_increment == 512
        assert f.body_len == 4


class TestHeadersFrame(object):
    def test_headers_frame_flags(self):
        f = HeadersFrame(1)
        flags = f.parse_flags(0xFF)

        assert flags == set(['END_STREAM', 'END_HEADERS',
                             'PADDED', 'PRIORITY'])

    def test_headers_frame_serializes_properly(self):
        f = HeadersFrame(1)
        f.flags = set(['END_STREAM', 'END_HEADERS'])
        f.data = b'hello world'

        s = f.serialize()
        assert s == (
            b'\x00\x00\x0B\x01\x05\x00\x00\x00\x01' +
            b'hello world'
        )

    def test_headers_frame_parses_properly(self):
        s = (
            b'\x00\x00\x0B\x01\x05\x00\x00\x00\x01' +
            b'hello world'
        )
        f = decode_frame(s)

        assert isinstance(f, HeadersFrame)
        assert f.flags == set(['END_STREAM', 'END_HEADERS'])
        assert f.data == b'hello world'
        assert f.body_len == 11

    def test_headers_frame_with_priority_parses_properly(self):
        # This test also tests that we can receive a HEADERS frame with no
        # actual headers on it. This is technically possible.
        s = (
            b'\x00\x00\x05\x01\x20\x00\x00\x00\x01' +
            b'\x80\x00\x00\x04\x40'
        )
        f = decode_frame(s)

        assert isinstance(f, HeadersFrame)
        assert f.flags == set(['PRIORITY'])
        assert f.data == b''
        assert f.depends_on == 4
        assert f.stream_weight == 64
        assert f.exclusive == True
        assert f.body_len == 5

    def test_headers_frame_with_priority_serializes_properly(self):
        # This test also tests that we can receive a HEADERS frame with no
        # actual headers on it. This is technically possible.
        s = (
            b'\x00\x00\x05\x01\x20\x00\x00\x00\x01' +
            b'\x80\x00\x00\x04\x40'
        )
        f = HeadersFrame(1)
        f.flags = set(['PRIORITY'])
        f.data = b''
        f.depends_on = 4
        f.stream_weight = 64
        f.exclusive = True

        assert f.serialize() == s


class TestContinuationFrame(object):
    def test_continuation_frame_flags(self):
        f = ContinuationFrame(1)
        flags = f.parse_flags(0xFF)

        assert flags == set(['END_HEADERS'])

    def test_continuation_frame_serializes(self):
        f = ContinuationFrame(1)
        f.parse_flags(0x04)
        f.data = b'hello world'

        s = f.serialize()
        assert s == (
            b'\x00\x00\x0B\x09\x04\x00\x00\x00\x01' +
            b'hello world'
        )

    def test_continuation_frame_parses_properly(self):
        s = b'\x00\x00\x0B\x09\x04\x00\x00\x00\x01hello world'
        f = decode_frame(s)

        assert isinstance(f, ContinuationFrame)
        assert f.flags == set(['END_HEADERS'])
        assert f.data == b'hello world'
        assert f.body_len == 11


class TestAltSvcFrame(object):
    payload_with_origin = (
        b'\x00\x00\x2B\x0A\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x1D\x00\x50\x00\x02'
        b'h2\x0Agoogle.comhttps://yahoo.com:8080'
    )
    payload_without_origin = (
        b'\x00\x00\x15\x0A\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x1D\x00\x50\x00\x02'
        b'h2\x0Agoogle.com'
    )

    def test_altsvc_frame_flags(self):
        f = AltSvcFrame()
        flags = f.parse_flags(0xFF)

        assert flags == set()

    def test_altsvc_frame_with_origin_serializes_properly(self):
        f = AltSvcFrame()
        f.host = b'google.com'
        f.port = 80
        f.protocol_id = b'h2'
        f.max_age = 29
        f.origin = Origin(scheme=b'https', host=b'yahoo.com', port=8080)

        s = f.serialize()
        assert s == self.payload_with_origin

    def test_altsvc_frame_with_origin_parses_properly(self):
        f = decode_frame(self.payload_with_origin)

        assert isinstance(f, AltSvcFrame)
        assert f.host == b'google.com'
        assert f.port == 80
        assert f.protocol_id == b'h2'
        assert f.max_age == 29
        assert f.origin == Origin(scheme=b'https', host=b'yahoo.com', port=8080)
        assert f.body_len == 43

    def test_altsvc_frame_without_origin_serializes_properly(self):
        f = AltSvcFrame()
        f.host = b'google.com'
        f.port = 80
        f.protocol_id = b'h2'
        f.max_age = 29

        s = f.serialize()
        assert s == self.payload_without_origin

    def test_altsvc_frame_without_origin_parses_properly(self):
        f = decode_frame(self.payload_without_origin)

        assert isinstance(f, AltSvcFrame)
        assert f.host == b'google.com'
        assert f.port == 80
        assert f.protocol_id == b'h2'
        assert f.max_age == 29
        assert f.origin is None
        assert f.body_len == 21

    def test_altsvc_frame_serialize_origin_without_port(self):
        f = AltSvcFrame()
        f.origin = Origin(scheme=b'https', host=b'yahoo.com', port=None)

        assert f.serialize_origin() == b'https://yahoo.com'

    def test_altsvc_frame_never_has_a_stream(self):
        with pytest.raises(ValueError):
            AltSvcFrame(stream_id=1)


class TestBlockedFrame(object):
    def test_blocked_has_no_flags(self):
        f = BlockedFrame(0)
        flags = f.parse_flags(0xFF)

        assert not flags
        assert isinstance(flags, Flags)

    def test_blocked_serializes_properly(self):
        f = BlockedFrame(2)

        s = f.serialize()
        assert s == b'\x00\x00\x00\x0B\x00\x00\x00\x00\x02'

    def test_blocked_frame_parses_properly(self):
        s = b'\x00\x00\x00\x0B\x00\x00\x00\x00\x02'
        f = decode_frame(s)

        assert isinstance(f, BlockedFrame)
        assert f.flags == set()
        assert f.body_len == 0
