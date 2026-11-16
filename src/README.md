# How to update the website

1. Edit the page text in `src/content/*.md`. Publications are in `src/data/publications.json`; the home page numbers, home page news and the list of supervised students are at the top of `src/build.py`.
2. Rebuild the pages: `pip install markdown` then `python3 src/build.py`.
3. Commit and push. GitHub Pages serves the repository root.

The profile photo is `images/profile.jpg` and the downloadable CV is `files/Muhammad_Zeeshan_CV.pdf`.
If the repository or account is renamed, update `SITE_URL` at the top of `src/build.py` and rebuild.

The Inter typeface in `assets/fonts` is under the SIL Open Font License (see `assets/fonts/Inter-LICENSE.txt`).
