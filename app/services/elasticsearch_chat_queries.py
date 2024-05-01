from fastapi import FastAPI, Query, HTTPException
from elasticsearch import Elasticsearch
from typing import List

from app.schemas import PaginationParams

async def paginated_es_search_by_keyword(keyword: str, pagination: PaginationParams, es: Elasticsearch):
    """
    Performs a paginated search for documents in Elasticsearch based on a given keyword.
    Utilizes a specified analyzer for text matching to ensure the relevance of search results.
    """
    try:
        # Calculate the offset for the pagination
        from_ = (pagination.page - 1) * pagination.page_size
        # Construct and execute the search query in Elasticsearch
        response = es.search(index="chats-*", body={
            "query": {
                "match": {
                    "content": {
                        "query": keyword,
                        "analyzer": "discord_analyzer"
                    }
                }
            },
            "from": from_,
            "size": pagination.page_size
        })
        # Extract and return the relevant documents and the total number of hits
        return [doc['_source'] for doc in response['hits']['hits']], response['hits']['total']['value']
    except Exception as e:
        # Handle any exceptions that occur during the search by raising an HTTPException
        raise HTTPException(status_code=500, detail=str(e))

async def paginated_es_search_by_date_range(
        start_date: str,
        end_date: str,
        pagination: PaginationParams,
        es: Elasticsearch):
    """
    Conducts a paginated search in Elasticsearch for documents within a specified date range.
    Handles the pagination logic and formats the dates to be compatible with Elasticsearch.
    """
    try:
        # Calculate the starting point for the results to fetch, based on the current page
        from_ = (pagination.page - 1) * pagination.page_size
        # Execute the search with a date range filter
        response = es.search(index="chats-*", body={
            "query": {
                "range": {
                    "message_date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            },
            "from": from_,
            "size": pagination.page_size
        })
        # Return the documents found and the total count of the results
        return [doc['_source'] for doc in response['hits']['hits']], response['hits']['total']['value']
    except Exception as e:
        # If an error occurs, handle it by throwing an HTTPException with the error details
        raise HTTPException(status_code=500, detail=str(e))
