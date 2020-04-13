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

class vetdata(hass.Hass):

  def initialize(self):

    #collect arg list
    self.hund_id = self.args["hund"]
    #run every 15 minutes
    self.run_every(self.gethund, datetime.datetime.now() + datetime.timedelta(seconds=20), 15*60)

  def gethund(self, kwargs):
    for hund in self.hund_id:
      hund_id = str(hund)
      #self.log("hund_id: "+hund_id)
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
      btnVeterinar = ""
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
      btnVeterinar = "Veterinär"
      HiddenButtonPress = "Veterinär"

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
      payload['__EVENTARGUMENT'] = eventarg
      payload['__VIEWSTATE'] = viewstate
      payload['__VIEWSTATEGENERATOR'] = viewstategen
      payload['__EVENTVALIDATION'] = eventval
      payload['ctl00$bodyContent$btnVeterinar'] = btnVeterinar
      payload['ctl00$bodyContent$HiddenButtonPress'] = HiddenButtonPress

      req = ses.post("https://hundar.skk.se/hunddata/Hund.aspx?hundid="+hund_id, headers = header, data = payload)

      page = req.text
      soup = BeautifulSoup(page, 'html.parser')

      self.textvalue = "Ny information! - "
      hund_namn = soup.find("span", {"id" : "bodyContent_lblHundnamn"}).text.strip()
      self.textvalue = " Namn: "+hund_namn+","
      hund_regnr = soup.find("span", {"id" : "bodyContent_lblRegnr"}).text.strip()
      self.textvalue = self.textvalue+" Regnr: "+hund_regnr+","
      self.textvalue = self.textvalue+" id: "+hund_id+","
      #self.log("First run: "+self.textvalue)
      # Collect VETDATA
      table = soup.find("table", {"id" : "bodyContent_ctl00_gridVeterinar"})
      if table:
        for row in table.findAll("tr")[1:]:
          cells = row.findAll("td")
          col1 = cells[0].text.strip()
          col2 = cells[1].text.strip()
          col3 = cells[2].text.strip()

          self.textvalue = self.textvalue+" Datum: "+col1+","
          self.textvalue = self.textvalue+" Klinik: "+col2+","
          self.textvalue = self.textvalue+" Resultat: "+col3+","

      else:
        self.textvalue = self.textvalue+" Resultat: "+"No data"

      self.readin = ""
      self.readin = self.get_state("input_text.vetdata"+hund_id)

      #self.log("readin: "+self.readin)
      self.readnew = ""
      self.readnew = str(self.textvalue)
      #self.log("readnew: "+self.readnew)

      if self.readin != self.readnew and self.readin != "" and self.readin != "unknown":
        #self.notify("Text changed")
        self.notify(self.readnew, name = "sendtext", target = ["+46739734588","+46730301608"])
        self.log("Sent notification by sms")
        self.set_textvalue("input_text.vetdata"+hund_id, self.readnew)
        self.log("Wrote text to vetdata")
      else:
        if self.get_state("input_text.vetdata"+hund_id) == "unknown":
          self.set_textvalue("input_text.vetdata"+hund_id, self.readnew)

      #Update Vetdata_lastupdate
      #self.set_textvalue("input_datetime.vetdata_lastupdate", datetime.datetime.now())
      new_time = datetime.datetime.now()
      date_str = new_time.strftime("%Y-%m-%d")
      time_str = new_time.strftime("%H:%M:%S")
      #self.log ("input_datetime.vetdata_lastupdate: "+str(datetime.datetime.strptime(self.get_state("input_datetime.vetdata_lastupdate"), "%Y-%m-%d %H:%M:%S")))
      #self.log ("check 1: "+str(datetime.datetime.strptime(self.get_state("input_datetime.vetdata_lastupdate"), "%Y-%m-%d %H:%M:%S") + timedelta(minutes=-2)))
      if new_time + timedelta(minutes=-2) > datetime.datetime.strptime(self.get_state("input_datetime.vetdata_lastupdate"), "%Y-%m-%d %H:%M:%S"):
        #self.log("Run only once?")
        self.call_service("input_datetime/set_datetime",
          entity_id = "input_datetime.vetdata_lastupdate",
          date = date_str,
          time = time_str
        )
        #self.log("No change")

