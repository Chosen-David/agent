#!/usr/bin/env bash
set -eu
git -C "$AGENT_TEST_PROJECT_ROOT" diff --check
