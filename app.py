import streamlit as st
import praw
import pandas as pd
import time

# Hardcoded Reddit API credentials
CLIENT_ID = "sDw5OFBsPITLReIfzBIuog"
CLIENT_SECRET = "ZaUehHHivPoV2cN-_fhMh_D8ZGFfKQ"
USER_AGENT = "research_project:v1.0 (by u/AlarmedEconomist9336)"

# Initialize PRAW
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)


# Function to scrape subreddit
def scrape_subreddit(subreddit_name, max_posts=100):
    """
    Scrape posts and comments from a subreddit.

    :param subreddit_name: Name of the subreddit to scrape.
    :param max_posts: Maximum number of posts to fetch (default: 100).
    :return: DataFrame containing posts and comments.
    """
    subreddit = reddit.subreddit(subreddit_name)
    posts_data = []
    post_count = 0

    try:
        for submission in subreddit.hot(limit=None):
            submission.comments.replace_more(limit=None)
            comments = [comment.body for comment in submission.comments.list()]
            post = {
                "id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "comments": comments,
            }
            posts_data.append(post)
            post_count += 1
            time.sleep(1)  # Delay to respect API limits
            if post_count >= max_posts:
                break

        return pd.DataFrame(posts_data)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame(posts_data)


# Streamlit UI
st.title("Reddit Subreddit Scraper")

# User inputs
subreddit_name = st.text_input("Enter the name of the subreddit:", value="")
max_posts = st.number_input("Enter the number of posts to scrape:", min_value=1, max_value=1000, value=100)

if st.button("Scrape Subreddit"):
    if subreddit_name:
        with st.spinner("Scraping subreddit..."):
            data = scrape_subreddit(subreddit_name, max_posts=max_posts)
            if not data.empty:
                st.success("Scraping complete!")
                st.dataframe(data)

                # Provide download option for the scraped data
                csv = data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{subreddit_name}_posts.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No data found or an error occurred.")
    else:
        st.warning("Please enter a subreddit name.")
