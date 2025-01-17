from abc import ABC, abstractmethod
from typing import Dict, Set

class WordSource(ABC):
    @abstractmethod
    def get_words(self) -> Dict[int, Set[str]]:
        """Returns {length: wordset}."""
        pass

    @abstractmethod
    def save_raw_data(self, data_lake_path: str) -> None:
        """Save raw data (e.g. original text) in data_lake/."""
        pass
