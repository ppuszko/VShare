# What is it?
### This project is at it's heart a data ingestion pipeline with hybrid search engine. 
It utilizies dense and sparse vectors for initial oversampled search and performs reranking on this sample with heavy multivectors to assure highest precision. 
Dense vectors used for initial are quantized (int8) to ensure high performance and lower memory costs. 
Data ingestion is performed by passing documents (currently supported: pdf, odt, docx), which are saved, turned into chunks and inserted to vector database.
### All around engine
This system is intended to use inside of hermetic groups of users. One can query the database and ingest data only inside of his group, with no access to resources of other groups.
API is built with FastAPI and is accessible through simple fontend. 
(Please note that the frontend is there only to simplify interaction with API and is as basic as they come, as i wanted to focus purely on backend and operations on vectors.)
