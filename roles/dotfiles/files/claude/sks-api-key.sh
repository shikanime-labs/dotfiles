#!/bin/sh
grep '^SKS_API_KEY=' "$HOME/.hermes/.env" | cut -d= -f2-
