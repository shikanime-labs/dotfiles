# Dotfiles

Shikanime personal dotfiles, managed by chezmoi. (Note: this repo is NOT the
Nix `home/`+`hosts/` project the old Stack Workflow section described — that
text was removed.)

## Structure

- `dot_*` / `private_dot_*` — chezmoi-managed dotfiles (ssh, jj, git, hermes…)
- `.chezmoihooks/` — sops decrypt/re-encrypt hooks
- `.chezmoiignore` — deploy-time excludes (state, OS junk, age private key)
- `README.md` — quick start + the chezmoi+sops secrets workflow

## Commit Style

- Plain-text capitalized title, no conventional-commit prefix.
- Keep Markdown wrapped at 80 columns.

## PR Workflow (plain `gh pr`, NOT `gh stack`)

The org removed `gh stack` / `ghstack` entirely. Land changes with plain
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

Secrets are encrypted with `sops` (age) and decrypted by chezmoi hooks at apply
time. See `README.md` "Secrets (chezmoi + sops)". Never commit private key
material (age key, SSH private keys, GPG private keys).
