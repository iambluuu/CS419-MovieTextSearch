import logging
import requests
import fake_useragent as fu
import wget
import json

import isodate

from bs4 import BeautifulSoup
import wget

# from ..models.movies import MovieInfo

log = logging.getLogger(name="MovieApp")

def get_soup(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept" : "*/*",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        log.error(f"Failed to crawl movies from the web: {str(e)}")
        return {"error": f"Failed to crawl movies from the web: {str(e)}"}
    
    return BeautifulSoup(response.text, "html.parser")

def get_cast(url) -> dict:
    result = {
        "cast": "unknown",
        "director": "unknown"
    }
    soup = get_soup(url)

    with open("cast.html", "w", encoding='utf-8') as f:
        f.write(soup.prettify())

    try:
        cast_table = soup.find("table", class_="cast_list")
        cast_rows = cast_table.find_all("tr", class_=True)
        cast = []
        for row in cast_rows:
            actor = row.find("td", class_="primary_photo").find("img")["alt"]
            cast.append(actor)
            
        result["cast"] = ", ".join(cast) or "unknown"
    except Exception as e:
        log.error(f"Failed to get cast: {str(e)}")

    try:
        director_heading = soup.find("h4", id="director")
        directors = director_heading.find_next("table").find_all("a")
        director_names = []
        for director in directors:
            director_names.append(director.text.strip())

        result["director"] = ", ".join(director_names) or "unknown"
    except Exception as e:
        log.error(f"Failed to get director: {str(e)}")

    return result


def get_plot(url) -> dict:
    result = {
        'synopsis': 'unknown',
    }
    soup = get_soup(url)

    with open("plot.html", "w", encoding='utf-8') as f:
        f.write(soup.prettify())
    
    try:
        section = soup.find("div", attrs={"data-testid": "sub-section-synopsis"})
        outer_div = section.find("div", class_="ipc-html-content ipc-html-content--base")
        content_html = outer_div.find("div", class_="ipc-html-content-inner-div").decode_contents()
        content_soup = BeautifulSoup(str(content_html), "html.parser")

        for br_tag in content_soup.find_all("br"):
            br_tag.insert_before("\n")

        text_content = content_soup.get_text()

        result['synopsis'] = text_content

        with open("plot.txt", "w", encoding='utf-8') as f:
            f.write(text_content)
    except Exception as e:
        log.error(f"Failed to get plot: {str(e)}")
    
    return result

def get_metadata(url) -> dict:
    result = {
        "title": "unknown",
        "original_title": "unknown",
        "poster_path": "unknown",
        "release_date": "unknown",
        "rating": 0,
        "rating_count": 0,
        "genres": "unknown",
        "runtime": 0,
        "production_companies": "unknown",
        "production_countries": "unknown",
        "original_language": "unknown",
        "spoken_languages": "unknown",
        "budget": 0,
        "revenue": 0
    }

    soup = get_soup(url)
    data = soup.find("script", type="application/ld+json") # Contains title, rating, rating count, genre, date, poster path
    detail_data = soup.find("script", id="__NEXT_DATA__") # Contains production company, country, language, budget, revenue

    try:
        data_json = json.loads(data.contents[0])
        detail_data_json = json.loads(detail_data.contents[0])
        with open("movie_metadata.json", "w", encoding='utf-8') as f:
            json.dump(data_json, f, indent=4)
        
        with open("movie_detail.json", "w", encoding='utf-8') as f:
            json.dump(detail_data_json, f, indent=4)
    except Exception as e:
        log.error(f"Failed to get metadata: {str(e)}")

    try:
        detail_props = detail_data_json['props']['pageProps']['aboveTheFoldData']
        main_column_data = detail_data_json['props']['pageProps']['mainColumnData']

        result['title'] = detail_props.get('titleText', {}).get('text', 'unknown')
        result['original_title'] = detail_props.get('originalTitleText', {}).get('text', 'unknown')
        result['poster_path'] = data_json.get('image', 'unknown')
        result['release_date'] = data_json.get('datePublished', 'unknown')
        result['rating'] = detail_props.get('ratingsSummary', {}).get('aggregateRating', 0)
        result['rating_count'] = detail_props.get('ratingsSummary', {}).get('voteCount', 0)
        result['genres'] = ", ".join(data_json.get('genre', [])) or 'unknown'
        result['runtime'] = detail_props.get('runtime', {}).get('seconds', 0) // 60

        result['production_companies'] = ', '.join(
            [edge['node']['company']['companyText']['text'] for edge in detail_props.get('production', {}).get('edges', [])]
        ) or 'unknown'

        result['production_countries'] = ", ".join(
            [country['text'] for country in main_column_data.get('countriesOfOrigin', {}).get('countries', [])]
        ) or 'unknown'

        result['original_language'] = detail_props.get('plot', {}).get('language', {}).get('id', 'unknown').split("-")[0]
        result['spoken_languages'] = ", ".join(
            [language['text'] for language in main_column_data.get('spokenLanguages', {}).get('spokenLanguages', [])]
        ) or 'unknown'

        result['budget'] = main_column_data.get('productionBudget', {}).get('budget', {}).get('amount', 0)
        result['revenue'] = main_column_data.get('lifetimeGross', {}).get('total', {}).get('amount', 0)
    except Exception as e:
        log.error(f"Failed to get metadata: {str(e)}")

    return result

def RC_crawl_movies(target_url: str) -> dict:
    """Crawl movies from the web.

    Returns:
        MovieInfo: Crawl results.
    """
    log.info("Crawling movies from the web...")

    if not target_url:
        return {"error": "Target URL is required."}
    
    if not target_url.startswith("https://www.imdb.com/title/"):
        return {"error": "Invalid URL. Please provide a valid IMDb movie URL."}
    
    if not target_url.endswith("/"):
        target_url += "/"

    # Crawl movies from the web
    result = {}
    try:
        result.update(get_metadata(target_url))
        result.update(get_plot(target_url + "plotsummary"))
        result.update(get_cast(target_url + "fullcredits"))
    except Exception as e:
        log.error(f"Failed to crawl movies from the web: {str(e)}")
        return {"error": f"Failed to crawl movies from the web: {str(e)}"}

    return result

if __name__ == "__main__":
    target_url = "https://www.imdb.com/title/tt21692408/"
    result = RC_crawl_movies(target_url)
    for key, value in result.items():
        if key != "synopsis":
            print(f"{key}: {value}")