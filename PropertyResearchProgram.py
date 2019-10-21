import re
import requests
import pandas as pd
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

inputcsvpath='PropertyResearchProgram-input.csv'
APN_input.to_csv(inputcsvpath, index=False)
APN_input=pd.read_csv(inputcsvpath)
APN_input['xPIN']=["{:08d}".format(x) for x in APN_input['PIN']]


# sometimes needs to be len 10 to work for some reason, most only len 8 with leading 0s 
# proposal didn't get accepted so no need to make it perfect anymore
# APNs=['0011111120', '0011111121', '0011111122', '0292011148', '07415111'] #8 digits

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }

# i=1
APNs=APN_input['PIN']
scrapped = []
loopLen=len(APNs)

for i in range(loopLen):

    txtAPNval="{:08d}".format(int(APNs[i])) #8 digits
    url = f"https://sccounty01.co.santa-cruz.ca.us/ASR/ParcelList/linkHREF?txtAPN={txtAPNval}"

    s = requests.session()
    r = s.get(url, headers=headers, verify=False)
    cookie = r.cookies.get_dict()
    response = s.get(url, cookies=cookie, headers=headers, verify=False)
    soup = BeautifulSoup(response.content, features="lxml")

    try:
        plmTbody = soup.find('div', attrs={'class': 'plmTbody'})
        foundAPN=plmTbody.find('div', attrs={'title': 'APN'}).text.strip()
        foundAddress=re.sub(' +', ' ', plmTbody.find('div', attrs={'title': 'Situs Address'}).text.strip())
        foundClass=plmTbody.find('div', attrs={'title': 'Class'}).text.strip()

    except AttributeError:
        foundAPN=None
        foundAddress=None
        foundClass=None

    appendme=[foundAPN, foundAddress, foundClass]
    scrapped.append(appendme)
    print("{}/{}".format(i+1, loopLen))

col_names = ['xPIN', 'Address', 'Class',]
scrapped_df = pd.DataFrame(scrapped, columns = col_names,)

# TODO change PIN to either string or int on both DFs
APN_input.dtypes
scrapped_df.dtypes

final=APN_input\
    .drop(['Class'], axis=1)\
    .merge(scrapped_df, how='left', on='xPIN')
