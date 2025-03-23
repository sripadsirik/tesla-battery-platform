import os
import json
import boto3
from datetime import datetime, timezone
from decimal import Decimal

def get_dynamodb_client():
    if 'AWS_SAM_LOCAL' in os.environ:
        print("Using DynamoDB Local endpoint")
        return boto3.resource('dynamodb',
                              endpoint_url='http://host.docker.internal:8000',
                              region_name='us-east-2',
                              aws_access_key_id='dummy',
                              aws_secret_access_key='dummy')



dynamodb = get_dynamodb_client()

def lambda_handler(event, context):
    try:
        # Get the table name from environment variable
        table_name = os.environ.get('BATTERY_TABLE_NAME')  # Changed from 'BatteryData'
        if not table_name:
            raise ValueError("BATTERY_TABLE_NAME environment variable is not set")
            
        table = dynamodb.Table(table_name)

        battery_id = "battery-1234"
        timestamp = datetime.now(timezone.utc).isoformat()

        item = {
            "battery_id": battery_id,
            "timestamp": timestamp,
            "state_of_charge": Decimal("85.0"),
            "temperature": Decimal("35.2")
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Item saved successfully!", "item": item}, default=str)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
