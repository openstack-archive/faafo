#!/bin/sh

oat-worker \
    --amqp-url amqp://tutorial:secretsecret@service:5672/ \
    --target /home/vagrant
