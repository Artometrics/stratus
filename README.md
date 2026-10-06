# Stratus

**Stratus** is Rainfall Health's data intelligence, research, and interactive reporting platform for the CMS Transforming Episode Accountability Model (TEAM) and bundled payments.

- **Production Live URL (Firebase)**: [https://stratus-510519.web.app](https://stratus-510519.web.app)
- **GitHub Repository**: [https://github.com/Artometrics/stratus](https://github.com/Artometrics/stratus)
- **GitHub Pages**: [https://artometrics.github.io/stratus/](https://artometrics.github.io/stratus/)

---

## Running in Cursor

To open and run the project in **Cursor**:

1. Open the folder `~/Desktop/stratus` in Cursor (`File > Open Folder...`).
2. When prompted, install recommended extensions (`quarto.quarto`, `REditorSupport.r`, `esbenp.prettier-vscode`).
3. Open a terminal in Cursor (`Ctrl + \`` or `Cmd + \``) and run:

```bash
# Start the local hot-reloading development preview
npm run preview
# (or: quarto preview)
```

The browser will open with the full Stratus platform running locally.

---

## Available Commands

| Command | Description |
|---------|-------------|
| `npm run preview` | Runs the Quarto local development server with instant reload |
| `npm run build` | Compiles the full static site into `_site/` |
| `npm run convert` | Re-runs the article conversion script (`tools/convert_articles.py`) |
| `npm run deploy` | Deploys the built static site to Firebase Hosting |

---

## Platform Structure

```
stratus/
├── _quarto.yml              # Quarto website configuration and navbar
├── index.qmd                # Stratus homepage
├── media.qmd                # Filterable media index matching corporate UI
├── articles/                # 48+ converted 2-column research articles
├── states/                  # State-level whitepapers (California, New York, Florida, etc.)
│   └── california/          # Includes interactive audio listen-along player
├── regions/                 # Regional briefings (Northeast, South & Midwest, etc.)
├── newsletter/              # Investigative briefs and CJR market analysis
├── assets/                  # Media banners, author portraits, and brand SVGs
├── styles/                  # stratus-media.css (Rainfall Health corporate design system)
└── tools/                   # Automation scripts (convert_articles.py, link_report_assets.sh)
```

---

## Deployment

- **Firebase Hosting**: Run `npm run deploy` to publish changes to Firebase CDN edge nodes.
- **GitHub Pages**: Pushes to `main` automatically trigger `.github/workflows/deploy.yml` to build and deploy to GitHub Pages.
