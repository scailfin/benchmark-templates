-- This file is part of the Reproducible Open Benchmarks for Data Analysis
-- Platform (ROB).
--
-- Copyright (C) 2019 NYU.
--
-- ROB is free software; you can redistribute it and/or modify it under the
-- terms of the MIT License; see LICENSE file for more details.


-- -----------------------------------------------------------------------------
-- This file defines the database schema for the part of the benchmark engine
-- that maintains information about benchmark runs.
-- -----------------------------------------------------------------------------

--
-- Drop all tables (if they exist)
--
DROP TABLE IF EXISTS benchmark_run;

--
-- Each benchmark run has a unique identifier, a reference to the run status
-- and various timestamps that are set at different workflow state changes.
--
CREATE TABLE benchmark_run(
    run_id CHAR(32) NOT NULL,
    submission_id CHAR(32) NOT NULL,
    state VARCHAR(8) NOT NULL,
    created_at CHAR(26) NOT NULL,
    started_at CHAR(26),
    ended_at CHAR(26),
    PRIMARY KEY(run_id)
);
