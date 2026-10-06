# Move Fast, Don't Break Things (with dbt)

## Introduction
- Gabriel Strauss, Senior Data Engineer at OTI
- The data engineering team:
  - builds and maintains a wide range of data products that support analytics and reporting needs across the city.
  - owns pipelines for around 150 Open Data datasets.
  - administers the data platform that powers all of this work.
- Fairly large team - 9 FTEs and several contractors.

# Modernization

- Migrating from on-prem Oracle to Snowflake on Microsoft Azure.
- More stuff about what modernization "means" for the team, its practices and processes, etc.

# dbt Recap (CITE)

- dbt is a free and open-source framework to transform and test data.
  - Define data transformations as code, making them version-controlled and testable.
  - Supports modularity and reusability with macros and packages.
  - Declarative approach - write SELECTs, let dbt handle DDL. 

See https://cityshare.nycnet/intranets/anex/assets/anex/downloads/McCullough-Slides.pdf

# dbt Recap (CITE)

- model: A SELECT statement that dbt will "materialize" as a table or view in the database.
- source: read-only data that dbt can reference but will not modify.
- Directed acyclic graph (DAG): A representation of the dependencies between dbt models.

# dbt Principles

Data transformations are:
  - Declarative
  - Idempotent
  - Acyclic

# Real-life horror stories

Things you can do in an imperative pipeline:
    - `CALL mysteriously_named_stored_procedure()`
    - Two unrelated transformations that update the same table.
    - "SQL Override"
    - Default columns
    - Powercenter vs database processing

No one source of truth!

(You can avoid all of these things in Powercenter, and you can technically do all of them in dbt as well, but dbt actively discourages them.)

# dbt Metadata

PARSE -> COMPILE -> RUN

- PARSE: read project files and constructs a "manifest".
- COMPILE: converts models into executable SELECT statements.
- RUN: wraps SELECTs in DDL based on the database state, and runs them.

# Continuous Integration

Goals:
  - Find problems early.
  - Maintain quality and consistency.
  - Deliver faster.

# Ingredients we're working with

- manifest
- isolated env
- idempotency and read-only sources

# Project structure and organization (dbt-bouncer)

- Ingredients: manifest
- automatically check project conventions
    - line length
    - naming conventions
    - dependencies
    - documentation
    - etc

# Data validation

- We want to actually run any changed models.
- How do we know what changed?
  - Cloud compute is fast, but not free.
  - Want to limit the build to as few models as possible.
  - Originally, git diff and run downstream models
  - Now use dbt state
- compare `main` branch manifest to current branch manifest.
- How do we build the models in an isolated environment?
    - remember: read-only sources. 
    - `generate_schema_name` to create isolated schemas for CI.

# This can still be a bit slow and expensive

- `--defer` flag: reuse the results from a previous run.

# We're not there yet

- We aren't using `defer` yet 
- For automated CI, we are using the `--empty` flag, just ensuring the SQL "compiles"
- Dev manually triggers the full build pipeline.
- QA is still manual

# dbt is not a magic bullet

- dbt itself is nothing special, the important thing is that everything lives in the version-controlled code.
