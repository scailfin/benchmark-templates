-- This file is part of the Reproducible Open Benchmarks for Data Analysis
-- Platform (ROB).
--
-- Copyright (C) 2019 NYU.
--
-- ROB is free software; you can redistribute it and/or modify it under the
-- terms of the MIT License; see LICENSE file for more details.


-- -----------------------------------------------------------------------------
-- This file defines the database schema for the benchmark repository. The
-- repository maintains basic information about registered benchmarks.
-- -----------------------------------------------------------------------------

--
-- Drop all tables (if they exist)
--
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
