# Jira Daily Task Logger

A lightweight browser-based tool to log your daily tasks and push them as subtasks to a Jira parent issue — with live status sync, inline attachments, and screenshot paste support.

Built with plain HTML, CSS, and JavaScript. Hosted on GitHub Pages. Uses a Cloudflare Worker as a proxy to communicate with the Jira REST API.

---

## File Structure

```
├── index.html           # Main app — all UI structure and JavaScript logic
├── style.css            # All visual styling and layout
├── jira-config.js       # Jira field mappings, custom fields, status definitions
├── favicon.ico          # Tab icon (blue J)
├── worker.js            # Cloudflare Worker proxy (deployed separately, not on GitHub Pages)
└── server.py            # Local development proxy (Python, for running on localhost)
```

---

## How It Works

```
Browser (GitHub Pages)
  → POST to Cloudflare Worker
    → Worker adds auth headers
      → Jira REST API
    ← Jira response
  ← Worker forwards response
← App updates UI
```

Your Jira credentials never touch GitHub Pages directly. They are sent to the Cloudflare Worker over HTTPS, forwarded to Jira server-side, and never logged or stored.

---

## Setup — GitHub Pages (Production)

### 1. Deploy the Cloudflare Worker

1. Go to [workers.cloudflare.com](https://workers.cloudflare.com) and sign up (free)
2. Click **Create Worker** → **Edit Code**
3. Paste the contents of `worker.js` into the editor
4. In the `ALLOWED_ORIGINS` array at the top, add your GitHub Pages URL:
   ```js
   var ALLOWED_ORIGINS = [
     'https://yourusername.github.io',
     'http://localhost:8765',
   ];
   ```
5. Click **Deploy**
6. Copy your worker URL — it looks like `https://your-worker.yourname.workers.dev`

### 2. Push to GitHub

Upload these files to your repository root:
```
index.html
style.css
jira-config.js
favicon.ico
```

> `worker.js` and `server.py` do not need to be on GitHub Pages — they run separately.

### 3. Enable GitHub Pages

Go to your repo → **Settings** → **Pages** → set source to **main branch** → Save.

Your app will be live at `https://yourusername.github.io/your-repo/`

### 4. Configure the App

Open your GitHub Pages URL, click the **⚙ settings icon** in the top bar and fill in:

| Field | Example |
|---|---|
| Parent Issue URL | `https://yourcompany.atlassian.net/browse/PROJ-123` |
| Email | `you@company.com` |
| API Token | Your Atlassian API token (see below) |
| Proxy URL | Your Cloudflare Worker URL |

To generate a Jira API token: [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

Click **Test Connection** to verify, then **Save & Connect**.

---

## Setup — Local Development

If you want to run and develop the app locally without Cloudflare:

### Requirements
- Python 3.x

### Steps

1. Clone the repo
2. Run the local proxy server:
   ```bash
   python server.py
   ```
3. Open your browser at:
   ```
   http://localhost:8765/index.html
   ```
4. In the app's ⚙ config, set Proxy URL to:
   ```
   http://localhost:8765/jira-proxy
   ```

The Python server serves the static files and proxies all Jira API calls, bypassing CORS locally.

---

## Customising Jira Fields

Edit `jira-config.js` to match your Jira project:

```js
const JIRA_CONFIG = {

  // Change issue type if needed
  issueType: 'Subtask',

  // Summary prefix format
  summaryFormat: '[{date}] {summary}',

  // Statuses shown in the dropdown
  statuses: [
    { jiraName: 'To Do',       label: 'To Do',        color: '#aaaaaa', cssClass: 'todo' },
    { jiraName: 'In Progress', label: 'In Progress',  color: 'var(--accent)', cssClass: 'inprogress' },
    { jiraName: 'Done',        label: 'Done',         color: 'var(--green)', cssClass: 'done' },
  ],

  // Custom fields — add your project's custom field IDs here
  customFields: {
    // customfield_10016: 1,           // Story Points
    // customfield_10020: { id: 123 }, // Sprint
  },
};
```

To find your custom field IDs, call:
```
GET https://yourcompany.atlassian.net/rest/api/3/field
```

---

## Features

- **Quick task logging** — type a task and press Enter to queue it
- **Push to Jira** — create subtasks under your parent issue with one click, auto-assigned to you
- **Live status sync** — sync button pulls latest subtask statuses from Jira
- **Status updates** — click the status pill on any task to transition it in Jira (To Do → In Progress → Done)
- **Inline attachments** — drag & drop, browse, or paste screenshots directly with Ctrl+V
- **Auto-assignee** — subtasks are automatically assigned to you on creation
- **Custom fields** — define once in `jira-config.js`, applied to every new subtask
- **Daily scope** — tasks are stored per day in sessionStorage, fresh slate each morning

---

## What You Can Learn From This Repo

### REST APIs
Jira exposes its functionality through a REST API — a standard pattern where you use HTTP verbs to interact with resources:
- `GET /rest/api/3/issue/PROJ-123` — read an issue
- `POST /rest/api/3/issue` — create an issue
- `POST /rest/api/3/issue/PROJ-123/transitions` — change its status

You learned to read API documentation, construct request bodies, handle responses, and deal with errors.

### CORS (Cross-Origin Resource Sharing)
Browsers enforce a security policy that blocks websites from calling APIs on other domains unless that API explicitly allows it. Jira does not allow arbitrary browser origins, which is why a direct call from GitHub Pages fails.

Understanding CORS is essential for any frontend developer working with external APIs.

### Proxy / Middleware Pattern
The Cloudflare Worker is a proxy — it sits between two systems and forwards requests. This is a fundamental pattern in web architecture used everywhere: API gateways, load balancers, authentication layers, and rate limiters all use the same concept.

The key insight: **servers can call other servers freely**. CORS only restricts browsers. So by adding a server-side step (the Worker), you bypass the restriction cleanly.

### Serverless Functions
The Cloudflare Worker is a serverless function. You wrote backend logic without provisioning or managing any server. It runs on-demand, scales automatically, and costs nothing at low usage. This is the same concept as AWS Lambda, Vercel Edge Functions, and Netlify Functions.

### Authentication — Basic Auth
Jira Cloud uses HTTP Basic Authentication. You send `email:api_token` encoded as base64 in an `Authorization` header on every request. Understanding how auth headers work is foundational to calling any protected API.

### Frontend Architecture — Separation of Concerns
The project is deliberately split across files:
- **Structure** (`index.html`) — what exists on the page
- **Style** (`style.css`) — how it looks
- **Config** (`jira-config.js`) — what is specific to your environment
- **Logic** (inline JS in `index.html`) — how it behaves

This separation makes the project easier to maintain and extend.

### Browser APIs
- **sessionStorage** — temporary per-tab key-value storage, used here to persist config and tasks
- **FileReader / Blob** — reading local files and converting them to base64 for upload
- **Clipboard API** — intercepting paste events to capture screenshots directly from the clipboard
- **Fetch API** — making HTTP requests from the browser

### GitHub Pages + Static Hosting
You learned that static hosting (HTML/CSS/JS with no server) is free, fast, and sufficient for many tools — as long as any server-side needs are handled by an external service like a Cloudflare Worker.

---

## Why Not Build Without the Worker?

The browser's CORS policy means you cannot call Jira's API directly from a static page. Alternatives exist (GitHub Actions, OAuth flows) but all require some server-side component. The Cloudflare Worker is the simplest and most transparent solution — free tier supports up to 100,000 requests per day.
