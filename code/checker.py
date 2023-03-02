from email.base64mime import body_encode
import time
from serpapi import GoogleSearch
import requests
import neuspell
from neuspell import BertChecker
from spellchecker import SpellChecker


class Checker:
    def __init__(self, sentence):
        self.sentence = sentence
        

    '''
    100 per month
    '''
    def google_correct(self):
        time.sleep(1)
        print(self.sentence)
        params = {
            "q": self.sentence,
            "hl": "en",
            "gl": "us",
            "api_key": "xxxxxx"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        search_information = results.get('search_information', {})
        return search_information.get('spelling_fix', self.sentence)

    '''
    250 per day
    '''
    def language_tool_correct(self):
        time.sleep(2)
        print(self.sentence)
        url = "https://dnaber-languagetool.p.rapidapi.com/v2/check"
        res_sentence = self.sentence
        payload = f"language=en-US&text={self.sentence.replace(' ', '%20')}"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'x-rapidapi-host': "dnaber-languagetool.p.rapidapi.com",
            'x-rapidapi-key': "xxxxxx"
        }

        response = requests.request("POST", url, data=payload.encode("utf-8"), headers=headers)
        for e in response.json().get('matches', []):
            if 'shortMessage' in e and 'replacements' in e and 'offset' in e and 'length' in e and e.get('shortMessage', '') == 'Spelling mistake':
                first_value = e.get('replacements', [{'value': 0}])[0]['value']
                if first_value:
                    res_sentence = res_sentence.replace(self.sentence[e['offset']:e['offset']+e['length']], first_value)
        return res_sentence

    '''
    1,000 transactions free per month 
    '''
    def bing_correct(self):
        api_key = "xxxxxx"
        res_sentence = self.sentence
        endpoint = "https://api.bing.microsoft.com/v7.0/spellcheck"
        data = {'text': self.sentence}
        params = {
        'mkt':'en-us',
        'mode':'proof'
        }
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': api_key,
        }
        response = requests.post(endpoint, headers=headers, params=params, data=data)
        # print(response.text)
        for e in response.json().get('flaggedTokens', []):
            if 'token' in e and 'suggestions' in e and e['suggestions']:
                res_sentence = res_sentence.replace(e['token'], e['suggestions'][0]['suggestion'])

        # print("pert: ", self.sentence)
        # print("correct: ", res_sentence)
        return res_sentence

        
    def neuspell_correct(self, neuchecker=None):
        if not neuchecker:
            neuchecker = BertChecker()
            neuchecker.from_pretrained("subwordbert-probwordnoise/")
        return neuchecker.correct(self.sentence)


    def spell_checker_correct(self,d=3):
        spell_checker = SpellChecker(distance=d)
        return spell_checker.correction(self.sentence)