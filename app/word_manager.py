import os
from typing import Dict, Set
from word_sources.word_source import WordSource

class WordManager:
    def __init__(self, word_source: WordSource):
        self.word_source = word_source

    def process_words(self, data_lake_path: str, data_mart_path: str) -> Dict[int, int]:
        new_words_count = {}

        self.word_source.save_raw_data(data_lake_path)

        words_by_length = self.word_source.get_words()
        if not os.path.isdir(data_mart_path):
            os.makedirs(data_mart_path)

        for length, word_set in words_by_length.items():
            file_name = f"words_{length}.txt"
            file_path = os.path.join(data_mart_path, file_name)

            existing = set()
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = {line.strip() for line in f if line.strip()}

            new_set = word_set - existing
            new_words_count[length] = len(new_set)

            combined = existing.union(word_set)
            with open(file_path, 'w', encoding='utf-8') as f:
                for w in sorted(combined):
                    f.write(w + "\n")

        return new_words_count
