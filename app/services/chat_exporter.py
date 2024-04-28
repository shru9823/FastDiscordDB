import subprocess
import json
from datetime import datetime, timedelta, date

import json
from sqlalchemy import create_engine, text
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


        # Prepare bulk insert data
        bulk_data = [{
            'message_id': item['id'],
            'channel_id': channel_id,
            'message_date': datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').date(),
            'content': item['content'],
            'content_tsvector': text("to_tsvector('english', :content)")  # Prepare tsvector during bulk insertion
        } for item in messages]

        # Bulk insert using execute with text SQL
        sql = text("""
                    INSERT INTO discord_chats (message_id, channel_id, message_date, content, content_tsvector)
                    VALUES (:message_id, :channel_id, :message_date, :content, to_tsvector('english', :content))
                """)
        session.execute(sql, bulk_data)
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
