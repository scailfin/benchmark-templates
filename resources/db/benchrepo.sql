-- -----------------------------------------------------------------------------
-- This file is part of the Reproducible Open Benchmarks for Data Analysis
-- Platform (ROB).
--
-- Copyright (C) 2019 NYU.
--
-- ROB is free software; you can redistribute it and/or modify it under the
-- terms of the MIT License; see LICENSE file for more details.
-- -----------------------------------------------------------------------------

-- -----------------------------------------------------------------------------
-- This file defines the database schema for the benchmark repository. The
-- repository maintains basic information about registered benchmarks as well
-- as status information for benchmark runs.
-- -----------------------------------------------------------------------------


--
-- Drop all tables (if they exist)
--
DROP TABLE IF EXISTS benchmark_run;
DROP TABLE IF EXISTS template;

--
-- Each template has a unique identifier and name, an optional short descriptor
-- and an optional set of instructions.
--
CREATE TABLE template(
    id CHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    PRIMARY KEY(id),
    UNIQUE(name)
);

--
-- For each benchmark run the run state is maintained as well as timestamps for
-- different stages of the executed workflow.
--
CREATE TABLE benchmark_run(
    run_id CHAR(32) NOT NULL,
    template_id CHAR(32) NOT NULL REFERENCES template(id),
    state VARCHAR(8) NOT NULL,
    created_at CHAR(26) NOT NULL,
    started_at CHAR(26),
    ended_at CHAR(26),
    PRIMARY KEY(run_id)
);
