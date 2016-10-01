from bench.utils.factories import FRAME_FACTORIES


class TestFlagBenchmarks:
    def test_set_flags(self, benchmark):
        frame = FRAME_FACTORIES["headers"]()
        benchmark(frame.flags.add, "PADDED")

    def test_get_flags(self, benchmark):
        frame = FRAME_FACTORIES["headers"]()
        frame.flags.add("PADDED")
        benchmark(lambda: "PADDED" in frame.flags)

    def test_remove_flags(self, benchmark):
        frame = FRAME_FACTORIES["headers"]()
        @benchmark
        def _benchmark():
            frame.flags.add("PADDED")
            frame.flags.remove("PADDED")
