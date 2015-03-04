#!/bin/sh

oat-tracker \
    --amqp-url amqp://tutorial:secretsecret@service:5672/ \
    --database-url mysql://tutorial:secretsecret@service:3306/tutorial
