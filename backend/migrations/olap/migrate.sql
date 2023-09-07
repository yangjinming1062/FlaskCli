CREATE TABLE IF NOT EXISTS api_request_logs
(
    `id`         UUID,
    `user_id` LowCardinality(String),
    `created_at` DateTime64(3),
    `method` LowCardinality(String),
    `blueprint` LowCardinality(String),
    `uri` LowCardinality(String),
    `status`     Int32,
    `duration`   Int32,
    `source_ip`  IPv4,

    INDEX arl_duration_index duration TYPE minmax GRANULARITY 2,
    INDEX arl_status_code_index status TYPE minmax GRANULARITY 4
) ENGINE = MergeTree
      PARTITION BY toYYYYMMDD(created_at)
      ORDER BY (user_id, created_at, id)
      TTL toDateTime(created_at) + toIntervalDay(180)
      SETTINGS index_granularity = 1024;


CREATE TABLE IF NOT EXISTS api_request_logs_queue
(
    `id`         UUID,
    `user_id` LowCardinality(String),
    `created_at` DateTime64(3),
    `method` LowCardinality(String),
    `blueprint` LowCardinality(String),
    `uri` LowCardinality(String),
    `status`     Int32,
    `duration`   Int32,
    `source_ip`  IPv4
) ENGINE = Kafka
      SETTINGS kafka_broker_list = 'kafka:9092',
          kafka_topic_list = 'ApiRequestLogs',
          kafka_group_name = 'write-data',
          kafka_format = 'JSONEachRow',
          kafka_skip_broken_messages = 1,
          kafka_num_consumers = 1;


CREATE MATERIALIZED VIEW IF NOT EXISTS ApiRequestLogs
            TO api_request_logs
            (
             `id` UUID,
             `user_id` LowCardinality(String),
             `created_at` DateTime,
             `method` LowCardinality(String),
             `blueprint` LowCardinality(String),
             `uri` LowCardinality(String),
             `status` Int32,
             `duration` Int32,
             `source_ip` IPv4
                )
AS
SELECT id,
       user_id,
       toDateTime(created_at) AS created_at,
       method,
       blueprint,
       uri,
       status,
       duration,
       toIPv4(source_ip)      AS source_ip
FROM api_request_logs_queue;
