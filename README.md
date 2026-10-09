# dotfiles

Managed by [Ansible](https://ansible.com).

## Quick start

```bash
ansible-playbook playbooks/dotfiles.yaml
```

Secrets for `~/.hermes/.env` are supplied at runtime via
`--extra-vars @secrets.yaml` under the `hermes_env` mapping -- never
committed.

## Contents

- `inventory/hosts.yaml` -- workstations grouped by OS (darwin / linux /
  windows)
- `inventory/group_vars/`, `inventory/host_vars/` -- per-OS file lists and
  per-host values (soul operator)
- `roles/dotfiles/files/` -- verbatim dotfiles
  - `ssh_config` -- public SSH host aliases for `shikanime-labs/machines`
  - `git-ignore` -- global git ignore
  - `hermes_config.yaml` -- full hermes config (no secrets)
  - `soul-<host>.md` -- host-specific SOUL
  - `jj_config_windows.toml` -- Windows jj config (AppData path)
- `roles/dotfiles/templates/` -- Jinja2 templates
  - `hermes_env.j2` -- hermes secrets env (from `hermes_env` extra-vars)
  - `gitconfig.j2` -- git config (Windows vs unix identity/signing)
  - `jj_config.toml.j2` -- jj config (ssh signing backend)
  - `codex_config.toml.j2` -- Codex config
  - `zshrc.j2` / `zprofile.j2` / `bash_profile.j2` -- shells (darwin)
  - `nix_conf.j2` -- nix.conf (darwin)
- `playbooks/dotfiles.yaml` -- converge playbook
- `ansible.cfg` -- roles path + default inventory

## Host-specific SOUL

`hermes_soul_operator` (host_vars) selects the operator profile by filename
`soul-<operator>.md`:

| Host      | Operator | Archetype                     |
| --------- | -------- | ----------------------------- |
| telsha    | 21O      | The Strict Guardian (ISTJ)    |
| ishtar    | 17O      | The Flight-Bay Analyst (ESFJ) |
| kaltashar | 11O      | The Logistics Anchor (ISTJ)   |

## Shell config: zprofile vs zshrc split

The split follows zsh's own execution model, not a preference:

- `zprofile.j2` -- runs **once per login shell** (`zsh -l`, SSH, terminal
  launch). Sets the base environment that every subsequent shell inherits:
  `~/.local/bin`, and the MacPorts `/opt/local` PATH. Declared here exactly
  once so the PATH is not re-prepended on every interactive prompt. On Apple
  Silicon the brew shellenv is sourced here; Intel Macs no longer set brew
  PATH (brew is deprecated there).
- `zshrc.j2` -- runs **per interactive shell** (each new prompt/tab). Holds
  shell-session tooling that must re-evaluate per shell: the `cargo`/`rd`/
  `pnpm` PATH additions and the `direnv` hook.

Keeping login-only setup out of `.zshrc` avoids duplicate PATH entries.
`bash_profile.j2` mirrors the `zprofile.j2` role for bash login shells.

## Hermes secrets (env-vars)

Hermes Agent secrets are injected via `hermes_env.j2` from the `hermes_env`
mapping supplied at runtime (`--extra-vars @secrets.yaml`). Keys:

- `DISCORD_BOT_TOKEN`
- `DISCORD_ALLOWED_USERS`
- `MATRIX_HOMESERVER`
- `API_SERVER_KEY`
- `GOOGLE_API_KEY`
- `GITHUB_TOKEN`
- `DISCORD_HOME_CHANNEL`
