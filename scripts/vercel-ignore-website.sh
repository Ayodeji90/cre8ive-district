#!/bin/bash
# Vercel Ignored Build Step for the current static website.
# Set this as the "Ignored Build Step" in the existing Vercel project settings.
# Returns exit 1 (proceed with build) if root website files changed,
# exit 0 (skip build) if only platform-web files changed.

echo "Checking if website root files changed..."

# These are the directories/files that make up the current static site
git diff HEAD^ HEAD --quiet -- \
  index.html \
  about \
  contact \
  services \
  work \
  assets \
  vercel.json

if [ $? -eq 1 ]; then
  echo "→ Website files changed — proceeding with build"
  exit 1
fi

echo "→ No website changes — skipping build"
exit 0
