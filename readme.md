# SAML2AWS

## Description

This is a script to generate and obtain temporary credentials on AWS (access key pair) from a federated login via SAML. 

This scripts relies on authenticating in an ADFS Portal (like MS ADFS Services), getting a list of possible IAM Roles to assume and generating temporary credentials that can be passed in an AWS Config File.

## How to install

Clone this repo
```sh
git clone git@github.com:totvscloud-seginf/saml2aws.git
```

Install python3 from https://www.python.org/downloads/

Install library dependencies
```sh
cd saml2aws
pip install -r requirements.txt
```

## How to use it

Run the script:
```sh
cd saml2aws
python saml2aws.py
```
<strong>note: </strong>This script works with Python version3. If you already have Python version2 installed, use "python3 saml2aws.py" instead to run the correct runtime.

The script will ask you for 3 inputs:
- Your ADFS address (only the fqdn or ip address. Exclude https prefix or path).
eg: if your ADFS Portal is accessed in https://adfs.company.com/adfs/ldapsign/ your input should be only <strong>adfs.company.com</strong>

- Your username. This can be your full email address or your domain followed by your username (eg: DOMAIN\firstname.lastname)

- Your domain password.

Then the script will list the roles you have access to so you can choose one to be assumed.


After choosing the number of your option, it will present the json with your temporary credentials data.

Copy the access_key, secret_key and session_token in your AWS Credentials file (~/.aws/credentials) <strong>with the following format</strong>
```yaml
[default] #or a profile name you want to use
aws_access_key_id = ASIA000000000JYBYK6L
aws_secret_access_key = bSh4H2200000000000009XR/Z2/wEEPcw3NDq5
aws_session_token = FwoGZXIvY000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000AEuHocpSIe9pzMwc7G7uml+rMD0fmuqNsvbJJMhIbWiVEtT+hf6ZVx8SaQ+xqRVVskw=

```

## Common issues

### 1. SSL Validation error on login attempt

When your ADFS Portal uses a SelfSigned Certificate, the connection will fail due to a security validation. If that's your case and you can't replace the certificate on the ADFS Portal to a trusted one, add the parameter 'verify=False' on the requests call:

On the function login() replace:
```python
session.get(adfs_url) 
with 
session.get(adfs_url, verify=False)
```

### 2. SSL Validation error after choosing the role to be assumed

This is a rare and odd case, but iy may happen if you have some kind of SSL Inspection solution sniffing your API calls. That usually can be verified on your endpoint protection solution (Antivirus, EDR, etc) or on network tools (IPS, NGFW, CASB, etc).
In that case the best solution is to ask your IT Department to exclude the <strong>https://sts.amazonaws.com endpoint from the scanning filter</strong> categorizing it as a exception.
If that's not possible, add the same parameter to ignore validation on the assume_role funtion.

On the function assume_role() replace:
```python
client = boto3.client('sts')
with 
client = boto3.client('sts', verify=False)
```

