# -*- coding: utf-8 -*-

import boto3
import getpass
import requests
import urllib.parse
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json



adfs_domain = input("Insert your ADFS Portal domain name or ip: ")
adfs_url = f"https://{adfs_domain}/adfs/ls/idpinitiatedsignon.aspx?loginToRp=urn:amazon:webservices"
username = input("Insert your email address: ")
password = getpass.getpass("Insert your password: ")

session = None

def login(username, password) -> requests.Response:
    global session
    session = requests.Session()
    session.get(adfs_url, verify=False)
    data = {
        "Username": username,
        "Password": password,
        "AuthMethod":"FormsAuthentication",
    }
    data = urllib.parse.urlencode(data)
    return session.post(adfs_url, data=data)

def get_saml(request:requests.Response) -> str:
    soup = BeautifulSoup(request.text, features="lxml")
    assertion = ''
    # Look for the SAMLResponse attribute of the input tag (determined by
    # analyzing the debug print lines above)
    for inputtag in soup.find_all('input'):
        if(inputtag.get('name') == 'SAMLResponse'):
            #print(inputtag.get('value'))
            assertion = inputtag.get('value')
    return assertion

def get_roles_available(saml:str) -> list:
    '''
    Parse the XML SAML to get the roles

    Format:  <principal arn>,<role arn>
    '''
    awsroles = []
    root = ET.fromstring(base64.b64decode(saml))
    for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        if (saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
            for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                # text value: <principal arn>,<role arn>
                # awsroles.append(saml2attributevalue.text.split(",")[1])
                awsroles.append(saml2attributevalue.text)
    return awsroles

def assume_role(role_arn, principal_arn, saml_assertion) -> dict:
    client = boto3.client('sts')
    response = client.assume_role_with_saml(
        RoleArn=role_arn,
        PrincipalArn=principal_arn,
        SAMLAssertion=saml_assertion,
        DurationSeconds=3600
    )
    
    return response["Credentials"]


print("Authenticating..")
login_response = login(username, password)
xml_saml_response = get_saml(login_response)

roles = get_roles_available(xml_saml_response)

counter = 1
for role in roles:
    print(f"{counter} - {role.split(',')[0]} - {role.split(',')[1]}")
    counter += 1

max_roles_available = len(roles)
role_to_access = ""
while True:
    # 1 - <principal arn>,<role arn>
    # 2 - <principal arn>,<role arn>
    # 3 - <principal arn>,<role arn>
    # 4 - <principal arn>,<role arn>
    role_to_access = input("Insert the number to connect: ")
    try:
        role_to_access = int(role_to_access)
    except ValueError:
        print("Invalid input")
        continue
    
    if role_to_access < 1 or role_to_access > max_roles_available:
        print("Invalid input")
        continue
    
    break

accessed_role = roles[role_to_access-1]
principal_arn = accessed_role.split(",")[0]
role_arn = accessed_role.split(",")[1]

try:
    credentials = assume_role(
        role_arn=role_arn, 
        principal_arn=principal_arn,
        saml_assertion=xml_saml_response,
    )
except Exception as e:
    print("An unexpected error occured...")



print("Credentials successfully granted!")
print("Copy credentials to your AWS config file.")
print(json.dumps(credentials, indent=2, default=str))