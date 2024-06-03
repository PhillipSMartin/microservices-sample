#!/usr/bin/env python3
import aws_cdk as cdk
import os

from microservices.stack import MicroservicesSampleStack


app = cdk.App()
MicroservicesSampleStack(app, "MicroservicesSampleStack",
    env=cdk.Environment(account=os.getenv('AWS_ACCOUNT_ID'), region=os.getenv('AWS_REGION')),
)

app.synth()
