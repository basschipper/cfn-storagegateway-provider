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
        "NFSFileShareDefaults" : { "type": ["object", "null"],
            "properties": {
                "FileMode": { 
                    "type": "string",
                    "desription" : "The Unix file mode in the form nnnn.",
                    "default": "0666"
                },
                "DirectoryMode": { 
                    "type": "string",
                    "desription" : "The Unix directory mode in the form nnnn." ,
                    "default": "0777"
                },
                "GroupId": { 
                    "type": "integer",
                    "desription" : "The default group ID for the file share (unless the files have another group ID specified).",
                    "default": 65534
                },
                "OwnerId": { 
                    "type": "integer",
                    "desription" : "The default owner ID for files in the file share (unless the files have another owner ID specified).",
                    "default": 65534
                }
            },
            "default": {}
        },
        "GatewayARN": {
            "type": "string",
            "description": "The Amazon Resource Name (ARN) of the file gateway on which you want to create a file share." 
        },
        "Role": { 
            "type": "string",
            "description": "The ARN of the AWS Identity and Access Management (IAM) role that a file gateway assumes when it accesses the underlying storage." 
        },
        "LocationARN": { 
            "type": "string",
            "description": "The ARN of the backed storage used for storing file data." 
        },
        "DefaultStorageClass": { 
            "type": "string",
            "description": "The default storage class for objects put into an Amazon S3 bucket by the file gateway.",
            "enum": ["S3_STANDARD", "S3_STANDARD_IA", "S3_ONEZONE_IA"],
            "default": "S3_STANDARD" 
        },
        "ObjectACL": { 
            "type": "string",
            "description": "A value that sets the access control list permission for objects in the S3 bucket that a file gateway puts objects into.",
            "enum": ["private", "public-read", "public-read-write", "authenticated-read", "bucket-owner-read", "bucket-owner-full-control", "aws-exec-read"],
            "default": "private"
        },
        "ClientList": { 
            "type": "array",
            "description": "The list of clients that are allowed to access the file gateway. The list must contain either valid IP addresses or valid CIDR blocks." 
        },
        "Squash": { 
            "type": "string",
            "description": "A value that maps a user to anonymous user.",
            "enum": ["RootSquash", "NoSquash", "AllSquash"],
            "default": "RootSquash"
        },
        "ReadOnly": { 
            "type": "boolean",
            "description": "A value that sets the write status of a file share.",
            "default": False 
        },
        "GuessMIMETypeEnabled": { 
            "type": "boolean",
            "description": "A value that enables guessing of the MIME type for uploaded objects based on file extensions.",
            "default": True 
        },
        "RequesterPays": { 
            "type": "boolean",
            "description": "A value that sets who pays the cost of the request and the cost associated with data download from the S3 bucket.",
            "default": False 
        },
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
                NFSFileShareDefaults=self.get("NFSFileShareDefaults"),
                GatewayARN=self.get("GatewayARN"),
                Role=self.get("Role"),
                LocationARN=self.get("LocationARN"),
                DefaultStorageClass=self.get("DefaultStorageClass"),
                ObjectACL=self.get("ObjectACL"),
                ClientList=self.get("ClientList"),
                Squash=self.get("Squash"),
                ReadOnly=self.get("ReadOnly"),
                GuessMIMETypeEnabled=self.get("GuessMIMETypeEnabled"),
                RequesterPays=self.get("RequesterPays"),
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
        try:
            log.info("Updating SGW NFS file share %s", self.physical_resource_id)

            response = self.storagegw.update_nfs_file_share(
                FileShareARN=self.physical_resource_id,
                NFSFileShareDefaults=self.get("NFSFileShareDefaults"),
                DefaultStorageClass=self.get("DefaultStorageClass"),
                ObjectACL=self.get("ObjectACL"),
                ClientList=self.get("ClientList"),
                Squash=self.get("Squash"),
                ReadOnly=self.get("ReadOnly"),
                GuessMIMETypeEnabled=self.get("GuessMIMETypeEnabled"),
                RequesterPays=self.get("RequesterPays")
            )

            log.debug("%s", response)

            self.set_attribute('Arn', response["FileShareARN"])
            self.physical_resource_id = response["FileShareARN"]
        except ClientError as e:
            log.error("ClientError %s", str(e))
            self.physical_resource_id = 'could-not-update'
            self.fail(str(e))

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
