import json
import re
from pathlib import Path
from typing import Union

import arabic_reshaper
import demoji
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """Generate xhat statistics from a telegram chat json file
    """
    def __init__(self, chat_json: Union[str, Path]) :
        """
        :param chat_json: path to telegram export json file
        """
        # load chat data
        logger.info(f"loading chat data from {chat_json}")
        with open(chat_json) as f:
            self.chat_data = json.load(f)

        self.normalizer = Normalizer()

        # load stopwords
        stop_words = open(DATA_DIR / 'stopwords.txt').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))


    def deEmojify(self, text):
         regrex_pattern = re.compile(pattern = "["
          "\u2069"
           "\u2066"
                 "]+", flags = re.UNICODE)
         return demoji.replace(regrex_pattern.sub(r'',text), " ")


   
    def generate_word_cloud(self, output_dir: Union[str, Path]):
        """generate a word cloud from the chat data

        :param output_dir: path to output directory for word cloud image
        """
        logger.info("loading text content...")
        text_content = ''
        
        for msg in self.chat_data['messages']:
             if type(msg['text']) is str:
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda item: item not in self.stop_words, tokens))
                text_content += f" {' '.join(tokens)}" 


        # remove emoji, normalize, reshape for final word cloud
        text_content = self.deEmojify(text_content)
        text_content = self.normalizer.normalize(text_content)
        text_content = arabic_reshaper.reshape(text_content)
        text_content = get_display(text_content)
        
        #to solve arabic problem
        text_content = arabic_reshaper.reshape(text_content)
        text_content = get_display(text_content)

        logger.info("generating word cloud...")
        # generate word cloud
        wordcloud = WordCloud(
            width=1200, height=1200,
            font_path=str(DATA_DIR / 'Vazirmatn-Black.ttf'),
            background_color='white'
        ).generate(text_content)

        logger.info(f"saving word cloud to {output_dir}")
        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png'))

if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR / 'result.json')
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)

    print('Done!')
  