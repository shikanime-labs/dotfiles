# Dotfiles

Shikanime personal dotfiles, managed by Ansible. (Note: this repo is NOT the
Nix `home/`+`hosts/` project — and the former chezmoi layout was removed in
favor of the Ansible layout below.)

## Structure

- `inventory/hosts.yaml` — workstations grouped by OS (darwin/linux/windows)
- `group_vars/`, `host_vars/` — per-OS and per-host file lists and values
- `roles/dotfiles/` — the single deployment role
  - `files/` — verbatim dotfiles (ssh config, hermes config.yaml, souls)
  - `templates/` — Jinja2 templates (env, gitconfig, jj, nix, shells)
- `playbooks/dotfiles.yaml` — entry point: `ansible-playbook playbooks/dotfiles.yaml`

## Deploy

```sh
ansible-playbook -i inventory/hosts.yaml playbooks/dotfiles.yaml
```

Secrets for `~/.hermes/.env` are supplied at runtime via
`--extra-vars @secrets.yaml` (or an ansible-vault file) under the
`hermes_env` mapping — never committed.

## Commit Style

- Plain-text capitalized title, no conventional-commit prefix.
- Keep Markdown wrapped at 80 columns.

## PR Workflow (plain `gh pr`, NOT `gh stack`)

The org removed `gh stack` / ghstack entirely. Land changes with plain
GitHub PRs:

- Branch off `main`: `feat/…`, `fix/…`, or `<owner>/<short-desc>` when a
  repo ruleset constrains naming.
- Push to `origin`, then:
  ```sh
  gh pr create --repo shikanime-labs/dotfiles \
    --head shikanime-labs:<branch> --base main
  ```
- Keep one logical change per PR.
- `main` requires **signed commits** (ruleset `required_signatures`). Sign with
  an SSH or GPG key registered as a GitHub signing key:
  ```sh
  git config gpg.format ssh
  git config user.signingkey ~/.ssh/id_ed25519.pub
  git config gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
  ```
- Close the PR deliberately after merge; do not rely on auto-close keywords.

## Secrets

Never commit secret values or private key material (age key, SSH private
keys, GPG private keys). `hermes_env` comes from runtime extra-vars or
ansible-vault.

## Environment

This repository ships a `.envrc` for direnv. Run `direnv allow` once after
cloning; direnv then loads the Nix flake dev shell automatically on every
directory change (`.envrc` runs
`use flake . --accept-flake-config --no-pure-eval`). Without direnv, enter
the same shell manually with `nix develop`.
