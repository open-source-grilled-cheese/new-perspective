import os
import sys
import newspaper
import json
from urllib.parse import urlparse
from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


API_KEY = ''
environment_id = 'system'
collection_id = 'news-en'

def get_url():
    return "https://www.washingtonpost.com/politics/believe-it-or-not-bernie-sanders-is-relaxing/2019/11/09/f83a4030-fff8-11e9-8bab-0fc209e065a8_story.html"
    #for l in sys.stdin:
    #    url = l
    return url
    
def get_title(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    # print("article title: ".format(article.title))
    return article.title

def watson_auth():
    authenticator = IAMAuthenticator(API_KEY)
    discovery = DiscoveryV1(
        version='2019-04-30',
        authenticator=authenticator
    )
    discovery.set_service_url('https://gateway.watsonplatform.net/discovery/api')

    return discovery

    # Env and Collection IDs

def first_query(discovery, title):
    firstDoc = discovery.query(environment_id, collection_id, filter="title:{}".format(title), query="title:{}".format(title), deduplicate = True, deduplicate_field=title, count = 20)

    # print(firstDoc)
    return firstDoc

def second_query(discovery, docID, docurl, validHosts, alignment):
    #Insert code using data from first document to find similar documents
    secondDoc = discovery.query(environment_id, collection_id, query = "host:{}".format(" ".join(validHosts)),
                                similar=True, similar_document_ids=docID, count = 5, deduplicate = True)  

    docInfo = (secondDoc, alignment)
    return docInfo

def format_output(docsInfo):
    output = []
    for doc in docsInfo:
        title = doc[0].get_result()['results'][0]['title']
        url = doc[0].get_result()['results'][0]['url']
        bias = doc[1]
        obj = {
            "title": title,
            "url": url,
            "bias": bias
        }
        output.append(obj)
    return output

def main():
    url = get_url()
    title = get_title(url)
    docSource = urlparse(get_url()).netloc
    docSource = docSource[4:]

    discover = watson_auth()
    firstDoc = first_query(discover, title)
    #docID = print(json.dumps(firstDoc.get_result()[0], indent=2))
    #docID = firstDoc.get_result()['results'][0]['id']
    docID = firstDoc.get_result()['results'][0]['id']
    docTitle = firstDoc.get_result()['results'][0]['title']
    #docSource = firstDoc.get_result()['results'][0]['host']
    #print(docSource)
    #docConcepts = firstDoc.get_results()['enrichments'][0]['options']['concepts']
    #print(docConcepts)

    #Filter Sources
    center = ["bbc.com", "apnews.com", "reuters.com", "npr.org", "abcnews.go.com", "wsj.com", "nytimes.com", "politico.com", "cbsnews.com", "businessinsider.com", "fortune.com"]
    left = ["cnn.com", "msnbc.com", "washingtonpost.com", "vox.com", "newyorker.com", "theatlantic.com", "huffingtonpost.com", "vanityfair.com", "progressive.org"]
    right =["foxnews.com", "theamericanconservative.com", "nypost.com", "reason.com"]

    alreadyFound = False
    validHosts = ''

    if not alreadyFound:
        for site in left:
            if site in docSource:
                alreadyFound = True
                validHosts = center+right
                secondDocFirst = second_query(discover, docID, docTitle, center, "center")
                secondDocSecond = second_query(discover, docID, docTitle, right, "right")
                

    if not alreadyFound:
        for site in center:
            if site in docSource:
                alreadyFound = True
                validHosts = left+right
                secondDocFirst = second_query(discover, docID, docTitle, left, "left")
                secondDocSecond = second_query(discover, docID, docTitle, right, "right")

    if not alreadyFound:
        for site in right:
            if site in docSource:
                alreadyFound = True
                validHosts = center+left
                secondDocFirst = second_query(discover, docID, docTitle, center, "center")
                secondDocSecond = second_query(discover, docID, docTitle, left, "left")

    output = json.dumps(format_output([secondDocFirst, secondDocSecond]))
    print(output)

def test():
    url = get_url()
    title = get_title(url)
    discover = watson_auth()
    data = first_query(discover, title)
    print(data.get_result()[''])

if __name__ == "__main__":
    main()

"""
query(self, environment_id, collection_id, filter=None, query=None,
natural_language_query=None, passages=None, aggregation=None, count=None,
return_=None, offset=None, sort=None, highlight=None, passages_fields=None,
passages_count=None, passages_characters=None, deduplicate=None,
deduplicate_field=None, similar=, similar_document_ids=None,
similar_fields=None, bias=None, spelling_suggestions=None,
x_watson_logging_opt_out=None, **kwargs)
"""
