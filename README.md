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

## Tips

### Zip

If you use GitHub and want to zip your LaTeX repo, you can use this command:

```shell
git grep --cached -l "" | zip -r -v ${1:-gitzip}.zip -@
```

Source: [GitHub Gist](<https://gist.github.com/yasirroni/c533b78ae59b8a7282a0f640113241f1>).

## TODO

### Support add new page on `\include`

```tex
\newpage
```

### Support `\input@path`

```tex
\makeatletter
\def\input@path{
    {../data/}
    {./chapters/}
    {./sections/}
}
\makeatother
```
