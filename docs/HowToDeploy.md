#  How to deploy **qctokyo**

## Register your domain (optional)

For example, you can register your domain from Route53.
see https://aws.amazon.com/route53/ .

## Change your profile name to your own (mandatory)

the value of key name `custom.profile` to your own profile name. (default `qctokyo`)  
`custom.profile` is described to the following files:
- `<qctokyo>/serverless/common/serverless.yml`  
- `<qctokyo>/serverless/apps/serverless.yml`  

`custom.profile` must be changed as it is used for a unique name in the world.

## Describe the settings for each stage (mandatory)

Describe the settings for each stage in the yaml file.
- `<qctokyo>/serverless/conf/dev.yml`  
- `<qctokyo>/serverless/conf/prd.yml`

settings:
| key name         | description                                                                       |
| :--------------- | :-------------------------------------------------------------------------------- |
| webSiteName      | the URL of the website to be launched, omitting the protocol part.                |
| region           | the region to deploy.                                                             |
| schedule.enabled | whether to do daily updates. if do daily updates, set `true`. otherwise, `false`. |


## Configure paramters to AWS Systems Manager (mandatory)

Put following secret paramters to AWS Systems Manager(ssm) before `sls deploy`.
```
aws ssm put-parameter --profile <your_profile>-<stage> --name /account --type String --value "xxx"
aws ssm put-parameter --profile <your_profile>-<stage> --name /<your_profile>/<stage>/IBMQ_TOKEN --type String --value "xxx"
aws ssm put-parameter --profile <your_profile>-<stage> --name /<your_profile>/<stage>/SLACK_WEBHOOK_URL --type String --value "xxx"
```

## Make Qiskit as AWS Lambda layers (mandatory)

see [HowToMakeQiskitLayer.md](HowToMakeQiskitLayer.md).

## Deploy applications (mandatory)

Deploy in the order of `common` and `apps`.  

Deploy common(AWS Lambda Layers).
```
cd <qctokyo>/serverless/common
sls deploy --stage <stage>
```

Deploy applications(source codes and web contents).
```
cd <qctokyo>/serverless/apps
sls deploy --stage <stage>
```

## Configure Route53, Certificate Manager and CloudFront (optional)

see https://aws.amazon.com/route53/ .  
see https://aws.amazon.com/certificate-manager/ .  
see https://aws.amazon.com/cloudfront/ .
