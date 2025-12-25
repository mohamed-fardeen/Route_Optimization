# Frontend — Route Optimizer

Quick start

1. Install dependencies

```powershell
cd frontend
npm install
```

2. Run the Vite dev server

```powershell
npm run dev
```

The dev server is configured to proxy `/api` to `http://localhost:8000`.

Backend

Make sure the backend is running (from project root):

```powershell
uvicorn app.main:app --reload
```

Notes

- The app uses OpenStreetMap tiles via Leaflet — no API key required.
- If you updated `package.json` to add dependencies, `npm install` will pull them locally.
- To build for production: `npm run build` and serve with `npm run preview` or host the `dist/` output.
