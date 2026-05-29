# Hardware Hub - Frontend

This is the Vue 3 SPA frontend for the Hardware Hub equipment management system.

## Features
- Real-time inventory browsing.
- Admin dashboard for tracking and updating hardware.
- Integration with the FastAPI backend using JWT authentication.

## Development Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` by default and expects the backend to be running on `http://localhost:8000`.

## Production Build

To build for production:

```bash
npm run build
```

You can serve the `dist/` directory via any static file server like Nginx (see the `Dockerfile` for an example).
