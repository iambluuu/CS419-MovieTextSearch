import pandas as pd


def post_process(data_frame):
    """
    Post-process the dataframe:
    1. Drop all duplicate rows.
    2. Combine rows with the same 'id' by merging their 'plot_synopsis'.
    3. Merge 'overview', 'tagline', and 'keywords' into 'plot_synopsis' in the specified order.
    4. Drop the now-unnecessary columns.
    """

    # 1. Drop all duplicate rows
    data_frame = data_frame.drop_duplicates()

    # 2. Group by 'id' and aggregate the 'plot_synopsis' column
    data_frame = (
        data_frame.groupby('id', as_index=False)
        .agg({
            'title': 'first',
            'vote_average': 'first',
            'vote_count': 'first',
            'status': 'first',
            'release_date': 'first',
            'revenue': 'first',
            'runtime': 'first',
            'backdrop_path': 'first',
            'budget': 'first',
            'original_language': 'first',
            'overview': 'first',         
            'poster_path': 'first',
            'tagline': 'first',          
            'production_companies': 'first',
            'production_countries': 'first',
            'spoken_languages': 'first',
            'keywords': 'first',        
            'plot_synopsis': lambda x: ' '.join(x.dropna())  # Combine all non-NaN 'plot_synopsis' entries
        })
    )

    # 3. Combine 'overview', 'tagline', and 'keywords' into 'plot_synopsis'
    data_frame['plot_synopsis'] = (
        data_frame['plot_synopsis'].fillna('') + ' ' +
        data_frame['overview'].fillna('') + ' ' +
        data_frame['tagline'].fillna('') + ' ' +
        data_frame['keywords'].fillna('')
    ).str.strip() 

    # 4. Drop the now-unnecessary columns
    data_frame = data_frame.drop(columns=['overview', 'tagline', 'keywords'])

    return data_frame



if __name__ == "__main__":
    file1 = "TMDB_movie_dataset_v11.csv" 
    file2 = "mpst_full_data.csv"  

    tmdb_data = pd.read_csv(file1)
    mpst_data = pd.read_csv(file2)

    print("TMDB Dataset Columns:\n", tmdb_data.columns)
    print("MPST Dataset Columns:\n", mpst_data.columns)

    merged_data = pd.merge(tmdb_data[['id', 'title', 'vote_average', 'vote_count', 'status', 'release_date',
                                    'revenue', 'runtime', 'backdrop_path', 'budget', 'original_language', 'overview', 'poster_path', 'tagline', 'genres', 'production_companies', 'production_countries', 'spoken_languages', 'keywords']], 
                           mpst_data[['title', 'plot_synopsis']],
                           on="title",
                           how="inner")
    
    processed_data = post_process(merged_data)

    processed_data.to_excel("merged_movies_dataset.xlsx", index=False)
    print(f"Inner join complete! Merged dataset saved as 'merged_movies_dataset.xlsx'.")
