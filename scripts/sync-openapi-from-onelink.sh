#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ge 1 ]]; then
  SOURCE_REPO_PATH="$1"
elif [[ -d "../swagger/tag_groups" ]]; then
  SOURCE_REPO_PATH=".."
else
  SOURCE_REPO_PATH="../onelink"
fi

SOURCE_OPENAPI_DIR="${SOURCE_REPO_PATH%/}/swagger/tag_groups"
TARGET_OPENAPI_DIR="$(cd "$(dirname "$0")/.." && pwd)/openapi"

if [[ ! -d "$SOURCE_OPENAPI_DIR" ]]; then
  echo "Source OpenAPI directory not found: $SOURCE_OPENAPI_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_OPENAPI_DIR"

cp "$SOURCE_OPENAPI_DIR"/application_swagger.json "$TARGET_OPENAPI_DIR"/
cp "$SOURCE_OPENAPI_DIR"/platform_swagger.json "$TARGET_OPENAPI_DIR"/
cp "$SOURCE_OPENAPI_DIR"/client_swagger.json "$TARGET_OPENAPI_DIR"/
cp "$SOURCE_OPENAPI_DIR"/other_swagger.json "$TARGET_OPENAPI_DIR"/

echo "OpenAPI files synced from $SOURCE_OPENAPI_DIR to $TARGET_OPENAPI_DIR"
