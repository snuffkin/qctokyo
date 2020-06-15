#  How to make Qiskit as AWS Lambda layers

## Prepare an environment

If you already have an environment, skip this step.  
For example, prepare with the following command.

```
sudo yum update -y
sudo yum install gcc -y
sudo yum install python3-devel -y

pip3 install --user virtualenv
python3 -m venv venv
source ./venv/bin/activate
```

## Get the files to make layers

Use pip to get the files.
```
mkdir -p qiskit-layer/python
cd qiskit-layer/python
pip3 install qiskit-ibmq-provider==0.4.5 -t .
cd ../../
mkdir -p terra-tmp
cd terra-tmp
pip3 install qiskit-terra==0.11.1 -t .
cp -pr ./* ../qiskit-layer/python

cd ../qiskit-layer/python

rm -rf numpy/ numpy-1.18.5.dist-info/ numpy.libs/ scipy/ scipy-1.4.1.dist-info/ sympy/ sympy-1.6.dist-info/ urllib3/ urllib3-1.25.9.dist-info/
```

Modify `qiskit-layer/python/qiskit/providers/basicaer/basicaerjob.py` because `ProcessPoolExecutor` is not available on AWS Lambda.

Before:
```
    if sys.platform in ['darwin', 'win32']:
        _executor = futures.ThreadPoolExecutor()
    else:
        _executor = futures.ProcessPoolExecutor()
```

After:
```
    _executor = futures.ThreadPoolExecutor()
    #if sys.platform in ['darwin', 'win32']:
    #    _executor = futures.ThreadPoolExecutor()
    #else:
    #    _executor = futures.ProcessPoolExecutor()
```

## deploy

Copy `qiskit-layer` directory to `serverless/common` directory and deploy AWS Lambda Layers.
```
cp -pr qiskit-layer <qctokyo>/serverless/common
cd <qctokyo>/serverless/common
sls deploy --stage <stage>
```

Deploy applications(source codes and web contents).
```
cd <qctokyo>/serverless/apps
sls deploy --stage <stage>
```

# Limits

AWS Lambda has a limit of 250MB on the size of a deployment package.  
To work around this limit, **qctokyo** excludes `sympy` from AWS Lambda layers.  
Therefore, you cannot use any qiskit features that use `sympy` (e.g. parameterized circuits).
