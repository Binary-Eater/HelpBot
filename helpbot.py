from dotenv import load_dotenv, find_dotenv
# Don't use cPickle for Python 2 because it doesn't handle unicode objects
# Probably better to use Python 3 for fast pickle loading
import pickle
import requests as req
# To use the nps_chat data nltk.download() must be called
import nltk
import os
import sys
from fbchat import Client
from fbchat.models import *
import re

class AnswerClient(Client):
    def __init__(self, email, password, classifier):
        Client.__init__(self, email, password)
        self.classifier = classifier
        self.splitter = re.compile('[ ,]+')
        # TODO build a training model using stack overflow data
        self.question_words = ['what', 'where', 'when','how','why','did','do','does','have','has','am','is','are','can','could','may','would','will','should'
"didn't","doesn't","haven't","isn't","aren't","can't","couldn't","wouldn't","won't","shouldn't"]

    def onMessage(self, mid, author_id, message_object, thread_id, thread_type, ts, metadata, msg, **kwargs):
        msg_type = self.classifier.classify(msg)
        question_uri_data = None
        if message_object.text.startswith('ansbot'+' '):
            msg_arr = self.splitter.split(message_object.text)
            msg_arr = msg_arr[1:]
            question_uri_data = '%20'.join(msg_arr)
        elif msg_type == 'ynQuestion' or msg_type == 'whQuestion' or '?' in message_object.text or any(message_object.text.startswith(qword) for qword in self.question_words):
            msg_arr = self.splitter.split(message_object.text)
            question_uri_data = '%20'.join(msg_arr)
        if question_uri_data != None and question_uri_data != '':
            req_url = 'https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=relevance' + '&q='+question_uri_data+'&answers=1&site=stackoverflow'
            headers = {'Accept': 'application/json; charset=utf-8', 'User-Agent': 'RandomHeader'}
            resp = req.get(req_url, headers=headers)
            query_data = resp.json().get('items')
            didAns = False
            for q in query_data:
                ans_id = q.get('accepted_answer_id')
                q_score = q.get('score')
                if q_score == None or q_score < 0:
                    continue
                if ans_id == None:
                    msg_txt = q.get('link') + '\n\n- From AnswerBot'
                    self.send(Message(text=msg_txt), thread_id=thread_id, thread_type=thread_type)
                    break
                ans_url = 'https://api.stackexchange.com/2.2/answers/' + str(ans_id) + '?order=desc&filter=withbody&sort=creation&site=stackoverflow'
                ans_resp = req.get(ans_url, headers=headers)
                ans_data = ans_resp.json().get('items')
                if ans_data == None or len(ans_data) == 0:
                    self.send(Message(text='Wow! I cannot respond to this question.... - AnswerBot'), thread_id=thread_id, thread_type=thread_type)
                else:
                    ans_txt = ans_data[0].get('body')
                    if ans_txt != None or ans_txt != '':
                        msg_txt = ans_txt + '\n\n' + q.get('link') + '\n\n- From AnswerBot'
                        self.send(Message(text=msg_txt), thread_id=thread_id, thread_type=thread_type)
                didAns = True
                break
            if not didAns:
                self.send(Message(text='Wow! I cannot respond to this question.... - AnswerBot'), thread_id=thread_id, thread_type=thread_type)

def dialogue_component_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features['contains({})'.format(word.lower())] = True
    return features

def init_data():
    load_dotenv(find_dotenv())
    cl_pickle_fname = os.getenv('PICKLE_FILENAME')
    classifier = None
    if cl_pickle_fname and cl_pickle_fname != '':
        try:
            classifier = pickle.load( open(cl_pickle_fname, 'rb') )
        except IOError as e:
            classifier = None
    
    if not classifier:
        nltk.download('punkt')
        nltk.download('nps_chat')
        posts = nltk.corpus.nps_chat.xml_posts()[:10000]
        featuresets = [(dialogue_component_features(post.text), post.get('class')) for post in posts]
        size = int(len(featuresets) * 0.1)
        train_set, test_set = featuresets[size:], featuresets[:size]
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        if cl_pickle_fname:
            pickle.dump(classifier, open(cl_pickle_fname, 'wb') )
    return classifier

def load_callback(classifier):
    uid = os.getenv('FB_USER')
    passwd = os.getenv('FB_PASSWORD')
    if uid == None or passwd == None:
        print >> sys.stderr, 'Please provide FB_USER and FB_PASSWORD in .env file'
        return
    client = AnswerClient(uid, passwd, classifier)
    client.listen()

if __name__ == '__main__':
    cl = init_data()
    load_callback(cl)
