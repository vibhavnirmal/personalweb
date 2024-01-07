from nltk.corpus import stopwords
import matplotlib
matplotlib.use('Agg')
# this is needed to avoid error: _tkinter.TclError: no display name and no $DISPLAY environment variable
import matplotlib.pyplot as plt

import io



class JobDescUtils:
    def __init__(self):
        pass

    def preprocess_text(self, text):
        # convert to lower case
        text = text.lower()

        # remove punctuations
        punctuations = '''+!()-[]{};:'"\,<>./?@#$%^&*_~'''
        text = ''.join([char for char in text if char not in punctuations])

        # convert to lower case
        text = text.lower()

        # remove numbers
        text = ''.join([char for char in text if not char.isdigit()])

        # remove whitespaces
        text = ' '.join(text.split())

        return text

    def extract_keywords(self, listofsentences):
        text = self.preprocess_text(' '.join(listofsentences))

        # extract keywords from list of sentences
        keywords = []
        for sentence in text.split('.'):
            keywords.extend([word for word in sentence.split() if word not in stopwords.words('english')])

        return keywords

    def get_keyword_freq(self, keywords):
        # keyword frequency
        keyword_freq = {}

        for keyword in keywords:
            if keyword in keyword_freq:
                keyword_freq[keyword] += 1
            else:
                keyword_freq[keyword] = 1

        return keyword_freq
    
    def get_top_keywords(self, keyword_freq, top_n=10):
        # get top n keywords
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

        return top_keywords
    
    def plot_keyword_freq(self, keyword_freq, top_n=10):
        # plot keyword frequency
        top_keywords = self.get_top_keywords(keyword_freq, top_n)

        plt.figure(figsize=(10, 7))
        plt.bar([x[0] for x in top_keywords], [x[1] for x in top_keywords])
        plt.xticks(rotation=45)
        plt.xlabel('Keywords')
        plt.ylabel('Frequency')
        plt.title('Keyword Frequency')

        # return jpeg image to show in html
        buf = io.BytesIO()
        plt.savefig(buf, format='jpeg')
        buf.seek(0)

        return buf