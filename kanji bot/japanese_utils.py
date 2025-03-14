import requests
import urllib.parse

def get_kanji_info(kanji):
    try:
        response = requests.get(f'https://kanjiapi.dev/v1/kanji/{urllib.parse.quote(kanji)}')
        if response.status_code == 200:
            data = response.json()
            stroke_count = data.get('stroke_count', 'Unknown')
            grade = data.get('grade', 'N/A')
            meanings = ', '.join(data.get('meanings', []))
            kun_readings = ', '.join(data.get('kun_readings', []))
            on_readings = ', '.join(data.get('on_readings', []))
            
            return f"Strokes: {stroke_count}\nGrade: {grade}\nMeanings: {meanings}\nKun readings: {kun_readings}\nOn readings: {on_readings}"
    except Exception as e:
        print(f"Error getting kanji info: {str(e)}")
        return None

def get_example_sentences(data):
    try:
        examples = []
        if 'senses' in data:
            for sense in data['senses']:
                if len(examples) >= 2:  # Get max 2 examples
                    break
                if 'examples' in sense:
                    for example in sense['examples']:
                        jp = example.get('japanese', '')
                        en = example.get('english', '')
                        if jp and en:
                            examples.append(f"🔸 {jp}\n   {en}")
        
        if examples:
            return "\nExample Usage:\n" + "\n\n".join(examples)
        return None
    except Exception as e:
        print(f"Error getting examples: {str(e)}")
        return None

def lookup_word(word):
    try:
        # Encode the word for URL
        encoded_word = urllib.parse.quote(word)
        url = f'https://jisho.org/api/v1/search/words?keyword={encoded_word}'
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code != 200:
            return f"Error: Could not connect to dictionary (Status: {response.status_code})", None

        data = response.json()
        if not isinstance(data, dict) or 'data' not in data or not data['data']:
            return f"No results found for '{word}'", None

        entries = data['data']
        if not entries or not isinstance(entries, list):
            return f"No valid entries found for '{word}'", None

        entry = entries[0]
        info_parts = []

        # Process Japanese data
        if 'japanese' in entry and entry['japanese']:
            jp_data = entry['japanese'][0]
            if isinstance(jp_data, dict):
                if 'word' in jp_data:
                    info_parts.append(f"Word: {jp_data['word']}")
                if 'reading' in jp_data:
                    info_parts.append(f"Reading: {jp_data['reading']}")

        # Process meanings and examples
        if 'senses' in entry and entry['senses']:
            sense = entry['senses'][0]  # Get first sense
            # Add meanings
            if 'english_definitions' in sense:
                definitions = sense['english_definitions']
                if isinstance(definitions, list) and definitions:
                    info_parts.append(f"Meanings: {'; '.join(definitions)}")
            
            # Add examples directly from sense
            if 'examples' in sense:
                examples = []
                for ex in sense['examples'][:2]:  # Get up to 2 examples
                    jp = ex.get('japanese', '')
                    en = ex.get('english', '')
                    if jp and en:
                        examples.append(f"🔸 {jp}\n   {en}")
                if examples:
                    info_parts.append("\nExample Usage:\n" + "\n\n".join(examples))

        # Process kanji details (without diagrams)
        kanji_details = []
        if info_parts and 'Word: ' in info_parts[0]:
            word_kanji = info_parts[0].replace('Word: ', '')
            for char in word_kanji:
                if 0x4E00 <= ord(char) <= 0x9FFF:  # Is kanji
                    kanji_info = get_kanji_info(char)
                    if kanji_info:
                        kanji_details.append(f"Details for {char}:\n{kanji_info}")

        # Combine all information
        if not info_parts:
            return f"No information found for '{word}'", None

        full_info = "\n".join(info_parts)
        if kanji_details:
            full_info += "\n\n" + "\n\n".join(kanji_details)

        return full_info, None

    except requests.RequestException as e:
        return f"Network error: {str(e)}", None
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # Debug line
        return f"Error processing response for '{word}'", None
