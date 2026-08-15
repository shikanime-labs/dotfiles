# Dotfiles

Personal dotfiles and system configurations managed via Nix and chezmoi.

**Language:** Nix

## Structure

- `home/` — Home-manager modules
- `hosts/` — Host-specific NixOS configurations
- `modules/` — Shared Nix modules

## Commit Style

- Plain-text capitalized title, no conventional-commit prefix
- Body with labels: `Design:`, `Related:`, `Closes #`
- Keep Markdown lines wrapped at 80 columns and run `nix fmt` before shipping
