#!/bin/bash -e
#
# Startup-Skript for the container
#
aerich upgrade > /opt/aerich.log
uvicorn app:create --factory --host=${APP_HOST} --port=${APP_PORT}
