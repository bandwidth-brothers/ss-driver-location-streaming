# Liquibase for Database Changes

This project uses [Liquibase][liquibase] for database schema changes.
Changes to the database schema should be made by adding [changeset(s)][changesets] and then running the Liquibase `update` command.

[liquibase]: https://docs.liquibase.com/home.html
[changesets]: https://docs.liquibase.com/concepts/changelogs/changeset.html

* [Docker](#docker)
* [Run Liquibase Container](#run-liquibase-container)
* [`liquibase` Command](#liquibase-command)
* [Developer Workflow](#developer-workflow)
* [Best Practices](#best-practices)

## Docker

Liquibase can be run from a [Docker image][docker-image], but the MySQL driver will not be installed because of licensing conflicts.
The included Dockerfile runs the command to install the MySQL driver. You can build the image with the following script:

```bash
$ liquibase/buid.sh
```

## Run Liquibase Container

Liquibase can be run as a Docker container. Just run the following script:

```bash
$ liquibase/run.sh [local]
```

There is a `local` option which requires the `LIQUIBASE_DOCKER_NETWORK` environment variable to be set.
When starting the MySQL development container with the `scripts/mysql.sh` script, a Docker container will be started on a Docker network.
The name of the network will be printed to the terminal when the container starts up.
Use that network name to set the `LIQUIBASE_DOCKER_NETWORK` variable.

[docker-image]: https://hub.docker.com/r/liquibase/liquibase

## `liquibase` Command

When running the `liquibase` command, the `--username`, `--password`, and `--url` (in non development) options need to be present.

```bash
$ liquibase \
    --username=someuser \
    --password=somesecret \
    --url='jdbc:mysql://someurl/scrumptious' \
    update
```

Other required options `--changeLogFile`, `--driver` are in the `liquibase.properties` file.

## Developer Workflow

1. Add changeset
2. Verify SQL that will execute (`updateSQL`)
3. Save changelog to source control
4. Run database update command (`update`)
5. Verify that changeset(s) were executed

## Best Practices

* **Organize changelogs** - Make it easier to find specific changelogs. Changelogs can be organized by major release.
    * changelog-master.mysql.xml
    * changelog-1.0.mysql.xml
    * changelog-2.0.mysql.xml
* **Add comments to changesets** - Comment why a changeset what added, etc.
* **Use `include` tag** - Break up changelog using `include` tags. Changesets can be separated and organized by features, releases, or other logical boundaries. Included changelogs are run in the order they are listed. Make sure they are either independent or that dependent changelogs are listed first.
* **Use `includeApp` tag** - Call on directories with multiple changelogs using the `includeAll` tag. Use a "master" changelog in XML (using `includeAll`) that points to other changelogs that use the `include` tag.
* **Trim changelogs** - Remove unneeded/redundant/overlapping changesets. For example, a change set that adds a column, then another that removes a column. Just remove both changesets.
