from fastapi import FastAPI, Query, HTTPException
from elasticsearch import Elasticsearch
from typing import List

from app.schemas import PaginationParams


async def paginated_es_search_by_keyword(keyword: str, pagination: PaginationParams, es: Elasticsearch):
    try:
        from_ = (pagination.page - 1) * pagination.page_size
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
        return [doc['_source'] for doc in response['hits']['hits']], response['hits']['total']['value']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def paginated_es_search_by_date_range(
        start_date: str,
        end_date: str,
        pagination: PaginationParams,
        es: Elasticsearch):
    try:
        from_ = (pagination.page - 1) * pagination.page_size
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
        return [doc['_source'] for doc in response['hits']['hits']], response['hits']['total']['value']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# async def search_by_keyword(keyword: str, es: Elasticsearch):
#     try:
#         response = es.search(index="chats-*", body={
#             "query": {
#                 "match": {
#                     "content": {
#                         "query": keyword,
#                         "analyzer": "discord_analyzer"
#                     }
#                 }
#             },
#             "size": 1000
#         })
#         return [doc['_source'] for doc in response['hits']['hits']]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# async def search_by_date_range(
#     start_date: str,
#     end_date: str,
#     es: Elasticsearch
# ):
#     try:
#         response = es.search(index="chats-*", body={
#             "query": {
#                 "range": {
#                     "message_date": {
#                         "gte": start_date,
#                         "lte": end_date,
#                         "format": "yyyy-MM-dd"
#                     }
#                 }
#             },
#             "size": 1000
#         })
#         return [doc['_source'] for doc in response['hits']['hits']]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

