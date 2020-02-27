import os, sys
from zipfile import ZipFile
import tempfile
import boto3

bucket='er-lambda-python-code'
pkg = 'asana_tag_filter.zip'

files = ['pkg_lambda.py', 'asana.py', 'table.html']

def add_files_from_dir(d):
    for root, dn, fnames in os.walk(d):
        for fn in fnames:
            if not (fn.endswith('pyc') or fn.endswith('pyd')):
                files.append(os.path.join(root, fn))

for d in []:
    add_files_from_dir(d)


with ZipFile(pkg, 'w') as zf:
    for f in files:
        zf.write(f)

print('zip file created successfully')

s3 = boto3.client('s3')
s3.upload_file(pkg, bucket, pkg)

print('pkg {} uploaded to s3'.format(pkg))

aws_lambda = boto3.client('lambda')
out = aws_lambda.update_function_code(FunctionName='test_abc', S3Bucket=bucket, S3Key=pkg, DryRun=False)
if out['ResponseMetadata']['HTTPStatusCode'] == 200:
    print('lambda code update success')
else:
    print('lambda code udpate failed')
