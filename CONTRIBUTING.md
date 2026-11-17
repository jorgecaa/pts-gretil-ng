# Contributing

## Reporting an error in the text

Open an issue with the form «Error in the text» (Issues → New issue). It asks for:

- the volume, page and line (the line numbers are in the left margin of each page);
- what the page shows and what the printed PTS edition prints, if you have checked it;
- whether the word carries a mark (green: a transcription correction; orange dotted: a PTS correction
  of the edition, applied; red: braces in GRETIL).

`corrections.json` is not edited by hand here: it is exported from the corrections layer of the
foureditions project (not public), where every correction is checked against the scan and approved. A reported
error is reviewed there and reaches this repository with the next export.

## Changes to `build.py`

Pull requests are welcome. The build must stay deterministic: after `python3 build.py`, `git status`
must show no change in `corrected/` or `index.html` unless the change is meant to alter them, in
which case the rebuilt files go in the same pull request. The check in `.github/workflows/build.yml`
runs on every pull request.
