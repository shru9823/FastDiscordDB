import asyncio
import json
import logging
from datetime import datetime, timedelta

from elasticsearch import Elasticsearch, helpers
from fastapi import Depends, HTTPException
from aiofiles import open as aio_open
import backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")


async def execute_export_command(token, channel_id, formatted_date):
    """
    Executes the export command and returns the messages as JSON.
    """
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    # Async subprocess call
    process = await asyncio.create_subprocess_exec(
        "dotnet", "/Users/shruti/Downloads/DiscordChatExporter.Cli/DiscordChatExporter.Cli.dll", "export",
        "-t", token, "-c", channel_id, "-f", "Json",
        "--after", formatted_date, "--output", filename,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"Export failed: {stderr.decode()}")
        raise RuntimeError(f"Export failed: {stderr.decode()}")
    # Async file operations
    messages = {}
    async with aio_open(filename, 'r') as file:
        file_content = await file.read()  # Read the file content as a string
        messages = json.loads(file_content)['messages']  # Parse the string as JSON

    return messages


@backoff.on_exception(backoff.expo, Exception, max_tries=3)
async def insert_batch(batch, channel_id, index_name):

    actions = [
        {
            "_index": index_name,
            # Assuming 'message_id' can be used as a unique identifier
            "_id": item["id"],
            "_source": {"message_id": item['id'],
                        "channel_id": channel_id,  # Assuming each item has 'channel_id'
                        "message_date": datetime.strptime(item['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').date(),
                        "content": item['content']}
        }
        for item in batch
    ]

    try:
        responses = helpers.bulk(
            es, actions, raise_on_exception=False, raise_on_error=False)
        if responses[0]:  # Number of successfully executed operations
            logger.info(f"Successfully indexed {responses[0]} documents.")
        if len(responses[1]) > 0:  # Errors list
            logger.error(f"Errors occurred during bulk indexing: {responses[1]}")
            for error in responses[1]:
                logger.error(f"Error: {error}")  # Log each error detail
    except Exception as e:
        logger.exception(f"An error occurred during bulk insertion: {e}")
        raise

    return responses


async def create_index_if_not_exists(formatted_date):
    index_name = "chats-" + formatted_date

    # Create Elasticsearch index and mapping
    if not es.indices.exists(index=index_name):
        es_index = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "discord_analyzer": {
                            # "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "english_stop", "english_stemmer"]
                        }
                    },
                    "filter": {
                        "english_stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                        },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "message_id": {
                        "type": "keyword"
                    },
                    "channel_id": {
                        "type": "keyword"
                    },
                    "message_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "discord_analyzer"
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=es_index, ignore=[400])
    return index_name


async def export_chat(token, channel_id):
    """
    Exports chat messages and inserts them into the database.
    """
    try:
        now = datetime.now()
        days_ago = now - timedelta(days=7)
        formatted_date = days_ago.strftime("%Y-%m-%d")

        messages = await execute_export_command(token, channel_id, formatted_date)

        # Batching and database insertion
        batch_size = 1000
        total_inserted = 0
        total_messages = len(messages)

        index_name = await create_index_if_not_exists(now.strftime("%Y-%m-%d"))

        for i in range(0, total_messages, batch_size):
            batch = messages[i:i + batch_size]
            try:
                await insert_batch(batch, channel_id, index_name)
                total_inserted += len(batch)
            except Exception as e:
                logger.error(f"Failed to insert batch due to: {e}")
                continue  # Optionally, handle failed batches differently

        if total_inserted < total_messages:
            raise HTTPException(status_code=500,
                                detail=f"Failed to insert some messages. Successfully inserted: {total_inserted}, Failed: {total_messages - total_inserted}")

        return {"message": f"Successfully inserted {total_inserted} messages into the database."}

    except Exception as e:
        logger.exception("Failed to export chat")
        raise HTTPException(status_code=500, detail=str(e))
