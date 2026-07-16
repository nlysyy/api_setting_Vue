# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Vue 3 single-page application** for managing AI API service configurations (DeepSeek, OpenAI, Claude, Gemini, 通义千问). Users can select a provider, enter API credentials, configure models and temperature, test connections, and persist settings. Deployed to GitHub Pages.

## Commands

```sh
npm install          # Install dependencies
npm run dev          # Start Vite dev server with HMR
npm run build        # Type-check + production build (runs vue-tsc and vite build)
npm run build-only   # Vite build only (skip type-checking)
npm run type-check   # Run vue-tsc type checking only
npm run preview      # Preview the production build locally
```

- **Node requirement**: `^22.18.0 || >=24.12.0`

## Architecture

```
src/
├── main.ts                  # App entry: creates Vue app, installs Pinia + Router
├── App.vue                  # Root component: layout, theme CSS vars, global toast, help modal
├── router/index.ts          # Vue Router (empty routes — SPA, no navigation)
├── stores/configStore.ts    # Single Pinia store: all state + localStorage persistence
└── components/
    ├── AppBar.vue           # Top bar: back button, title, theme toggle, help button
    ├── StatusCard.vue       # Shows validation status (configured / incomplete)
    ├── ProviderSelect.vue   # Dropdown to pick AI provider (switches store state)
    ├── ApiConfigInputs.vue  # Endpoint URL + API key inputs (conditionally shown per provider)
    ├── ModelConfig.vue      # Model selection: fetch from API or manual input; per-provider fetch logic
    ├── TemperatureSlider.vue# Collapsible temperature slider (0.0–2.0) with color-coded labels
    └── ActionButtons.vue    # Test connection, save config, clear config with confirmation dialog
```

### Key Patterns

- **All global styles** live in `App.vue`'s `<style>` block (no separate CSS files). Component `<style scoped>` blocks are used sparingly or left empty.
- **Theme system**: CSS custom properties defined on `:root` (light) and `[data-theme="dark"]` (dark). The toggle in `AppBar.vue` sets the `data-theme` attribute on `<html>`.
- **State management**: Single Pinia store (`useConfigStore`) using the composition API style (`defineStore('config', () => { ... })`). All provider definitions (`PROVIDERS`) are hardcoded in the store.
- **localStorage persistence**: Config saved/loaded under key `api_config`. `loadFromStorage()` is called in `App.vue`'s `onMounted`.
- **Toast notifications**: `window.showToast(message, type)` — exposed globally from `App.vue` by attaching it to the `window` object. Creates a DOM element directly on `document.body`. ModelConfig.vue also has its own local toast implementation.
- **Model fetching**: `ModelConfig.vue` contains per-provider `fetch*Models()` functions that call real provider APIs (OpenAI-compatible `/models` endpoints, Anthropic Messages API validation, Gemini models endpoint). Falls back to manual input mode on failure.
- **Connection testing**: `ActionButtons.vue` sends a minimal chat completions request to verify credentials. Uses OpenAI-compatible format with Bearer auth.
- **Path alias**: `@` → `./src` (configured in both `vite.config.ts` and `tsconfig.app.json`).
- **No tests exist** in this project.

### Deployment

The GitHub Actions workflow (`.github/workflows/static.yml`) deploys the entire repository to GitHub Pages on pushes to `main`. The `base` in `vite.config.ts` is set to `/api_setting_Vue/` to match the repository name. The workflow uploads the root directory (not just `dist/`), so `index.html` at the repo root serves as the entry point.
