import boto3
import os
import uuid

def lambda_handler(event, context):
    
    recordId = str(uuid.uuid4())
    voice = event["voice"]
    text = event["text"]

    print('Generate dynamodb with id: ' + recordId)
    print('Input Text: ' + text)
    print('Selected voice: ' + voice)
    
    # Puts info in dynamodb
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    table.put_item(
        Item={
            'id' : recordId,
            'text' : text,
            'voice' : voice,
            'status' : 'PROCESSING'
        }
    )
    
    # Send notification to sns
    client = boto3.client('sns')
    client.publish(
        TopicArn = os.environ['SNS_TOPIC'],
        Message = recordId
    )
    
    return recordId
