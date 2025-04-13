import pickle
import streamlit as st
import requests


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')

        if not poster_path:
            print(f"[Warning] No poster found for movie ID: {movie_id}")
            return "https://via.placeholder.com/500x750?text=No+Poster"

        return "https://image.tmdb.org/t/p/w500/" + poster_path

    except Exception as e:
        print(f"[Error] Failed to fetch poster for movie ID: {movie_id} — {e}")
        return "https://via.placeholder.com/500x750?text=Image+Unavailable"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters


# ---------------- STYLING ----------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
        color: #1f2937;
    }
    h1 {
        text-align: center;
        color: #0ea5e9;
        font-weight: bold;
    }
    .movie-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .movie-card:hover {
        transform: scale(1.05);
    }
    .stButton > button {
        background-color: #0ea5e9;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 16px;
        margin-top: 15px;
    }
    .stButton > button:hover {
        background-color: #0284c7;
    }
    .movie-card h5 {
        color: #1f2937;
        font-size: 16px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- APP HEADER ----------------
st.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---------------- DROPDOWN ----------------
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Select a movie to get recommendations", movie_list)

# ---------------- BUTTON ----------------
if st.button('🔍 Show Recommendations'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
                <div class='movie-card'>
                    <h5>{recommended_movie_names[i]}</h5>
                    <img src="{recommended_movie_posters[i]}" width="100%" style="border-radius:10px"/>
                </div>
            """, unsafe_allow_html=True)
