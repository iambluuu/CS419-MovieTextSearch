import streamlit as st
from streamlit_searchbox import st_searchbox    
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
    if query is not None:
        response = get_response("movies/suggest", {"query": query})
        response = response["suggestions"]
    else:
        response = []
    
    if not response or response[0].lower() != query.strip().lower():
        response.insert(0, query.strip())

    return response

def search_movies():
    query = st.session_state.query
    genres = st.session_state.genres
    release_year = st.session_state.release_year
    director = st.session_state.director
    casts = st.session_state.casts

    params = {"page": st.session_state.page}
    if query is not None and query.strip():
        params["query"] = query
    if genres is not None and len(genres) > 0:
        params["genres"] = genres
    if release_year is not None and release_year.strip():
        params["release_year"] = release_year
    if director is not None and director.strip():
        params["director"] = director
    if casts is not None and casts.strip():
        params["cast"] = casts.split(",")
    print(params)
    response = get_response("movies/search", params)
    return (response["total"], response["results"])

def run():
    st.set_page_config(page_title="Movie Text Search", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Movie Text Search</h1>", unsafe_allow_html=True)

    st.sidebar.title("Advanced Search Options")
    genres = st.sidebar.multiselect("Genres", get_all_genres())
    release_year = st.sidebar.text_input("Release Year", placeholder="Enter release year")
    director = st.sidebar.text_input("Director", placeholder="Enter director name")
    casts = st.sidebar.text_input("Casts", placeholder="Enter cast names, separated by commas")
    
    query = st_searchbox(get_suggestions, "Search text for the movie (e.g., title, plot)")

    _, col, _ = st.columns([1, 1, 1])
    submit = col.button("Search", use_container_width=True, type="primary")
    
    if submit or query:
        st.session_state.query = query
        st.session_state.genres = genres
        st.session_state.release_year = release_year
        st.session_state.director = director
        st.session_state.casts = casts
        st.session_state.page = 1
        st.session_state.results = search_movies()
    
    if 'results' not in st.session_state:
        return

    if st.session_state.results[0] == 0:
        st.warning("No results found.")
        return

    st.success(f"Found {st.session_state.results[0]} results.")
    for result in st.session_state.results[1]:
        with st.expander(f"**{result['title']} ({result['release_date'][:4]}) | Average Rating: {result['vote_average']}**", expanded=True):
            if result["homepage"] != "Unknown":
                st.markdown(f"## [{result['title']} ({result['release_date'][:4]})]({result['homepage']})")
            else:
                st.markdown(f"## {result['title']} ({result['release_date'][:4]})", unsafe_allow_html=True)
            st.markdown(f"#### Directed by: {result['director']}", unsafe_allow_html=True)
            st.markdown(f"**Genres:** {', '.join(result['genres'])} | **Release Date:** {result['release_date']} | **Runtime:** {result['runtime']} minutes | **Popularity:** {result['popularity']}")
            st.markdown(f"{result['overview']}")

    is_first_page = st.session_state.page == 1
    is_last_page = st.session_state.results[0] <= st.session_state.page * 10

    if is_first_page and is_last_page:
        return

    _, col1, col2 , col3, _ = st.columns([11, 5, 1, 5, 11])
    col2.markdown(f"<p style='text-align: center; padding-top: 5px;'>{st.session_state.page}</p>", unsafe_allow_html=True)
    if is_first_page:
        prev_page = col1.button("Previous page", use_container_width=True, type="primary", disabled=True)
    else:
        prev_page = col1.button("Previous page", use_container_width=True, type="primary")

    if is_last_page:
        next_page = col3.button("Next page", use_container_width=True, type="primary", disabled=True)
    else:
        next_page = col3.button("Next page", use_container_width=True, type="primary")
    
    if prev_page is not None and prev_page:
        st.session_state.page -= 1
        st.session_state.results = search_movies()

    if next_page is not None and next_page:
        st.session_state.page += 1
        st.session_state.results = search_movies()

if __name__ == "__main__":
    run()