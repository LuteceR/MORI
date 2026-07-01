# Nuxt Server guide

[![Nuxt UI](https://img.shields.io/badge/Made%20with-Nuxt%20UI-00DC82?logo=nuxt&labelColor=020420)](https://ui.nuxt.com)

## Setup
Install pnpm
```bash [Terminal]
npm install -g pnpm@latest-11
```

Make sure to install the dependencies:

```bash
pnpm install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
pnpm dev
```
With LAN availability 
```bash
pnpm dev -- --host
```

## Production

Build the application for production (app will be built in .output folder):

```bash
pnpm build
```
To run production server in LAN
```bash
HOST=0.0.0.0 PORT=3000 node .output/server/index.mjs
```
Locally preview production build:

```bash
pnpm preview
```
