<!-- owner: Automata | zone: technical | purpose: Canonical technical index for the Ansible-managed dotfiles repository -->
# dotfiles

Personal dotfiles managed by [Ansible](https://ansible.com). One converge
playbook deploys verbatim files and Jinja2-templated configs to a small fleet
of workstations grouped by OS. Secrets for `~/.hermes/.env` are supplied at
runtime via `--extra-vars @secrets.yaml` and never committed.

## Canonical sources

- [Repository README](https://github.com/shikanime-labs/dotfiles#readme)
- [Technical wiki](https://github.com/shikanime-labs/dotfiles/wiki)

## Layout

- `playbooks/dotfiles.yaml` — converge playbook applying the dotfiles role.
- `inventory/hosts.yaml` — workstations grouped by OS (darwin, linux,
  windows), with `ansible_user: shika`.
- `inventory/group_vars/`, `inventory/host_vars/` — per-OS file lists and
  per-host values, including `hermes_soul_operator`.
- `roles/dotfiles/tasks/main.yaml` — deployment tasks.
- `roles/dotfiles/files/` — verbatim dotfiles: `ssh_config` (public host
  aliases for shikanime-labs/machines), `git-ignore`, secret-free
  `hermes_config.yaml`, `soul-<operator>.md`, `jj_config_windows.toml`, and
  the `claude/` and `dsh/` config trees.
- `roles/dotfiles/templates/` — Jinja2 templates: `hermes_env.j2`,
  `gitconfig.j2` (Windows vs unix identity/signing), `jj_config.toml.j2`
  (SSH signing backend), `codex_config.toml.j2`, `zshrc.j2` / `zprofile.j2` /
  `bash_profile.j2`, `nix_conf.j2`, `syncthing_config.xml.j2`.
- `ansible.cfg` — roles path and default inventory.

## Subsystems

### Hosts and SOUL profiles

`hermes_soul_operator` in host_vars selects the operator profile by filename
`soul-<operator>.md`: telsha (darwin) → 21O, Strict Guardian (ISTJ);
kaltashar (darwin) → 11O, Logistics Anchor (ISTJ); ishtar (windows) → 17O,
Flight-Bay Analyst (ESFJ).

### Shell configuration

`zprofile.j2` runs once per login shell and owns the base environment:
`~/.local/bin`, MacPorts `/opt/local`, and brew shellenv on Apple Silicon
only. `zshrc.j2` runs per interactive shell and holds per-session tooling:
cargo, rd and pnpm PATH entries plus the direnv hook. `bash_profile.j2`
mirrors `zprofile.j2`. Keeping login-only setup out of `.zshrc` avoids
duplicate PATH entries.

### dsh patch layer

`roles/dotfiles/files/dsh/` holds one patch file per dsh profile
(`cordis-desktop.patch.yml`, `cordis-headless.patch.yml`), copied to
`~/.dsh/profiles/<profile>/cordis.patch.yml` and applied after every bundle
layer as a top-level array of id-targeted loader patches. The `dsh-llm-pi-ai`
inference provider accepts only routes whose models are declared in the
patch's `models:` list with their `contextWindow`, so that list must track the
inference gateway's routes byte-for-byte when routes change.

### Hermes secrets

`hermes_env.j2` injects the runtime `hermes_env` mapping as env keys including
`DISCORD_BOT_TOKEN`, `DISCORD_ALLOWED_USERS`, `MATRIX_HOMESERVER`,
`API_SERVER_KEY`, `GOOGLE_API_KEY`, `GITHUB_TOKEN` and
`DISCORD_HOME_CHANNEL`. Never commit age, SSH or GPG private key material;
`main` requires signed commits and the plain `gh pr` flow (no ghstack).

## Operations

```sh
ansible-playbook -i inventory/hosts.yaml playbooks/dotfiles.yaml --extra-vars @secrets.yaml
```

## Documentation rule

In-repo `docs/` is canonical for technical detail. The wiki is a rendered
human index that links here.
