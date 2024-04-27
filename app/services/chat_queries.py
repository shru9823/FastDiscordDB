import subprocess
from datetime import datetime, timedelta, date

import json
from datetime import datetime
from ..models import Message, Base  # Assuming you've defined models corresponding to your table


def search_by_keyword(keyword, session):
    try:
        messages = session.query(Message).filter(Message.content.ilike(f"%{keyword}%")).all()
        print(f"Successfully fetched {len(messages)} messages from the database.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        session.close()
    return messages

def search_by_date_range(start_date, end_date, session):
    try:
        messages = session.query(Message).filter(Message.message_date.between(start_date, end_date)).all()
        print(f"Successfully fetched {len(messages)} messages from the database.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        session.close()
    return messages