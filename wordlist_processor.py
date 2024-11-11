# wordlist_processor.py
import logging

def load_wordlist(wordlist_path):
    try:
        with open(wordlist_path, "r", encoding="latin-1") as file:
            # Filter out any blank lines to prevent empty password attempts
            wordlist = [line.strip() for line in file if line.strip()]
            logging.info(f"Loaded {len(wordlist)} passwords from the wordlist.")
            return wordlist
    except FileNotFoundError:
        logging.error("Wordlist file not found.")
    except IOError as e:
        logging.error(f"Error reading wordlist file: {e}")
    return None
