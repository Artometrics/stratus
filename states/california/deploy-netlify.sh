#!/usr/bin/env bash
exec "$(cd "$(dirname "$0")" && pwd)/../../tools/deploy-netlify.sh" "$(cd "$(dirname "$0")" && pwd)"
