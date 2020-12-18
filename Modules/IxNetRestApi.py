# PLEASE READ DISCLAIMER
#
#    This class demonstrates sample IxNetwork REST API usage for
#    demo and reference purpose only.
#    It is subject to change for updates without warning.
#
# REQUIREMENTS
#    - Python 2.7 (Supports Python 2 and 3)
#    - Python modules: requests
#

from __future__ import absolute_import, print_function, division
import os, re, sys, requests, json, time, subprocess, traceback, time, datetime, platform
from ixnetwork_restpy import SessionAssistant
from ixnetwork_restpy import TestPlatform


class IxNetRestApiException(Exception):
    def __init__(self, msg=None):
        if platform.python_version().startswith('3'):
            super().__init__(msg)

        if platform.python_version().startswith('2'):
            super(IxNetRestApiException, self).__init__(msg)

        if Connect.robotStdout is not None:
            Connect.robotStdout.log_to_console(msg)

        showErrorMsg = '\nIxNetRestApiException error: {0}\n\n'.format(msg)
        print(showErrorMsg)
        if Connect.enableDebugLogFile:
            with open(Connect.debugLogFile, 'a') as restLogFile:
                restLogFile.write(showErrorMsg)


class Connect:
    # For IxNetRestApiException
    debugLogFile = None
    enableDebugLogFile = False
    robotStdout = None

    def __init__(self, apiServerIp=None, serverIpPort=None, serverOs='windows', linuxChassisIp=None,
                 manageSessionMode=False,
                 webQuickTest=False, username=None, password='admin', licenseServerIp=None, licenseMode=None,
                 licenseTier=None,
                 deleteSessionAfterTest=True, verifySslCert=False, includeDebugTraceback=True, sessionId=None,
                 httpsSecured=None,
                 apiKey=None, generateLogFile=True, robotFrameworkStdout=False, linuxApiServerTimeout=120):
        """
        Description
           Initializing default parameters and making a connection to the API server

        Notes
            Starting IxNetwork 8.50, https will be enforced even for Windows connection.
            If you still want to use http, you need to add -restInsecure to the IxNetwork.exe appliaction under "target".

        Examples
            Right click on "IxNetwork API server", select properties and under target
            ixnetwork.exe -restInsecure -restPort 11009 -restOnAllInterfaces -tclPort 8009

        Parameters
           apiServerIp: (str): The API server IP address.
           serverIpPort: (str): The API server IP address socket port.
           serverOs: (str): windows|windowsConnectionMgr|linux
           linuxChassisIp: (str): Connect to a Linux OS chassis IP address.
           webQuickTest: (bool): True: Using IxNetwork Web Quick Test. Otherwise, using IxNetwork.
           includeDebugTraceback: (bool):
                                   True: Traceback messsages are included in raised exceptions.
                                   False: No traceback.  Less verbose for debugging.
           username: (str): The login username. For Linux API server only.
           password: (str): The login password. For Linux API server only.
           licenseServerIp: (str): The license server IP address.
           licenseMode: (str): subscription | perpetual | mixed
           licenseTier: (str): tier1 | tier2 | tier3
           linuxApiServerTimeout: (int): For Linux API server start operation timeout. Defaults to 120 seconds.
           deleteSessionAfterTest: (bool): True: Delete the session.
                                           False: Don't delete the session.
           verifySslCert: (str): Optional: Include your SSL certificate for added security.
           httpsSecured: (bool): This parameter is only used by Connection Mgr when user wants to connect to
                                 an existing session.
                                 True = IxNetwork ReST API server is using HTTPS.
                                 This parameter must also include sessionId and serverIpPort=<the ssl port number>

           serverOs: (str): Defaults to windows. windows|windowsConnectionMgr|linux.
           includeDebugTraceback: (bool): True: Include tracebacks in raised exceptions.
           sessionId: (str): The session ID on the Linux API server or Windows Connection Mgr to connect to.
           apiKey: (str): The Linux API server user account API-Key to use for the sessionId connection.
           generateLogFile: True|False|<log file name>.  If you want to generate a log file, provide
                                the log file name.
                                True = Then the log file default name is ixNetRestApi_debugLog.txt
                                False = Disable generating a log file.
                                <log file name> = The full path + file name of the log file to create.
           robotFrameworkStdout: (bool):  True = Print to stdout.
           httpInsecure: (bool): This parameter is only for Windows connections.
                                     True: Using http.  False: Using https.
                                     Starting 8.50: IxNetwork defaults to use https.
                                     If you are using versions prior to 8.50, it needs to be a http connection.
                                     In this case, set httpInsecure=True.

        Notes
            Class attributes
               self._session: The requests initial Session().
               self.serverOs: windows|windowsConnectionMgr|linux

               self.httpHeader: http://{apiServerIp}:{port}
               self.sessionId : http://{apiServerIp}:{port}/api/v1/sessions/{id}
               self.sessionUrl: http://{apiServerIp}:{port}/api/v1/sessions/{id}/ixnetwork
               self.headlessSessionId: /api/v1/sessions/{id}
               self.apiSessionId:      /api/v1/sessions/{id}/ixnetwork

               self.jsonHeader: The default header: {"content-type": "application/json"}
               self.apiKey: For Linux API server only. Automatically provided by the server when login
                            successfully authenticated.
                            You could also provide an API-Key to connect to an existing session.
                            Get the API-Key from the Linux API server user account.

        Examples:
           Steps to connect to Linux API server steps:
               1> POST: https://{apiServerIp}/api/v1/auth/session
                  DATA: {"username": "admin", "password": "admin"}
                  HEADERS: {'content-type': 'application/json'}

               2> POST: https://{apiServerIp:{port}/api/v1/sessions
                  DATA: {"applicationType": "ixnrest"}
                  HEADERS: {'content-type': 'application/json', 'x-api-key': 'd9f4da46f3c142f48dddfa464788hgee'}

               3> POST: https://{apiServerIp}:443/api/v1/sessions/4/operations/start
                  DATA: {}
                  HEADERS: {'content-type': 'application/json', 'x-api-key': 'd9f4da46f3c142f48dddfa464788hgee'}

               sessionId = https://{apiServerIp}:443/api/v1/sessions/{id}

           Steps to connect to Linux Web Quick Test:
               1> POST: https://{apiServerIp}:443/api/v1/auth/session
                  DATA: {"username": "admin", "password": "admin"}
                  HEADERS: {'content-type': 'application/json'}

               2> POST: https://{apiServeIp}:443/api/v1/sessions
                  DATA: {'applicationType': 'ixnetwork'}

               3> POST: https://{apiServerIp}:443/api/v1/sessions/2/operations/start
                  DATA: {'applicationType': 'ixnetwork'}

            sessionId = https://{apiServerIp}/ixnetworkweb/api/v1/sessions/{id}

           Notes
              To connect to an existing configuration.
                 Windows: Nothing special to include. The session ID is always "1".
                 Linux API server: Include the api-key and sessionId that you want to connect to.
                 Windows Connection Manager: Include just the sessionId: For example: 8021.
        """
        from requests.exceptions import ConnectionError
        from requests.packages.urllib3.connection import HTTPConnection

        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()

        # Disable non http connections.
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self._session = requests.Session()

        self.serverOs = serverOs  # windows|windowsConnectionMgr|linux
        self.jsonHeader = {"content-type": "application/json"}
        self.username = username
        self.password = password
        self.apiKey = apiKey
        self.verifySslCert = verifySslCert
        self.linuxApiServerIp = apiServerIp
        self.manageSessionMode = manageSessionMode
        self.apiServerPort = serverIpPort
        self.webQuickTest = webQuickTest
        self.generateLogFile = generateLogFile
        self.robotFrameworkStdout = robotFrameworkStdout
        self.linuxChassisIp = linuxChassisIp
        self.linuxApiServerTimeout = linuxApiServerTimeout

        # Make Robot print to stdout
        if self.robotFrameworkStdout:
            from robot.libraries.BuiltIn import _Misc
            self.robotStdout = _Misc()
            Connect.robotStdout = self.robotStdout

        if generateLogFile:
            if generateLogFile == True:
                # Default the log file name
                self.restLogFile = 'ixNetRestApi_debugLog.txt'
                Connect.enableDebugLogFile = True
                Connect.debugLogFile = self.restLogFile

            if type(generateLogFile) != bool:
                self.restLogFile = generateLogFile

        if serverOs == 'linux':
            if self.apiServerPort == None:
                self.apiServerPort = 443
            self.testPlatform = TestPlatform(ip_address=self.linuxApiServerIp,
                                             rest_port=self.apiServerPort,
                                             platform='linux',
                                             verify_cert=verifySslCert)
            self.testPlatform.Authenticate(self.username, self.password)
            if apiKey != None and sessionId == None:
                raise IxNetRestApiException('Providing an apiKey must also provide a sessionId.')
            # Connect to an existing session on the Linux API server
            if apiKey and sessionId:
                self.session = self.testPlatform.Sessions.find(Id=sessionId)

            if apiKey == None and sessionId:
                self.session = self.testPlatform.Sessions.find(Id=sessionId)
            if apiKey == None and sessionId == None:
                self.session = self.testPlatform.Sessions.add()
            self.ixNetwork = self.session.Ixnetwork
            self.session_name = self.session.Name

        if licenseServerIp or licenseMode or licenseTier:
            self.configLicenseServerDetails(licenseServerIp, licenseMode, licenseTier)

        # For Linux API Server and Windoww Connection Mgr only: Delete the session when script is done if deleteSessionAfterTest = True.
        self.deleteSessionAfterTest = deleteSessionAfterTest
        #
        # match = re.match('http.*(/api.*/sessions/[0-9]+)/ixnetwork', self.sessionUrl)
        # self.headlessSessionId = match.group(1)

        if includeDebugTraceback == False:
            sys.tracebacklimit = 0

    def get(self, restApi, data={}, stream=False, silentMode=False, ignoreError=False, maxRetries=5):
        """
        Description
            A HTTP GET function to send REST APIs.

        Parameters
           restApi: (str): The REST API URL.
           data: (dict): The data payload for the URL.
           silentMode: (bool):  To display on stdout: URL, data and header info.
           ignoreError: (bool): True: Don't raise an exception.  False: The response will be returned.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.

        Syntax
            /api/v1/sessions/1/ixnetwork/operations
        """
        retryInterval = 3
        restExecutionFailures = 0
        while True:
            if silentMode is False:
                self.logInfo('\n\tGET: {0}'.format(restApi))

            try:
                # For binary file
                if stream:
                    response = self._session.request('GET', restApi, stream=True, headers=self.jsonHeader,
                                                     allow_redirects=True, verify=self.verifySslCert)

                if stream == False:
                    response = self._session.request('GET', restApi, headers=self.jsonHeader, allow_redirects=True,
                                                     verify=self.verifySslCert)

                if silentMode is False:
                    for redirectStatus in response.history:
                        if '307' in str(response.history):
                            self.logInfo('\t{0}: {1}'.format(redirectStatus, response.url), timestamp=False)

                    self.logInfo('\tSTATUS CODE: {0}'.format(response.status_code), timestamp=False)

                if not str(response.status_code).startswith('2'):
                    if ignoreError == False:
                        if 'message' in response.json() and response.json()['messsage'] != None:
                            self.logWarning('\n%s' % response.json()['message'])

                        errMsg = 'GET Exception error: {0}'.format(response.text)
                        raise IxNetRestApiException(errMsg)

                return response

            except (requests.exceptions.RequestException, Exception) as errMsg:
                errMsg = 'GET Exception error {}/{} retries: {}'.format(restExecutionFailures, maxRetries, errMsg)

                if restExecutionFailures < maxRetries:
                    self.logError(errMsg)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue

                if restExecutionFailures == maxRetries:
                    raise IxNetRestApiException(errMsg)

    def post(self, restApi, data={}, headers=None, silentMode=False, noDataJsonDumps=False, ignoreError=False,
             maxRetries=5):
        """
        Description
           A HTTP POST function to create and start operations.

        Parameters
           restApi: (str): The REST API URL.
           data: (dict): The data payload for the URL.
           headers: (str): The special header to use for the URL.
           silentMode: (bool):  To display on stdout: URL, data and header info.
           noDataJsonDumps: (bool): True: Use json dumps. False: Accept the data as-is.
           ignoreError: (bool): True: Don't raise an exception.  False: The response will be returned.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.
        """
        if headers != None:
            originalJsonHeader = self.jsonHeader
            self.jsonHeader = headers

        if noDataJsonDumps == True:
            data = data
        else:
            data = json.dumps(data)

        retryInterval = 3
        restExecutionFailures = 0
        while True:
            if silentMode == False:
                self.logInfo('\n\tPOST: {0}\n\tDATA: {1}'.format(restApi, data))

            try:
                if self.linuxChassisIp and json.loads(data) == {}:
                    # Interacting with LinuxOS chassis doesn't like empty data payload. So excluding it here.
                    response = self._session.request('POST', restApi, headers=self.jsonHeader, allow_redirects=True,
                                                     verify=self.verifySslCert)
                else:
                    response = self._session.request('POST', restApi, data=data, headers=self.jsonHeader,
                                                     allow_redirects=True,
                                                     verify=self.verifySslCert)

                # 200 or 201
                if silentMode == False:
                    for redirectStatus in response.history:
                        if '307' in str(response.history):
                            self.logInfo('\t{0}: {1}'.format(redirectStatus, response.url), timestamp=False)

                    self.logInfo('\tSTATUS CODE: %s' % response.status_code, timestamp=False)

                if str(response.status_code).startswith('2') == False:
                    if ignoreError == False:
                        if 'errors' in response.json():
                            errMsg = 'POST Exception error: {0}\n'.format(response.json()['errors'])
                            raise IxNetRestApiException(errMsg)

                        raise IxNetRestApiException('POST error: {0}\n'.format(response.text))

                # Change it back to the original json header
                if headers != None:
                    self.jsonHeader = originalJsonHeader

                return response

            except (requests.exceptions.RequestException, Exception) as errMsg:
                errMsg = 'POST Exception error {}/{} retries: {}'.format(restExecutionFailures, maxRetries, errMsg)

                if restExecutionFailures < maxRetries:
                    self.logError(errMsg)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue

                if restExecutionFailures == maxRetries:
                    raise IxNetRestApiException(errMsg)

    def patch(self, restApi, data={}, silentMode=False, ignoreError=False, maxRetries=5):
        """
        Description
           A HTTP PATCH function to modify configurations.

        Parameters
           restApi: (str): The REST API URL.
           data: (dict): The data payload for the URL.
           silentMode: (bool):  To display on stdout: URL, data and header info.
           ignoreError: (bool): True: Don't raise an exception.  False: The response will be returned.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.
        """
        retryInterval = 3
        restExecutionFailures = 0
        while True:
            if silentMode == False:
                self.logInfo('\n\tPATCH: {0}\n\tDATA: {1}'.format(restApi, data))

            try:
                response = self._session.request('PATCH', restApi, data=json.dumps(data), headers=self.jsonHeader,
                                                 allow_redirects=True,
                                                 verify=self.verifySslCert)

                if silentMode == False:
                    for redirectStatus in response.history:
                        if '307' in str(response.history):
                            self.logInfo('\t{0}: {1}'.format(redirectStatus, response.url), timestamp=False)

                    self.logInfo('\tSTATUS CODE: %s' % response.status_code, timestamp=False)

                    if ignoreError == False:
                        if not str(response.status_code).startswith('2'):
                            if response.json() and 'errors' in response.json():
                                errMsg = 'PATCH Exception error: {0}\n'.format(response.json()['errors'])
                                raise IxNetRestApiException('PATCH error: {0}\n'.format(errMsg))

                return response

            except (requests.exceptions.RequestException, Exception) as errMsg:
                errMsg = 'PATCH Exception error {}/{} retries: {}\n'.format(restExecutionFailures, maxRetries, errMsg)

                if restExecutionFailures < maxRetries:
                    self.logError(errMsg)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue

                if restExecutionFailures == maxRetries:
                    raise IxNetRestApiException(errMsg)

    def options(self, restApi, data={}, silentMode=False, ignoreError=False, maxRetries=5):
        """
        Description
            A HTTP OPTIONS function to send REST APIs.

        Parameters
           restApi: (str): The REST API URL.
           silentMode: (bool):  To display on stdout: URL, data and header info.
           ignoreError: (bool): True: Don't raise an exception.  False: The response will be returned.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failu
        """
        retryInterval = 3
        restExecutionFailures = 0
        while True:
            if silentMode is False:
                self.logInfo('\n\tOPTIONS: {0}'.format(restApi))

            try:
                # For binary file
                response = self._session.request('OPTIONS', restApi, headers=self.jsonHeader, allow_redirects=True,
                                                 verify=self.verifySslCert)

                if silentMode is False:
                    for redirectStatus in response.history:
                        if '307' in str(response.history):
                            self.logInfo('\t{0}: {1}'.format(redirectStatus, response.url), timestamp=False)

                    self.logInfo('\tSTATUS CODE: {0}'.format(response.status_code), timestamp=False)

                if not str(response.status_code).startswith('2'):
                    if ignoreError == False:
                        if 'message' in response.json() and response.json()['messsage'] != None:
                            self.logWarning('\n%s' % response.json()['message'])

                        errMsg = 'OPTIONS Exception error: {0}'.format(response.text)
                        raise IxNetRestApiException(errMsg)
                return response

            except (requests.exceptions.RequestException, Exception) as errMsg:
                errMsg = 'OPTIONS Exception error {}/{} retries: {}'.format(restExecutionFailures, maxRetries, errMsg)

                if restExecutionFailures < maxRetries:
                    self.logError(errMsg)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue

                if restExecutionFailures == maxRetries:
                    raise IxNetRestApiException(errMsg)

    def delete(self, restApi, data={}, headers=None, maxRetries=5):
        """
        Description
           A HTTP DELETE function to delete the session.
           For Linux and Windows Connection Mgr API server only.

        Paramters
           restApi: (str): The REST API URL.
           data: (dict): The data payload for the URL.
           headers: (str): The headers to use for the URL.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.
        """
        if headers != None:
            self.jsonHeader = headers

        retryInterval = 3
        restExecutionFailures = 0
        while True:
            self.logInfo('\n\tDELETE: {0}\n\tDATA: {1}'.format(restApi, data))

            try:
                response = self._session.request('DELETE', restApi, data=json.dumps(data), headers=self.jsonHeader,
                                                 allow_redirects=True,
                                                 verify=self.verifySslCert)

                for redirectStatus in response.history:
                    if '307' in str(response.history):
                        self.logInfo('\t{0}: {1}'.format(redirectStatus, response.url), timestamp=False)

                self.logInfo('\tSTATUS CODE: %s' % response.status_code, timestamp=False)
                if not str(response.status_code).startswith('2'):
                    self.showErrorMessage()
                    errMsg = 'DELETE Exception error: {0}\n'.format(response.text)
                    self.logError(errMsg)
                    raise IxNetRestApiException(errMsg)
                return response

            except (requests.exceptions.RequestException, Exception) as errMsg:
                errMsg = 'DELETE Exception error {}/{} retries: {}\n'.format(restExecutionFailures, maxRetries, errMsg)

                if restExecutionFailures < maxRetries:
                    self.logError(errMsg)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue

                if restExecutionFailures == maxRetries:
                    raise IxNetRestApiException(errMsg)

    def getDate(self):
        dateAndTime = str(datetime.datetime.now()).split(' ')
        return dateAndTime[0]

    def getTime(self):
        dateAndTime = str(datetime.datetime.now()).split(' ')
        return dateAndTime[1]

    def getSelfObject(self):
        """
        Description
           For Robot Framework support only.

        Return
           The instance object.
        """
        return self

    def createWindowsSession(self, ixNetRestServerIp, ixNetRestServerPort='11009'):
        """
        Description
           Connect to a Windows IxNetwork API Server. This is
           for both Windows and Windows server with IxNetwork Connection Manager.
           This will set up the session URL to use throughout the test.

        Parameter
          ixNetRestServerIp: (str): The Windows IxNetwork API Server IP address.
          ixNetRestServerPort: (str): Default: 11009.  Provide a port number to connect to.
                               On a Linux API Server, a socket port is not needed. State "None".
        """
        # Handle __import__(IxNetRestApi) to not error out
        if ixNetRestServerIp == None: return

        url = '{0}://{1}:{2}/api/v1/sessions'.format(self.httpScheme, ixNetRestServerIp, ixNetRestServerPort)

        if self.serverOs == 'windowsConnectionMgr':
            try:
                self.logInfo('Please wait while IxNetwork Connection Mgr starts up an IxNetwork session...')
                self.logInfo('\t{}'.format(url), timestamp=False)
                response = self._session.request('POST', url, data={}, verify=self.verifySslCert, allow_redirects=True)

            except requests.exceptions.RequestException as errMsg:
                errMsg = 'Creating new session failed: {0}'.format(errMsg)
                raise IxNetRestApiException(errMsg)

            sessionIdNumber = response.json()['links'][0]['href'].split('/')[-1]
            response = self._session.request('GET', url + '/' + str(sessionIdNumber), verify=self.verifySslCert,
                                             allow_redirects=False)

            if str(response.status_code).startswith('3'):
                # >= 8.50
                self.httpScheme = 'https'
                # https://192.168.70.3:443/api/v1/sessions/8020
                self.sessionId = response.headers['location']
                match = re.match('https://.*:([0-9]+)/api.*', self.sessionId)
                ixNetRestServerPort = match.group(1)
            else:
                # < 8.50
                self.sessionId = url + '/' + str(sessionIdNumber)

            self.sessionUrl = '{httpScheme}://{apiServer}:{port}/api/v1/sessions/{id}/ixnetwork'.format(
                httpScheme=self.httpScheme,
                apiServer=ixNetRestServerIp,
                port=ixNetRestServerPort,
                id=sessionIdNumber)

            counterStop = 10
            for counter in range(1, counterStop + 1):
                response = self.get(self.sessionId)
                if type(response.json()) == list:
                    currentState = response.json()[0]['state']
                else:
                    currentState = response.json()['state']

                self.logInfo('\n\tNew Windows session current state: {0}'.format(currentState), timestamp=False)
                if currentState != 'ACTIVE' and counter < counterStop:
                    self.logInfo('\tWaiting {0}/{1} seconds'.format(counter, counterStop), timestamp=False)
                    time.sleep(1)

                if currentState != 'ACTIVE' and counter == counterStop:
                    raise IxNetRestApiException('New Windows session state failed to become ACTVIE state')

                if currentState == 'ACTIVE' and counter < counterStop:
                    break

            # Version < 8.50 requires more waiting time. And we cannot verify the version number at this point.
            time.sleep(25)

        if self.serverOs == 'windows':
            # windows sessionId is always 1 because it only supports one session.
            self.sessionUrl = url + '/1/ixnetwork'

            try:
                self.logInfo('\nVerifying API server connection: {}'.format(self.sessionUrl))
                response = self._session.request('GET', self.sessionUrl, allow_redirects=False,
                                                 verify=self.verifySslCert)
                if '307' in str(response.status_code) and response.headers['location'].startswith('https'):
                    # Overwrite the sessionUrl with the redirected https URL
                    self.sessionUrl = response.headers['location']

            except requests.exceptions.RequestException as errMsg:
                errMsg = 'Connection failed: {0}'.format(errMsg)
                raise IxNetRestApiException(errMsg)

            # http://192.168.70.127:11009/api/v1/sessions/1
            self.sessionId = self.sessionUrl.split('/ixnetwork')[0]

        # http://192.168.70.127:11009
        self.httpHeader = self.sessionUrl.split('/api')[0]

        # /api/v1/sessions/{id}/ixnetwork
        self.apiSessionId = '/api/v1/sessions/{0}/ixnetwork'.format(str(self.sessionId))

        self.get(self.sessionUrl)

    def deleteSession(self):
        """
        Description
           Delete the instance session ID. For Linux and Windows Connection Manager only.
        """
        if self.deleteSessionAfterTest:
            self.delete(self.sessionId)

    def logInfo(self, msg, end='\n', timestamp=True):
        """
        Description
           An internal function to print info to stdout

        Parameters
           msg: (str): The message to print.
        """
        currentTime = self.getTime()

        if timestamp:
            msg = '\n' + currentTime + ': ' + msg
        else:
            # No timestamp and no newline are mainly for verifying states and status
            msg = msg

        print('{0}'.format(msg), end=end)
        if self.generateLogFile:
            with open(self.restLogFile, 'a') as restLogFile:
                restLogFile.write(msg + end)

        if self.robotFrameworkStdout:
            self.robotStdout.log_to_console(msg)

    def logWarning(self, msg, end='\n', timestamp=True):
        """
        Description
           An internal function to print warnings to stdout.

        Parameter
           msg: (str): The message to print.
        """
        currentTime = self.getTime()

        if timestamp:
            msg = '\n{0}: Warning: {1}'.format(currentTime, msg)
        else:
            # No timestamp and no newline are mainly for verifying states and status
            msg = msg

        print('{0}'.format(msg), end=end)
        if self.generateLogFile:
            with open(self.restLogFile, 'a') as restLogFile:
                restLogFile.write('Warning: ' + msg + end)

        if self.robotFrameworkStdout:
            self.robotStdout.log_to_console(msg)

    def logError(self, msg, end='\n', timestamp=True):
        """
        Description
           An internal function to print error to stdout.

        Parameter
           msg: (str): The message to print.
        """
        currentTime = self.getTime()

        if timestamp:
            msg = '\n{0}: Error: {1}'.format(currentTime, msg)
        else:
            # No timestamp and no newline are mainly for verifying states and status
            msg = '\nError: {0}'.format(msg)

        print('{0}'.format(msg), end=end)
        if self.generateLogFile:
            with open(self.restLogFile, 'a') as restLogFile:
                restLogFile.write('Error: ' + msg + end)

        if self.robotFrameworkStdout:
            self.robotStdout.log_to_console(msg)

    def getIxNetworkVersion(self):
        """
        Description
           Get the IxNetwork version.

        Syntax
            GET: /api/v1/sessions/{id}/globals
        """
        buildNumber = self.ixNetwork.Globals.BuildNumber
        return buildNumber

    def getAllSessionId(self):
        """
        Show all opened session IDs.

        Return
           A list of opened session IDs.

           {4: {'startedOn': '2018-10-06 12:09:18.333-07:00',
              'state': 'Active',
              'subState': 'Ready',
              'userName': 'admin'},
            5: {'startedOn': '2018-10-06 18:49:05.691-07:00',
              'state': 'Active',
              'subState': 'Ready',
              'userName': 'admin'}
           }
        """
        sessionId = {}
        sessions= self.testPlatform.Sessions.find()
        for session in sessions:
            sessionId.update(session.Id, {
                'state':session.State,
                'UserName':session.UserName
            })

        return sessionId

    def showErrorMessage(self, silentMode=False):
        """
        Description
           Show all the error messages from IxNetwork.

        Parameter
          silentMode: (bool): True: Don't print the REST API on stdout.

        Syntax
            GET: /api/v1/sessions/{id}/globals/appErrors/error
        """
        errorList = []
        response = self.get(self.sessionUrl + '/globals/appErrors/error', silentMode=silentMode)
        print()
        for errorId in response.json():
            if errorId['errorLevel'] == 'kError':
                print('CurrentErrorMessage: {0}'.format(errorId['name']))
                print('\tDescription: {0}'.format(errorId['lastModified']))
                errorList.append(errorId['name'])
        print()
        return errorList

    def waitForComplete(self, response='', url='', silentMode=False, ignoreException=False, httpAction='get',
                        timeout=90):
        """
        Description
           Wait for an operation progress to complete.

        Parameters
           response: (json response/dict): The POST action response.  Generally, after an /operations action.
                         Such as /operations/startallprotocols, /operations/assignports.
           silentMode: (bool):  If True, display info messages on stdout.
           ignoreException: (bool): ignoreException is for assignPorts.  Don't want to exit test.
                            Verify port connectionStatus for: License Failed and Version Mismatch to report problem immediately.

           httpAction: (get|post): Defaults to GET. For chassisMgmt, it uses POST.
           timeout: (int): The time allowed to wait for success completion in seconds.
        """
        if not silentMode:
            self.logInfo('\nwaitForComplete:', timestamp=False)
            self.logInfo("\tState: %s " % response.json()["state"], timestamp=False)

        if not response.json():
            raise IxNetRestApiException('waitForComplete: response is empty.')

        if response.json() == '' or response.json()['state'] == 'SUCCESS':
            return response

        if 'errors' in response.json():
            raise IxNetRestApiException(response.json()["errors"][0])

        if response.json()['state'] in ["ERROR", "EXCEPTION"]:
            raise IxNetRestApiException('WaitForComplete: STATE=%s: %s' % (response.json()['state'], response.text))

        for counter in range(1, timeout + 1):
            if httpAction == 'get':
                response = self.get(url, silentMode=True)
            if httpAction == 'post':
                response = self.post(url, silentMode=True)

            state = response.json()["state"]
            if not silentMode:
                if state != 'SUCCESS':
                    self.logInfo("\tState: {0}: Wait {1}/{2} seconds".format(state, counter, timeout), timestamp=False)
                if state == 'SUCCESS':
                    self.logInfo("\tState: {0}".format(state), timestamp=False)

            if counter < timeout and state in ["IN_PROGRESS", "down"]:
                time.sleep(1)
                continue

            if counter < timeout and state in ["ERROR", "EXCEPTION"]:
                # ignoreException is for assignPorts.  Don't want to exit test.
                # Verify port connectionStatus for: License Failed and Version Mismatch to report problem immediately.
                if ignoreException:
                    return response
                raise IxNetRestApiException(response.text)

            if counter < timeout and state == 'SUCCESS':
                return response

            if counter == timeout and state != 'SUCCESS':
                if ignoreException:
                    return response
                raise IxNetRestApiException('waitForComplete failed: %s' % response.json())

    def connectToLinuxIxosChassis(self, chassisIp, username, password):
        self.ixNetwork.ConnectToChassis(chassisIp)

    def connectToLinuxApiServer(self, linuxServerIp, linuxServerIpPort, username='admin', password='admin',
                                verifySslCert=False, timeout=120):
        """
        Description
           Connect to a Linux API server.

        Parameters
           linuxServerIp: (str): The Linux API server IP address.
           username: (str): Login username. Default = admin.
           password: (str): Login password. Default = admin.
           verifySslCert: (str): Default: None.  The SSL Certificate for secure access verification.
           timeout: (int): Default:120.  The timeout to wait for the Linux API server to start up.
                           Problem: In case the linux api server is installed in a chassis and the DNS is misconfigured,
                                    it takes longer to start up.

       Syntax
            POST: /api/v1/auth/session
        """
        pass

    def linuxServerGetGlobalLicense(self, linuxServerIp):
        """
        Description
           Get the global license server details from the Linux API server.

        Paramters
           linuxServerIp: (str): The IP address of the Linux API server.

        Syntax
            GET: /api/v1/sessions/9999/ixnetworkglobals/license
        """
        licenseServerIp = self.ixNetwork.globals.Licensing.LicensingServers
        licenseServerMode = self.ixNetwork.globals.Licensing.Mode
        licenseServerTier = self.ixNetwork.globals.Licensing.Tier
        return licenseServerIp, licenseServerMode, licenseServerTier

    def configLicenseServerDetails(self, licenseServer=None, licenseMode=None, licenseTier=None):
        """
        Description
           Configure license server details: license server IP, license mode and license tier.

        Parameters
           licenseServer: (str): License server IP address(s) in a list.
           licenseMode: (str): subscription | perpetual | mixed
           licenseTier: (str): tier1 | tier2 | tier3 ...

        Syntax
           PATCH: /api/v1/sessions/{id}/ixnetwork/globals/licensing
        """
        # Each new session requires configuring the new session's license details.

        if licenseServer:
            self.ixNetwork.Globals.Licensing.LicensingServers = licenseServer
        if licenseMode:
            self.ixNetwork.Globals.Licensing.Mode = licenseMode
        if licenseTier:
            self.ixNetwork.Globals.Licensing.Tier = licenseTier

        self.showLicenseDetails()

    def showLicenseDetails(self):
        """
        Description
           Display the new session's license details.

        Syntax
            GET: /api/v1/sessions/{id}/globals/licensing
        """

        self.logInfo('\nVerifying sessionId license server: %s' % self.ixNetwork, timestamp=False)
        self.logInfo('\tLicensce Servers: %s' % self.ixNetwork.Globals.Licensing.LicensingServers, timestamp=False)
        self.logInfo('\tLicensing Mode: %s' % self.ixNetwork.Globals.Licensing.Mode, timestamp=False)
        self.logInfo('\tTier Level: %s' % self.ixNetwork.Globals.Licensing.Tier, timestamp=False)

    def getAllOpenSessionIds(self):
        """
        Description
           Get a list of open session IDs and some session metas.
           
        Syntax
            GETE: /api/v1/sessions

        Return
            A dict
            
        """
        activeSessionDict = {}
        availableSessions = TestPlatform(self.linuxApiServerIp).Sessions.find()
        for session in availableSessions:
            if session.State == 'ACTIVE':
                activeSessionDict.update({session.Id: 
                                                    {'id':session.Id,
                                                      'sessionIdUrl':session.href, 
                                                      'username':session.UserName,
                                                      'state':session.State }
                                         }
                                         )

            return activeSessionDict
    def linuxServerStopAndDeleteSession(self):
        """
        Description
           Wrapper to stop and delete the session ID on the Linux API server.

        Requirements
           linuxServerStopOperations()
           linuxServerDeleteSession()

        Syntax
           GET = /api/v1/sessions/{id}
        """
        if self.serverOs == 'linux' and self.deleteSessionAfterTest == True:
            self.linuxServerStopOperations()
            self.linuxServerDeleteSession()

    def linuxServerStopOperations(self, sessionId=None):
        """
        Description
           Stop the session ID on the Linux API server.

        Parameter
           sessionId: (str): The session ID to stop.

        Requirement
           self.linuxServerWaitForSuccess()

        Syntax
            POST: /api/v1/sessions/{id}/operations/stop
        """

        if sessionId is not None:
            sessionId = sessionId
        else:
            sessionId = self.sessionId

        self.testPlatform.Sessions.find(sessionId).remove()

    def linuxServerDeleteSession(self, sessionId=None):
        """
        Description
           Delete the session ID on the Linux API server.

        Paramter
          sessionId: (str): The session ID to delete on the Linux API server.

        Syntax
            DELETE: /api/v1/sessions/{id}/operations/stop
        """
        if sessionId is not None:
            sessionId = sessionId
        else:
            sessionId = self.sessionId

        self.testPlatform.Sessions.find(Id=sessionId).remove()

    def linuxServerWaitForSuccess(self, url, timeout=120):
        """
        Description
           Wait for a success completion on the Linux API server.

        Paramters
           url: (str): The URL's ID of the operation to verify.
           timeout: (int): The timeout value.
        """
        availableSessions = TestPlatform(self.linuxApiServerIp).Sessions.find()
        for session in availableSessions:
            if session.href == url:
                break

        for counter in range(1, timeout + 1):
            currentStatus = session.State
            self.logInfo('\tCurrentStatus: {0}:  {1}/{2} seconds'.format(currentStatus, counter, timeout),
                         timestamp=False)
            if counter < timeout + 1 and currentStatus != 'Operation successfully completed':
                time.sleep(1)

            if counter == timeout + 1 and currentStatus != 'Operation successfully completed':
                return 1

            if counter < timeout + 1 and currentStatus == 'Operation successfully completed':
                return 0


    def newBlankConfig(self):
        """
        Description
           Start a new blank configuration.

        Requirement
            self.waitForComplete()

        Syntax:
           /api/v1/sessions/{1}/ixnetwork/operations/newconfig
        """
        self.ixNetwork.NewConfig()

    def refreshHardware(self, chassisObj):
        """
        Description
           Refresh the chassis

        Parameter
           chassisObj: (str):The chassis object.
                           Ex: /api/v1/sessions/{1}/ixnetwork/availableHardware/chassis/1

        Requirement
           self.waitForComplete()

        Syntax
            /api/v1/sessions/{1}/ixnetwork/availableHardware/chassis/operations/refreshinfo
        """
        self.ixNetwork.AvailableHardware.Chassis.RefreshInfo()

    def query(self, data, silentMode=False):
        """
        Description
           Query for objects using filters.

        Paramater
           silentMode: (bool): True: Don't display any output on stdout.

        Notes
            Assuming this is a BGP configuration, which has two Topologies.
            Below demonstrates how to query the BGP host object by
            drilling down the Topology by its name and the specific the BGP attributes to modify at the
            BGPIpv4Peer node: flap, downtimeInSec, uptimeInSec.
            The from '/' is the entry point to the API tree.
            Notice all the node. This represents the API tree from the / entry point and starting at
            Topology level to the BGP host level.

        Notes
           Use the API Browser tool on the IxNetwork GUI to view the API tree.
            data: {'from': '/',
                    'nodes': [{'node': 'topology',    'properties': ['name'], 'where': [{'property': 'name', 'regex': 'Topo1'}]},
                              {'node': 'deviceGroup', 'properties': [], 'where': []},
                              {'node': 'ethernet',    'properties': [], 'where': []},
                              {'node': 'ipv4',        'properties': [], 'where': []},
                              {'node': 'bgpIpv4Peer', 'properties': ['flap', 'downtimeInSec', 'uptimeInSec'], 'where': []}]
                }

        Requirements
            self.waitForComplete()

        Examples
            response = restObj.query(data=queryData)
            bgpHostAttributes = response.json()['result'][0]['topology'][0]['deviceGroup'][0]['ethernet'][0]['ipv4'][0]['bgpIpv4Peer'][0]

            # GET THE BGP ATTRIBUTES TO MODIFY
            bgpHostFlapMultivalue = bgpHostAttributes['flap']
            bgpHostFlapUpTimeMultivalue = bgpHostAttributes['uptimeInSec']
            bgpHostFlapDownTimeMultivalue = bgpHostAttributes['downtimeInSec']

            restObj.configMultivalue(bgpHostFlapMultivalue, multivalueType='valueList', data={'values': ['true', 'true']})
            restObj.configMultivalue(bgpHostFlapUpTimeMultivalue, multivalueType='singleValue', data={'value': '60'})
            restObj.configMultivalue(bgpHostFlapDownTimeMultivalue, multivalueType='singleValue', data={'value': '30'})
        """
        pass

    def select(self, data):
        """
        Description
           Using the Select operation to query for objects using filters.
        """
        response = self.ixNetwork.Select(data)
        return response

    def configMultivalue(self, multivalueUrl, multivalueType, data):
        """
        Description
           Configure multivalues.

        Parameters
           multivalueUrl: (str): The multivalue: /api/v1/sessions/{1}/ixnetwork/multivalue/1
           multivalueType: (str): counter|singleValue|valueList
           data: (dict): singleValue: data={'value': '1.1.1.1'})
                             valueList:   data needs to be in a [list]:  data={'values': [list]}
                             counter:     data={'start': value, 'direction': increment|decrement, 'step': value}
        """
        if multivalueType.lower() == "counter":
            if data['direction'] == "increment":
                multivalueUrl.Increment(start_value=data['start'], step_value=data['step'])
            if data['direction'] == "decrement":
                multivalueUrl.Decrement(start_value=data['start'], step_value=data['step'])
        elif multivalueType.lower() == "singlevalue":
            multivalueUrl.Single(data['value'])
        elif multivalueType.lower() == "valuelist":
            multivalueUrl.ValueList(data['values'])
        elif multivalueType.lower() == "randomrange":
            multivalueUrl.RandomRange(min_value=data['min_value'], max_value=data['max_value'],
                                      step_value=data['step_value'], seed=data['seed'])
        elif multivalueType.lower() == "custom":
            multivalueUrl.Custom(start_value=data['start_value'], step_value=data['step_value'],
                                 increments=data['increments'])
        elif multivalueType.lower() == "alternate":
            multivalueUrl.Alternate(data['alternating_value'])
        elif multivalueType.lower() == "distributed":
            multivalueUrl.Distributed(algorithm=data['algorithm'], mode=data['mode'], values=data['values'])
        elif multivalueType.lower() == "randommask":
            multivalueUrl.RandomMask(fixed_value=data['fixed_value'], mask_value=data['mask_value'], seed=data['seed'],
                                     count=data['count'])
        elif multivalueType.lower() == "string":
            multivalueUrl.String(string_pattern=data['string_pattern'])

    def getMultivalueValues(self, multivalueObj, silentMode=False):
        """
        Description
           Get the multivalue values.

        Parameters
           multivalueObj: <str>: The multivalue object: /api/v1/sessions/{1}/ixnetwork/multivalue/{id}
           silentMode: <bool>: True=Display the GET and status code. False=Don't display.

        Syntax
            /api/v1/sessions/{id}/ixnetwork/multivalue/{id}?includes=count

        Requirements
           self.ixnObj.waitForComplete()

        Return
           The multivalue values
        """
        return multivalueObj.Values

    def getObjAttributeValue(self, obj, attribute):
        """
        Description
           Based on the object handle, get any property attribute and return the value.

        Parameter
           obj: <str:obj>: An object handle:
                For example: If you want the ethernet MTU, then pass in the ethernet object handle:
                            /api/v1/sessions/{id}/ixnetwork/topology/{id}/deviceGroup/{id}/ethernet/{id}
                            and set attribute='mtu'

        Note:
           Where to get the object's attribute names:
              - Use the API browser and go to your object.
              - All the attributes are listed on the right pane.
        """
        response = self.get(self.httpHeader + obj)

        # value: Could be /api/v1/sessions/{id}/ixnetwork/multivalue/{id} or the actual value
        value = response.json()[attribute]
        if type(value) == str and 'multivalue' in value:
            multivalueObj = value
            value = self.getMultivalueValues(multivalueObj)
            return value
        else:
            return value

    def stdoutRedirect(self):
        """
        Description
           For Robot Framework.  Robot captures the stdout. This stdoutRedirect
           will redirect the output back to stdout so you could see the test progress
           and to troubleshoot.
        """
        for attr in ('stdin', 'stdout', 'stderr'):
            setattr(sys, attr, getattr(sys, '__%s__' % attr))

    @staticmethod
    def prettyprintAllOperations(sessionUrl):
        """
        Description
           A staticmethod to rendering a nice output of an operations options and descriptions.

        Parameter
           sessionUrl: (str): http://{apiServerIp}:{port}/api/v1/sessions/1/ixnetwork

        Syntax:
            /api/v1/sessions/{1}/ixnetwork/operations
        """
        response = self._session.request('GET', sessionUrl + '/operations')
        for item in response.json():
            if 'operation' in item.keys():
                print('\n', item['operation'])
                print('\t%s' % item['description'])
                if 'args' in item.keys():
                    for nestedKey, nestedValue in item['args'][0].items():
                        print('\t\t%s: %s' % (nestedKey, nestedValue))

    @staticmethod
    def printDict(obj, nested_level=0, output=sys.stdout):
        """
        Description
           Print each dict key with indentions for human readability.
        """
        spacing = '   '
        spacing2 = ' '
        if type(obj) == dict:
            print('%s' % (nested_level * spacing), file=output)
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    print('%s%s:' % ((nested_level + 1) * spacing, k), file=output, end='')
                    IxNetRestMain.printDict(v, nested_level + 1, output)
                else:
                    print('%s%s: %s' % ((nested_level + 1) * spacing, k, v), file=output)

            print('%s' % (nested_level * spacing), file=output)
        elif type(obj) == list:
            print('%s[' % (nested_level * spacing), file=output)
            for v in obj:
                if hasattr(v, '__iter__'):
                    IxNetRestMain.printDict(v, nested_level + 1, file=output)
                else:
                    print('%s%s' % ((nested_level + 1) * spacing, v), file=output)
            print('%s]' % (nested_level * spacing), output)
        else:
            print('%s%s' % ((nested_level * spacing2), obj), file=output)

    def placeholder(self):
        pass
