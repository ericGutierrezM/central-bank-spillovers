# Imports
import pandas as pd
from pathlib import Path
import re
from datetime import datetime


# Directory containing cleaned ECB transcripts
fed_dir = Path('data/transcripts_cleaned/Fed')

fed_complete = []
fed_remarks = []
fed_answers = []

def clean_transcript_pages(text):
    # 1. Target the full multi-line block: 
    # Date -> [Chair]'s Press Conference -> FINAL -> Page X of Y
    block_pattern = (
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},\s+\d{4}\s*\n"   # Matches the date (e.g., March 18, 2015)
        r".*?(?:Press Conference)\s*\n" # Matches the title line (e.g., Chair Yellen's Press Conference)
        r".*?FINAL\s*\n"                # Matches the FINAL tag
        r".*?Page\s+\d+\s+of\s+\d+\s*"  # Matches Page X of Y
    )
    
    # Replace the whole block with a single space so split sentences reconnect cleanly
    text = re.sub(block_pattern, " ", text, flags=re.IGNORECASE)
    
    # 2. Catch-all for any stray page numbers that might be missing the date/title above them
    stray_page_pattern = r"^\s*Page\s+\d+\s+of\s+\d+\s*$"
    text = re.sub(stray_page_pattern, "", text, flags=re.MULTILINE | re.IGNORECASE)
    
    return text

for transcript_path in sorted(fed_dir.iterdir()):
    if transcript_path.is_file() and transcript_path.suffix == '.txt':
        data = transcript_path.read_text(encoding='utf-8')

        # Extract date from filename
        date_text = re.findall(r'_(\d{8})', transcript_path.name)
        date = datetime.strptime(date_text[0], "%Y%m%d")
        day_of_week = date.strftime('%a')

        # Extract bank from filename
        bank = 'fed'

        # Build id
        id = f"{date.strftime('%Y%m%d')}-{bank}"

        # Retrieve chair
        chair_raw = data.split('.')[1].split()[-1]

        name_map = {
            "YELLEN": "Janet Yellen",
            "POWELL": "Jerome Powell"        
        }
        chair = name_map.get(chair_raw, "Jerome Powell") 
        # The only transcript that failed because of a formatting change
        # was one of Powell's

        # Remove page marks
        cleaned_text = clean_transcript_pages(data)

        # Retrieve remarks
        pattern = r"^[A-Z\s\-]{4,}\."
        matches = list(re.finditer(pattern, cleaned_text, flags=re.MULTILINE))
        if len(matches) >= 2:
            second_name_index = matches[1].start()
            remarks = cleaned_text[:second_name_index].strip()
            
        else:
            remarks = cleaned_text.strip()

        # Retrieve answers from Q&A
        q_n_a = cleaned_text[second_name_index:].strip()
        speaker_pattern = r"^([A-Z\s\-]{4,}\.)"
        parts = re.split(speaker_pattern, q_n_a, flags=re.MULTILINE)

        chair_answers = []

        # parts[0] is any loose text before the first split (usually empty here)
        # After that, it alternates: parts[1] is Speaker, parts[2] is Text, parts[3] is Speaker, etc.
        for i in range(1, len(parts) - 1, 2):
            speaker = parts[i].strip()
            text = parts[i+1].strip()
            
            # Check if the speaker is the Chair (Using .startswith catches CHAIR, CHAIRMAN, etc.)
            if speaker.startswith("CHAIR"):
                # We append just the text, leaving the "CHAIR YELLEN." part behind
                chair_answers.append(text)

        # Join all the answers together into a clean, single string separated by newlines
        answers = "\n\n".join(chair_answers)

        # Concatenate remarks and answers
        complete_text = remarks + '\n\n' + answers

        # Word counts
        complete_word_count = len(complete_text.split())
        remarks_word_count = len(remarks.split())
        answers_word_count = len(answers.split())

        # Append to corpus
        fed_complete.append({
            "id": id,
            "date": date.strftime('%Y-%m-%d'),
            "bank": bank,
            "chair": chair,
            "day_of_week": day_of_week,
            "text": complete_text,
            "word_count": complete_word_count
        })

        fed_remarks.append({
            "id": id,
            "date": date.strftime('%Y-%m-%d'),
            "bank": bank,
            "chair": chair,
            "day_of_week": day_of_week,
            "text": remarks,
            "word_count": remarks_word_count
        })

        fed_answers.append({
            "id": id,
            "date": date.strftime('%Y-%m-%d'),
            "bank": bank,
            "chair": chair,
            "day_of_week": day_of_week,
            "text": answers,
            "word_count": answers_word_count
        })

fed_complete_df = pd.DataFrame(fed_complete).set_index('id')
fed_remarks_df = pd.DataFrame(fed_remarks).set_index('id')
fed_answers_df = pd.DataFrame(fed_answers).set_index('id')

fed_complete_df.to_csv('data/corpus/fed_complete.csv')
fed_remarks_df.to_csv('data/corpus/fed_remarks.csv')
fed_answers_df.to_csv('data/corpus/fed_answers.csv')