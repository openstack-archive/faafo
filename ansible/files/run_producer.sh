#!/bin/sh

faafo-producer \
    --config-file producer.conf \
    --api-url http://127.0.0.1:5000 \
    --debug --verbose
