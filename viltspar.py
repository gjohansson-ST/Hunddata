import requests
from bs4 import BeautifulSoup
import time
import collections
import json

from parameters import dogs_param

def HUNDDATA_LIST(hund_id):
    payload = collections.OrderedDict()
    header = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
          'Accept-Encoding' : 'gzip, deflate',
          'Accept-language' : 'en-US,en;q=0.9',
          'Cache-Control' : 'max-age=0',
          'Connection' : 'keep-alive',
          'Content-Type': 'text/html; charset=utf-8',
          'Host' : 'www.bolsamadrid.es',
          'Origin' : 'null',
          'Upgrade-Insecure-Requests' : '1',
          'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
          }

    ses = requests.session()

    eventtarget = ""
    viewstategen = ""
    eventarg = ""
    viewstate = ""
    eventval = ""
    btnTavling = ""
    HiddenButtonPress = ""

    req = ses.get("https://hundar.skk.se/hunddata/Hund.aspx?hundid="+hund_id, headers = header)

    page = req.text
    soup = BeautifulSoup(page, "lxml")
    # find POST variables
    viewstate = soup.select("#__VIEWSTATE")[0]['value']
    #print("VIEWSTATE: ", viewstate)
    eventval = soup.select("#__EVENTVALIDATION")[0]['value']
    eventtarget = soup.select("#__EVENTTARGET")[0]['value']
    viewstategen = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
    eventarg = soup.select("#__EVENTARGUMENT")[0]['value']
    btnTavling = "Tävling"
    HiddenButtonPress = "Tävling"

    header = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Accept-Encoding' : 'gzip, deflate',
      'Accept-language' : 'en-US,en;q=0.9',
      'Cache-Control' : 'max-age=0',
      'Connection' : 'keep-alive',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Host' : 'www.bolsamadrid.es',
      'Origin' : 'null',
      'Upgrade-Insecure-Requests' : '1',
      'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
      }
    payload = collections.OrderedDict()
    payload['__EVENTTARGET'] = eventtarget
    #payload['__EVENTTARGET'] = "GoPag"
    #payload['__EVENTTARGET'] = "ct100$Contenido$GoPag"
    #payload['__EVENTTARGET'] = target.format(i + 1)
    payload['__EVENTARGUMENT'] = eventarg
    payload['__VIEWSTATE'] = viewstate
    payload['__VIEWSTATEGENERATOR'] = viewstategen
    payload['__EVENTVALIDATION'] = eventval
    payload['ctl00$bodyContent$btnTavling'] = btnTavling
    payload['ctl00$bodyContent$HiddenButtonPress'] = HiddenButtonPress

    req = ses.post("https://hundar.skk.se/hunddata/Hund.aspx?hundid="+hund_id, headers = header, data = payload)

    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    #print(req.request.body)
    #print(req.request.headers)
    #print(req.request.url)

    print("")
    hund_namn = soup.find("span", {"id" : "bodyContent_lblHundnamn"}).text.strip()
    print ("Namn: "+hund_namn)
    hund_regnr = soup.find("span", {"id" : "bodyContent_lblRegnr"}).text.strip()
    print ("Regnr: "+hund_regnr)
    print ("id: "+hund_id)


    #        print("EVENTVALIDATION: ", eventval)
    # Collect VILTSPÅR
    vilt=False
    table1 = soup.find("table", {"id" : "bodyContent_ctl00_tblTavling"})
    for table2 in table1.findAll("table"):
      for row in table2.findAll("tr"):
        cells = row.findAll("td")
        col1 = cells[0].text.strip()
        col2 = cells[1].text.strip()
        col3 = cells[2].text.strip()
        col4 = cells[3].text.strip()
        if col3 == "VILTSPÅRPROV":
          vilt = True
        if col4 != "" and col3 != "VILTSPÅRPROV":
          vilt = False
        if col4 != "" and vilt:
          print("Typ: "+col3)
        if col4 == "" and vilt:
          if col1!= "":
            print("Datum: "+col1)
          if col2[0:6] == "Domare":
            print("Domare: "+col3)
          if col2[0:5] == "Öppen":
            print("Klass: "+col2)
          elif col2[0:5] =="Anlag":
            print("Klass: "+col2)
          if col2[-2:] == "GK":
            print("Anlag GK: "+col2)
          if col2[0:4] == "Pris":
            print("Pris: "+col2[-1])
          if col2 == "HP":
            print("HP: "+col2)
          if col2[-3:] == "VCH" and col2[0:7] == "Godkänt":
            print("Champion: "+col2[-6:])

          #print("Information: "+col1+" "+col2+" "+col3)

for hund_id in dogs_param("dogs"):
  hund_id = str(hund_id)
  HUNDDATA_LIST(hund_id)
