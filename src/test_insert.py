import json
from dotenv import load_dotenv
from parse import parse_match_json
from db import insert_data_pipeline

load_dotenv()   # loads DATABASE_URL so db.py can read it

with open("tests/fixtures/test_match.json") as f:
    match_json = json.load(f)

match_row, participant_rows, ban_rows = parse_match_json(match_json)
insert_match_data_pipeline(match_row, participant_rows, ban_rows)
print("done")