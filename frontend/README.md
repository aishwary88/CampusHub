# Frontend Environment & Google Sign-In Setup

This file describes how to configure Google Identity for the frontend during local development.

1) Add your Google client ID

Create `frontend/.env.local` (ignored by git) or set environment variables in your shell. Use the key shown in `frontend/.env.example`:

```
VITE_GOOGLE_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
```

2) Configure Google Cloud OAuth credentials

- In Google Cloud Console, create an OAuth 2.0 Client ID (type: Web application).
- Add your current dev origin to "Authorized JavaScript origins".
  - For example, if Vite starts on port 3004 then use `http://localhost:3004`.
  - If your app runs on another port, use that port instead.

3) Restart the dev server

From the `frontend` directory:

```bash
npm install   # if you haven't already
npm run dev
```

4) Backend / docker notes

- If your backend validates Google tokens using a `GOOGLE_CLIENT_ID` env var, set it in your backend environment (or docker-compose) to the same client ID.
- Example docker-compose env entry:

```yaml
environment:
  - GOOGLE_CLIENT_ID=your-real-client-id.apps.googleusercontent.com
```

5) Troubleshooting

- If you see "The given client ID is not found" or a 403 in the console: ensure the client ID is correct and the origin matches an authorized JS origin in Google Cloud.
- If `VITE_GOOGLE_CLIENT_ID` is not configured, the Google login box will still show but login will be unavailable until the real client ID is provided.
