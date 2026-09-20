#!/usr/bin/env bash
set -euo pipefail

: "${AI_EDITOR_ASSET_BASE_URL:?Set AI_EDITOR_ASSET_BASE_URL to the directory containing models.zip, resource.zip, and web static assets.}"

# Create required directories
mkdir -p .storyline resource

# 1. Download models.zip to .storyline/ and extract it (keep original directory name)
wget "${AI_EDITOR_ASSET_BASE_URL%/}/models.zip" \
  -O .storyline/models.zip

unzip -o .storyline/models.zip -d .storyline/models/

# Remove the original archive
rm .storyline/models.zip


# 2. Download resource.zip to .storyline/ and extract it into ./resource
wget "${AI_EDITOR_ASSET_BASE_URL%/}/resource.zip" \
  -O .storyline/resource.zip

unzip -o .storyline/resource.zip -d resource

# Remove the original archive
rm .storyline/resource.zip

# List of filenames
files=("brand_black.png" "brand_white.png" "logo.png" "dice.png" "github.png" "node_map.png" "user_guide.png")

# Download each file
for f in "${files[@]}"; do
    wget "${AI_EDITOR_ASSET_BASE_URL%/}/web/static/$f" -O "web/static/$f"
done
