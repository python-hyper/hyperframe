from bench.utils import _BaseBenchmark


class WarmupBenchmark(_BaseBenchmark):
    def __init__(self):
        _BaseBenchmark.__init__(self, "_warmup", 1000000)

    def setup(self):
        pass

    def benchmark(self):
        for _ in range(1000000):
            self.start_watch()
            self.stop_watch()

    def cleanup(self):
        pass
