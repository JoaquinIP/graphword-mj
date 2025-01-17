import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from word_manager import WordManager
from word_sources.local_dictionary_word_source import LocalDictionaryWordSource
from word_sources.project_gutenberg_word_source import ProjectGutenbergWordSource
from word_sources.exceptions import WordSourceException
from config import DATA_LAKE_PATH, DATA_MART_PATH

def main():
    print("Select the data source:")
    print("1. Local dictionary file")
    print("2. Project Gutenberg Book")
    option = input("Enter 1 or 2: ")

    try:
        if option == '1':
            file_path = input("Write the path to the local dictionary file: ")
            word_source = LocalDictionaryWordSource(file_path)
        elif option == '2':
            book_url = input("Write the URL of the Project Gutenberg book: ")
            word_source = ProjectGutenbergWordSource(book_url)
        else:
            print("Invalid option")
            return

        word_manager = WordManager(word_source)
        new_words_count = word_manager.process_words(DATA_LAKE_PATH, DATA_MART_PATH)
        print("Processing completed.")
        
        total_new_words = sum(new_words_count.values())
        print(f"Total number of new words added: {total_new_words}")
        for length, count in sorted(new_words_count.items()):
            print(f"Length {length}: {count} new words")
    except (WordSourceException, ValueError, IOError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
