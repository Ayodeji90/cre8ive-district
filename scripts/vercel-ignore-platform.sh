#!/bin/bash
# Vercel Ignored Build Step for the platform-web project.
# Set this as the "Ignored Build Step" in the Vercel project settings.
# Returns exit 1 (proceed with build) if platform-web files changed,
# exit 0 (skip build) if only other files changed.

echo "Checking if platform-web files changed..."

# This script may run from Vercel's configured Root Directory. Always compare
# paths from the Git repository root.
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

# A first deployment has no prior commit to compare, so it must build.
if ! git rev-parse --verify HEAD^ >/dev/null 2>&1; then
  echo "→ First deployment — proceeding with build"
  exit 1
fi

# Compare against the previous commit. API and agent changes do not require a
# marketing-site rebuild; this deployment only serves the public waitlist app.
git diff HEAD^ HEAD --quiet -- \
  platform-web/apps/marketing \
  platform-web/packages \
  platform-web/package.json \
  platform-web/pnpm-lock.yaml \
  platform-web/turbo.json \
  platform-web/tsconfig.base.json \
  platform-web/vercel.json \
  scripts/vercel-ignore-platform.sh

if [ $? -eq 1 ]; then
  echo "→ platform-web changed — proceeding with build"
  exit 1
fi

echo "→ No platform-web changes — skipping build"
exit 0
