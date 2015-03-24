#!/bin/sh

faafo-api \
    --database-url mysql://faafo:secretsecret@127.0.0.1:3306/faafo \
    --debug --verbose
