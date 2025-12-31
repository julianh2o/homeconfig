# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository manages Home Assistant configuration files synced from a remote server at `192.168.0.110:/config/`. It serves as version control and local backup for a Home Assistant installation.

## Commands

### Sync Configuration from Remote Server

```bash
npm run pull
# or
yarn pull
```

Pulls the latest configuration from the remote Home Assistant server using rsync. Files matching patterns in `.rsyncignore` are excluded (databases, logs, cache, hidden files/folders, etc.).

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
