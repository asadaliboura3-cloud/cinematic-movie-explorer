# CineVerse — Movies, Series & Anime Explorer

A beginner-friendly Streamlit project using Python and the TMDB API. It can be stored on GitHub and deployed with Streamlit Community Cloud. Kaggle can be used separately to explore public datasets and experiment with recommendation models.

## Features
- Popular movies and TV series
- Search titles
- Language/display-language selection
- Posters, summaries, release years and ratings
- Basic anime discovery filter
- Session-based watchlist
- Find trailer links when TMDB lists a YouTube trailer
- Responsive Streamlit layout

## 1. Get a TMDB API token
Follow the official TMDB getting-started instructions: https://developer.themoviedb.org/docs/getting-started

Do not commit your token to GitHub.

## 2. Run locally (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the local URL shown in your terminal.

## 3. Upload to GitHub
Create a repository named `cineverse-movie-explorer`. Upload `app.py`, `requirements.txt`, and `README.md`. Do not upload your API token.

## 4. Deploy on Streamlit Community Cloud
1. Open https://share.streamlit.io/
2. Sign in with GitHub.
3. Choose **Create app**, then select your repository and `app.py`.
4. In **Advanced settings → Secrets**, add:
   ```toml
   TMDB_READ_ACCESS_TOKEN = "YOUR_PRIVATE_TMDB_READ_ACCESS_TOKEN"
   ```
5. Deploy.

Official deployment guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy

## 5. What Kaggle does
Kaggle is useful for downloading permitted datasets and experimenting with recommendation models. It does not automatically host this Streamlit website. Keep Kaggle notebooks/data work separate; use GitHub as the project source and Streamlit Community Cloud for the public app.

## Notes
- TMDB API results, language translations and posters depend on the TMDB database and API rules.
- Language selection affects metadata/display language and is not a guarantee that a title is originally produced in that language.
- The Anime section is a simple discovery filter, not a complete anime database.
- This app does not host copyrighted movie files or provide unauthorized downloads.
- The watchlist is kept in the current Streamlit session; it is not a permanent account database.
