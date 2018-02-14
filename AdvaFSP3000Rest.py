# a nice fancy header goes here

import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import pprint

HTTP_METHOD = "https"
AOS_API_VERSION = "1.0"

HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class CloudConnectAPIError(Exception):
    """Base error"""
    pass

class HTTPError(CloudConnectAPIError):
    """Generic error raised from CloudConnect API.
    """
    _errorcodes = {
        400: 'A request body cannot be properly parsed by the server.',
        401: 'Authentication credentials are invalid.',
        403: 'Client\'s user is unauthorized to access the requested resource or an RBAC violation.',
        404: 'Invalid URI.',
        405: 'HTTP verb not supported.',
        406: 'Invalid Accept header is specified for a method which takes an Accept header.',
        409: 'Duplicate Name Exception.',
        415: 'Invalid client specified by client for a media type while a URI specified by the client exists.',
        500: 'Internal server error.',
        503: 'Service unavailable.'
    }

    def __init__(self, msg, code=None):
        CloudConnectAPIError.__init__(self, msg)
        self.msg = msg
        self.code = code
        print '----------------'
        if code:
            print "Reason : %s" % self._errorcodes[code]
        print '----------------'

class CloudConnectApiClient(object):
    USER_AGENT = "CloudConnect API Client"

    def __init__(self, username=None, password=None, logger=logging):
        self._username = username
        self._password = password
        self._server = None
        self._token = None
        self._logger = logger

    def getServer(self):
       return self._server

    def setServer(self, server):
        self._server = HTTP_METHOD + '://' + server 

    def _modifyHeaders(self, headers):
        if self._token is not None:
            headers['X-Auth-Token'] = self._token

        headers['AOS-API-Version'] = "%s" %AOS_API_VERSION
        headers['User-Agent'] = self.USER_AGENT
        return headers

    def _get(self, data):
        return self._SendRequest('GET', data['path'], self._token, None, None, self._modifyHeaders(data['headers']))

    def _put(self):
        pass

    def _post(self, data):
        return self._SendRequest('POST', data['path'], self._token, None, data['body'], self._modifyHeaders(data['headers']))

    def _delete(self):
        pass

    def _Send(self, method, path, query, content, headers):
        pass

    def _SendRequest(self, method, path, token, query, content, headers):
        url = "%s/%s" % (self._server, path) #chek if self._server is None
        params = query
        data = content
        print '\n -------- DEBUG INFO ---------\n'
        print 'Method is %s \n' % method
        print 'URL is %s\n' % url
        print 'Params are %s\n' % params
        print "HEADERS are %s\n" %headers
        print 'Token is %s\n' %token
        print 'data are %s\n' %data
        print '\n -------- DEBUG INFO ---------\n'
        try:
            req = requests.request('%s' %method, url, params=params, headers=headers, auth=None, data=data, verify=False, timeout=120)  #ToDo set timeout parameter
            http_code = req.status_code
            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HTTPError (e, req.status_code)
        except (requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.RequestException) as e:
            raise HTTPError (e)

        print "Returned HTTP code %d\n" % http_code

        response = req.raw.read()
        response = req.text
        print response
        response_content = json.loads(response)
        try:
            response_content = req.json()
        except ValueError:
            raise CloudConnectAPIError(e)
        # Have to do some error handling here....
        if self._token is None:
            self._token = req.headers['X-Auth-Token']
        return response_content

    def login(self):
        """The login operation is used to authenticate a client to the REST
        API, begin a session and return a security token to the client.
        """
        token = None
        data = {}
        data['path'] = 'auth?actn=lgin'
        data['headers'] = {'Accept':'application/json;ext=nn', 
                    'Content-Type':'application/json;ext=nn'}

        req = {
                "in": {
                  "un": self._username,
                  "pswd": self._password
                }
              }
        data['body'] = json.dumps(req)
        return self._post(data)

    def GetSlotInventory(self):
        """Retreives inventory information from all slots of shelf 1
        """
        data = {}
        data['path'] = 'col/eqh?filter={"sl":{"$exists":true},"$ancestorsIn":["/mit/me/1/eqh/sh,1"]}'
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)
    
    def GetConfignStatus(self, shelf, slot):
        """Retrieves configuration and status information for an MP-2B4CT
        """
        data = {}
        data['path'] = 'mit/me/1/eqh/shelf,%d/eqh/slot,%d/eq/card' % (shelf, slot)
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def GetSubnetworkConnections(self, shelf, slot):
        """Retrieves Subnetwork connections are cross connections
        """
        data = {}
        data['path'] = 'mit/me/1/eqh/shelf,%d/eqh/slot,%d/eq/card/sn/odu4/snc' % (shelf, slot)
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def GetAlarmSummary(self):
        """Retrieves a summary of all alarms on the node/shelf.
        """
        data = {}
        data['path'] = 'mit/me/1/almsum'
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def GetAllSystemAlarms(self):
        """Retrieves all active alarms on the node
        """
        data = {}
        data['path'] = 'mit/me/1/alm'
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def GetModulePMData(self, shelf):
        """Retrieves module PM data
        """
        data = {}
        data['path'] = 'mit/me/1/eqh/shelf,%d/eqh/slot,cem/eq/card/pm/crnt' % (shelf)
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def GetPMDataNetworkPort(self, shelf, slot, port):
        """Retrieves  the current performance monitoring bin for a port,shelf,slot
        """
        data = {}
        data['path'] = 'mit/me/1/eqh/shelf,%d/eqh/slot,%d/eq/card/ptp/nw,%d/opt/pm/crnt' % (shelf, slot, port)
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def GetPMDataClientNetworkPort(self, shelf, slot, port):
        """Retrieves  the current performance monitoring bin for a port,shelf,slot
        """
        data = {}
        data['path'] = 'mit/me/1/eqh/shelf,%d/eqh/slot,%d/eq/card/ptp/cl,%d/ctp/et100/ety6/pm/crnt' % (shelf, slot, port)
        data['headers'] = {'Accept':'application/json;ext=nn', 
                           'Accept-Encoding': 'gzip',
                           'Content-Type':'application/json;ext=nn'}
        return self._get(data)

    def AddSubnetworkConnection(self, entname, shelf, slot):
        """Provisions the client and network ports
        """
        data = {}
        data['path'] = 'mit/me/1/eqh/shelf,%d/eqh/slot,%d/eq/card/sn/odu4/snc/%d' % (shelf, slot, entname)
        data['headers'] = {'Accept':'application/json;ext=nn', 
                   'Accept-Encoding': 'gzip',
                   'Content-Type':'application/json;ext=nn'}

        req = {"entname": str(entname), 
               "aendlist": ["/mit/me/1/eqh/shelf," + str(shelf) + "/eqh/slot," +
                            str(slot) + "/eq/card/ptp/cl," + str(entname) + 
                            "/ctp/et100/ctp/odu4"], 
               "zendlist": ["/mit/me/1/eqh/shelf," + str(shelf) + "/eqh/slot," +
                            str(slot) + "/eq/card/ptp/nw,2/ctp/ot200/ctp/odu4-2"]
               }
        
        data['body'] = json.dumps(req)
        return self._post(data)
