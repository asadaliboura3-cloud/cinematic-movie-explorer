import os
import requests
import streamlit as st

st.set_page_config(
    page_title="CineVerse | Movies, Series & Anime",
    page_icon="🎬",
    layout="wide",
)

TMDB_BASE = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def get_token():
    try:
        return st.secrets.get("TMDB_READ_ACCESS_TOKEN", "")
    except Exception:
        return os.getenv("TMDB_READ_ACCESS_TOKEN", "")

TOKEN = get_token()

st.markdown("""
<style>
.stApp { background: #101014; color: #f5f5f5; }
section[data-testid="stSidebar"] { background: #19191f; }
.hero {
  padding: 1.5rem 1.7rem; border-radius: 18px;
  background: linear-gradient(120deg, #29213b, #17171d 70%);
  border: 1px solid #383344; margin-bottom: 1rem;
}
.brand { color: #ffca28; font-size: 2.2rem; font-weight: 800; }
.muted { color: #b9bac5; }
div[data-testid="stImage"] img { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

def tmdb_get(path, params=None):
    if not TOKEN:
        return {"results": [], "error": "Missing API token"}
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "accept": "application/json",
    }
    try:
        response = requests.get(
            f"{TMDB_BASE}{path}", headers=headers,
            params=params or {}, timeout=20
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"results": [], "error": str(exc)}

def get_items(kind, query="", language="en-US", page=1):
    if query.strip():
        path = f"/search/{kind}"
        params = {
            "query": query.strip(),
            "language": language,
            "include_adult": "false",
            "page": page,
        }
    else:
        path = "/movie/popular" if kind == "movie" else "/tv/popular"
        params = {"language": language, "page": page}
    return tmdb_get(path, params)

def get_anime(query="", language="en-US"):
    # TV search/popular results filtered using genre and original language.
    # Anime availability in TMDB metadata varies by title.
    data = get_items("tv", query=query, language=language)
    if data.get("error"):
        return data
    results = data.get("results", [])
    filtered = []
    for item in results:
        genre_ids = item.get("genre_ids", [])
        original_language = item.get("original_language", "")
        # Animation genre is 16; Japanese/Korean/Chinese originals are common,
        # but this is a discovery filter, not a complete anime catalogue.
        if 16 in genre_ids or original_language in ("ja", "zh", "ko"):
            filtered.append(item)
    data["results"] = filtered
    return data

def card_grid(items, kind):
    if not items:
        st.info("No titles found. Try another search or language.")
        return
    cols_per_row = 5
    for start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, item in zip(cols, items[start:start + cols_per_row]):
            title = item.get("title") or item.get("name") or "Untitled"
            date = item.get("release_date") or item.get("first_air_date") or ""
            rating = item.get("vote_average")
            poster_path = item.get("poster_path")
            with col:
                if poster_path:
                    st.image(IMAGE_BASE + poster_path, use_container_width=True)
                else:
                    st.markdown("🎞️ **Poster unavailable**")
                st.markdown(f"**{title}**")
                st.caption(f"{date[:4] if date else 'Year unknown'} · ⭐ {rating:.1f}" if isinstance(rating, (int, float)) else (date[:4] if date else "Year unknown"))
                with st.expander("Details"):
                    overview = item.get("overview") or "No description available."
                    st.write(overview)
                    st.caption(f"Original language: {item.get('original_language', 'unknown')}")
                    item_id = item.get("id")
                    if item_id:
                        details_kind = "movie" if kind == "movie" else "tv"
                        if st.button("Find trailer", key=f"trailer-{details_kind}-{item_id}-{kind}"):
                            videos = tmdb_get(f"/{details_kind}/{item_id}/videos")
                            video = next((v for v in videos.get("results", []) if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser")), None)
                            if video:
                                st.markdown(f"[Open trailer on YouTube](https://www.youtube.com/watch?v={video['key']})")
                            else:
                                st.caption("No trailer listed in TMDB for this title.")
                    key = f"{kind}-{item.get('id')}"
                    if st.button("＋ Add to watchlist", key=f"watch-{key}"):
                        st.session_state.watchlist[key] = {
                            "title": title, "year": date[:4],
                            "kind": kind, "id": item.get("id")
                        }
                        st.toast(f"Added {title} to your watchlist")

if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}

with st.container():
    st.markdown("""
    <div class="hero">
      <div class="brand">CINEVERSE 🎬</div>
      <div style="font-size:1.1rem">Discover movies, series and anime from around the world.</div>
      <div class="muted">Movie information, posters, release dates and ratings in one place.</div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("Explore")
    section = st.radio("Choose a section", ["Home", "Movies", "Series", "Anime", "My Watchlist"])
    st.divider()
    st.caption("Language filters use TMDB metadata. Not every title is available in every language.")

language_options = {
    "All / English interface": "en-US",
    "English": "en-US",
    "Punjabi": "pa-IN",
    "Urdu": "ur-PK",
    "Hindi": "hi-IN",
    "Korean": "ko-KR",
    "Japanese": "ja-JP",
    "Chinese": "zh-CN",
}
language_label = st.selectbox("Preferred display language", list(language_options.keys()))
api_language = language_options[language_label]
query = st.text_input("Search titles", placeholder="e.g. Punjabi film, anime, action, drama...")
search_clicked = st.button("Search", type="primary")

if not TOKEN:
    st.warning("Add your TMDB API token in Streamlit Secrets before using live movie data.")
    st.code('TMDB_READ_ACCESS_TOKEN = "paste_your_TMDB_API_read_access_token_here"', language="toml")
    st.markdown("[Get API access from TMDB](https://developer.themoviedb.org/docs/getting-started)")

if section == "My Watchlist":
    st.subheader("❤️ My Watchlist")
    if st.session_state.watchlist:
        for key, item in list(st.session_state.watchlist.items()):
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{item['title']}** · {item['year']} · {item['kind'].title()}")
            if c2.button("Remove", key=f"remove-{key}"):
                del st.session_state.watchlist[key]
                st.rerun()
    else:
        st.info("Your watchlist is empty. Add titles from Movies, Series or Anime.")
elif section == "Home":
    st.subheader("🔥 Popular Movies")
    movies = get_items("movie", language=api_language)
    if movies.get("error"):
        st.error("Could not load titles. Check your API token and internet connection.")
    else:
        card_grid(movies.get("results", [])[:10], "movie")
    st.subheader("📺 Popular Series")
    shows = get_items("tv", language=api_language)
    if shows.get("error"):
        st.error("Could not load series.")
    else:
        card_grid(shows.get("results", [])[:10], "tv")
    st.subheader("🍥 Anime discovery")
    anime = get_anime(language=api_language)
    if not anime.get("error"):
        card_grid(anime.get("results", [])[:10], "tv")
elif section == "Movies":
    st.subheader("🎬 Movies")
    data = get_items("movie", query=query if search_clicked or query else "", language=api_language)
    if data.get("error"):
        st.error("Could not load movies. Check your API token.")
    else:
        card_grid(data.get("results", [])[:20], "movie")
elif section == "Series":
    st.subheader("📺 Series")
    data = get_items("tv", query=query if search_clicked or query else "", language=api_language)
    if data.get("error"):
        st.error("Could not load series. Check your API token.")
    else:
        card_grid(data.get("results", [])[:20], "tv")
elif section == "Anime":
    st.subheader("🍥 Anime discovery")
    data = get_anime(query=query if search_clicked or query else "", language=api_language)
    if data.get("error"):
        st.error("Could not load anime. Check your API token.")
    else:
        card_grid(data.get("results", [])[:20], "tv")

st.divider()
st.caption("Movie data and images are provided by TMDB. This independent project is not endorsed or certified by TMDB. It provides discovery information, not full movie streaming or downloads.")
