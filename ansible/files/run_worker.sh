#!/bin/sh

faafo-worker \
    --amqp-url amqp://tutorial:secretsecret@service:5672/ \
    --target /home/vagrant \
    --debug --verbose
