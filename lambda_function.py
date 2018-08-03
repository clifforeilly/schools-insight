import boto3
import uuid
import datetime
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    print(e)

def soupIt(content):
    html = BeautifulSoup(content, 'html.parser')
    return html

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during request to {0} : {1}'.format(url,str(e)))
        return None

def get_file_url():
    raw_html = simple_get('https://www.gov.uk/government/publications/schools-in-england')
    for i, a in enumerate(soupIt(raw_html).select('a')):
        if(a['href'].find("EduBase_Schools")!=-1 & a['href'].find(".ods") != -1):
            file_url = 'https://www.gov.uk/' + a['href']
    return file_url

def get_now():
    fmt = '%Y%m%d%H%M%S.%f'
    return datetime.datetime.now().strftime(fmt)

def lambda_handler(event, context):
    client = boto3.resource('dynamodb')
    table = client.Table("schools-insight-testing")
    started=get_now()
    new_url=get_file_url()
    ended=get_now()
    response = table.put_item(Item= {'SchoolID': uuid.uuid4().hex ,'SchoolName':  new_url, 'Started': started, 'Ended': ended})

    return {'statusCode': 200, 'headers': { 'Content-Type': 'application/json' },'body': str(response)}
