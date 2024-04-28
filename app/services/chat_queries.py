import subprocess
from datetime import datetime, timedelta, date

import json
from datetime import datetime
from sqlalchemy import func
from ..models import Message, Base  # Assuming you've defined models corresponding to your table


def exact_search_by_keyword(search_term, session):
    messages = []
    try:
        query = func.plainto_tsquery('english', search_term)
        # Perform the query using both the full-text search and exact match criteria
        messages = session.query(Message).filter(
            Message.content_tsvector.op('@@')(query),
            Message.content.ilike(f"%{search_term}%")
        ).all()

        # Print the number of messages fetched
        print(f"Successfully fetched {len(messages)} messages from the database.")

    except Exception as e:
        # Handle exceptions and print an error message
        print(f"An unexpected error occurred: {e}")

    finally:
        # Ensure the database session is closed after the query
        session.close()

    # Return the list of messages that match the query
    return messages


def search_by_keyword(keyword, session):
    messages = []
    try:
        query = func.plainto_tsquery('english', keyword)
        messages = session.query(Message).filter(Message.content_tsvector.op('@@')(query)).all()
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