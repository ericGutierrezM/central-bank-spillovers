# Imports
import pandas as pd
from pathlib import Path
import re
from datetime import datetime


# Directory containing cleaned ECB transcripts
ecb_dir = Path('data/transcripts_cleaned/ECB')

ecb_complete = []
ecb_remarks = []
ecb_answers = []

def extract_only_answers(text):
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
    answer_paragraphs = []
            
    for para in paragraphs:
        para_lower = para.lower()
                
        # Rule 1: If it ends with a question mark, it's a journalist's question.
        if para.endswith('?'):
            continue
                    
        # Rule 2: If the paragraph ends with "my first/second question" instead of a '?'
        if "question" in para_lower[-30:] and ("my" in para_lower[-30:] or "first" in para_lower[-30:] or "second" in para_lower[-30:]):
            continue
                    
        answer_paragraphs.append(para)
                
    # Join all the answer paragraphs back together with clean spacing
    return "\n\n".join(answer_paragraphs)

# Loop over every file under the ECB folder
for transcript_path in sorted(ecb_dir.iterdir()):
    if transcript_path.is_file() and transcript_path.suffix == '.txt':
        data = transcript_path.read_text(encoding='utf-8')

        # Extract date from filename
        date_text = re.findall(r'_(\d{8})', transcript_path.name)
        date = datetime.strptime(date_text[0], "%Y%m%d")
        day_of_week = date.strftime('%a')

        # Extract bank from filename
        bank = re.findall(r'(\w+)_', transcript_path.name)[0].lower() # We can just hard-code it

        # Build id
        id = f"{date.strftime('%Y%m%d')}-{bank}"

        # Retrieve president
        chair = data.split(',')[0]

        # Retrieve remarks
        parts = re.split(r"\*\s*\*\s*\*", data, maxsplit=1)
        remarks = parts[0].strip()

        # Retrieve answers from Q&A
        answers = extract_only_answers(parts[1].strip())

        # Concatenate remarks and answers
        complete_text = remarks + '\n\n' + answers

        # Word counts
        complete_word_count = len(complete_text.split())
        remarks_word_count = len(remarks.split())
        answers_word_count = len(answers.split())
        
        # Append to corpus
        ecb_complete.append({
            "id": id,
            "date": date.strftime('%Y-%m-%d'),
            "bank": bank,
            "chair": chair,
            "day_of_week": day_of_week,
            "text": complete_text,
            "word_count": complete_word_count
        })

        ecb_remarks.append({
            "id": id,
            "date": date.strftime('%Y-%m-%d'),
            "bank": bank,
            "chair": chair,
            "day_of_week": day_of_week,
            "text": remarks,
            "word_count": remarks_word_count
        })

        ecb_answers.append({
            "id": id,
            "date": date.strftime('%Y-%m-%d'),
            "bank": bank,
            "chair": chair,
            "day_of_week": day_of_week,
            "text": answers,
            "word_count": answers_word_count
        })

ecb_complete_df = pd.DataFrame(ecb_complete).set_index('id')
ecb_remarks_df = pd.DataFrame(ecb_remarks).set_index('id')
ecb_answers_df = pd.DataFrame(ecb_answers).set_index('id')

ecb_complete_df.to_csv('data/corpus/ecb_complete.csv')
ecb_remarks_df.to_csv('data/corpus/ecb_remarks.csv')
ecb_answers_df.to_csv('data/corpus/ecb_answers.csv')