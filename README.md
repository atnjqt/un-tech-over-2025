# UN Tech-Over 2025 Hackathon

Sample Dashboard for the [UN Tech-Over 2025 Hackathon](https://www.un.org/digital-emerging-technologies/content/open-source-week-2025).

Explores applications of `giga-spatial` for OSM handler paired with HDX handler / UNCHR data

## Setup

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install flask giga-spatial
pip install folium matplotlib mapclassify
```

- to avoid spamming APIs, save some data locally:
- `./data/unhcr/camps_raster.tif`
- `./data/unhcr/...`

## Development

- Local Flask app with necessary API keys set as environment variables:

```bash
export GEOREPO_API_KEY="lAG..."
export GEOREPO_USER_EMAIL="jacquot.etienne@gmail.com"
python application.py
```
- [127.0.0.1:8000/](http://127.0.0.1:8000/)

## Deployment

- A sample [Dockerfile](./Dockerfile) is provided for development purposes, as the project is currently not production-ready beyond MacOS Python 3.10.


## Disclaimer on AI Tools

This repository was quickly bootstrapped together using generative AI tools such as VSCode Copilot, and as such is for demonstrative and development purposes fit for leaarning in a hackathon context.