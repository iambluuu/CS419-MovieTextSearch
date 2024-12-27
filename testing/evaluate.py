import requests
import pandas as pd
from openpyxl import Workbook, load_workbook
import matplotlib.pyplot as plt
import numpy as np


def is_relevant(title_a, title_b):
    title_a = title_a.lower()
    title_b = title_b.lower()

    return title_a in title_b or title_b in title_a

def precision_at_k(results, target, k = 10):
    return sum([1 for item in results[:k] if is_relevant(item["title"], target)]) / k

def truncate(sentence, max_words = 5):
    return " ".join(sentence.split()[:max_words])

def evaluate(queries, titles):
    q = 0
    reciporical_ranks = []
    query_lengths = []
    for query, title in zip(queries, titles):
        if not query or not isinstance(query, str) or len(query) < 10:
            continue

        q += 1
        # query = truncate(query)
        response = requests.get(f"http://127.0.0.1:3001/movies/search?query={query}")
        results = response.json()["results"]
        
        title_results = [item["title"] for item in results]
        rank = (title_results.index(title) + 1) if title in title_results else 0

        reciporical_rank = 1 / rank if rank else 0

        if reciporical_rank < 0.5:
            print(f"Low reciporical Rank for '{title}': {reciporical_rank}")
        
        reciporical_ranks.append(reciporical_rank)
        query_lengths.append(len(query.split()))
      
    return reciporical_ranks, query_lengths

def plot_frequency(precision, query_length, title):
    # Convert to pandas DataFrame for easier manipulation
    df = pd.DataFrame({'Reciprocal Rank': precision, 'Query Length': query_length})

    # Define the number of bins for the query lengths
    bins = np.arange(0, 5, 1)  # Bins from 0 to max query length in steps of 10

    # Bin the query lengths
    df['Length Bin'] = pd.cut(df['Query Length'], bins)

    # Calculate the average precision for each bin
    average_precision = df.groupby('Length Bin')['Reciprocal Rank'].mean()

    # Plotting the bar chart
    plt.figure(figsize=(8, 6))
    average_precision.plot(kind='bar', color='skyblue', edgecolor='black')

    # Adding labels and title
    plt.title(title, fontsize=14)
    plt.xlabel('Query Length (Binned)', fontsize=12)
    plt.ylabel('Reciprocal Rank', fontsize=12)

    # Show the plot
    plt.show()

test_data = pd.read_excel("test_data.xlsx")

queries = test_data["query"].tolist()
keywords = test_data["keywords"].tolist()
titles = test_data["title"].tolist()

# ranks_short, short_lengths = evaluate(keywords, titles)
# mrr_short = sum(ranks_short) / len(ranks_short)
ranks_long, long_lengths = evaluate(queries, titles)
mrr_long = sum(ranks_long) / len(ranks_long)

print(f"MRR Keywords: {mrr_long}")
# print(f"MRR Queries: {mrr_short}")

# plot_frequency(ranks_long, long_lengths, 'Reciprocal Rank vs Query Length (Binned) for Complete Queries (Truncated)')

