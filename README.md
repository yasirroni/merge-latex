# Merge LaTeX

Iteratively search for and merge both `\include` and `\input` commands into the main LaTeX file.

## Run locally

uvicorn api.main:app --reload

html on pages/index.html

{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/main.py"
    }
  ]
}