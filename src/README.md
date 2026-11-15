# How to update the website

1. Edit the page text in `src/content/*.md` (for example `index.md` for the home page and news, `publications.md` for papers).
2. Rebuild the pages: `pip install markdown` then `python3 src/build.py`.
3. Commit and push. GitHub Pages serves the repository root.

The profile photo is `images/profile.jpg` and the downloadable CV is `files/Muhammad_Zeeshan_CV.pdf`.
If the repository or account is renamed, update `SITE_URL` at the top of `src/build.py` and rebuild.

Styling is from the [AcademicPages](https://github.com/academicpages/academicpages.github.io) theme (MIT licence, see `LICENSE-AcademicPages`).
