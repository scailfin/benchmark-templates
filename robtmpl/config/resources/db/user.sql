CREATE TABLE individual(
    id CHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY(id),
    UNIQUE(name)
);

--
-- Each team has a unique identifier and a unique name. All identifiers are
-- expected to be created using the benchtmpl.util.core.get_unique_identifier
-- method which returns string of 32 characters.
--
CREATE TABLE organization(
    id CHAR(32) NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner_id CHAR(32) NOT NULL REFERENCES individual (id),
    PRIMARY KEY(id),
    UNIQUE(name)
);

--
-- Mapping of users to teams
--
CREATE TABLE org_member(
    org_id CHAR(32) NOT NULL REFERENCES organization (id),
    indv_id CHAR(32) NOT NULL REFERENCES individual (id),
    PRIMARY KEY(org_id, indv_id)
);
