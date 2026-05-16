# Imports
import pandas as pd
from pathlib import Path
import re
from datetime import datetime


# Directory containing cleaned ECB transcripts
boe_dir = Path('data/transcripts_cleaned/BoE')

boe_complete = []
boe_remarks = []
boe_answers = []

link_pairs = {}

def extract_date_from_header(text):
    # Split the text into individual lines and remove any completely blank lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for i in range(4, len(lines) - 1): # Skip 4 first lines because that's where the header is
        # Check if the current line is entirely uppercase
        if lines[i].isupper():
            # If it is, the very next line is your date!
            return lines[i+1]
            
    return None

# Generate remarks / Q&A pairs

for transcript_path in sorted(boe_dir.iterdir()):
    if transcript_path.is_file() and transcript_path.suffix == '.txt':
        if 'opening' in transcript_path.name:
            date_text = re.findall(r'_(\d{6})', transcript_path.name)
            link_pairs[date_text[0]] = [transcript_path, 0]
        elif 'transcript' in transcript_path.name:
            date_text = re.findall(r'_(\d{6})', transcript_path.name)
            link_pairs[date_text[0]][1] = transcript_path

for date, links in link_pairs.items():
    data_rem = links[0].read_text(encoding='utf-8')
    data_qna = links[1].read_text(encoding='utf-8')

    # Process common information

    # Extract date from remarks
    date_str = extract_date_from_header(data_rem)
    clean_date_text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
    date = datetime.strptime(clean_date_text, "%A %d %B %Y")
    day_of_week = date.strftime('%a')

    date_text = date.strftime('%Y-%m-%d')

    bank = 'boe'

    # Build id
    id = f"{date.strftime('%Y%m%d')}-{bank}"

    # Retrieve governor
    if date < datetime.strptime('2020-05-16', "%Y-%m-%d"):
        chair = 'Mark Carney'
    else:
        chair = 'Andrew Bailey'

    # Retrieve remarks
    remarks = data_rem

    # Retrieve answers
    print(data_qna)


    break

    