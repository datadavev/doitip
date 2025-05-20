# doitip

`doitip` is a python tool for exploring DOIs.

```
$ doi
Usage: doi [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  info      Show the registration info for a DOI.
  meta      Try and retrieve registered metadata for doi.
  prefixes  List prefixes registered by a Registration Agency.
  ra        Show the Regitration Agency for a DOI.
  ras       List Registration Agencies known to this tool.
  resolve   Resolve a DOI, showing the targets on the way.
```


## Dev notes

Release process:

0. Do stuff. When complete, then next steps.
1. `uvx --from=toml-cli toml set --toml-path=pyproject.toml project.version $NEWVERSION`
2. `uv sync` to ensure versions up to date
3. `pytest`
4. Commit changes
5. Push
