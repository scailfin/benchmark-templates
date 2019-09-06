-- This file is part of the Reproducible Open Benchmarks for Data Analysis
-- Platform (ROB).
--
-- Copyright (C) 2019 NYU.
--
-- ROB is free software; you can redistribute it and/or modify it under the
-- terms of the MIT License; see LICENSE file for more details.


-- -----------------------------------------------------------------------------
-- This file defines the database schema for the benchmark submissions. Each
-- submission has a name. Submission names are unique for each template
-- since the name is used for display purposes to identify the submission.
-- -----------------------------------------------------------------------------

--
-- Drop all tables (if they exist)
--
DROP TABLE IF EXISTS submission;

--
-- Submissions are named collections of benchmark runs. The name of each
-- submission is unique (for a template).
--
CREATE TABLE submission(
    submission_id CHAR(32) NOT NULL,
    template_id CHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY(submission_id),
    UNIQUE(template_id, name)
);
