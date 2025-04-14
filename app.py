import pickle
import streamlit as st
import requests
import os
import gdown


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')

        if not poster_path:
            return "https://via.placeholder.com/500x750?text=No+Poster"

        return "https://image.tmdb.org/t/p/w500/" + poster_path

    except Exception as e:
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
    .status-message {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- APP HEADER ----------------
st.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------
@st.cache_resource  # Cache the loaded data to improve performance
def load_data():
    # Show a loading spinner while data is being loaded
    with st.spinner("Loading movie data..."):
        try:
            # Load movies.pkl silently
            movies = pickle.load(open('movies.pkl', 'rb'))

            # Try to load similarity matrix from local path
            similarity_path = "similarity.pkl"

            if os.path.exists(similarity_path) and os.path.getsize(similarity_path) > 0:
                try:
                    with open(similarity_path, 'rb') as f:
                        # Read to verify it's a valid pickle file
                        test_read = pickle.load(f)
                    similarity = pickle.load(open(similarity_path, 'rb'))
                    return movies, similarity
                except Exception:
                    # Remove the corrupted file silently
                    os.remove(similarity_path)

            # If the file doesn't exist or is invalid, download it silently
            file_id = "1WIR0FkmM1iY0_ysLvC1nUbxUfwk6L1W_"  # Your Google Drive file ID

            try:
                # Use gdown for more reliable Google Drive downloads
                output = gdown.download(
                    f"https://drive.google.com/uc?id={file_id}",
                    similarity_path,
                    quiet=True  # Set to True to hide download progress
                )

                if output:
                    # Load the downloaded file
                    similarity = pickle.load(open(similarity_path, 'rb'))
                    return movies, similarity
                else:
                    st.error("Unable to load movie database. Please try again later.")
                    st.stop()
            except Exception:
                st.error("Unable to load movie database. Please try again later.")
                st.stop()

        except Exception:
            st.error("Something went wrong while loading the movie database. Please try again later.")
            st.stop()


# Load data
movies, similarity = load_data()

# ---------------- DROPDOWN ----------------
st.markdown(
    "<p style='text-align:center'>Find movies similar to your favorites! Select a movie from the dropdown below:</p>",
    unsafe_allow_html=True)
movie_list = movies['title'].values
selected_movie = st.selectbox("🎥 Select a movie to get recommendations", movie_list)

# ---------------- BUTTON ----------------
if st.button('🔍 Show Recommendations'):
    with st.spinner("Finding movies you'll love..."):
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