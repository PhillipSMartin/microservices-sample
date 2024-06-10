import boto3
import os

client = boto3.resource('events')
event_busname = os.get_env("EVENT_BUSNAME")
event_source = os.get_env("EVENT_SOURCE")
detail_type = os.get_env("DETAIL_TYPE")  
