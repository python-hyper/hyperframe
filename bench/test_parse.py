from bench.utils.factories import FRAME_FACTORIES
from bench.utils import get_int


NUMBER_OF_FRAMES = 100


def _parse_function(frame_and_data):
    frame, data = frame_and_data
    data = memoryview(data[get_int(0, NUMBER_OF_FRAMES - 1)])
    frame.parse_frame_header(data[:9])
    frame.parse_body(data[9:])


def _create_frames(frame_type):
    data = [FRAME_FACTORIES[frame_type]().serialize() for _ in range(100)]
    frame = FRAME_FACTORIES[frame_type]()
    frame = type(frame)(frame.stream_id)
    return frame, data


class TestParseBenchmarks:
    def test_parse_data_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("data"))

    def test_parse_priority_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("priority"))

    def test_parse_rst_stream_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("rst_stream"))

    def test_parse_settings_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("settings"))

    def test_parse_settings_ack_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("settings_ack"))

    def test_parse_push_promise_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("push_promise"))

    def test_parse_ping_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("ping"))

    def test_parse_headers_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("headers"))

    def test_parse_go_away_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("go_away"))

    def test_parse_window_update_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("window_update"))

    def test_parse_continuation_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("continuation"))

    def test_parse_alt_svc_frame(self, benchmark):
        benchmark(_parse_function, _create_frames("alt_svc"))
