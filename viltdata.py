# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import datetime
from datetime import timedelta
import collections
import json
import os.path
import hassapi as hass

#from parameters import dogs_param
#hund_id = "2935205"

class viltdata(hass.Hass):

  def initialize(self):
    #collect arg list
    self.hund_id = self.args["hund"]
    #run every 15 minutes
    self.run_every(self.gethundvilt, datetime.datetime.now() + datetime.timedelta(seconds=20), 60*60)

  def gethundvilt(self, kwargs):
    for hund in self.hund_id:
      hund_id = str(hund)
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
      soup = BeautifulSoup(page, "html.parser")
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
      soup = BeautifulSoup(page, "html.parser")
      #print(req.request.body)
      #print(req.request.headers)
      #print(req.request.url)

      #print("")
      hund_namn = soup.find("span", {"id" : "bodyContent_lblHundnamn"}).text.strip()
      #print ("Namn: "+hund_namn)
      hund_regnr = soup.find("span", {"id" : "bodyContent_lblRegnr"}).text.strip()
      #print ("Regnr: "+hund_regnr)
      #print ("id: "+hund_id)
      huvuddata = "Namn: "+hund_namn+", "+"Regnr: "+hund_regnr+", "+"id: "+hund_id+""
      linjedata = ""
      #        print("EVENTVALIDATION: ", eventval)
      # Collect VILTSPÅR
      vilt=False
      table1 = soup.find("table", {"id" : "bodyContent_ctl00_tblTavling"})
      if table1:
        for table2 in table1.findAll("table"):
          for row in table1.findAll("tr"):
            cells = row.findAll("td")
            col1 = cells[0].text.strip()
            col2 = cells[1].text.strip()
            col3 = cells[2].text.strip()
            col4 = cells[3].text.strip()
            if col3 == "VILTSPÅRPROV":
              vilt = True
            if col4 != "" and col3 != "VILTSPÅRPROV":
              vilt = False
            #if col4 != "" and vilt:
            #  print("Typ: "+col3)
            if col4 == "" and vilt:
              if col1!= "":
                #print("")
                if linjedata == "":
                  linjedata = linjedata+"\nDatum: "+col1+""
                else:
                  linjedata = linjedata+"\n\nDatum: "+col1+""
                #print("Datum: "+col1)
              if col2[0:6] == "Domare":
                linjedata = linjedata+"\nDomare: "+col3+""
                #print("Domare: "+col3)
              if col2[0:5] == "Öppen":
                linjedata = linjedata+"\nKlass: "+col2+""
                #print("Klass: "+col2)
              elif col2[0:5] =="Anlag":
                linjedata = linjedata+"\nKlass: "+col2+""
                #print("Klass: "+col2)
              if col2[-2:] == "GK":
                linjedata = linjedata+"\nAnlag res: "+col2+""
                #print("Anlag res: "+col2)
              if col2[0:4] == "Pris":
                linjedata = linjedata+"\nPris: "+col2[-1]+""
                #print("Pris: "+col2[-1])
              if col2 == "HP":
                linjedata = linjedata+"\nHP: "+col2+""
                print("HP: "+col2)
              if col2[-3:] == "VCH" and col2[0:7] == "Godkänt":
                huvuddata = huvuddata+"\n\nChampion: "+col2[-6:]+""
                #print("Champion: "+col2[-6:])
      else:
        linjedata = " No data"
      #print (huvuddata)
      #print (linjedata)
      #print (len(linjedata))

      #run back
      new_time = datetime.datetime.now()
      date_str = new_time.strftime("%Y-%m-%d")
      time_str = new_time.strftime("%H:%M:%S")
      if new_time + timedelta(minutes=-2) > datetime.datetime.strptime(self.get_state("input_datetime.vetdata_lastupdate"), "%Y-%m-%d %H:%M:%S"):
        #self.log("Run only once?")
        self.call_service("input_datetime/set_datetime",
          entity_id = "input_datetime.viltdata_lastupdate",
          date = date_str,
          time = time_str
        )
      self.readin = float(0)
      self.readnew = float(0)
      self.readin = float(self.get_state("input_number.viltdata"+hund_id))
      self.readnew = float(len(linjedata))

      if self.readin <= float(8):
        self.set_value("input_number.viltdata"+hund_id, self.readnew)
        #self.log("id: "+hund_id+": first update")

      if self.readin != self.readnew:
        #send mail
        #self.log("Värde har ändrats: "+str(self.readnew))
        self.log("hund: "+hund_id)
        self.log("readin: "+str(self.readin))
        self.log("readnew: "+str(self.readnew))
        self.notify("Fullt utdrag:\n\n"+huvuddata+linjedata, title = "Viltspårdata ändrat för "+hund_namn+"/"+hund_regnr, name = "sendgmail")
        self.set_value("input_number.viltdata"+hund_id, self.readnew)
