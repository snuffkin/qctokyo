#  How to install **qctokyo**

## Get your account about cloud services.

1. get your AWS account. see https://aws.amazon.com/ .
1. get your IBM Q account. see https://www.ibm.com/quantum-computing/technology/experience/ .
1. get your Slack account. see https://slack.com/ .

## Software requirements

1. install Node.js. see https://nodejs.org/en/ .
2. install Python 3.7. see https://www.python.org/ .
3. install AWS Command Line Interface(AWS CLI). see https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html .
4. configure AWS CLI profiles.

In a standard configuration, use the stage `dev` and `prd`.

| stage | purpose of use                                  |
| :---- | :---------------------------------------------- |
| dev   | to deploy the development environment(for test) |
| prd   | to deploy the production environment            |

```
$ aws configure --profile <your_profile>-<stage>
AWS Access Key ID [None]: <your_access_key>
AWS Secret Access Key [None]: <your_secret_key>
Default region name [None]:
Default output format [None]:
```

5. get **qctokyo** source codes.
```
$ git clone https://github.com/snuffkin/qctokyo.git
```

From now on, the directory where **qctokyo** is cloned is written as `<qctokyo>`.

6. create coding environment by pipenv.
```
$ cd <qctokyo>
$ pip install pipenv
$ export PIPENV_VENV_IN_PROJECT=true
$ pipenv install --dev
```

7. install Serverless Framewok. see https://www.serverless.com/ .
```
$ npm install -g serverless

$ cd <qctokyo>/serverless/common
$ npm install

$ cd <qctokyo>/serverless/apps
$ npm install
```
