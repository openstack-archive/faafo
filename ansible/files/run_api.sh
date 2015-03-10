#!/bin/sh

faafo-api \
    --database-url mysql://tutorial:secretsecret@service:3306/tutorial \
    --debug --verbose
