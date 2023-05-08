CREATE TABLE api_request_logs
(

    `id`             UUID,

    `user_id` LowCardinality(String),

    `create_time`    DateTime64(3),

    `method` LowCardinality(String),

    `version` LowCardinality(String),

    `blueprint` LowCardinality(String),

    `uri` LowCardinality(String),

    `status_code`    Int32,

    `duration`       Int32,

    `source_ip`      IPv4,

    `destination_ip` IPv4,

    INDEX arl_duration_index duration TYPE minmax GRANULARITY 2,

    INDEX arl_status_code_index status_code TYPE minmax GRANULARITY 4
) ENGINE = MergeTree
      PARTITION BY toYYYYMMDD(create_time)
      PRIMARY KEY (user_id, create_time, id)
      ORDER BY (user_id, create_time, id)
      TTL toDateTime(create_time) + toIntervalDay(180)
      SETTINGS index_granularity = 1024;


CREATE TABLE api_request_logs_queue
(

    `id`             UUID,

    `user_id` LowCardinality(String),

    `create_time`    DateTime64(3),

    `method` LowCardinality(String),

    `version` LowCardinality(String),

    `blueprint` LowCardinality(String),

    `uri` LowCardinality(String),

    `status_code`    Int32,

    `duration`       Int32,

    `source_ip`      IPv4,

    `destination_ip` IPv4
) ENGINE = Kafka
      SETTINGS kafka_broker_list = 'kafka:9092',
          kafka_topic_list = 'ApiRequestLogs',
          kafka_group_name = 'write-data',
          kafka_format = 'JSONEachRow',
          kafka_skip_broken_messages = 1,
          kafka_num_consumers = 1;


CREATE MATERIALIZED VIEW ApiRequestLogs
            TO api_request_logs
            (
             `id` UUID,
             `user_id` LowCardinality(String),
             `created_at` DateTime,
             `method` LowCardinality(String),
             `version` LowCardinality(String),
             `blueprint` LowCardinality(String),
             `uri` LowCardinality(String),
             `status_code` Int32,
             `duration` Int32,
             `source_ip` IPv4,
             `destination_ip` IPv4
                )
AS
SELECT id,

       user_id,

       toDateTime(create_time) AS created_at,

       method,

       version,

       blueprint,

       uri,

       status_code,

       duration,

       toIPv4(source_ip)       AS source_ip,

       toIPv4(destination_ip)  AS destination_ip
FROM api_request_logs_queue;