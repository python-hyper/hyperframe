from bench.utils import _BaseBenchmark
from bench.utils.factories import FRAME_FACTORIES


FRAMES_TO_SERIALIZE = 100000


class _SerializeFrameBenchmark(_BaseBenchmark):
    def __init__(self, frame_type):
        self.factory = FRAME_FACTORIES[frame_type]
        _BaseBenchmark.__init__(self, "serialize_{}_frame".format(frame_type), FRAMES_TO_SERIALIZE)

    def setup(self):
        pass

    def benchmark(self):
        frames = [self.factory() for _ in range(50)]
        for i in range(FRAMES_TO_SERIALIZE):
            frame = frames[i % 50]

            self.start_watch()
            frame.serialize()
            self.stop_watch()

    def cleanup(self):
        pass


class SerializeDataFrameBenchmark(_SerializeFrameBenchmark):
    def __init__(self):
        _SerializeFrameBenchmark.__init__(self, "data")


class SerializePriorityFrameBenchmark(_SerializeFrameBenchmark):
    def __init__(self):
        _SerializeFrameBenchmark.__init__(self, "priority")


class SerializeRstStreamFrameBenchmark(_SerializeFrameBenchmark):
    def __init__(self):
        _SerializeFrameBenchmark.__init__(self, "rst_stream")


class SerializeSettingsFrameBenchmark(_SerializeFrameBenchmark):
    def __init__(self):
        _SerializeFrameBenchmark.__init__(self, "settings")


class SerializeSettingsFrameAckBenchmark(_SerializeFrameBenchmark):
    def __init__(self):
        _SerializeFrameBenchmark.__init__(self, "settings_ack")


class SerializePushPromiseFrameBenchmark(_SerializeFrameBenchmark):
    def __init__(self):
        _SerializeFrameBenchmark.__init__(self, "push_promise")
