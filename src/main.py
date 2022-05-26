import json
import requests
import os
from dotenv import load_dotenv
import base64
import click

load_dotenv()

organization = os.environ.get("DEVOPS_ORG")
project = os.environ.get("DEVOPS_PROJECT")
repositoryId = os.environ.get("DEVOPS_REPO")
DEVOPS_USER = os.environ.get("DEVOPS_USER")
DEVOPS_PAT = os.environ.get("DEVOPS_PAT")
DEVOPS_DISPLAY_NAME = ""

authorization = str(base64.b64encode(bytes(':'+DEVOPS_PAT, 'ascii')), 'ascii')

headers = {
    'Accept': 'application/json',
    'Authorization': 'Basic '+authorization
}

prs = []
reviews = []
comments = []

def create_md_file():
    with open(f"{DEVOPS_DISPLAY_NAME}.md", "w", encoding="utf-8") as fd:
        txt = f"# Stats for {DEVOPS_DISPLAY_NAME} in {project} - {repositoryId}\n"
        fd.write(f'{txt}\n')

def write_output(txt):
    print(txt)
    with open(f"{DEVOPS_DISPLAY_NAME}.md", "a", encoding="utf-8") as fd:
        fd.write(f'{txt}\n')

def write_my_prs(my_prs):

    txt = """## My PR's

|ID|Name|
|-|-|
"""

    for pr in my_prs:
        txt = txt + f"|{pr['pullRequestId']}|{pr['title']}|\n"
    write_output(txt)

def write_my_reviews(my_reviews):

    txt = """## PR's that I reviewed

|ID|Name|
|-|-|
"""
    for pr in my_reviews:
        txt = txt + f"|{pr['pullRequestId']}|{pr['title']}|\n"
    write_output(txt)

def write_my_comments(my_comments):

    txt = """## PR's that I commented on

|ID|Name|Comment|
|-|-|-|
"""
    for pr in my_comments:
        if pr['reply'] == False:
            comment = str(pr['comment']).replace('\n', ' ')
            txt = txt + f"|{pr['pullRequestId']}|{pr['title']}|{comment}|\n"
    write_output(txt)

def write_stats(prs, my_prs, my_reviews, my_comments):

    md_str = f"""## Summary

- PR's: {prs}
- My PR's: {my_prs}
- My reviews: {my_reviews}
- My comments: {my_comments}
"""
    write_output(md_str)

def get_request(url):
    response = requests.get(
        url=url, headers=headers)
    return response.text

def get_reviewers(pullRequestId, title):

    j = get_request(f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullRequests/{pullRequestId}/reviewers?api-version=6.0")

    for value in json.loads(j)["value"]:

        if value["vote"] != 0:

            review = {
                'pullRequestId': pullRequestId,
                'title': title,
                'createdBy': value["displayName"]
            }

            reviews.append(review)

def get_comments(pullRequestId, title,  comment_trim, include_replies):

     j = get_request(f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullRequests/{pullRequestId}/threads?api-version=6.0")

     for thread in json.loads(j)["value"]:

        for comment in thread["comments"]:

            if comment['commentType'] != 'text':
                continue

            if len(comment.get('content','-')) < comment_trim:
                continue

            if not include_replies and (comment['parentCommentId'] != 0):
                continue

            my_comment = {
                'pullRequestId': pullRequestId,
                'title': title,
                'createdBy': comment['author']["displayName"],
                'comment': comment.get('content','-'),
                'reply': (comment['parentCommentId'] != 0)
            }

            comments.append(my_comment)

def get_prs(list_size: int, comment_trim: int, include_replies: bool):
    j = get_request(
        f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullrequests?searchCriteria.status=completed&$top={list_size}&api-version=6.0")

    with click.progressbar(json.loads(j)["value"]) as bar:
        for value in bar:

            pr = {
                'title': value["title"],
                'createdBy': value["createdBy"]["displayName"],
                'pullRequestId': value["pullRequestId"]
            }

            prs.append(pr)
            get_reviewers(pr['pullRequestId'], pr['title'])
            get_comments(pr['pullRequestId'], pr['title'], comment_trim, include_replies)

### MAIN CODE
@click.command()
@click.option(
    '--name', 
    prompt='Your name', envvar='DEVOPS_DISPLAY_NAME', 
    help='The display name in Azure DevOps')
@click.option(
    '--fetch', 
    prompt='How many rows to fetch',
    default=200,
    help='How many rows to fetch')
@click.option(
    '--comment-trim', 
    prompt='Ignore comments shorter than this length',
    default=50,
    help='Ignore comments shorter than this length')
@click.option(
    '--include-replies', 
    prompt='Include my comments that are replies to other comments',
    default=True,
    help='Include my comments that are replies to other comments')
def main(name, fetch, comment_trim, include_replies):

    global DEVOPS_DISPLAY_NAME 
    DEVOPS_DISPLAY_NAME = name

    print("getting pr's...")
    get_prs(fetch, comment_trim, include_replies)

    my_prs = list(filter(lambda pr: pr['createdBy'] == DEVOPS_DISPLAY_NAME, prs))
    print(f"---My PR's ({name}): {len(my_prs)}")

    my_reviews = list(filter(lambda r: r['createdBy'] == DEVOPS_DISPLAY_NAME, reviews))
    print(f"\n---My Reviews ({name}): {len(my_reviews)}")

    my_comments = list(filter(lambda c: c['createdBy'] == DEVOPS_DISPLAY_NAME, comments))
    print(f"\n---My Comments ({name}): {len(my_comments)}")

    create_md_file()
    write_stats(len(prs), len(my_prs), len(my_reviews), len(my_comments))
    write_my_prs(my_prs)
    write_my_reviews(my_reviews)
    write_my_comments(my_comments)

if __name__ == '__main__':
    main()