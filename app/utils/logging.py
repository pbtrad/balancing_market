import logging
import watchtower
import boto3

LOG_GROUP = "balancing-market-logs"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

log_stream_name = "application-logs"

boto3_client = boto3.client("logs")

logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group=LOG_GROUP,
    stream_name=log_stream_name,
    boto3_client=boto3_client
))

logger.info("CloudWatch logging setup complete.")
