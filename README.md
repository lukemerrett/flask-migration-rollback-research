# Flask Migration Rollback Research

Finding out what happens when a flask upgrade fails, in terms of rolling back the state of the database.

## Background

We want to understand what happens when a `flask db upgrade` fails in terms of the state of the database it
was being applied to.

An upgrade can fail if the database is in a different state that expected when the migrations are being applied,
or if there's an error in the migration scripts themselves.

Scenarios with theorised outcomes:

```gherkin
Scenario: Single migration in set succeeds
    Given a migration set consisting of [X]
    When the migration X succeeds
    Then the migration X is applied to the database
    
Scenario: Single migration in set fails
    Given a migration set consisting of [X]
    When the migration X fails
    Then the migration X is rolled back
    
Scenario: Multiple migrations in set, 1 fails in the set
    Given a migration set consisting of [X, Y, Z]
    When the migration Y fails
    Then the migration Y is rolled back
    And the migration X is rolled back
    And the migration Z is never applied
```

## Executing the scenarios

### Pre-requisites

* [Docker](https://www.docker.com/) installed and running
* [Python 3.9+](https://www.python.org/downloads/) installed and on your path

### Setting up the environment

Install the dependencies required to run this demo by using:

```bash
pip install -r requirements.txt
```

Then launch the Postgres database container by running:

```bash
# The "-d" flag starts it in the background to free up your terminal
docker compose up -d
```

This will launch Postgres on localhost:6456 (a non-standard port to avoid any local Postgres installs you may have).

### Running each scenario

We have this series of migrations to simulate a failure:

1. `dd7c69423ad9` - Stable
2. `5a77262c502b` - Stable
3. `653d68312991` - Broken, will error
4. `5929dc9c624a` - Stable

**Single migration in set succeeds**

Run the first migration, which works when applied to a fresh database.

```bash
flask db upgrade dd7c69423ad9
```

**Single migration in set fails**

Run this to apply all migrations up to `5a77262c502b`

```bash
flask db upgrade 5a77262c502b
```

Then run this to attempt to apply the broken migration:

```bash
flask db upgrade 653d68312991
```

Flask will throw an error on that script, and the database will be 
reverted to the state of the previous revision (`5a77262c502b`)

**Multiple migrations in set, 1 fails in the set**

Run this to ensure our database is in the correct state following any previous migration runs:

```bash
# Ensure we've at least applied the stable first revision
flask db upgrade dd7c69423ad9
# Ensure if other revisions have been applied since, we return to the stable revision
flask db downgrade dd7c69423ad9
```

Then run this to apply all remaining revisions in the migrations folder 
(these are revisions: `5a77262c502b`, `653d68312991` (broken) and `5929dc9c624a`):

```bash
flask db upgrade
```

Flask will throw an error on that script, and the database will be 
reverted to the state of the revision it was at before any of the batch were run (`dd7c69423ad9`)

### Tearing down

To stop the Postgres database container run:

```bash
docker compose down
```

## Findings

### Rollback Behaviour

If any of the scripts in a batch fail during a `flask db upgrade`, then none of the scripts in that batch are applied.

This means the database isn't left in a state where only partial migrations have been applied.

This proves all our theorised scenarios are correct.

This works exactly the same in `multidb` mode; if 1 script across any of the databases fails on `upgrade`,
every script in the batch across all databases is rolled back 
(see the [behaviour-on-multi-db](https://github.com/lukemerrett/flask-migration-rollback-research/tree/behaviour-on-multi-db) branch)

### Command Reference

* `flask db upgrade` - Will run will all scripts not already run into the target database
* `flask db upgrade dd7c69423ad9` - Run up to and including the supplied revision
* `flask db downgrade` - Reverts the last migration applied`
* `flask db downgrade dd7c69423ad9` - Downgrade to a specific revision, reverts all later revisions but not the supplied one
* `flask db upgrade --sql` - Rather than applying to the database, prints the SQL it _would_ have applied. Useful for debugging