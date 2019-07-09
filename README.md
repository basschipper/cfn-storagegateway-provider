# AWS Storage Gateway provider

The missing provider for managing a Storage Gateway from CloudFormation.
This custom resource currently consists of 3 providers:

* Custom::StorageGateway - [schema](src/cfn_storage_gateway_provider.py)
* Custom::StorageGatewayCache - [schema](src/cfn_cache_provider.py) 
* Custom::StorageGatewayNfsFileShare - [schema](src/cfn_file_share_provider.py)

For more information on the used parameters please refer to the [Boto 3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/storagegateway.html).

## Example

```yaml
---
AWSTemplateFormatVersion: 2010-09-09
Description: Storage Gateway
Resources:
  StorageGateway:
    Type: Custom::StorageGateway
    Properties:
      ActivationKey: HCI67-V3G3Q-HGJ1R-PC2H5-N1A9O
      GatewayName: example-storage
      GatewayTimezone: GMT+1:00
      GatewayRegion: eu-west-1
      GatewayType: FILE_S3
      Tags:
        - Key: Department
          Value: Finance
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:knmi-cfn-storagegateway-provider'
  StorageGatewayCache:
    Type: Custom::StorageGatewayCache
    Properties:
      GatewayARN: !Ref StorageGateway
      DiskNodes:
        - /dev/sdf
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:knmi-cfn-storagegateway-provider'
  StorageGatewayFileShareRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: storagegateway.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: StorageGatewayProvider
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action:
                  - s3:GetAccelerateConfiguration
                  - s3:GetBucketLocation
                  - s3:GetBucketVersioning
                  - s3:ListBucket
                  - s3:ListBucketVersions
                  - s3:ListBucketMultipartUploads
                Resource: arn:aws:s3:::target-bucket
                Effect: Allow
              - Action:
                  - s3:AbortMultipartUpload
                  - s3:DeleteObject
                  - s3:DeleteObjectVersion
                  - s3:GetObject
                  - s3:GetObjectAcl
                  - s3:GetObjectVersion
                  - s3:ListMultipartUploadParts
                  - s3:PutObject
                  - s3:PutObjectAcl
                Resource: arn:aws:s3:::target-bucket/*
                Effect: Allow
  StorageGatewayNfsFileShare:
    Type: Custom::StorageGatewayNfsFileShare
    Properties:
      NFSFileShareDefaults:
        FileMode: "0666"
        DirectoryMode: "0777"
        GroupId: 65534
        OwnerId: 65534
      GatewayARN: !GetAtt StorageGateway.Arn
      Role: !GetAtt StorageGatewayFileShareRole.Arn
      LocationARN: arn:aws:s3:::target-bucket
      DefaultStorageClass: S3_STANDARD
      ObjectACL: private
      ClientList:
        - 0.0.0.0/0
      Squash: RootSquash
      ReadOnly: False
      GuessMIMETypeEnabled: True
      RequesterPays: False
      Tags:
        - Key: Department
          Value: Finance
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:knmi-cfn-storagegateway-provider'
```