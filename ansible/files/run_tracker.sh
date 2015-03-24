#!/bin/sh

faafo-tracker \
    --amqp-url amqp://faafo:secretsecret@127.0.0.1:5672/ \
    --api-url http://127.0.0.1:5000 \
    --debug --verbose
