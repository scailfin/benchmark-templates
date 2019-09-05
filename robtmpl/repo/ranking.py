# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""
"""


class LeaderboardEntry(object):
    """Entry in the leaderboard for a benchmark. Each entry contains a reference
    to the user that submitted the run and a dictionary containing the run
    results.
    """
    def __init__(self, user, results):
        """Initialize the components of the leaderboard entry.

        Parameters
        ----------
        user: benchengine.user.base.RegisteredUser
            User that submitted the benchmark run
        result: dict
            Dictionary of run results. The result values are keyed by the column
            identifier from the benchmark schema.
        """
        self.user = user
        self.results = results
