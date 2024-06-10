import boto3
import os

client = boto3.client('events')
event_busname = os.getenv("EVENT_BUSNAME")
event_source = os.getenv("EVENT_SOURCE")
detail_type = os.getenv("DETAIL_TYPE")  
