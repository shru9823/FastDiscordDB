import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from aiofiles import open as aio_open
import backoff
import re

# Set up logging for the application
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Executor for handling multiple threads for potential asynchronous tasks
executor = ThreadPoolExecutor(max_workers=7)

async def execute_export_command(token, channel_id, formatted_date):
    """
    Asynchronously executes an export command using an external CLI tool,
    returning the messages as JSON.
    Handles subprocess creation, execution, and file reading.
    """
    # Define the filename with timestamp to avoid collisions and maintain uniqueness
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    try:
        # Start an asynchronous subprocess to run the export command
        process = await asyncio.create_subprocess_exec(
            "dotnet", "/Users/shruti/Downloads/DiscordChatExporter.Cli/DiscordChatExporter.Cli.dll", "export",
            "-t", token, "-c", channel_id, "-f", "Json",
            "--after", formatted_date, "--output", filename,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        # Wait for the process to complete and capture stdout and stderr
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"Export failed: {stderr.decode()}")
            error = stderr.decode()
            if re.search('not contain any messages within the specified period', error):
                return {}
            raise RuntimeError(f"Export failed: {stderr.decode()}")

        # Open and read the exported file asynchronously
        messages = {}
        async with aio_open(filename, 'r') as file:
            file_content = await file.read()
            return json.loads(file_content)['messages']
    except asyncio.CancelledError:
        logger.error("Subprocess was cancelled")
        raise HTTPException(status_code=500, detail="Export command was cancelled")
    except Exception as e:
        logger.error(f"Error during export: {e}")
        raise HTTPException(status_code=500, detail=f"Error during export: {str(e)}")

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
async def insert_batch(session, batch, channel_id):
    """
    Inserts a batch of messages into the database with retry logic using backoff,
    handling potential exceptions and rollbacks.
    """
    try:
        # SQL execution of batch insert using prepared statements
        await session.execute(text("""
                    INSERT INTO discord_chats (message_id, channel_id, message_date, content, content_tsvector)
                    VALUES (:message_id, :channel_id, :message_date, :content, to_tsvector('english', :content))
                    ON CONFLICT (message_id, message_date) DO NOTHING
                """), [
            {'message_id': int(item['id']), 'channel_id': int(channel_id),
             'message_date': datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').date(),
             'content': item['content'], 'content_tsvector': text("to_tsvector('english', :content)")}
            for item in batch
        ])
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to insert batch: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert batch: {str(e)}")

async def export_chat(token, channel_id, session: AsyncSession):
    """
    Main function to export chat messages from a specified channel and insert
    them into a database. It handles full export workflow from command execution
    to database insertion.
    """
    try:
        # Calculate date range for the messages to be exported
        now = datetime.now()
        days_ago = now - timedelta(days=7)
        formatted_date = days_ago.strftime("%Y-%m-%d")

        # Execute the export command
        messages = await execute_export_command(token, channel_id, formatted_date)

        # Prepare for batching and insertion
        batch_size = 1000
        total_inserted = 0
        total_messages = len(messages)

        # Handling cases where no messages are found
        if total_messages == 0:
            raise HTTPException(status_code=404,
                                detail="No chat messages found for the past 7 days")

        # Insert messages in batches to the database
        for i in range(0, total_messages, batch_size):
            batch = messages[i:i + batch_size]
            try:
                await insert_batch(session, batch, channel_id)
                total_inserted += len(batch)
            except Exception as e:
                logger.error(f"Insertion failed for a batch: {e.detail}")
                continue  # Optionally, handle failed batches differently

        # Check if all messages were successfully inserted
        if total_inserted < total_messages:
            raise HTTPException(status_code=500,
                                detail=f"Failed to insert some messages. Successfully inserted: {total_inserted}, Failed: {total_messages - total_inserted}")

        return {"message": f"Successfully inserted {total_inserted} messages into the database."}
    except HTTPException as e:
        logger.error(f"Overall export failed: {e.detail}")
        raise
    except Exception as e:
        logger.error("Unexpected error during export")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error during export: {str(e)}")
