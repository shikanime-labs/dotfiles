#!/usr/bin/env python3
"""Finish creating AGENT.md PRs — shikanime-studio + shikanime."""
import base64
import json
import subprocess
import sys
import os
import tempfile

AGENT_MD_CONTENT = """# AGENT.md

## Pull Request Convention

All pull requests MUST be created via [ghstack](https://github.com/ezyang/ghstack).

### Why ghstack

ghstack stacks PRs cleanly on GitHub — each commit becomes its own PR, dependencies are tracked automatically, and the review/merge flow stays linear.

### How to submit a PR

    uvx ghstack

That's it. Push your commits to the repo's default branch namespace and ghstack opens (or updates) PRs for each commit.

### Commit message style

- Capitalize the first letter of the subject line.
- Use imperative mood: "Update foo bar for reason x y" not "Updated foo bar...".
- Keep the subject line under 72 characters.
- Add a body only when the change needs explanation.

### Before landing

1. Wait for CI to pass on the PR.
2. Check `gh pr checks` -- all green before merge.
3. Merge via `gh pr merge` or the GitHub UI.

### Notes

- Do NOT use `--ignore-immutable` with ghstack when working in a jj repo. Use `git commit` directly for commits intended for ghstack.
- GPG signing is required on some repos. Ensure your signing key is configured.
"""

TITLE = "Add AGENT.md with ghstack PR convention"
BODY = "Adds AGENT.md documenting the ghstack-based PR workflow and commit message conventions."
BASE_BRANCH = "add-agent-md"

SKIP_SHIKANIME = {
    "nixpkgs", "devenv", "nixos-hardware", "gitnr", "jj-spr", "treefmt-nix",
    "terminus", "hermes-agent", "mautrix-manager", "copyparty", "home-manager",
    "discord", "tailscale", "ghstack", "console", "socle", "sapling",
    "langchain", "website", "event-emitter", "backupstore", "WSL2-Linux-Kernel",
    "k0s", "longhorn-ui", "longhorn-engine", "k0sctl", "shellcheck",
    "nix-darwin", "csi-provisioner", "helix", "cluster-api-provider-vcluster",
    "langchain-vertexai-extended", "vertex-ai-samples", "airbyte", "tokio",
    "pgcat", "AvantHeim", "rancher-desktop", "devcontainer-features",
    "devcontainers-constrib-features", "rancher-desktop-wsl-distro", "pytorch",
    "nix", "flakehub-push", "treefmt", "NixOS-WSL", "command", "cli",
    "skaffold", "obs-studio", "scoop-extras", "streamlit", "python-aiplatform",
    "keycloak-theme-dsfr", "longhorn-charts", "longhorn-manager", "jj",
    "github", "gitignore",
}


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return result


def create_file_and_pr(owner, repo):
    full = f"{owner}/{repo}"

    # Check if PR already exists
    pr_check = run(["gh", "pr", "list", "-R", full, "--head", BASE_BRANCH, "--jq", ".[].html_url"])
    if pr_check.returncode == 0 and pr_check.stdout.strip():
        print(f"    PR exists: {pr_check.stdout.strip()}")
        return

    # Get default branch
    db = run(["gh", "api", f"repos/{full}", "--jq", ".default_branch"])
    if db.returncode != 0 or not db.stdout.strip():
        print(f"    ERROR: no default branch")
        return
    default_branch = db.stdout.strip()

    # Check if branch exists
    branch = run(["gh", "api", f"repos/{full}/git/ref/heads/{BASE_BRANCH}", "--jq", ".ref"])
    branch_exists = branch.returncode == 0

    if not branch_exists:
        # Get default branch SHA
        sha_res = run(["gh", "api", f"repos/{full}/git/ref/heads/{default_branch}", "--jq", ".object.sha"])
        if sha_res.returncode != 0 or not sha_res.stdout.strip():
            print(f"    ERROR: cannot get SHA")
            return
        sha = sha_res.stdout.strip()

        # Create branch
        ref_res = run(["gh", "api", f"repos/{full}/git/refs",
                       "-f", f"ref=refs/heads/{BASE_BRANCH}", "-f", f"sha={sha}"])
        if ref_res.returncode != 0 and "already exists" not in ref_res.stderr:
            print(f"    ERROR creating branch: {ref_res.stderr[:150]}")
            return

    # Check if file already exists on branch
    file_check = run(["gh", "api", f"repos/{full}/contents/AGENT.md?ref={BASE_BRANCH}", "--jq", ".name"])
    file_exists = file_check.returncode == 0 and file_check.stdout.strip()

    if not file_exists:
        # Create file via API — write base64 to temp file, use @file syntax
        content_b64 = base64.b64encode(AGENT_MD_CONTENT.encode()).decode()
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.b64', delete=False)
        tmp.write(content_b64)
        tmp.close()

        file_res = run(["gh", "api", f"repos/{full}/contents/AGENT.md",
                        "-f", f"message={TITLE}",
                        "-f", f"branch={BASE_BRANCH}",
                        "--raw-field", f"content=@{tmp.name}"])
        os.unlink(tmp.name)

        if file_res.returncode != 0:
            print(f"    ERROR creating file: {file_res.stderr[:200]}")
            return

    # Create PR
    pr_res = run(["gh", "api", f"repos/{full}/pulls",
                  "-f", f"title={TITLE}",
                  "-f", f"head={BASE_BRANCH}",
                  "-f", f"base={default_branch}",
                  "-f", f"body={BODY}",
                  "--jq", ".html_url"])
    if pr_res.returncode != 0:
        print(f"    ERROR creating PR: {pr_res.stderr[:200]}")
        return

    print(f"    PR: {pr_res.stdout.strip()}")


def get_repos(owner):
    res = run(["gh", "repo", "list", owner, "--limit", "100",
               "--json", "name,isArchived",
               "--jq", ".[] | select(.isArchived == false) | .name"])
    if res.returncode != 0:
        return []
    return [r.strip() for r in res.stdout.strip().splitlines() if r.strip()]


def main():
    targets = [
        ("shikanime-studio", None),
        ("shikanime", SKIP_SHIKANIME),
    ]

    all_prs = []

    for owner, skip_set in targets:
        print(f"=== {owner} ===")
        repos = get_repos(owner)
        for repo in repos:
            if skip_set and repo in skip_set:
                print(f"    SKIP: {repo}")
                continue
            print(f">>> {owner}/{repo}")
            create_file_and_pr(owner, repo)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
