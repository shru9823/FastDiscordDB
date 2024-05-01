# FastDiscordDB Project

## Overview
FastDiscordDB is a FastAPI-powered application designed to handle the storage and retrieval of Discord chat exports into a PostgreSQL database and Elasticsearch. This project utilizes DiscordChatExporter to fetch chats and provides API endpoints for querying these chats by keyword or date range.

## Features

### Discord Chat Exports
- **Functionality**: Automatically downloads and stores chats from the last 7 days from a specified Discord channel into a PostgreSQL database using given user credentials.
- **Integration**: Utilizes [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) to fetch chat data in JSON format and stores it as structured data in PostgreSQL.

### Search by Keyword API
- **Endpoint**: `/api/search/keyword`
- **Method**: `GET`
- **Description**: Searches the database for chat messages containing the specified keyword.

### Search by Date API
- **Endpoint**: `/api/search/date`
- **Method**: `GET`
- **Description**: Retrieves chat messages within a specified date range from the database.


## Project Structure
```
/FastDiscordDB
│
├── app                     # Main application package
│   ├── __init__.py         # Initializes the Python package
│   ├── main.py             # Entry point to the FastAPI app, contains app configurations
│   ├── dependencies.py     # Dependency injection for database sessions and configurations
│   ├── models.py           # SQLAlchemy ORM models for your database schema
│   ├── schemas.py          # Pydantic models for data validation and serialization
│   ├── crud.py             # CRUD operations (database interaction logic)
│   ├── services            # Business logic and service layer
│   │   ├── __init__.py
│   │   ├── chat_exporter.py # Handles the logic for exporting chats using DiscordChatExporter
│   │   ├── chat_queries.py  # Business logic for querying chat data
│   │   ├── elasticsearch_chat_exporter.py # Handles the logic for exporting chats to Elasticsearch using DiscordChatExporter
│   │   └── elasticsearch_chat_queries.py  # Business logic for querying chat data from Elasticsearch

│   ├── api                 # API endpoints organized by functionality
│   │   ├── __init__.py
│   │   ├── chat.py         # Endpoints for chat operations and dynamic channel handling
│   │   └── search.py       # Endpoints for searching chats by keyword and date
│   └── core                # Core application components
│       ├── config.py       # Configuration settings (e.g., database URL, API keys)
│       ├── security.py     # Security and authentication functions
│       └── database.py     # Database connection setup
│
├── tests                   # Test modules
│   ├── __init__.py
│   └── test_api            # Tests for API endpoints
│       ├── __init__.py
│       ├── test_chat.py    # Tests for chat export and dynamic channel functionality
│       └── test_search.py  # Tests for search functionality
│
│
├── venv                    # Virtual environment directory (not committed to version control)
│
├── requirements.txt        # Project dependencies
├── .gitignore              # Specifies intentionally untracked files to ignore
└── README.md               # Project overview and setup instructions
```

## System Architecture
![Alt text for your diagram](readme_diagrams/system_architecture.png)

## System Design and Optimizations

### Architecture
FastDiscordDB utilizes a sophisticated system architecture combining several technologies to ensure efficient data handling and retrieval:

- **FastAPI**: Serves as the backbone of the web server, offering high performance and easy asynchronous support.
- **Redis**: Used as a caching layer to decrease load times and reduce database queries for frequently accessed data.
- **PostgreSQL**: Acts as the primary data store, optimized with indexes for efficient data retrieval.
- **Elasticsearch**: Integrated to enhance search capabilities, allowing for rapid, full-text search functionalities across massive datasets.



#### Benefits of Asynchronous Programming

##### 1. **Improved Performance**
- **Non-blocking Calls**: Asynchronous calls are non-blocking and allow the application to make better use of system resources while waiting for I/O operations to complete, such as database queries or HTTP requests.
- **Concurrency**: Enables the handling of multiple operations at the same time, which is critical for serving multiple clients concurrently without waiting for each task to complete sequentially.

##### 2. **Efficient Database Interactions**
- **Async Database Sessions**: By using asynchronous database sessions, FastDiscordDB can initiate and manage database transactions more efficiently. This approach is particularly beneficial when dealing with multiple, simultaneous database operations.
- **Reduced Latency**: Asynchronous database sessions help in reducing the response time of the system by managing database operations in a non-blocking manner, which is crucial for operations like large batch inserts or updates.

##### 3. **Scalability**
- **Handling More Requests**: Asynchronous programming allows FastDiscordDB to handle a larger number of incoming requests with the same hardware resources, improving the system's overall throughput.
- **Adaptability**: Makes the application more adaptable to changes in load, providing consistent performance under both high and low traffic conditions.

##### 4. **Developer Productivity and Error Handling**
- **Simplified Code**: Despite the complexity of handling concurrent operations, modern frameworks like FastAPI provide abstractions that simplify writing asynchronous code, making it more readable and maintainable.
- **Improved Error Handling**: Asynchronous programming provides structured ways to handle exceptions and errors that arise during asynchronous operations, ensuring that the system remains robust and stable.

### Technology Stack and Implementation Details

#### SQLAlchemy
**SQLAlchemy** is a SQL toolkit and Object-Relational Mapping (ORM) system for Python, providing an efficient and high-level abstraction for database access and manipulation. Here’s why it’s beneficial for FastDiscordDB:

- **Data Model Representation**: It allows you to define data models in Python code, which are then translated into database tables, making database operations more intuitive and secure.
- **Database Agnostic**: SQLAlchemy supports multiple database backends, facilitating easy switches between databases like SQLite, MySQL, and PostgreSQL without significant code changes.
- **Query Language**: Offers a powerful query language that's flexible and database-agnostic, enabling complex queries to be written in Python instead of SQL, enhancing maintainability and security.

#### Pydantic
**Pydantic** is a data validation and settings management library using Python type annotations. Pydantic ensures that the data your application sends and receives is correct:

- **Data Validation**: Automatically validates data so that your application operates on clean, well-defined data structures, reducing bugs and errors.
- **Editor Support**: Pydantic models are classes defined with standard Python types, making them easy to create and manipulate while also being supported by linters and IDEs for auto-completion.
- **Performance**: Offers fast data parsing and validation by leveraging Python's native type hints.

#### Bulk Upload to PostgreSQL
Handling bulk data efficiently is crucial for performance:

- **Efficiency**: Bulk operations reduce the number of transactions sent to the database, decreasing I/O overhead and increasing throughput.
- **Transaction Management**: Bulk operations can be wrapped in a single transaction, ensuring data integrity and reducing the risk of partial updates.

#### Bulk Upload to Elasticsearch
For full-text search capabilities, bulk uploading to Elasticsearch optimizes performance:

- **Indexing Speed**: Bulk uploading reduces the number of index refresh cycles needed, which significantly speeds up the indexing process.
- **Reduced Overhead**: Sending data in bulk over the network reduces the overhead of making multiple HTTP requests, making the data ingestion process faster and more reliable.




### Optimizations

#### Message Indexing
- **Implementation**: Messages stored in PostgreSQL are indexed to speed up query times for searches, sorts, and data retrieval operations.

#### SQL Indexing
- **Details**: Strategic indexing of SQL queries in PostgreSQL to minimize response times and maximize efficiency for complex query operations.

#### Full-Text Search Optimization with PostgreSQL tsvector

#### Implementation
FastDiscordDB uses PostgreSQL's full-text search capabilities through the use of the `tsvector` data type on the `content` column of the `Message` table. This allows for indexing and efficient searching of chat messages using natural language processing techniques. 

#### How It Works
- **tsvector**: This is a data type in PostgreSQL designed specifically for full-text search. In FastDiscordDB, the `content` column of chat messages is stored as a `tsvector`, which indexes the content for efficient search operations.
- **plainto_tsquery**: This function simplifies the search string into a format that can be compared against the `tsvector` index. It converts the search term provided by the user into a tsquery object, which supports searching for phrases in natural language, ignoring noise words.

#### Query Optimizations
- **Techniques**: Queries are carefully crafted and tested to ensure they run with optimal efficiency, reducing computational overhead and speeding up response times.


### Database Optimization with Partitioning

#### Implementation
FastDiscordDB optimizes PostgreSQL database queries by implementing `PARTITION BY RANGE` on the `message_date` column. This approach involves creating a month-wise partition of the `Message` table, allowing for more efficient data management and faster query performance, especially when querying messages within specific date ranges.

#### Benefits
- **Improved Query Performance**: Partitioning the table by date range allows the database engine to quickly locate and retrieve data from specific partitions, reducing the time spent scanning irrelevant data.
- **Scalability and Maintenance**: Easier management of data through partitions facilitates routine maintenance tasks such as data purging or archiving, especially for large datasets.
- **Optimized Data Storage**: Data is more organized and can be stored more efficiently, potentially improving I/O performance for read and write operations.

### Full-Text Search Capabilities with tsvector

#### Types of Searches
`tsvector` supports various types of full-text searches, enhancing the functionality of FastDiscordDB:

- **Phrase Search**: Allows users to search for exact phrases or combinations of words in the text, providing precise control over the search results.
- **Lexeme Matching**: Breaks down the searchable content into lexemes or normalized words, which are then indexed. This enables the system to ignore punctuation, capitalization, and affixes, focusing only on the base words.
- **Ranking and Relevance**: `tsvector` can rank search results based on the frequency and proximity of the search terms in the text, prioritizing more relevant results to the top.
- **Boolean Operators**: Supports the use of boolean operators like AND, OR, and NOT in search queries, allowing for more complex and targeted search criteria.

### Enhancing Text Search Efficiency with pg_trgm

#### Implementation
To further refine the text search capabilities within FastDiscordDB, the project utilizes the PostgreSQL `ilike` operator for case-insensitive text searches. To optimize the performance of these searches, the `pg_trgm` extension is employed, which supports GIN (Generalized Inverted Index) indexing of trigrams in text data.






#### Redis Cache
- **Usage**: Frequently requested data is stored in Redis, enabling quick access and reducing the number of queries made directly to the PostgreSQL database. This is particularly useful for data that does not change often but is requested frequently.

### Utilizing Redis for Enhancing Search Capabilities

#### Why Redis?
Redis is an in-memory data structure store, known for its exceptional speed and flexibility. It serves as an excellent caching and messaging broker. In the context of FastDiscordDB, Redis is leveraged to enhance the performance of search operations, making both "search by keyword" and "search by date range" more efficient.

#### Benefits of Redis in Search Operations

##### 1. **Speed**
- **Fast Access**: Redis operates with in-memory datasets, offering sub-millisecond response times. This speed is crucial for caching results of frequently made search queries, such as popular keywords or common date ranges.
- **Immediate Updates**: Redis provides a rapid mechanism to invalidate stale cache when new data is inserted or existing data is updated in the database, ensuring that search results are up-to-date.

##### 2. **Reduced Load on Primary Database**
- **Cache Frequent Queries**: By caching the results of common queries, Redis reduces the number of direct queries to PostgreSQL, minimizing load and preventing performance bottlenecks during peak times.
- **Offload Complex Operations**: Date range searches can be computationally intensive on the primary database; caching these results with Redis allows for repeated quick access without re-executing complex queries.

##### 3. **Scalability**
- **Horizontal Scaling**: Redis can scale horizontally by adding more nodes to the Redis cluster. This scalability is vital for maintaining performance as the number and complexity of search operations increase.
- **Flexibility with Data Eviction Policies**: Redis offers various data eviction policies which can be configured based on the application needs to manage memory efficiently.

##### 4. **Persistence Options**
- **Data Durability**: While primarily used as an in-memory solution, Redis also offers options for persistence, ensuring that cached data isn't lost during system failures. This is beneficial for maintaining a reliable cache that can quickly repopulate after a restart.

##### 5. **Simplicity and Developer Friendliness**
- **Easy Integration**: Redis is straightforward to integrate and manage with existing backend technologies like FastAPI and PostgreSQL. It supports a wide range of data structures such as strings, hashes, lists, and sets, which can be used flexibly depending on the caching needs.







#### Elasticsearch Integration
- **Purpose**: Elasticsearch is utilized for its powerful full-text search capabilities, making it possible to quickly search through large volumes of chat data using various attributes and complex query strings.

### Advantages of Using Elasticsearch Over PostgreSQL for Full-Text Search

#### 1. **Designed for Search Operations**
Elasticsearch is built specifically for search operations. It is based on the Lucene search engine and optimized for fast full-text searching. PostgreSQL, while capable of full-text search through its `tsvector` and `pg_trgm` features, is primarily a relational database and not specifically optimized for search.

#### 2. **Scalability**
Elasticsearch excels in scalability. It is designed to handle massive volumes of data and support high query loads. The distributed nature of Elasticsearch allows it to expand easily by adding more nodes to the cluster, providing both horizontal scalability and high availability. In contrast, scaling PostgreSQL for large-scale search operations often involves more complex replication setups and can be more resource-intensive.

#### 3. **Real-Time Search**
Elasticsearch provides near real-time search capabilities. This means that once a document is indexed, it can be searched for almost immediately. This is particularly advantageous for environments where data is constantly being updated and needs to be searchable without delay. PostgreSQL, on the other hand, may experience a slight lag between data insertion and index updating.

#### 4. **Complex Query Language**
Elasticsearch supports a rich, flexible query language that allows for complex search queries, including fuzzy searching, wildcard searches, and boolean logic. While PostgreSQL also supports a variety of search queries, Elasticsearch's query DSL (Domain Specific Language) is more extensive and tailored for complex search scenarios.

#### 5. **Full-Text Search Features**
Elasticsearch provides extensive full-text search capabilities that go beyond simple keyword search. It supports text analysis features such as custom tokenizers, filters, and analyzers, which allow for advanced text processing and the ability to tailor the search experience. PostgreSQL's full-text search is powerful but lacks the fine-grained control and customization that Elasticsearch offers.

#### 6. **Performance and Efficiency**
For large datasets, Elasticsearch often performs faster in search queries due to its inverted indexing and ability to maintain an index that is constantly optimized for search operations. PostgreSQL might perform well with smaller datasets or less complex queries but can become slower as the data volume and complexity increase.

#### 7. **Built-in Support for Aggregation and Analytics**
Elasticsearch includes powerful aggregation features, which enable performing complex analytics in real-time. This can be used to generate summaries or insights from the data quickly, which is beneficial for creating dashboards or reports directly from search data. PostgreSQL can perform similar aggregations but usually at a slower pace and with greater load on the database.


### Implementing Pagination in Search APIs

#### Overview
Pagination is a crucial feature for any application that handles large datasets or returns numerous search results. In FastDiscordDB, pagination has been implemented across all search APIs to improve user experience and system performance.

#### Why Pagination?
- **Improved User Experience**: Pagination allows users to navigate through search results easily and intuitively. It provides a better user interface by breaking large sets of data into smaller, manageable chunks.
- **Reduced Server Load**: By limiting the number of results returned in a single request, pagination helps in reducing the load on the server. This is particularly important for performance during peak usage times.
- **Enhanced Performance**: Loading fewer items at a time speeds up response times and conserves bandwidth. This is essential for applications like FastDiscordDB, which deal with large volumes of data and users.
- **Resource Control**: It gives a better control over network traffic and resource allocation, which is critical in cloud environments or services with limited resources.

#### Implementation Details
Each search API in FastDiscordDB supports pagination parameters such as `page` and `page_size`. These parameters allow users to specify the page of results they are interested in, and the number of items per page.



### Conclusion
While PostgreSQL offers robust data integrity and transactional support, Elasticsearch provides superior capabilities specifically tailored for search and analytics. Integrating Elasticsearch into FastDiscordDB enhances the system’s performance, scalability, and search flexibility, making it an ideal choice for applications requiring advanced search over large datasets.



### Benefits
The combined use of these technologies and optimizations ensures that FastDiscordDB can handle large scales of data efficiently, maintain high availability, and provide quick response times to API requests. This design is particularly well-suited for environments where data integrity, speed, and reliability are critical.

## Getting the Most Out of FastDiscordDB
For best performance:
- Ensure proper configuration of Elasticsearch indices according to the data structure.
- Monitor Redis cache hit rates and adjust cache size as needed.
- Regularly update and optimize database indices based on query patterns observed in logs.

## Scalability
This system is designed to scale with your needs. Whether scaling vertically by enhancing server capabilities or horizontally by adding more nodes, FastDiscordDB’s architecture supports growth to handle increasing loads seamlessly.


## Installation
```bash
# Clone the repository
git clone https://github.com/shru9823/FastDiscordDB.git
cd FastDiscordDB

# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## To start the application
```bash
uvicorn app.main:app --reload
```

## Postgres Database setup
```bash
CREATE TABLE discord_chats (
    message_id BIGINT,
    channel_id BIGINT,
    message_date DATE,
    content TEXT,
    PRIMARY KEY (message_id, message_date)
) PARTITION BY RANGE (message_date);


ALTER TABLE discord_chats
ADD COLUMN content_tsvector TSVECTOR;


UPDATE discord_chats
SET content_tsvector = to_tsvector('english', content);

CREATE INDEX idx_content_tsvector ON discord_chats USING gin(content_tsvector);

CREATE INDEX idx_message_date ON discord_chats(message_date);

CREATE extension pg_trgm;

CREATE INDEX discord_chats_trgm_gin ON discord_chats USING gin (content gin_trgm_ops);

CREATE TABLE discord_chats_2024_04 PARTITION OF discord_chats FOR VALUES FROM ('2022-04-01') TO ('2022-04-30');
```

## API Documentation

### 1. Export Chat to PostgreSQL

This endpoint exports chat data from a specified Discord channel to a PostgreSQL database.

#### HTTP Method
`POST`

#### URL
`/api/chats/export/{channel_id}`

#### URL Parameters
- **channel_id**: The unique identifier for the Discord channel. This parameter is required and must be specified in the URL.

#### Headers
- **X-Token**: A Discord authentication token required to access the channel. This should be included in the headers as `X-Token`. If this header is missing, the API will return a 400 error indicating the Discord token is missing.

#### Request
No request body is needed for this API call. The required data is provided via URL parameters and headers.

#### Response
The response will be in JSON format with the following keys:
- **status**: The status of the operation (`success` or `error`).
- **data**: The data returned from the Discord chat export operation.
- **process_time**: The time taken to process the chat export, in seconds.

#### Success Response Example
```json
{
  "status": "success",
  "data": {
      "message": "Successfully inserted 11 messages into the database."
  },
  "process_time": "2.8182 seconds"
}
```

#### Error Response Example
Missing Discord Token - Status Code: 400 Bad Request
```{
  "detail": "Missing Discord token."
}
```

Internal Server Error - Status Code: 500 Internal Server Error
```{
  "detail": "An error occurred while processing your request."
}
```


### 2.  Export Chat to Elasticsearch

This endpoint facilitates the exportation of chat data from a specified Discord channel to an Elasticsearch index.

#### HTTP Method
`POST`

#### URL
`/api/es/chats/export/{channel_id}`

#### URL Parameters
- **channel_id**: The unique identifier for the Discord channel from which chat data will be exported. This parameter is required and must be specified in the URL.

#### Headers
- **X-Token**: A required Discord authentication token to access the channel's data. It should be included in the headers as `X-Token`. Omitting this token will result in a 400 error, indicating the absence of the required Discord token.

#### Request
This API does not require a body for the request. All necessary data is provided through URL parameters and headers.

#### Response
The API response is structured in JSON format, providing details about the operation status, data retrieved, and the time taken to process the request.

#### Success Response Example
```json
{
  "status": "success",
  "data": {
      "message": "Successfully inserted 11 messages into the database."
  },
  "process_time": "2.5471 seconds"
}
```

#### Error Response Example
Missing Discord Token - Status Code: 400 Bad Request
```{
  "detail": "Missing Discord token."
}
```

Internal Server Error - Status Code: 500 Internal Server Error
```{
  "detail": "An error occurred while processing your request."
}
```


### 3.  Search Chat Messages by Keyword

This endpoint allows for the exact searching of chat messages by keyword, returning paginated results. It integrates caching to enhance performance by reducing database load for frequently made queries.

#### HTTP Method
`GET`

#### URL
`/api/chats/search`

#### Query Parameters
- **search_term**: A keyword string used for searching within chat messages. This parameter is mandatory and must be between 1 and 100 characters in length.
- **page**: The page number in the pagination sequence.
- **page_size**: The number of chat messages to return per page.

#### Headers
No specific headers required for this request.

#### Request
Include the `search_term`, `page`, and `page_size` in the query string of your request URL.

#### Response Model
The response will be structured as a JSON object that follows the `PaginatedChatMessagesResponse` model, including fields for the total number of messages, the current page, total pages, and the list of messages.

#### Success Response Example
For a page 1 and page_size 10, the response is given below for a search_term - "pie"
```json
{
  "messages": [
    {
      "message_id": 1232782017872138200,
      "channel_id": 1165030189714129000,
      "content": "The Posters and Pies event is happening this Friday!\nhttps://sdc.csc.ncsu.edu/posters-and-pies",
      "message_date": "2024-04-24"
    },
    {
      "message_id": 1232782050931769300,
      "channel_id": 1165030189714129000,
      "content": "Does anyone know if they have pecan pie",
      "message_date": "2024-04-24"
    },
    {
      "message_id": 1233571560565112800,
      "channel_id": 1165030189714129000,
      "content": "They had pecan pie, peach pie, apple pie, blueberry pie, chocolate pie",
      "message_date": "2024-04-26"
    },
    {
      "message_id": 1233571669289730000,
      "channel_id": 1165030189714129000,
      "content": "and the tea was not too sweet to make way for the pie",
      "message_date": "2024-04-26"
    },
    {
      "message_id": 1233571790580617200,
      "channel_id": 1165030189714129000,
      "content": "I got to all the pies except chocolate. 10/10 event",
      "message_date": "2024-04-26"
    },
    {
      "message_id": 1233571991882305500,
      "channel_id": 1165030189714129000,
      "content": "the pecan pie was so good",
      "message_date": "2024-04-26"
    }
  ],
  "count": 6,
  "total_count": 6
}
```

#### Error Response Example
Keyword Missing - Status Code: 400 Bad Request
```{
  "detail": "Keyword must not be empty"
}
```

Internal Server Error - Status Code: 500 Internal Server Error
```{
  "detail": "An internal error occurred"
}
```

No Messages Found - Status Code: 200 OK
```{
  "detail": "No messages found"
}
```


### 4.  Search All Chat Messages by Keyword

This endpoint performs an exact keyword search across all chat messages, retrieving data without pagination either from the cache or the database, depending on availability and cache validity.

#### HTTP Method
`GET`

#### URL
`/api/chats/search/all`

#### Query Parameters
- **search_term**: A keyword string used for searching within all chat messages. This parameter is required and must be between 1 and 100 characters in length.

#### Headers
No specific headers are required for this request.

#### Request
Include the `search_term` in the query string of your request URL.

#### Response Model
The response is structured as a JSON object following the `ChatMessagesResponse` model, which includes fields for the count of messages and a list of the messages themselves.

#### Success Response Example
```json
{
  "messages": [
    {
      "message_id": 1233920393488633900,
      "channel_id": 1165030189714129000,
      "content": "Good luck with exams everyone! You got this!!",
      "message_date": "2024-04-27"
    }
  ],
  "count": 1
}
```

#### Error Response Example
Keyword Missing - Status Code: 400 Bad Request
```{
  "detail": "Keyword must not be empty"
}
```

Internal Server Error - Status Code: 500 Internal Server Error
```{
  "detail": "An internal error occurred"
}
```

No Messages Found - Status Code: 200 OK
```{
  "detail": "No messages found"
}
```



