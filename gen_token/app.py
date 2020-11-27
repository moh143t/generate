
from fyers_api import accessToken
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sys
import time
import re
import boto3
from alice_blue import *

options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=options,executable_path='geckodriver.exe')

# If you are using Chrome



# Load all the credentials from .env file

USERNAME='DM01293'
PASSWORD='yadaV$963'
PANCARD='EKXPK1061C'
APPID='VJU8B75HKB'
SECRETID='Q18B6KZ6WI'



def generate_token_url(app_id, secret_id):
    """ This function will generate the url which contains the Access Token

    Parameters:
    -----------
    app_id: string
        App Id is generated when we create an app in Fyers API. Saved in .env file as APPID
    secret_id: string
        Secret Id is generated when we create an app in Fyers API. Saved in .env file as SECRETID

    Returns:
    --------
    url_with_token: string
        It returns the url which contains the token of the kind
        https://127.0.0.1?access_token=gAAAAABc3Sh9QpE5mNx2mSz6vvvT29SAsELqkfbKQKa2977zHw3NdPBhe6jAZCBumHvYUum87j53-AzMEPXMjQw31wkRviZ1TdM5OimgTYWEEorWDmWuHnY=&user_id=FYXXXX
    """

    app_session = accessToken.SessionModel(app_id, secret_id)
    response = app_session.auth()
    # Check if we gets the response
    if response["code"] != 200:
        sys.exit()
        print('Error- Response Code != 200')
    # Get Authorization Code
    auth_code = response['data']['authorization_code']
    app_session.set_token(auth_code)
    # Get URL with the Authorization Code
    generate_token_url = app_session.generate_token()
    # Open the URL in browser
    driver.get(generate_token_url)
    # Get credentials elements from the html
    user_name = driver.find_element_by_id('fyers_id')
    password = driver.find_element_by_id('password')
    pan_card = driver.find_element_by_id('pancard')
    submit_button = driver.find_element_by_id('btn_id')
    # Fill in the credentials
    user_name.send_keys('DM01293')
    password.send_keys(PASSWORD)
    pan_card.send_keys(PANCARD)
    submit_button.click()
    # Wait for a while so that the url changes
    time.sleep(30)
    # Get the current URL (which contains access token)
    url_with_token = driver.current_url
    driver.quit() # Close the browser
    return url_with_token


def extract_token(full_url):
    """ This function extracts the Access Token from the complete url returned by generate_token_url() function using regex.

    Parameters:
    -----------
    full_url: str
        It is the complete url returned by generate_token_url
        https://127.0.0.1?access_token=gAAAAABc3Sh9QpE5mNx2mSz6vvvT29SAsELqkfbKQKa2977zHw3NdPBhe6jAZCBumHvYUum87j53-AzMEPXMjQw31wkRviZ1TdM5OimgTYWEEorWDmWuHnY=&user_id=FYXXXX

    Returns:
    access_token : sting > pickle
        It returns the access token in str format and later on saves it as a pickle in a file called fyers_token.pickle
        This access token is valid through 7-8 AM of the next day.
    """
    access_token = re.search(r'(?<=https://api-docs.fyers.in/v1\?access_token=).*?(?=user_id=DM01293)', full_url).group(0)
    if access_token:
        access_token_final=access_token+'user_id=DM01293'
        write_s3_fyers(access_token_final)
        return access_token_final
    else:
        print("No token generated")
        return "No token generated"

def token_gen():
    access_token = AliceBlue.login_and_get_access_token(username='102626', password='Ram@123', twoFA='a',
                                                        api_secret="HK1XF29WIGY6CTEDQKP5E9QX9X86NBNILLEWBFQSKBGORQ3EBI9AGJQI3DXS3CJG")
    bear_token=str("{")+str("'Authorization': 'Bearer")+str(" ")+str(access_token)+str("'")+str("}")
    write_s3_alice(str(bear_token))
    return {"Authorization":bear_token}

def write_s3_fyers(data):
    s3 = boto3.resource('s3')
    s3.Bucket('fyers77').put_object(Key='key.txt',Body=str(data))
    print("fyers token ---s3 written")

def write_s3_alice(data):
    s3 = boto3.resource('s3')
    s3.Bucket('aliceblue77').put_object(Key='key.txt',Body=str(data))
    print("aliceblue token ---s3 written")

def main():
    full_url = generate_token_url(APPID, SECRETID)
    r=extract_token(full_url)
    token_gen()
    return {'response':r}


if __name__ == '__main__':
    main()
