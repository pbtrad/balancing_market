import json
import boto3
import os


def handler(event, context):
    lambda_client = boto3.client("lambda")

    try:
        response = lambda_client.invoke(
            FunctionName=os.environ["FEATURE_FUNCTION_ARN"],
            InvocationType="Event",
        )

        return {
            "statusCode": 200,
            "body": json.dumps("Feature generation triggered successfully"),
        }
    except Exception as e:
        print(f"Error triggering feature generation: {str(e)}")
        raise
