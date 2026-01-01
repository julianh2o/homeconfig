# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository manages Home Assistant configuration files synced from a remote server at `192.168.0.110:/config/`. It serves as version control and local backup for a Home Assistant installation.

## Commands

### Configuration Sync

**Pull configuration from remote server:**
```bash
npm run pull
```
Downloads the latest configuration from `192.168.0.110:/config/` using rsync. Files matching patterns in `.rsyncignore` are excluded (databases, logs, cache, hidden files/folders, etc.).

**Push local changes to remote server:**
```bash
npm run push
```
Uploads local configuration changes to the remote Home Assistant server using rsync with the same exclusions.

### Home Assistant Control

These commands require the `HA_TOKEN` environment variable to be set with a Home Assistant long-lived access token.

**Reload YAML configuration:**
```bash
npm run reload
```
Triggers Home Assistant to reload YAML configuration files without restarting. Use after pushing configuration changes.

**Restart Home Assistant:**
```bash
npm run restart
```
Triggers a full Home Assistant restart. Required for some configuration changes.

**View logs:**
```bash
npm run logs          # Show last 100 lines
npm run logs:follow   # Follow logs in real-time
```
Displays Home Assistant logs from the remote server via SSH.

**Get all entity states:**
```bash
npm run status        # Concise output (recommended for quick inspection)
npm run states        # Full detailed output with timestamps
```
Retrieves and displays the current state of all entities/sensors from Home Assistant using the REST API. The `status` command shows a clean view with just entity IDs, states, and attributes. Use `states` for the full output including timestamps and context.

### Setting up HA_TOKEN

Create a long-lived access token in Home Assistant:
1. Go to your Home Assistant profile (click your username in the sidebar)
2. Scroll to "Long-Lived Access Tokens" and create a new token
3. Set the token as an environment variable:
   ```bash
   export HA_TOKEN="your_token_here"
   ```
   Or add it to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.)

## Architecture

### Configuration Structure

Home Assistant uses a split configuration approach:

- `config/configuration.yaml` - Main configuration file that includes other YAML files
- `config/automations.yaml` - All automation rules
- `config/scripts.yaml` - Script definitions
- `config/scenes.yaml` - Scene configurations
- `config/secrets.yaml` - Sensitive values (gitignored)

### Key Directories

- `config/esphome/` - ESPHome device configurations for ESP32/ESP8266 devices
- `config/blueprints/` - Reusable automation/script templates organized by type
- `config/custom_components/` - Custom integrations (HACS installations excluded from sync)

### Sync Behavior

The `.rsyncignore` file excludes:
- Database files (`*.db`, `*.db-shm`, `*.db-wal`)
- Logs (`*.log`, `*.log.*`)
- Compressed files (`*.gz`)
- Hidden files and directories (`.*`)
- Python cache (`__pycache__/`)
- TTS audio cache (`tts/`)
- HACS custom component files (`custom_components/hacs/`)

When making changes to sync behavior, update `.rsyncignore` rather than modifying the rsync command directly.
