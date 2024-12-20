import streamlit as st
from streamlit_searchbox import st_searchbox
from st_keyup import st_keyup
import requests
import unicodedata

api_url = "http://127.0.0.1:3001"
image_url = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
movie_url = "https://www.themoviedb.org/movie"
year_range = (1900, 2100)


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
    try:
        response = get_response("movies/suggest", {"query": query})
        response = response["suggestions"]
    except:
        response = []

    if not response or response[0].lower() != query.strip().lower():
        response.insert(0, query.strip())

    response = [response[0]] + [
        response[i] for i in range(1, len(response)) if response[i] != response[i - 1]
    ]

    return response


def search_movies():
    query = st.session_state.query
    genres = st.session_state.genres
    start_year = st.session_state.start_year
    end_year = st.session_state.end_year
    director = st.session_state.director
    casts = st.session_state.casts

    print("query: ", query)

    params = {"page": st.session_state.page}
    if query is not None and query.strip():
        params["query"] = query
    if genres is not None and len(genres) > 0:
        params["genres"] = genres
    if start_year is not None and start_year != year_range[0]:
        params["from_year"] = start_year
    if end_year is not None and end_year != year_range[1]:
        params["to_year"] = end_year
    if director is not None and director.strip():
        params["director"] = director
    if casts is not None and casts.strip():
        params["cast"] = casts.split(",")
    print(params)
    response = get_response("movies/search", params)
    return (response["total"], [result["id"] for result in response["results"]])


def get_movie_details(id):
    return get_response(f"movies/{id}")["results"][0]


def get_movie_url(id):
    title = get_movie_details(id)["title"]
    title = "".join(
        c
        for c in unicodedata.normalize("NFD", title)
        if unicodedata.category(c) != "Mn"
    )
    title = title.lower().replace(" ", "-")

    return f"{movie_url}/{id}-{title}"


def load_more():
    st.session_state.page += 1
    st.session_state.results[1].extend(search_movies()[1])


def init():
    if "init" not in st.session_state:
        st.session_state.query = ""
        st.session_state.genres = []
        st.session_state.start_year = year_range[0]
        st.session_state.end_year = year_range[1]
        st.session_state.director = ""
        st.session_state.casts = ""
        st.session_state.page = 1
        st.session_state.results = None
        st.session_state.init = True


def run():
    st.set_page_config(page_title="Movie Text Search", layout="wide")
    st.markdown(
        "<h1 style='text-align: center;'>Movie Text Search</h1>",
        unsafe_allow_html=True,
    )

    st.sidebar.title("Advanced search options")
    search_gui = st.sidebar.selectbox(
        "Search GUI", ["Clunky search box", "Double search box"]
    )
    st.sidebar.multiselect("Genres", get_all_genres(), key="id_genres")
    col1, col2, col3 = st.sidebar.columns([5, 1, 5])
    start_year = col1.number_input(
        "Start year",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range[0],
        key="id_start_year",
    )
    col2.write("")
    col2.write("")
    col2.markdown("<p style='text-align: center;'>to</p>", unsafe_allow_html=True)
    col3.number_input(
        "End year",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range[1],
        key="id_end_year",
    )
    st.sidebar.text_input(
        "Director", placeholder="Enter director name", key="id_director"
    )
    st.sidebar.text_input(
        "Casts", placeholder="Enter cast names, separated by commas", key="id_casts"
    )

    last_query = st.session_state.query if "query" in st.session_state else ""
    if search_gui == "Clunky search box":
        query = st_searchbox(
            get_suggestions,
            label="Query",
            placeholder="Search text for the movie (e.g., title, plot)",
        )
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            query = st_keyup(
                "Query", placeholder="Search text for the movie (e.g., title, plot)"
            )
        with col2:
            query = st.selectbox(
                "Suggestions",
                get_suggestions(query),
                help="Select a suggestion from your query",
            )

    if query is None:
        query = ""

    _, col, _ = st.columns([1, 1, 1])
    submit = col.button("**Search**", use_container_width=True, type="primary")

    if submit:
        st.session_state.query = query
        st.session_state.genres = st.session_state.id_genres
        st.session_state.start_year = st.session_state.id_start_year
        st.session_state.end_year = st.session_state.id_end_year
        st.session_state.director = st.session_state.id_director
        st.session_state.casts = st.session_state.id_casts
        st.session_state.page = 1
        st.session_state.results = search_movies()

    if not st.session_state.results:
        return

    searched = ""
    if st.session_state.query:
        searched += f'movie "{st.session_state.query}" '
    else:
        searched += "all movies "
    if st.session_state.genres:
        searched += f"in genres {', '.join(st.session_state.genres)} "
    if (
        st.session_state.start_year != year_range[0]
        and st.session_state.end_year != year_range[1]
    ):
        searched += f"released between {st.session_state.start_year} and {st.session_state.end_year} "
    elif st.session_state.start_year != year_range[0]:
        searched += f"released after {st.session_state.start_year} "
    elif st.session_state.end_year != year_range[1]:
        searched += f"released before {st.session_state.end_year} "
    if st.session_state.director:
        searched += f"directed by {st.session_state.director} "
    if st.session_state.casts:
        searched += f"with casts {', '.join(st.session_state.casts.split(','))} "
    searched = searched.strip()

    if st.session_state.results[0] == 0:
        st.warning(f"No results found for {searched}.")
        return

    st.success(f"Found {st.session_state.results[0]} results for {searched}.")

    for i, id in enumerate(st.session_state.results[1]):
        result = get_movie_details(id)
        with st.expander(
            f"**Result #{i + 1}: {result['title']} ({result['release_date'][:4]}) | Average Rating: {float(result['vote_average']):.2f}**",
            expanded=True,
        ):
            col1, col2 = st.columns([1, 4])

            if (
                "poster_path" in result
                and result["poster_path"]
                and result["poster_path"] != "Unknown"
            ):
                col1.image(
                    f"{image_url}{result['poster_path']}", use_container_width=True
                )
            else:
                col1.image(
                    "https://via.placeholder.com/600x900?text=Poster+not+available",
                    use_container_width=True,
                )

            col2.markdown(
                f"## [{result['title']} ({result['release_date'][:4]})]({get_movie_url(id)})",
                unsafe_allow_html=True,
            )
            col2.markdown(
                f"#### Directed by: {', '.join(result['director'])}",
                unsafe_allow_html=True,
            )
            col2.markdown(
                f"**Genres:** {', '.join(result['genres'])} | **Release Date:** {result['release_date']} | **Runtime:** {result['runtime']} minutes | **Popularity:** {float(result['popularity']):.2f}"
            )

            if "overview" in result:
                overview = result["overview"]
            elif "plot_synopsis" in result:
                overview = result["plot_synopsis"]
            overview = str(overview).strip()
            if len(overview) > 500:
                overview = overview[:500] + "..."

            col2.write(overview)

    if st.session_state.results[0] <= st.session_state.page * 10:
        return

    _, col, _ = st.columns([2, 1, 2])
    col.button("Load more...", use_container_width=True, on_click=load_more)


if __name__ == "__main__":
    init()
    run()
