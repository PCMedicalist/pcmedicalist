#!/bin/sh
# Configure git to use the repo-local .githooks directory for hooks
git config core.hooksPath .githooks
echo "Configured git to use .githooks as hooksPath"
