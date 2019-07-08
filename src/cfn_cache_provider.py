import os
import logging
import string
import random

from cfn_resource_provider import ResourceProvider

import boto3
from botocore.exceptions import ClientError


schema = {
    "type": "object",
    "oneOf": [{
        "required": ["GatewayARN", "DiskIds"],
        "properties": {
            "GatewayARN": { "type": "string",
                "description": "The Amazon Resource Name (ARN) of the file gateway on which you want to create a file share." },
            "DiskIds": { "type": "array",
                "description": "An array of strings that identify disks that are to be configured as working storage.",
                "items": {
                    "type": "string"
                }
            }
        }
    }, {
        "required": ["GatewayARN", "DiskNodes"],
        "properties": {
            "GatewayARN": { "type": "string",
                "description": "The Amazon Resource Name (ARN) of the file gateway on which you want to create a file share." },
            "DiskNodes": { "type": "array",
                "description": "The device node of a local disk as assigned by the virtualization environment.",
                "items": {
                    "type": "string"
                }
            }
        }
    }]
}


class StorageGatewayCacheProvider(ResourceProvider):
    def __init__(self):
        super(StorageGatewayCacheProvider, self).__init__()
        self.request_schema = schema
        self.storagegw = boto3.client('storagegateway')

    def convert_property_types(self):
        self.heuristic_convert_property_types(self.properties)

    @staticmethod
    def random_string(size=8):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

    def create(self):
        try:
            log.info("Creating SGW cache %s", self.get("GatewayARN"))

            response = self.storagegw.add_cache(
                GatewayARN=self.get("GatewayARN"),
                DiskIds=self.get_disk_ids()
            )

            log.debug("%s", response)

            gateway_id = self.get("GatewayARN").split("/")[-1]
            self.physical_resource_id = "cfn-sg-cache-{}-{}".format(
                gateway_id, self.random_string())
        except ClientError as e:
            log.error("ClientError %s", str(e))
            self.physical_resource_id = 'could-not-create'
            self.fail(str(e))

    def get_disk_ids(self):
        if self.get("DiskIds") is not None:
            return self.get("DiskIds")
        else:
            response = self.storagegw.list_local_disks(
                GatewayARN=self.get("GatewayARN")
            )
            disk_ids = []
            for disk in response["Disks"]:
                if disk["DiskNode"] not in self.get("DiskNodes"): continue
                disk_ids.append(disk["DiskId"])
            return disk_ids

    def update(self):
        pass

    def delete(self):
        pass


provider = StorageGatewayCacheProvider()


def handler(request, context):
    return provider.handle(request, context)
