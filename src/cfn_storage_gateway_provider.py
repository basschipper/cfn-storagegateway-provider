import os
import logging

from cfn_resource_provider import ResourceProvider

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


schema = {
    "type": "object",
    "required": ["ActivationKey", "GatewayName", "GatewayTimezone", "GatewayRegion"],
    "properties": {
        "ActivationKey": { "type": "string",
            "description": "Your gateway activation key. " },
        "GatewayName": { "type": "string",
            "description": "The name you configured for your gateway." },
        "GatewayTimezone": { "type": "string",
            "description": "A value that indicates the time zone you want to set for the gateway." },
        "GatewayRegion": { "type": "string",
            "description": "A value that indicates the region where you want to store your data." },
        "GatewayType": { "type": "string",
            "description": "A value that defines the type of gateway to activate." },
        "Tags": { "type": "array",
            "description": "A list of up to 50 tags that can be assigned to the gateway.",
            "items": {
                "type": "object",
                "required": ["Key", "Value"],
                "properties": {
                    "Key": {
                        "type": "string"
                    },
                    "Value": {
                        "type": "string"
                    }
                }
            }
        }
    }
}


class StorageGatewayProvider(ResourceProvider):
    def __init__(self):
        super(StorageGatewayProvider, self).__init__()
        self.request_schema = schema
        self.storagegw = boto3.client('storagegateway')

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    def create(self):
        try:
            log.info("Creating SGW %s", self.get("GatewayName"))

            response = self.storagegw.activate_gateway(
                ActivationKey=self.get("ActivationKey"),
                GatewayName=self.get("GatewayName"),
                GatewayTimezone=self.get("GatewayTimezone"),
                GatewayRegion=self.get("GatewayRegion"),
                GatewayType=self.get("GatewayType"),
                Tags=self.get("Tags")
            )

            log.debug("%s", response)

            self.set_attribute('Arn', response["GatewayARN"])
            self.physical_resource_id = response["GatewayARN"]
        except ClientError as e:
            log.error("ClientError %s", str(e))
            self.physical_resource_id = 'could-not-create'
            self.fail(str(e))

    def update(self):
        pass

    def delete(self):
        try:
            log.info("Deleting SGW %s", self.physical_resource_id)

            response = self.storagegw.delete_gateway(
                GatewayARN=self.physical_resource_id
            )

            log.debug("%s", response)
        except ClientError as e:
            log.error("ClientError %s", str(e))
            self.fail(str(e))


provider = StorageGatewayProvider()


def handler(request, context):
    return provider.handle(request, context)
