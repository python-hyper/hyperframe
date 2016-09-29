from bench.utils import _BaseBenchmark
from bench.utils.factories import FRAME_FACTORIES


FRAMES_TO_PARSE = 500000


class _ParseFrameBenchmark(_BaseBenchmark):
    def __init__(self, frame_type):
        self.factory = FRAME_FACTORIES[frame_type]
        _BaseBenchmark.__init__(self, "parse_{}_frame".format(frame_type), FRAMES_TO_PARSE)

    def setup(self):
        pass

    def benchmark(self):
        frames = [self.factory() for _ in range(50)]
        frame = type(frames[0])(frames[0].stream_id)
        frames = [memoryview(x.serialize()) for x in frames]

        for i in range(FRAMES_TO_PARSE):
            data = frames[i % 50]

            self.start_watch()
            frame.parse_frame_header(data[:9])
            frame.parse_body(data[9:])
            self.stop_watch()

    def cleanup(self):
        pass


class ParseDataFrameBenchmark(_ParseFrameBenchmark):
    def __init__(self):
        _ParseFrameBenchmark.__init__(self, "data")


class ParsePriorityFrameBenchmark(_ParseFrameBenchmark):
    def __init__(self):
        _ParseFrameBenchmark.__init__(self, "priority")


class ParseRstStreamFrameBenchmark(_ParseFrameBenchmark):
    def __init__(self):
        _ParseFrameBenchmark.__init__(self, "rst_stream")


class ParseSettingsFrameBenchmark(_ParseFrameBenchmark):
    def __init__(self):
        _ParseFrameBenchmark.__init__(self, "settings")


class ParseSettingsFrameAckBenchmark(_ParseFrameBenchmark):
    def __init__(self):
        _ParseFrameBenchmark.__init__(self, "settings_ack")


class ParsePushPromiseFrameBenchmark(_ParseFrameBenchmark):
    def __init__(self):
        _ParseFrameBenchmark.__init__(self, "push_promise")
