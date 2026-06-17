// API configuration for TeamMatch AI
// When deploying the static frontend to Vercel, requests to relative '/api' paths fail
// because Vercel doesn't run the Python backend.
// Prepending API_BASE resolves this:
// - Local dev (Vite proxy): Uses relative path ("")
// - Production (Vercel): Points directly to the local backend ("http://localhost:5000") or your hosted Render/Railway URL.

export const API_BASE = import.meta.env.PROD
  ? "https://teammatch-ai.onrender.com"
  : "";
