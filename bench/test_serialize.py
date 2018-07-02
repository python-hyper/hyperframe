from bench.utils.factories import FRAME_FACTORIES
from bench.utils import get_int


NUMBER_OF_FRAMES = 100


def _serialize_function(frames):
    frame = frames[get_int(0, NUMBER_OF_FRAMES - 1)]
    frame.serialize()


def _create_frames(frame_type):
    return [FRAME_FACTORIES[frame_type]() for _ in range(100)]


class TestSerializeBenchmarks:
    def test_serialize_data_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("data"))

    def test_serialize_priority_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("priority"))

    def test_serialize_rst_stream_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("rst_stream"))

    def test_serialize_settings_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("settings"))

    def test_serialize_settings_ack_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("settings_ack"))

    def test_serialize_push_promise_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("push_promise"))

    def test_serialize_ping_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("ping"))

    def test_serialize_headers_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("headers"))

    def test_serialize_go_away_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("go_away"))

    def test_serialize_window_update_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("window_update"))

    def test_serialize_continuation_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("continuation"))

    def test_serialize_alt_svc_frame(self, benchmark):
        benchmark(_serialize_function, _create_frames("alt_svc"))
