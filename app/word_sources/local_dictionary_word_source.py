# word_sources/local_dictionary_word_source.py

import os
import re
from typing import Dict, Set
from .word_source import WordSource
from .exceptions import WordSourceException

class LocalDictionaryWordSource(WordSource):
    def __init__(self, file_path: str):
        if not os.path.isfile(file_path):
            raise ValueError(f"Archivo inexistente: {file_path}")
        self.file_path = file_path
        self.raw_content = ""  # contenido del diccionario local

    def get_words(self) -> Dict[int, Set[str]]:
        """
        Lee el archivo local, almacena su contenido en 'self.raw_content',
        filtra palabras >= 3 letras (o ajusta la condición que desees),
        y retorna {longitud: set(...)}.
        """
        words_by_length = {}
        try:
            # Leer todo el contenido
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()  # guardamos en raw_content

            # Extraer las palabras con regex similar a PG
            # o simplemente line by line. 
            # Aqui usaremos una regex, igual que project_gutenberg
            all_words = re.findall(r"\b[a-zA-Z]+\b", self.raw_content)

            for w in all_words:
                w_lower = w.lower()
                # Ignorar <3 letras
                if len(w_lower) >= 3:
                    words_by_length.setdefault(len(w_lower), set()).add(w_lower)

            return words_by_length
        except OSError as e:
            raise WordSourceException(f"Error leyendo archivo {self.file_path}: {e}")

    def save_raw_data(self, data_lake_path: str) -> None:
        """
        Similar a ProjectGutenbergWordSource: creamos un archivo 'localdict_{basename}.txt'
        pero NO copiamos todo el archivo original. Solo escribimos un encabezado o algo mínimo.
        """
        try:
            if not os.path.isdir(data_lake_path):
                os.makedirs(data_lake_path)

            base_name = os.path.basename(self.file_path)
            file_name = f"localdict_{base_name}.txt"
            file_path = os.path.join(data_lake_path, file_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                # Guardamos un encabezado mínimo
                f.write(f"# Local dictionary from: {self.file_path}\n")

        except OSError as e:
            raise WordSourceException(f"Error guardando archivo en datalake: {e}")

    def _is_valid_word(self, word: str) -> bool:
        """
        (Opcional) Si quisieras una validación distinta, la cambiarías aquí.
        Pero en la versión 'similar a PG', la mayor parte del filtrado
        ya se hace con la regex y la condición >= 3 letras.
        """
        return word.isalpha() and len(word) >= 3
