# AWS Storage Gateway provider

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
      GatewayARN: !GetAtt StorageGateway.Arn
      Role: !GetAtt StorageGatewayFileShareRole.Arn
      LocationARN: arn:aws:s3:::target-bucket
      ClientList:
        - 0.0.0.0/0
      Tags:
        - Key: Department
          Value: Finance
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:knmi-cfn-storagegateway-provider'
```