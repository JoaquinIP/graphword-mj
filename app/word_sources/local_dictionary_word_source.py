import os
import re
from typing import Dict, Set
from .word_source import WordSource
from .exceptions import WordSourceException

class LocalDictionaryWordSource(WordSource):
    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        self.file_path = file_path
        self.raw_content = ""

    def get_words(self) -> Dict[int, Set[str]]:
        words_by_length = {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()

            all_words = re.findall(r"\b[a-zA-Z]+\b", self.raw_content)

            for w in all_words:
                w_lower = w.lower()
                if len(w_lower) >= 3:
                    words_by_length.setdefault(len(w_lower), set()).add(w_lower)

            return words_by_length
        except OSError as e:
            raise WordSourceException(f"Error reading file {self.file_path}: {e}")

    def save_raw_data(self, data_lake_path: str) -> None:
        try:
            if not os.path.isdir(data_lake_path):
                os.makedirs(data_lake_path)

            base_name = os.path.basename(self.file_path)
            file_name = f"localdict_{base_name}.txt"
            file_path = os.path.join(data_lake_path, file_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Local dictionary from: {self.file_path}\n")

        except OSError as e:
            raise WordSourceException(f"Error saving file to datalake: {e}")

    def _is_valid_word(self, word: str) -> bool:
        return word.isalpha() and len(word) >= 3
