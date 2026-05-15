#!/bin/bash
# Script to push MyHermes to GitHub
# Usage: GITHUB_TOKEN=ghp_xxx ./push-to-github.sh

set -e

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN not set"
    echo "Get token from: https://github.com/settings/tokens"
    echo "Required scopes: repo"
    exit 1
fi

REPO_NAME="MyHermes"
USERNAME="kongsak4807017"

echo "Creating GitHub repo..."
curl -s -X POST \\
    -H "Authorization: token $GITHUB_TOKEN" \\
    -H "Accept: application/vnd.github.v3+json" \\
    https://api.github.com/user/repos \\
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"Personal Hermes Agent skills collection - 148 skills across 44 categories\",\"private\":false}" > /tmp/github-response.json

if grep -q "Bad credentials" /tmp/github-response.json; then
    echo "Error: Invalid GitHub token"
    exit 1
fi

if grep -q "already exists" /tmp/github-response.json; then
    echo "Repo already exists, continuing..."
fi

echo "Pushing to GitHub..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://$USERNAME:$GITHUB_TOKEN@github.com/$USERNAME/$REPO_NAME.git"
git push -u origin main

echo "Done! Repo: https://github.com/$USERNAME/$REPO_NAME"
