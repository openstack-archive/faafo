#!/bin/sh

faafo-worker \
    --amqp-url amqp://faafo:secretsecret@127.0.0.1:5672/ \
    --target /home/vagrant \
    --debug --verbose
