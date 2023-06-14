"""
PRAW Docs: https://praw.readthedocs.io/en/stable/tutorials/comments.html
Sentiment Analysis Using HuggingFace: https://huggingface.co/blog/sentiment-analysis-python
Cultural Analytics with Python: https://melaniewalsh.github.io/Intro-Cultural-Analytics/04-Data-Collection/14-Reddit-Data.html
"""

import pandas as pd
from datetime import datetime
import csv
import praw

# Set up Pandas

pd.set_option('max_colwidth', 500)

# Set up PRAW with athentication

reddit = praw.Reddit(client_id = "QErgebb-REIyaM6wsoQ-Nw", 
                     client_secret = "PPuRFlKap6UQ4D5f9tYi_pvY68ePkA", 
                     username = "Ok_Scientist2546", 
                     password = "EZ8y@'ctT!f4A%L", 
                     user_agent = "Praw-test")


### FUNCTIONS ###

def pull_submissions(num_subs: int, sub_name: str, sort: str="hot", keywords=[]):
    """
    Gets key details about num_subs number of submissions on a particular subreddit sub_name. 


    Inputs:
        - num_subs [int]: the number of submissions to pull
        - sub_name [str]: subreddit name without the r/, i.e., "scarystories"
        - sort [str]: the way to sort the subreddit, i.e. by "controversial," 
            "gilded," "hot," "new," "rising," or "top". By default, sorted by "hot."
        - keywords [List[str]]: list of keywords to filter by. By default an empty list. At least 1 
            keyword must appear once in the submission text for the submission to be returned

    
    Returns:
        [List[Dict[9 items]]]: a list of dictionaries, one for each submission in the specified subreddit 
    """

    res = []
    subreddit = reddit.subreddit(sub_name)

    SORTED_SUBMISSIONS = {"hot": subreddit.hot(limit=num_subs), 
                          "controversial": subreddit.controversial(limit=num_subs), 
                          "gilded": subreddit.gilded(limit=num_subs),
                          "top": subreddit.top(limit=num_subs),
                          "new": subreddit.new(limit=num_subs),
                          "rising": subreddit.rising(limit=num_subs)
                          }
    
    for submission in SORTED_SUBMISSIONS[sort]:
        if keywords == [] or key_words_in_text(keywords, submission.selftext):
            story = {}
            story["title"] = submission.title
            story["submission_id"] = submission.id
            story["score"] = submission.score
            story["url"] = submission.url
            story["author"] = submission.author.name
            story["text"] = (submission.selftext.replace("’", "'").
                             replace("…", "...").replace("\n", " ").replace("“", "\"").
                             replace("”", "\""))
            story["subreddit"] = submission.subreddit
            story["num_comments"] = submission.num_comments
            story["date_created"] = datetime.fromtimestamp(submission.created_utc)
            res.append(story)
    return res


def key_words_in_text(keywords, text):
    """
    Checks if any of the keywords are in the text.

    Inputs:
        keywords [List[str]]: a list of key words to check
        text [str]: string text to check for words

    Returns: True if any of the keywords are in the text, False otherwise.
    """
    for word in keywords: 
        if word in text.lower(): 
            return True
    return False

def pull_comments(subreddit_id: str, amount: str="all"):
    """
    Pull all or top level comments from a certain reddit submission.

    Inputs:
        subreddit_id [str]: the subreddit id of subreddit you want to pull from
        amount [str]: how many comments to pull, all comments or only top level comments. 
            By default, this variable has value "all"


    Returns: 
        [List[Dict[8 items]]]: a list of comments from a single submission with the comment details
    """

    submission = reddit.submission(subreddit_id)

    # Select top level comments or all comments 
    submission.comments.replace_more(limit=None)
    if amount == "top_level":
        comments = []
        for top_level_comment in submission.comments:
            comments.append(top_level_comment) 
    else:
        comments = submission.comments.list()

    # Return List of dictionaries with comment details
    res = []
    for comment in comments:
        new_comment = {}
        new_comment["text"] = comment.body.replace("’", "'").replace("\n", " ").replace("“", "\"")
        # Text needs to contain the keyword to be returned!
        new_comment["author"] = comment.author.name
        new_comment["score"] = comment.score
        new_comment['comment_id'] = comment.id
        new_comment["is_op"] = comment.is_submitter
        new_comment["submission_id"] = comment._submission.id
        new_comment["subreddit"] = comment.subreddit_name_prefixed
        new_comment["subreddit_id"] = comment.subreddit_id
        res.append(new_comment)
    return res


def write_to_csv(obj, file, mode="a"):
     """
     Writes info from a List[Dict[items]] object into a csv file.

     Inputs:
        mode [str]: "w" for write or "a" for append. By default, "a" for append.
        obj [List[Dict[items]]]: the object that contains the info to write
        file [str]: csv file name

     Returns:
        Nothing
     """
     fieldnames = obj[0].keys()
     with open(file, mode, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(obj)


### CASE STUDY ONE: PULLING SUBMISSIONS AND COMMENTS ###

# write submissions from r/scarystories to submissions.csv 
# hot_ten_stories = pull_submissions(num_subs=10, sub_name="scarystories", sort="top")
# write_to_csv(hot_ten_stories, "submissions.csv", "w")


# Write newly-pulled comments from a specific post to comments.csv 
# new_story = pull_comments(subreddit_id="149dze9")
# write_to_csv(new_story, 'comments.csv', "w")



### CASE STUDY TWO ###
# if text doesn't contain a keyword, don't pull the submission
# subs_50 = pull_submissions(num_subs=50, sub_name="scarystories", keywords=["scary", "stab", "kill"])
# write_to_csv(subs_50, 'submissions.csv', "w")
 

# TODO: Delete duplicates
subs_50 = pull_submissions(num_subs=50, sub_name="scarystories", keywords=["scary", "stab", "kill"])
write_to_csv(subs_50, 'submissions.csv', "w")

# other_50 = pull_submissions(num_subs=50, sort="hot", sub_name="scarystories", keywords=["frightened", "dark", "fear"])
# df = pd.read_csv("submissions.csv", delimiter=',', encoding='utf-8')
# write_to_csv(subs_50, 'submissions.csv', "a")
# pd.read_csv('submissions.csv').append(df).drop_duplicates().to_csv('submissions.csv')

# TODO: Only pull between a certain time range

# current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
# one_week_ago = current_time - 604800
# subreddit = reddit.subreddit("scarystories")

# for submission in subreddit.new(limit=25):
# 	if submission.created_utc >= one_week_ago and < another_time_range:
# 		# do stuff
# 		pass

# need to go through csv manually to make sure that keyword is not accidental 
# - probably less lilely if keyword is "Cisco", but more likely with something like "stab"