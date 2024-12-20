# Merge LaTeX

Iteratively search for and merge both `\include` and `\input` commands into the main LaTeX file.

## Run locally

Run:

```shell
uvicorn api.main:app --reload
```

Then the page will be displayed at `http://localhost:8000/` and the swagger at `http://localhost:8000/docs`.
