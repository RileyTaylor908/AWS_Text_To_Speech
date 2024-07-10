import boto3
import os
from contextlib import closing
from boto3.dynamodb.conditions import Key

def get_post_item(postId):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    postItem = table.query(KeyConditionExpression=Key('id').eq(postId))
    if not postItem["Items"]:
        print("Post not found in DynamoDB")
        return None
    return postItem["Items"][0]

def split_text(text, max_length=1100):
    text_blocks = []
    rest = text
    while len(rest) > max_length:
        end = rest.find(".", max_length - 100)
        if end == -1:
            end = rest.find(" ", max_length - 100)
        if end == -1:
            break
        text_blocks.append(rest[:end + 1])
        rest = rest[end + 1:]
    text_blocks.append(rest)
    return text_blocks

def synthesize_speech(text_blocks, voice, output_path):
    polly = boto3.client('polly')
    with open(output_path, "wb") as file:
        for block in text_blocks:
            response = polly.synthesize_speech(
                OutputFormat='mp3',
                Text=block,
                VoiceId=voice
            )
            if "AudioStream" in response:
                with closing(response["AudioStream"]) as stream:
                    file.write(stream.read())

def upload_to_s3(file_path, bucket_name, post_id):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bucket_name, f"{post_id}.mp3")
    return f"https://{bucket_name}.s3.amazonaws.com/{post_id}.mp3"

def update_dynamodb_status(post_id, url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_NAME'])
    response = table.update_item(
        Key={'id': post_id},
        UpdateExpression="SET #statusAtt = :statusValue, #urlAtt = :urlValue",
        ExpressionAttributeValues={
            ':statusValue': 'UPDATED',
            ':urlValue': url
        },
        ExpressionAttributeNames={
            '#statusAtt': 'status',
            '#urlAtt': 'url'
        },
    )
    print(f"DynamoDB UpdateItem Response: {response}")

def lambda_handler(event, context):
    postId = event["Records"][0]["Sns"]["Message"]
    print(f"Text to Speech function. Post ID in DynamoDB: {postId}")

    try:
        post_item = get_post_item(postId)
        if not post_item:
            return

        text = post_item["text"]
        voice = post_item["voice"]
        text_blocks = split_text(text)

        output_path = os.path.join("/tmp/", f"{postId}.mp3")
        synthesize_speech(text_blocks, voice, output_path)

        url = upload_to_s3(output_path, os.environ['BUCKET_NAME'], postId)
        update_dynamodb_status(postId, url)

    except Exception as e:
        print(f"Error processing Lambda function: {e}")
        raise e  # Re-raise the exception to ensure Lambda failure is logged
