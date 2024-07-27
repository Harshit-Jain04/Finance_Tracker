import json
import requests
from datetime import datetime
import os 
def convert_to_ddmmyyyy(date_str):
    # List of date formats to try
    date_formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%b %d, %Y",
        "%B %d, %Y",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d %B %Y"
    ]

    for fmt in date_formats:
        try:
            # Try to parse the date string with the current format
            date_obj = datetime.strptime(date_str, fmt)
            # Return the date in dd-mm-yyyy format
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            # If parsing failed, try the next format
            continue
    return datetime.today()
    # If none of the formats match, raise an error
def extract(file):
    
    headers = {"Authorization":os.getenv('ACCESS')}

    url = "https://api.edenai.run/v2/ocr/financial_parser"
    data = {
        "providers": "amazon",
        "document_type" : "invoice",
        #"fallback_providers": ""
        "language": "en",
    }
    files = {'file': file}
    print('Request sent')
    response = requests.post(url, data=data, files=files, headers=headers)

    result = json.loads(response.text)
    print(result)
    result = result['amazon']['extracted_data'][0]
    date_string = result['financial_document_information']['invoice_date']

    date_string = convert_to_ddmmyyyy(date_string)
    
    r = {
        'Description':result['merchant_information']['name'] or "Uploaded Transaction",
        'Amount':result['payment_information']['total'],
        'Date': date_string or date.today().strftime("%Y-%m-%d") ,
    }
    return r
