import os
import json
import boto3
from datetime import datetime, timezone
from decimal import Decimal

def get_dynamodb_client():
    if 'AWS_SAM_LOCAL' in os.environ:
        print("Using DynamoDB Local endpoint")
        return boto3.resource(
            'dynamodb',
            endpoint_url='http://host.docker.internal:8000',
            region_name='us-east-2',
            aws_access_key_id='dummy',
            aws_secret_access_key='dummy'
        )
    print("Using remote AWS DynamoDB")
    return boto3.resource('dynamodb', region_name='us-east-2')

dynamodb = get_dynamodb_client()

def lambda_handler(event, context):
    try:
        table_name = os.environ.get('BATTERY_TABLE_NAME')
        if not table_name:
            raise ValueError("BATTERY_TABLE_NAME environment variable is not set")

        table = dynamodb.Table(table_name)

        # Parse JSON body from the incoming POST request
        body = {}
        if "body" in event and event["body"]:
            body = json.loads(event["body"])

        battery_id = body.get("battery_id", "battery-unknown")
        timestamp = body.get("timestamp", datetime.now(timezone.utc).isoformat())
        state_of_charge = body.get("state_of_charge", 50.0)
        temperature = body.get("temperature", 25.0)
        voltage = body.get("voltage", 3.7)
        state = body.get("state", "unknown")  # Get the state

        # Convert numeric fields to Decimal for DynamoDB
        item = {
            "battery_id": battery_id,
            "timestamp": timestamp,
            "state_of_charge": Decimal(str(state_of_charge)),
            "temperature": Decimal(str(temperature)),
            "voltage": Decimal(str(voltage)),
            "state": state  # Store the state
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
