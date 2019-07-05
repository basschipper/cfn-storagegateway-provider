import os
import logging
import cfn_storage_gateway_provider
import cfn_file_share_provider

log = logging.getLogger()
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def handler(request, context):
    if request['ResourceType'] == 'Custom::StorageGatewayNfsFileShare':
        return cfn_file_share_provider.handler(request, context)
    else:
        return cfn_storage_gateway_provider.handler(request, context)
