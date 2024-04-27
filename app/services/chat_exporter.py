import subprocess
import json
from datetime import datetime, timedelta, date

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..models import Message, Base  # Assuming you've defined models corresponding to your table


def export_chat(token, channel_id, session):
    try:
        # Calculate the date 7 days ago
        days_ago = datetime.now() - timedelta(days=90)
        formatted_date = days_ago.strftime("%Y-%m-%d")
        print("Starting chat export...")
        current_timestamp = datetime.now()
        filename = f"{current_timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"  # Creates a filename with the format: YYYY-MM-DD_HH-MM-SS.json
        # Build the command to call DiscordChatExporter
        command = [
            "dotnet", "/Users/shruti/Downloads/DiscordChatExporter.Cli/DiscordChatExporter.Cli.dll", "export",
            "-t", token,
            "-c", channel_id,
            "-f", "Json",
            "--after", formatted_date,
            "--output", filename
        ]
        print("Command built:", command)

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Export failed: {result.stderr}")

        print("Export successful, processing results...")

        # Load JSON data
        messages = None
        with open(filename, 'r') as file:
            messages = json.load(file)['messages']

        print("Messages loaded successfully:", messages)

        # Insert messages into the database
        for item in messages:
            message_date = datetime.strptime(item['timestamp'],
                                             '%Y-%m-%dT%H:%M:%S.%f%z').date()  # Parse timestamp to date
            db_message = Message(
                message_id=item['id'],
                channel_id=channel_id,
                message_date=message_date,
                content=item['content']
            )
            session.add(db_message)

        session.commit()
        print(f"Successfully inserted {len(messages)} messages into the database.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while exporting chats: {e}")
    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding the JSON data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        session.close()
