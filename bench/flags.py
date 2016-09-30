from bench.utils import _BaseBenchmark
from bench.utils.factories import FRAME_FACTORIES


FLAGS_TO_PROCESS = 1000000


class SettingFlagsBenchmark(_BaseBenchmark):
    def __init__(self):
        self.frame = FRAME_FACTORIES["headers"]()
        self.flags = ["END_STREAM", "END_HEADERS", "PRIORITY", "PADDED"]
        _BaseBenchmark.__init__(self, "flags_set", FLAGS_TO_PROCESS)

    def setup(self):
        pass

    def benchmark(self):
        for i in range(self.rounds):
            flag = self.flags[i % 4]
            self.frame = type(self.frame)(self.frame.stream_id)

            self.start_watch()
            self.frame.flags.add(flag)
            self.stop_watch()

    def cleanup(self):
        pass


class GettingFlagsBenchmark(_BaseBenchmark):
    def __init__(self):
        self.frame = FRAME_FACTORIES["headers"]()
        self.flags = ["END_STREAM", "END_HEADERS", "PRIORITY", "PADDED"]
        _BaseBenchmark.__init__(self, "flags_get", FLAGS_TO_PROCESS)

    def setup(self):
        pass

    def benchmark(self):
        for i in range(self.rounds):
            flag = self.flags[i % 4]

            self.start_watch()
            flagged = flag in self.frame.flags
            self.stop_watch()

    def cleanup(self):
        pass
