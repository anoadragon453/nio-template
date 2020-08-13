# Contributing to nio-template

Thank you for taking interest in this little project. Below is some information
to help you with contributing.

## Setting up your development environment

### Using `docker-compose`

It is **recommended** to use Docker Compose to run the bot while
developing, as all necessary dependencies are handled for you. After
installation and ensuring the `docker-compose` command works, you need to:

1. Create a data directory and config file by following the
   [docker setup instructions](docker#setup).

2. Create a docker volume pointing to that directory:

   ```
   docker volume create \
     --opt type=none \
     --opt o=bind \
     --opt device="/path/to/data/dir" data_volume
   ```

Run `docker/start-dev.sh` to start the bot.

**Note:** If you are trying to connect to a Synapse instance running on the
host, you need to allow the IP address of the docker container to connect. This
is controlled by `bind_addresses` in the `listeners` section of Synapse's
config. If present, either add the docker internal IP address to the list, or
remove the option altogether to allow all addresses.

### Running natively

If you would rather not or are unable to run docker, please follow the Native
Installation, Configuration and Running sections in the
[project readme](README.md#native-installation).

## Development dependencies

There are some python dependencies that are required for linting/testing etc.
You can install them with:

```
pip install -e ".[dev]"
```

## Code style

Please follow the [PEP8](https://www.python.org/dev/peps/pep-0008/) style
guidelines and format your import statements with
[isort](https://pypi.org/project/isort/).

## Linting

Run the following script to automatically format your code. This *should* make
the linting CI happy:

```
./scripts-dev/lint.sh
```

## What to work on

Take a look at the [issues
list](https://github.com/anoadragon453/nio-template/issues). What
feature would you like to see or bug do you want to be fixed?

If you would like to talk any ideas over before working on them, you can reach
me at `@andrewm:amorgan.xyz` on matrix.
