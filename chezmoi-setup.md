# Chezmoi secret encryption (native age)

This repo manages secrets with **chezmoi's native age encryption** (not sops —
chezmoi 2.72.0 has no sops backend; verified against source). Age is the same
encryption engine sops uses, so the security model is equivalent and the
existing `~/.config/sops/age/keys.txt` age key is reused.

## One-time local setup (per machine, NOT committed)

Create `~/.config/chezmoi/chezmoi.toml`:

```toml
encryption = "age"
sourceDir = "<path to this repo checkout>"

[age]
  # your age PUBLIC key (age-keygen -y ~/.config/sops/age/keys.txt)
  recipient = "age1...your-public-key..."
  # local private key used to decrypt on apply
  identity = "~/.config/sops/age/keys.txt"
```

The recipient is public and safe to share; the identity path points only at
your local private key and is never committed.

## Workflow

- Add a new secret (encrypted on write):
  ```sh
  chezmoi add --encrypt ~/.config/some/secret.json
  ```
- Edit an encrypted file:
  ```sh
  chezmoi edit-encrypted dot_config/some/secret.json
  ```
- Apply to your home (chezmoi decrypts transparently):
  ```sh
  chezmoi apply
  ```

## Layout convention

- `private_dot_*` → deployed at `0600` (secrets, per the chezmoi prefix).
- Encrypted source files keep the `private_dot_*` name; chezmoi stores the
  age ciphertext in the repo and decrypts on `apply`.
- The real age private key (`~/.config/sops/age/keys.txt`) is intentionally
  **NOT** committed — back it up out of band. `.chezmoiignore` excludes
  `dot_config/sops/`.

## Verified round-trip

`chezmoi encrypt <file> -o <file>` → age ciphertext; `chezmoi decrypt <file>`
→ original plaintext. Confirmed in this repo on 2026-08-22.
