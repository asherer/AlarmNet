#!/usr/bin/env python3

import xml.etree.ElementTree as ET 
import requests

class AlarmNet(object):

    def __init__(self, username=None, password=None):
        self._username = username
        self._password = password
        self.sessionID = None
        self.urlbase = 'https://rs.alarmnet.com/TC21api/tc2.asmx/'
        self.switches = {}
        self.locations = {}
        self.securityDeviceID = None
        self.automationDeviceID = None
        self.locationID = None

    def get_sessionid(self):
        #loginurl = 'AuthenticateUserLogin'
        loginurl = 'LoginAndGetSessionDetails'
        header = "?userName="+self._username + "&password="+self._password + "&ApplicationID=14588&ApplicationVersion=3.14.2&LocaleCode=1"
        ret = requests.get(self.urlbase+loginurl+header)
        if ret.status_code == 200:
            # tst = ret.text
            ret = ET.fromstring(ret.text)
            self.sessionID = ret.find('.//{https://services.alarmnet.com/TC2/}SessionID').text  

            #added 2/17/2018 
            self.securityDeviceID = ret.find('.//{https://services.alarmnet.com/TC2/}SecurityDeviceID').text
            self.locationID = ret.find('.//{https://services.alarmnet.com/TC2/}LocationID').text
            ret = ret.findall('.//{https://services.alarmnet.com/TC2/}DeviceInfoBasic')
            for locs in ret:
                alocation = {}
                for loc in locs:
                    alocation[loc.tag.replace('{https://services.alarmnet.com/TC2/}','')] = loc.text
                self.locations[alocation['DeviceName']] = dict(alocation)     
            self.automationDeviceID = self.locations['Automation']['DeviceID']
            # add 2/17/2018 end

            return (self.sessionID)
        else:
            return (ret.status_code) 

    def get_status(self):
        statusurl = 'GetPanelSecurityStatusforUser'
        header = '?SessionID=' + self.sessionID + '&LastSequenceNumber=1&LastUpdatedTimestampTicks=1'
        ret = requests.get(self.urlbase + statusurl + header)
        # print ("xxxx", ret.text)
        ret = ET.fromstring(ret.text)
        
        return  ret.find('.//{https://services.alarmnet.com/TC2/}ArmingState').text 

    def ControlSwitch(self, switchid, action):
       
        if type(action) != "<class 'str'>":
            action = str(action)
        statusstring = 'ControlASwitch'
        headerstring = '?SessionID=' + self.sessionID + '&DeviceID=' + self.automationDeviceID + '&SwitchID='+switchid+'&SwitchAction='+action
        #print (self.urlbase + statusstring + headerstring)
        ret = requests.get(self.urlbase + statusstring + headerstring)
        #p rint (ret.text)
        ret = ET.fromstring(ret.text)
        
        return  ret.find('.//{https://services.alarmnet.com/TC2/}ResultData').text 

    def GetAutomationDeviceStatus(self):
        statusstring = 'GetAutomationDeviceStatus'
        headerstring = '?SessionID=' + self.sessionID + '&DeviceID=' + self.automationDeviceID + '&AdditionalInput='
        ret = requests.get(self.urlbase + statusstring + headerstring)
        root = ET.fromstring(ret.text)
        root = root.findall('.//{https://services.alarmnet.com/TC2/}SwitchInfo')
        for devices in root:
            aswitch = {}
            for device in devices:
                aswitch[device.tag.replace('{https://services.alarmnet.com/TC2/}','')] = device.text
            self.switches[aswitch['SwitchName']] = dict(aswitch)

    def GetSessionDetails(self):
        statusstring = 'GetSessionDetails'
        headerstring = '?SessionID=' + self.sessionID + '&ApplicationID=14588&ApplicationVersion=3.14.2'
        ret = requests.get(self.urlbase + statusstring + headerstring)
        # rint (ret.text)
        root = ET.fromstring(ret.text)
        self.securityDeviceID = root.find('.//{https://services.alarmnet.com/TC2/}SecurityDeviceID').text
        self.locationID = root.find('.//{https://services.alarmnet.com/TC2/}LocationID').text
        root = root.findall('.//{https://services.alarmnet.com/TC2/}DeviceInfoBasic')
        for locs in root:
            alocation = {}
            for loc in locs:
                alocation[loc.tag.replace('{https://services.alarmnet.com/TC2/}','')] = loc.text
            self.locations[alocation['DeviceName']] = dict(alocation)     
        self.automationDeviceID = self.locations['Automation']['DeviceID']   

    def armSystem(self, usercode, armtype='1'):
        # 0 = Away   1 = Stay  2 = Instant
        if type(usercode) != "<class 'str'>":
            usercode = str(usercode)
        statusstring = 'ArmSecuritySystem'
        headerstring = '?SessionID=' + self.sessionID + '&LocationID=1098763&DeviceID=' + self.securityDeviceID+ '&ArmType=' + armtype + '&Usercode=' + usercode
        ret = requests.get(self.urlbase + statusstring + headerstring)
        print (ret.text)
    
    def disarmSystem(self, usercode):
        if type(usercode) != "<class 'str'>":
            usercode = str(usercode)
        statusstring = 'DisarmSecuritySystem'
        headerstring = '?SessionID=' + self.sessionID + '&LocationID=1098763&DeviceID=' + self.securityDeviceID+ '&Usercode=' + usercode
        ret = requests.get(self.urlbase + statusstring + headerstring)
        print (ret.text)

    def logout(self):
        statusstring = 'Logout'
        headerstring = '?SessionID=' + self.sessionID
        return (requests.get(self.urlbase + statusstring + headerstring).text)

    def getSceneList(self):
        statusstring = 'GetSceneList'
        headerstring = '?SessionID=' + self.sessionID + '&DeviceID=' + self.automationDeviceID
        return (requests.get(self.urlbase + statusstring + headerstring).text)

    def login(self):
        self.get_sessionid()
        self.GetSessionDetails()
        self.get_status()
