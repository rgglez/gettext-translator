import traceback
import requests
import uuid

from translator_service import TranslatorService
from rich.pretty import pprint

################################################################################

class TranslatorAzure(TranslatorService):
    def __init__(self, config) -> None:
        self.config = config        

        path = '/translate'
        self.constructed_url = 'https://api.cognitive.microsofttranslator.com' + path
        self.params = {
            'api-version': '3.0',
            'from': self.config.srclang,
            'to': self.config.dstlang,
            'textType': 'html'
        }
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.config.apikey,
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': self.config.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
    # __init__

    ###########################################################################

    def translate_one_by_one(self, texts_to_translate):
        try:
            translated_texts = []
            for msgid in texts_to_translate:
                body = []
                body.append({
                    'text': msgid
                })

                request = requests.post(self.constructed_url, params=self.params, headers=self.headers, json=body)
                response = request.json()
                        
                translated_texts.append({
                    "msgid": msgid,
                    "msgstr": response[0]['translations'][0]['text']
                })
            # for
                    
            return translated_texts

        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()            
            return []
    # translate_one_by_one

    ###########################################################################

    def translate_in_bulk(self, texts_to_translate):
        try:
            char_count = 0
            total_texts = len(texts_to_translate)
            translated_texts = []
            body = []
            i = 0
            j = 0

            for msgid in texts_to_translate:
                i = i + 1
                j = j + 1
                body.append({
                    'text': msgid
                })
                char_count = char_count + len(msgid)
                if char_count > 49500 or i + 1 > total_texts or j + 1 > 1000:
                    request = requests.post(self.constructed_url, params=self.params, headers=self.headers, json=body)
                    response = request.json()

                    print("*********************************************************")
                    pprint(response)
                    print("*********************************************************")

                    for translation, original in zip(response, body):
                        translated_texts.append({
                            "msgid": original['text'],
                            "msgstr": translation['translations'][0]['text']
                        })
                    # for

                    body = []
                    char_count = 0
                    j = 0
                # if
            # for

            return translated_texts

        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()
            return []
    # translate_in_bulk
# TranslatorAzure