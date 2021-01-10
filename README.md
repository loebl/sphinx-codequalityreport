# sphinx-codequalityreport

Experimental script to process sphinx warnings and produce a codequality report usable in Gitlab.
The code quality report usually has other uses, but this hijacks this feature to export the 
sphinx warnings as quality notes.

Run sphinx-builder with additional options `-w warn.log -N`

When using the sphinx-quickstart generated Makefile, call make with `make O="-w warn.log -N" html`.

Process the warnings: `./sphinx-report.py warn.log | sed -e "s%$(git rev-parse --show-toplevel)\/%%" > codequality.json`.
The short sed script removes the base path to get correct paths in gitlab.

The report has to be given as artifact in gitlab CI:
```
pages:
  artifacts:
    reports:
      codequality: codequality.json
```
