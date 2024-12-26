# Merge LaTeX

Iteratively search for and merge both `\include` and `\input` commands into the main LaTeX file. Available at <https://merge-latex.vercel.app/>.

> [!WARNING]  
> Current implementation didn't add new page on `\include` yet. Will be added if there is request for it.

## Run locally

Run:

```shell
uvicorn api.main:app --reload
```

Then the page will be displayed at `http://localhost:8000/` and the swagger at `http://localhost:8000/docs`.
