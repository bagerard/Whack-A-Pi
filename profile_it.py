import cProfile
import io
import pstats

DEFAULT_STATS_SORT_BY = "cumulative"
DEFAULT_STATS_N_ENTRIES = 20


def get_stats_as_str(pr, sorty_by, n_entries) -> str:
    stream = io.StringIO()
    ps = pstats.Stats(pr, stream=stream)
    ps.sort_stats(sorty_by).print_stats(n_entries)
    return stream.getvalue()


class profile_it(cProfile.Profile):
    """Context manager that gathers profiling data

    Usage:
        with profile_it() as pr:
            whatever()
        print(pr.pretty()) # or print pr
    """

    def __init__(
        self, sort_by=DEFAULT_STATS_SORT_BY, n_entries=DEFAULT_STATS_N_ENTRIES, **kwargs
    ):
        super().__init__(**kwargs)
        self.sort_by = sort_by
        self.n_entries = n_entries

    def __enter__(self) -> "profile_it":
        self.enable()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def pretty(self) -> str:
        return get_stats_as_str(self, self.sort_by, self.n_entries)

    def __str__(self):
        return super().__str__() + "\n" + self.pretty()
