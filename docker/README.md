# Docker

The docker image will run my-project-name with a SQLite database and
end-to-end encryption dependencies included. For larger deployments, a
connection to a Postgres database backend is recommended.

## Setup

### The `/data` volume

The docker container expects the `config.yaml` file to exist at
`/data/config.yaml`. To easily configure this, it is recommended to create a
directory on your filesystem, and mount it as `/data` inside the container:

```
mkdir data
```

We'll later mount this directory into the container so that its contents
persist across container restarts.

### Creating a config file

Copy `sample.config.yaml` to a file named `config.yaml` inside of your newly
created `data` directory. Fill it out as you normally would, with a few minor
differences:

* The bot store directory should reside inside of the data directory so that it
  is not wiped on container restart. Change it from the default to
  `/data/store`. There is no need to create this directory yourself, it will be
  created on startup if it does not exist.

* Choose whether you want to use SQLite or Postgres as your database backend.
  Postgres has increased performance over SQLite, and is recommended for
  deployments with many users.

  If using SQLite, ensure your database file is
  stored inside the `/data` directory:

  ```
  database: "sqlite:///data/bot.db"
  ```

  If using postgres, point to your postgres instance instead:

  ```
  database: "postgres://username:password@postgres/my-project-name?sslmode=disable"
  ```

  **Note:** a postgres container is defined in `docker-compose.yaml` for your convenience.
  If you would like to use it, set your database connection string to:

  ```
  database: "postgres://postgres:somefancypassword@postgres/postgres?sslmode=disable"
  ```

  The password `somefancypassword` is defined in the docker compose file.

Change any other config values as necessary. For instance, you may also want to
store log files in the `/data` directory.

## Running

First, create a volume for the data directory created in the above section:

```
docker volume create \
  --opt type=none \
  --opt o=bind \
  --opt device="/path/to/data/dir" data_volume
```

Optional: If you want to use the postgres container defined in
`docker-compose.yaml`, start that first:

```
docker-compose up -d postgres
```

Start the bot with:

```
docker-compose up my-project-name
```

This will run the bot and log the output to the terminal. You can instead run
the container detached with the `-d` flag:

```
docker-compose up -d my-project-name
```

(Logs can later be accessed with the `docker logs` command).

This will use the `latest` tag from
[Docker Hub](https://hub.docker.com/somebody/my-project-name).

If you would rather run from the checked out code, you can use:

```
docker-compose up local-checkout
```

This will build an optimized, production-ready container. If you are developing
instead and would like a development container for testing local changes, use
the `start-dev.sh` script and consult [CONTRIBUTING.md](../CONTRIBUTING.md).

**Note:** If you are trying to connect to a Synapse instance running on the
host, you need to allow the IP address of the docker container to connect. This
is controlled by `bind_addresses` in the `listeners` section of Synapse's
config. If present, either add the docker internal IP address to the list, or
remove the option altogether to allow all addresses.

## Updating

To update the container, navigate to the bot's `docker` directory and run:

```
docker-compose pull my-project-name
```

Then restart the bot.

## Systemd

A systemd service file is provided for your convenience at
[my-project-name.service](my-project-name.service). The service uses
`docker-compose` to start and stop the bot.

Copy the file to `/etc/systemd/system/my-project-name.service` and edit to
match your setup. You can then start the bot with:

```
systemctl start my-project-name
```

and stop it with:

```
systemctl stop my-project-name
```

To run the bot on system startup:

```
systemctl enable my-project-name
```

## Building the image

To build a production image from source, use the following `docker build` command
from the repo's root:

```
docker build -t somebody/my-project-name:latest -f docker/Dockerfile .
```
