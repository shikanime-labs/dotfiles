# Chezmoi + sops secret encryption

This repo manages secrets with **chezmoi hooks that shell out to `sops`** (age
backend). chezmoi 2.72.0 has no native `.sops` auto-decryption, so the
`pre-apply`/`post-apply` hooks under `.chezmoihooks/` decrypt `.sops.*` files
before chezmoi deploys them and re-encrypt afterward, so the repo only ever
holds ciphertext.

## One-time local setup (per machine, NOT committed)

1. Install the toolchain:
   ```sh
   scoop install chezmoi sops age
   ```
2. Generate an age keypair (the private key is yours alone):
   ```sh
   age-keygen -o C:/Users/<you>/.config/sops/age/keys.txt
   # record the public key:  age-keygen -y C:/Users/<you>/.config/sops/age/keys.txt
   ```
3. Add your age **public** key to `.sops.yaml` (`age:` field) so you can decrypt.
4. Tell sops where the private key is. On Windows the `sops` binary resolves
   `~/.config` via `%APPDATA%`, not the MSYS `$HOME`, so set the native path:
   ```sh
   export SOPS_AGE_KEY_FILE="C:/Users/<you>/.config/sops/age/keys.txt"
   ```
   The hooks set this default automatically; export it for manual `sops` use.
5. Create `~/.config/chezmoi/chezmoi.toml`:
   ```toml
   sourceDir = "C:/path/to/this/repo"
   ```

## Workflow

- Add a new secret (encrypt on write, commit the ciphertext):
  ```sh
  printf 'TOKEN=...\n' > private_dot_foo/secret.env
  sops --encrypt --config .sops.yaml private_dot_foo/secret.env > private_dot_foo/secret.sops.env
  rm -f private_dot_foo/secret.env
  git add private_dot_foo/secret.sops.env
  ```
- Apply (hooks decrypt → chezmoi deploys → hooks re-encrypt):
  ```sh
  chezmoi apply
  ```
- Edit an encrypted secret:
  ```sh
  sops -d private_dot_foo/secret.sops.env   # read
  sops -e -i private_dot_foo/secret.sops.env # edit in place (opens $EDITOR)
  ```

## Layout convention

- `private_dot_*` → deployed at `0600` (secrets, per the chezmoi prefix).
- Encrypted source files carry the `.sops.` infix (`secret.sops.env`); they are
  always ciphertext in the repo and plaintext only at deploy time.
- The real age private key (`~/.config/sops/age/keys.txt`) is intentionally
  **NOT** committed — back it up out of band. `.chezmoiignore` excludes
  `dot_config/sops/age/`.

## Verified round-trip

`sops -d private_dot_ssh/secrets.sops.env` returns the example plaintext
(`EXAMPLE_SOPS_SECRET=...`). Confirmed in this repo on 2026-08-22 with
`sops 3.13.3`, `age 1.3.1`, `chezmoi 2.72.0` on Windows.
