#!/bin/bash
# A script to quickly setup a running development environment
#
# It's primary purpose is to set up docker networking correctly so that
# the bot can connect to remote services as well as those hosted on
# the host machine.
#

# Change directory to where this script is located. We'd like to run
# `docker-compose` in the same directory to use the adjacent
# docker-compose.yml and .env files
cd `dirname "$0"`

function on_exit {
  cd -
}

# Ensure we change back to the old directory on script exit
trap on_exit EXIT

# To allow the docker container to connect to services running on the host,
# we need to use the host's internal ip address. Attempt to retrieve this.
#
# Check whether the ip address has been defined in the environment already
if [ -z "$HOST_IP_ADDRESS" ]; then
  # It's not defined. Try to guess what it is

  # First we try the `ip` command, available primarily on Linux
  export HOST_IP_ADDRESS="`ip route get 1 | sed -n 's/^.*src \([0-9.]*\) .*$/\1/p'`"

  if [ $? -ne 0 ]; then
    # That didn't work. `ip` isn't available on old Linux systems, or MacOS.
    # Try `ifconfig` instead
    export HOST_IP_ADDRESS="`ifconfig $(netstat -rn | grep -E "^default|^0.0.0.0" | head -1 | awk '{print $NF}') | grep 'inet ' | awk '{print $2}' | grep -Eo '([0-9]*\.){3}[0-9]*'`"
 
    if [ $? -ne 0 ]; then
      # That didn't work either, give up
      echo "
Unable to determine host machine's internal IP address.
Please set HOST_IP_ADDRESS environment variable manually and re-run this script.
If you do not have a need to connect to a homeserver running on the host machine,
set HOST_IP_ADDRESS=127.0.0.1"
      exit 1
    fi
  fi
fi

# Build and run latest code
docker-compose up --build local-checkout-dev
