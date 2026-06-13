import streamlit as st
import pickle
import requests
import os

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

@st.cache_resource
def load_data():
    movies     = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

try:
    movies, similarity = load_data()
except FileNotFoundError as e:
    st.error(
        f"Could not find pickle file: **{e.filename}**\n\n"
        "Make sure `movie_list.pkl` and `similarity.pkl` are in the same "
        "directory as `app.py`. Run the notebook first to generate them."
    )
    st.stop()

movie_list = movies["title"].values

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id: int, title: str) -> str | None:
    if TMDB_API_KEY:
        try:
            url  = (f"https://api.themoviedb.org/3/movie/{movie_id}"
                    f"?api_key={TMDB_API_KEY}&language=en-US")
            data = requests.get(url, timeout=5).json()
            path = data.get("poster_path")
            if path:
                return f"https://image.tmdb.org/t/p/w500{path}"
        except Exception:
            pass
    try:
        url  = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2dca580c2a14b55200e784d157207b4d"
        data = requests.get(url, timeout=5).json()
        path = data.get("poster_path")
        if path:
            return f"https://image.tmdb.org/t/p/w500{path}"
    except Exception:
        pass
    return None

def poster_placeholder(title: str) -> str:
    return (
        f"<div style='background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);"
        f"border-radius:10px;height:270px;display:flex;align-items:center;"
        f"justify-content:center;padding:12px;text-align:center;border:1px solid #333;'>"
        f"<span style='color:#eee;font-size:14px;font-weight:600;'>🎬<br><br>{title}</span></div>"
    )

def recommend(movie: str, n: int = 5):
    idx       = movies[movies["title"] == movie].index[0]
    distances = sorted(
        enumerate(similarity[idx]), key=lambda x: x[1], reverse=True
    )
    recs = []
    for i, _ in distances[1 : n + 1]:
        row = movies.iloc[i]
        recs.append({"title": row["title"], "movie_id": int(row["movie_id"])})
    return recs

st.markdown("""
<style>
    .movie-title {
        font-size: 14px;
        font-weight: 600;
        margin-top: 8px;
        text-align: center;
        min-height: 40px;
    }
    .list-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .list-rank {
        background: #e50914;
        color: white;
        border-radius: 50%;
        min-width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        font-weight: 700;
    }
    .list-title {
        color: #f0f0f0;
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("Movie Recommender")
st.markdown(
    "Pick a movie you love and get content-based recommendations "
)

c1, c2, c3 = st.columns([3, 1, 1])

with c1:
    selected_movie = st.selectbox(
        "Search or select a movie",
        movie_list,
        index=None,
        placeholder="e.g. The Dark Knight…",
    )
with c2:
    n_recs = st.slider("How many recs?", min_value=3, max_value=10, value=5)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)  
    show_posters = st.toggle("Show Posters", value=True)

st.divider()

if selected_movie:
    with st.spinner("Finding similar movies…"):
        recs = recommend(selected_movie, n=n_recs)

    st.subheader(f"Because you like **{selected_movie}**, you might enjoy:")
    st.markdown("")

    if show_posters:
        cols = st.columns(n_recs)
        for col, rec in zip(cols, recs):
            poster_url = fetch_poster(rec["movie_id"], rec["title"])
            with col:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown(poster_placeholder(rec["title"]), unsafe_allow_html=True)
                st.markdown(
                    f"<div class='movie-title'>{rec['title']}</div>",
                    unsafe_allow_html=True,
                )

    else:
        for rank, rec in enumerate(recs, 1):
            st.markdown(
                f"<div class='list-card'>"
                f"  <div class='list-rank'>{rank}</div>"
                f"  <div class='list-title'>🎬 &nbsp;{rec['title']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    if not TMDB_API_KEY:
        st.markdown("")
     

else:
    st.markdown(
        "<div style='text-align:center;color:#888;padding:4rem 0;font-size:18px;'>"
        "⬆️ Select a movie above to get started"
        "</div>",
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "Built with [Streamlit](https://streamlit.io) · "
    "Data: [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) · "
)
