import streamlit as st
import requests

api_url = "http://127.0.0.1:3001"

def get_response(endpoint, params=None):
    try:
        response = requests.get(f"{api_url}/{endpoint}", params=params)
        return response.json()
    except:
        st.error("Failed to connect to the API.")
        return None

def get_all_genres():
    response = get_response("movies/genres")
    return response["genres"]

def get_suggestions(query):
    response = get_response("movies/suggest", {"query": query})
    return response["suggestions"]

def search_movies(query, genres, release_year, director, cast):
    params = {}
    if query.strip():
        params["query"] = query
    if genres:
        params["genres"] = genres
    if release_year.strip():
        params["release_year"] = release_year
    if director.strip():
        params["director"] = director
    if cast.strip():
        params["cast"] = cast.split(",")
    response = get_response("movies/search", params)
    return (response["total"], response["results"])

def run():
    st.set_page_config(page_title="Movie Text Search", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Movie Text Search</h1>", unsafe_allow_html=True)

    st.sidebar.title("Advanced Search Options")
    selected_genres = st.sidebar.multiselect("Genres", get_all_genres())
    release_year = st.sidebar.text_input("Release Year", placeholder="Enter release year")
    director = st.sidebar.text_input("Director", placeholder="Enter director name")
    casts = st.sidebar.text_input("Casts", placeholder="Enter cast names, separated by commas")

    if "query" not in st.session_state:
        st.session_state.query = ""
    
    query = st.text_input("Search text for the movie (e.g., title, plot)", placeholder="Enter search text")

    _, col, _ = st.columns([2, 1, 2])
    submit = col.button("Search", use_container_width=True)
    
    if submit:
        st.session_state.results = search_movies(query, selected_genres, release_year, director, casts)
    
    results = None
    if 'results' in st.session_state:
        results = st.session_state.results
    
    if results is None:
        return

    if results[0] == 0:
        st.warning("No results found.")
        return

    st.success(f"Found {results[0]} results.")
    for result in results[1]:
        with st.expander(f"**{result['title']} ({result['release_date'][:4]}) | Average Rating: {result['vote_average']}**", expanded=True):
            if result["homepage"] != "Unknown":
                st.markdown(f"## [{result['title']} ({result['release_date'][:4]})]({result['homepage']})")
            else:
                st.markdown(f"## {result['title']} ({result['release_date'][:4]})", unsafe_allow_html=True)
            st.markdown(f"#### Directed by: {result['director']}", unsafe_allow_html=True)
            st.markdown(f"**Genres:** {', '.join(result['genres'])} | **Release Date:** {result['release_date']} | **Runtime:** {result['runtime']} minutes | **Popularity:** {result['popularity']}")
            st.markdown(f"{result['overview']}")

if __name__ == "__main__":
    run()