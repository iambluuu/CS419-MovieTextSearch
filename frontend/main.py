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

    response = [response[0]] + [response[i] for i in range(1, len(response)) if response[i] != response[i - 1]]

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
    if release_year is not None and release_year != (1900, 2030):
        params["release_year"] = release_year[0]
    if director is not None and director.strip():
        params["director"] = director
    if casts is not None and casts.strip():
        params["cast"] = casts.split(",")
    print(params)
    response = get_response("movies/search", params)
    return (response["total"], response["results"])

def load_more():
    st.session_state.page += 1
    st.session_state.results[1].extend(search_movies()[1])

def run():
    st.set_page_config(page_title="Movie Text Search", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Movie Text Search</h1>", unsafe_allow_html=True)

    st.sidebar.title("Advanced Search Options")
    genres = st.sidebar.multiselect("Genres", get_all_genres(), key="id_genres")
    release_year = st.sidebar.slider("Release Year", 1900, 2030, (1900, 2030), key="id_release_year")
    director = st.sidebar.text_input("Director", placeholder="Enter director name", key="id_director")
    casts = st.sidebar.text_input("Casts", placeholder="Enter cast names, separated by commas", key="id_casts")
    
    last_query = st.session_state.query if "query" in st.session_state else ""
    query = st_searchbox(get_suggestions, "Search text for the movie (e.g., title, plot)")

    _, col, _ = st.columns([1, 1, 1])
    submit = col.button("Search", use_container_width=True, type="primary")

    if query is None:
        query = ""
    
    if submit or (query and query != last_query):
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
        st.warning(f"No results found for '{st.session_state.query}'.")
        return

    st.success(f"Found {st.session_state.results[0]} results for '{st.session_state.query}'.")

    for i, result in enumerate(st.session_state.results[1]):
        with st.expander(f"**Result #{i + 1}: {result['title']} ({result['release_date'][:4]}) | Average Rating: {float(result['vote_average']):.2f}**", expanded=True):
            st.markdown(f"## {result['title']} ({result['release_date'][:4]})", unsafe_allow_html=True)
            st.markdown(f"#### Directed by: {', '.join(result['director'])}", unsafe_allow_html=True)
            st.markdown(f"**Genres:** {', '.join(result['genres'])} | **Release Date:** {result['release_date']} | **Runtime:** {result['runtime']} minutes | **Popularity:** {float(result['popularity']):.2f}")

            if "overview" in result:
                overview = result["overview"]
            elif "plot_synopsis" in result:
                overview = result["plot_synopsis"]
            overview = str(overview).strip()
            if len(overview) > 500:
                overview = overview[:500] + "..."

            st.markdown(f"{overview}")

    if st.session_state.results[0] <= st.session_state.page * 10:
        return

    _, col, _ = st.columns([2, 1, 2])
    col.button("Load more...", use_container_width=True, on_click=load_more)

if __name__ == "__main__":
    run()