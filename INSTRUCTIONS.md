# Pushing This Project to GitHub

Step-by-step guide to create a new GitHub repository and push the project.

---

## Prerequisites

- **Git** installed and on your PATH (`git --version` to verify).
- A **GitHub account** at [github.com](https://github.com).
- (Optional) **GitHub CLI** (`gh`) for creating the repo from terminal.

---

## Option A — Create the repo from the browser

1. Go to **github.com → "+" → New repository**.
2. Fill in the details:
   - **Repository name**: `customer-intelligence-platform` (or whatever you prefer)
   - **Description**: `End-to-end customer segmentation and churn prediction platform — ML pipeline, FastAPI backend, React + shadcn/ui dashboard.`
   - **Visibility**: Public (recommended for portfolio) or Private
   - **Do NOT** check "Add a README" or ".gitignore" — we already have both.
3. Click **Create repository**. Copy the repo URL (HTTPS or SSH).

## Option B — Create the repo from terminal (requires GitHub CLI)

```powershell
gh repo create customer-intelligence-platform --public --description "End-to-end customer segmentation and churn prediction platform" --source . --remote origin
```

---

## Initialize Git and Push

Open a terminal in the project root (`c:\Users\rohil\OneDrive\Desktop\resume_project`) and run:

```powershell
# 1. Initialize git
git init

# 2. Add the remote (replace <YOUR_USERNAME> and <REPO_NAME>)
git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git

# 3. Stage all files (the .gitignore will filter out data, models, node_modules, etc.)
git add .

# 4. Verify what's staged — make sure no large data/model files appear
git status

# 5. Create the first commit
git commit -m "Initial commit: ML pipeline, FastAPI API, React + shadcn/ui dashboard"

# 6. Rename default branch to main (if not already)
git branch -M main

# 7. Push to GitHub
git push -u origin main
```

---

## Verify

After pushing, visit your GitHub repo URL and confirm:

- The **README.md** renders correctly on the landing page.
- **No large data files** (CSVs, `.db`) were uploaded.
- **Model files** (`.joblib`, `.pth`) **should** be present — they're small and needed by the backend.
- The `.env` file is **not** visible (secrets stay local).
- `node_modules/` and `__pycache__/` are **not** present.

---

## Updating the Repo Later

```powershell
git add .
git commit -m "describe your changes here"
git push
```

---

## Notes

- **Large data files**: The raw Olist CSVs (~65 MB total) are excluded by `.gitignore`. The trained model files (~570 KB total) are committed since they're needed by the Render backend.
- **Branches**: For future features, create branches with `git checkout -b feature/your-feature` before committing.
- **`.env.example`**: Already included in the repo so collaborators know which environment variables to set up.

---

## Deploy to Production

The project deploys as two services:
- **Frontend** (React + Vite) → Vercel
- **Backend** (FastAPI + ML models) → Render

### Step 1: Deploy the Backend on Render

1. Go to [render.com](https://render.com) and sign up / log in.
2. Click **"New +" → "Web Service"**.
3. Connect your GitHub repo.
4. Configure:
   - **Name**: `customer-intelligence-api`
   - **Environment**: Python 3
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Click **"Create Web Service"** and wait for the build to complete.
6. Copy your Render service URL (e.g., `https://customer-intelligence-api.onrender.com`).
7. Test it: visit `https://your-service.onrender.com/health` — you should see `{"status": "healthy"}`.

### Step 2: Deploy the Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up / log in.
2. Click **"Add New..." → "Project"**.
3. Import your GitHub repo.
4. Configure:
   - **Root Directory**: `frontend`  (click "Edit" to set this)
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add an **Environment Variable**:
   - **Key**: `VITE_API_URL`
   - **Value**: your Render URL from Step 1 (e.g., `https://customer-intelligence-api.onrender.com`)
6. Click **"Deploy"**.

### Step 3: Verify

- Visit your Vercel URL — the dashboard should load.
- Navigate to Executive Overview — it should fetch data from the Render backend.
- First load after inactivity may take 30-60 seconds (Render free tier cold start).

### Updating After Deployment

Both Vercel and Render auto-deploy when you push to `main`:

```powershell
git add .
git commit -m "describe your changes"
git push
```
