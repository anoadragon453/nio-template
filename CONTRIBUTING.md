# Contributing to nio-template

Thank you for taking interest in this little project. Below is some information
to help you with contributing.

## Setting up your development environment

See the
[Install the dependencies section of SETUP.md](SETUP.md#install-the-dependencies)
for help setting up a running environment for the bot.

If you would rather not or are unable to run docker, the following instructions
will explain how to install the project dependencies natively.

#### Install libolm

You can install [libolm](https://gitlab.matrix.org/matrix-org/olm) from source,
or alternatively, check your system's package manager. Version `3.0.0` or
greater is required.

**(Optional) postgres development headers**

By default, the bot uses SQLite as its storage backend. This is fine for a
few hundred users, but if you plan to support a much higher volume
of requests, you may consider using Postgres as a database backend instead.

If you want to use postgres as a database backend, you'll need to install
postgres development headers:

Debian/Ubuntu:

```
sudo apt install libpq-dev libpq5
```

Arch:

```
sudo pacman -S postgresql-libs
```

#### Install Python dependencies

Create and activate a Python 3 virtual environment:

```
virtualenv -p python3 env
source env/bin/activate
```

Install python dependencies:

```
pip install -e .
```

(Optional) If you want to use postgres as a database backend, use the following
command to install postgres dependencies alongside those that are necessary:

```
pip install ".[postgres]"
```

### Development dependencies

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
me at [@andrewm:amorgan.xyz](https://matrix.to/#/@andrewm:amorgan.xyz)
on matrix.
