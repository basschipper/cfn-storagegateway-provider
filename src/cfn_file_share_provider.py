import os
import logging
import string
import random

from cfn_resource_provider import ResourceProvider

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


schema = {
    "type": "object",
    "required": ["GatewayARN", "Role", "LocationARN", "ClientList"],
    "properties": {
        "GatewayARN": { "type": "string",
            "description": "The Amazon Resource Name (ARN) of the file gateway on which you want to create a file share." },
        "Role": { "type": "string",
            "description": "The ARN of the AWS Identity and Access Management (IAM) role that a file gateway assumes when it accesses the underlying storage." },
        "LocationARN": { "type": "string",
            "description": "The ARN of the backed storage used for storing file data." },
        "ClientList": { "type": "array",
            "description": "The list of clients that are allowed to access the file gateway. The list must contain either valid IP addresses or valid CIDR blocks." },
        "Tags": { "type": "array",
            "description": "A list of up to 50 tags that can be assigned to the gateway.",
            "items": {
                "type": "object",
                "required": ["Key", "Value"],
                "properties": {
                    "Key": {
                        "type": "string"
                    }
                }
            }
        }
    }
}


class StorageGatewayNfsFileShareProvider(ResourceProvider):
    def __init__(self):
        super(StorageGatewayNfsFileShareProvider, self).__init__()
        self.request_schema = schema
        self.storagegw = boto3.client('storagegateway')

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    @staticmethod
    def random_string(size=8):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

    def create(self):
        try:
            log.info("Creating SGW NFS file share %s", self.get("GatewayARN"))

            response = self.storagegw.create_nfs_file_share(
                ClientToken=self.random_string(),
                GatewayARN=self.get("GatewayARN"),
                Role=self.get("Role"),
                LocationARN=self.get("LocationARN"),
                ClientList=self.get("ClientList"),
                Tags=self.get("Tags")
            )

            log.debug("%s", response)

            self.set_attribute('Arn', response["FileShareARN"])
            self.physical_resource_id = response["FileShareARN"]
        except ClientError as e:
            log.error("ClientError %s", str(e))
            self.physical_resource_id = 'could-not-create'
            self.fail(str(e))

    def update(self):
        pass

    def delete(self):
        try:
            log.info("Deleting SGW NFS file share %s", self.physical_resource_id)

            response = self.storagegw.delete_file_share(
                FileShareARN=self.physical_resource_id,
                ForceDelete=True
            )

            log.debug("%s", response)
        except ClientError as e:
            log.error("ClientError %s", str(e))
            self.fail(str(e))


provider = StorageGatewayNfsFileShareProvider()


def handler(request, context):
    return provider.handle(request, context)
