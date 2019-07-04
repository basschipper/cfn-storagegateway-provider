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
  StorageGatewayNfsFileShare:
    Type: Custom::StorageGatewayNfsFileShare
    Properties:
      GatewayARN: !GetAtt StorageGateway.Arn
      Role: arn:aws:iam::368462435992:role/s3-access
      LocationARN: arn:aws:s3:::target-bucket-2019
      ClientList:
        - 0.0.0.0/0
      Tags:
        - Key: Department
          Value: Finance
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:knmi-cfn-storagegateway-provider'
```