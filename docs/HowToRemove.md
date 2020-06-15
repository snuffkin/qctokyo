#  How to remove(undeploy) **qctokyo**

## Remove applications (mandatory)

Remove in the order of `apps` and `common`(reverse order of deployment).  

Remove applications(source codes and web contents).
```
cd <qctokyo>/serverless/apps
sls remove --stage <stage>
```

Remove common(AWS Lambda Layers).
```
cd <qctokyo>/serverless/common
sls remove --stage <stage>
```

## Delete paramters from AWS Systems Manager (mandatory)

Delete following secret paramters from AWS Systems Manager(ssm) after `sls remove`.
```
aws ssm delete-parameter --profile <your_profile>-<stage> --name /account --type String --value "xxx"
aws ssm delete-parameter --profile <your_profile>-<stage> --name /<your_profile>/<stage>/IBMQ_TOKEN --type String --value "xxx"
aws ssm delete-parameter --profile <your_profile>-<stage> --name /<your_profile>/<stage>/SLACK_WEBHOOK_URL --type String --value "xxx"
```

## Delete S3 buckets and DynamoDB tables (mandatory)

If you execute `sls remove`, S3 buckets and DynamoDB tables are not removed.  
Therefore, you must delete them manually.

see https://aws.amazon.com/jp/s3/ .  
see https://aws.amazon.com/jp/dynamodb/ .  

## Configure Route53, Certificate Manager and CloudFront (optional)

If you configured Route53, Certificate Manager and CloudFront when you deployed, delete them.

see https://aws.amazon.com/route53/ .  
see https://aws.amazon.com/certificate-manager/ .  
see https://aws.amazon.com/cloudfront/ .
