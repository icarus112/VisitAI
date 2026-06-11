Даже если pgvector установлен в систему, его ещё надо включить в твоей базе данных.

Зайди в psql, выполни:
CREATE EXTENSION IF NOT EXISTS vector;
