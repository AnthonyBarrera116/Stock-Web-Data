# Import the NewsSentiment class from the NewsSen module
# This assumes NewsSen.py contains the logic to fetch and score recent news headlines
import NewsSen as n

# Run the script only if executed directly (not when imported as a module)
if __name__ == '__main__':
    # Create an instance of the NewsSentiment class
    # - company: the company name to search for in news headlines
    # - max_articles: limit to 20 recent articles
    # - ignore_seen=True: avoids reprocessing previously analyzed headlines if tracking is used
    ns = n.NewsSentiment(company="nvidia", max_articles=20, ignore_seen=True)

    # Analyze all fetched articles and compute the final sentiment score
    # The output is a numeric score (e.g., -2 to 2) based on article tone
    score = ns.analyze()

    # Print the final computed news score for visibility or testing
    print(f"\nFinal news_score to use in model: {score}")
