# dotfiles

Managed by [chezmoi](https://chezmoi.io).

## Quick start

```bash
chezmoi init --apply <repo>
```

## Contents

- `dot_gitconfig` -- git config (no secrets; only public signing-key
  fingerprint)
- `dot_ssh/config` -- public SSH host aliases for `shikanime-labs/machines`
- `private_dot_jj/config.toml` -- jj config (ssh signing backend)
- `private_dot_codex/config.toml` -- Codex config
- `dot_hermes/` -- Hermes Agent config
  - `config.yaml` -- full hermes config (no secrets)
  - `SOUL.md.tmpl` -- host-specific SOUL (template)
  - `env.tmpl` -- secrets template (chezmoi `{{ env }}`)
- `dot_gitconfig.tmpl` -- git config (SSH commit signing; host-portable via
  `{{ .chezmoi.homeDir }}`)
- `dot_bash_profile.tmpl` -- bash login env (Apple Silicon brew shellenv)
- `dot_zprofile.tmpl` -- zsh **login** env (Apple Silicon brew shellenv +
  `~/.local/bin` + MacPorts PATH)
- `dot_zshrc` -- zsh **interactive** env (cargo/rd/pnpm PATH + direnv hook)
- `private_dot_jj/config.toml` -- jj config (ssh signing backend)
- `private_dot_codex/config.toml` -- Codex config
- `dot_config/jj/config.toml` -- jj config (XDG path, ssh signing;
  kaltashar/macOS)
- `dot_config/nix/nix.conf` -- nix `experimental-features = nix-command flakes`
- `.chezmoitemplates/` -- shared template fragments
  - `soul-telsha.md` -- Operator 21O (Telsha)
  - `soul-ishtar.md` -- Operator 17O (Ishtar)
  - `soul-kaltashar.md` -- Operator 11O (Kaltashar)
- `.chezmoihooks/` -- sops decrypt/re-encrypt hooks (see Secrets below)

## Host-specific SOUL

`SOUL.md.tmpl` selects the correct operator profile by hostname:

| Host      | Operator | Archetype                     |
| --------- | -------- | ----------------------------- |
| telsha    | 21O      | The Strict Guardian (ISTJ)    |
| ishtar    | 17O      | The Flight-Bay Analyst (ESFJ) |
| kaltashar | 11O      | The Logistics Anchor (ISTJ)   |

## Shell config: zprofile vs zshrc split

The split follows zsh's own execution model, not a preference:

- `dot_zprofile` -- runs **once per login shell** (`zsh -l`, SSH, terminal
  launch). Sets the base environment that every subsequent shell inherits:
  `~/.local/bin`, and the MacPorts `/opt/local` PATH. Declared here exactly once
  so the PATH is not re-prepended on every interactive prompt. On Apple Silicon
  the brew shellenv is sourced here; Intel Macs no longer set brew PATH (brew is
  deprecated there).
- `dot_zshrc` -- runs **per interactive shell** (each new prompt/tab). Holds
  shell-session tooling that must re-evaluate per shell: the `cargo`/`rd`/`pnpm`
  PATH additions and the `direnv` hook.

Keeping login-only setup out of `.zshrc` avoids duplicate PATH entries.
`.bash_profile` mirrors the `.zprofile` role for bash login shells.

## Secrets (chezmoi + sops)

Secrets are encrypted with `sops` (age backend) and decrypted by chezmoi hooks
at apply time. chezmoi 2.72.0 has no native `.sops` auto-decryption, so
`.chezmoihooks/sops-decrypt-on-apply` and
`.chezmoihooks/sops-reencrypt-post-apply` shell out to `sops` to decrypt
`.sops.*` files before deploy and re-encrypt afterwards. The repo only ever
holds ciphertext.

### Why sops-hooks instead of chezmoi's native age backend

chezmoi 2.72.0 only wires `encryption = "age"` (chezmoi-native) and `gpg`; it
has **no** `encryption = "sops"` option. Two valid ways to manage sops
ciphertext in chezmoi:

1. **sops-hooks (this repo's choice)** -- keep `.sops.*` files encrypted with
   the `sops` binary and let `.chezmoihooks/` shell out to `sops -d` on apply.
   Pros: the `sops` config lives in `flake.nix` (`devenv.shells.default.sops`
   via the devlib sops integration) so the age recipients are version-controlled
   alongside the repo; no change to the committed ciphertext format.
2. **chezmoi-native age** -- switch to `encryption = "age"` and let chezmoi own
   the age key (`~/.config/sops/age/keys.txt`). Pros: no `sops` binary at apply
   time. Cons: requires re-encrypting every secret under chezmoi's age format
   and dropping the `flake.nix` sops config -- a migration, not a config toggle.

We stay on sops-hooks to avoid re-encrypting committed secrets; the age key
material is identical either way.

### One-time local setup (per machine, NOT committed)

1. Install the toolchain:

   ```sh
   scoop install chezmoi sops age
   ```

2. Generate an age keypair (the private key is yours alone):

   ```sh
   age-keygen -o C:/Users/<you>/.config/sops/age/keys.txt
   # record the public key:  age-keygen -y C:/Users/<you>/.config/sops/age/keys.txt
   ```

3. On Windows, `sops` resolves `~/.config` via `%APPDATA%`, not MSYS `$HOME`, so
   set the native path (the hooks do this automatically):

   ```sh
   export SOPS_AGE_KEY_FILE="C:/Users/<you>/.config/sops/age/keys.txt"
   ```

4. Create `~/.config/chezmoi/chezmoi.toml`:

   ```toml
   sourceDir = "C:/path/to/this/repo"
   ```

### Workflow

- Add a new secret (commit only ciphertext):

  ```sh
  printf 'TOKEN=...\n' > private_dot_foo/secret.env
  # sops config is generated by the dev shell (flake.nix -> devlib sops):
  sops --config "$DEVENV_ROOT/sops.yaml" --encrypt \
    private_dot_foo/secret.env > private_dot_foo/secret.sops.env
  rm -f private_dot_foo/secret.env
  git add private_dot_foo/secret.sops.env
  ```

- Apply (hooks decrypt -> chezmoi deploys -> hooks re-encrypt):

  ```sh
  chezmoi apply
  ```

### Layout convention

- `private_dot_*` -> deployed at `0600` (secrets, per the chezmoi prefix).
- Encrypted source files carry the `.sops.` infix (`secret.sops.env`); they are
  always ciphertext in the repo and plaintext only at deploy time.
- The real age private key (`~/.config/sops/age/keys.txt`) is intentionally
  **NOT** committed -- back it up out of band. `.chezmoiignore` excludes
  `dot_config/sops/age/`.

### Hermes secrets (env-vars)

Hermes Agent secrets are injected via chezmoi templates (`dot_hermes/env.tmpl`)
from your local environment. Required env vars:

- `DISCORD_BOT_TOKEN`
- `DISCORD_ALLOWED_USERS`
- `MATRIX_HOMESERVER`
- `API_SERVER_KEY`
- `GOOGLE_API_KEY`
- `GITHUB_TOKEN`
- `DISCORD_HOME_CHANNEL`
- `OPENROUTER_API_KEY`
