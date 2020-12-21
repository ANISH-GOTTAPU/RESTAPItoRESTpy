import re, time , datetime , csv
from IxNetRestApi import IxNetRestApiException
from IxNetRestApiFileMgmt import FileMgmt
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant
from ixnetwork_restpy.files import Files


class Statistics(object):
    def __init__(self, ixnObj=None):
        self.ixnObj = ixnObj

        # For takesnapshot()
        self.fileMgmtObj = FileMgmt(self.ixnObj)
        self.ixNetObj = ixnObj.ixNetwork

    def setMainObject(self, mainObject):
        """
        Description
            For Python Robot Framework support.
        """
        self.ixnObj = mainObject

    def getStats(self, viewObject=None, viewName='Flow Statistics', csvFile=None, csvEnableFileTimestamp=False,
                 displayStats=True, silentMode=True, ignoreError=False):
        """
        Description
           Get stats for any viewName.
           The method calls two different methods based on the IxNetwork version that you are using.
           For IxNetwork version prior to 8.50, calls getStatsPage.
           For IxNetwork version >= 8.50, calls getStatsData. This has new APIs that is more robust and they don't
           work in versions prior to 8.50.

        Parameters
            csvFile = None or <filename.csv>.
                      None will not create a CSV file.
                      Provide a <filename>.csv to record all stats to a CSV file.
                      Example: getStats(sessionUrl, csvFile='Flow_Statistics.csv')

            csvEnableFileTimestamp = True or False. If True, timestamp will be appended to the filename.
            displayStats: True or False. True=Display stats.
            ignoreError: True or False.  Returns None if viewName is not found.
            viewObject: The view object: http://{apiServerIp:port}/api/v1/sessions/2/ixnetwork/statistics/view/13
                        A view object handle could be obtained by calling getViewObject().

            viewName options (Not case sensitive):
               NOTE: Not all statistics are listed here.
                  You could get the statistic viewName directly from the IxNetwork GUI in the statistics.
        """

        return self.getStatsData(viewObject=viewObject, viewName=viewName, csvFile=csvFile, csvEnableFileTimestamp=csvEnableFileTimestamp,
                                     displayStats=displayStats, silentMode=silentMode, ignoreError=ignoreError)

            
    def getStatsPage(self, viewObject=None, viewName='Flow Statistics', csvFile=None, csvEnableFileTimestamp=False,
                     displayStats=True, silentMode=True, ignoreError=False):
        """
        Description
            Get stats by the statistic name or get stats by providing a view object handle.
            This method uses deprecated APIs effective IxNetwork version 8.50: /statistics/statView/<id>/page
            Starting 8.50, the new API to use is: /statistics/statView/<id>/data, which is in getStatsData()

        Parameters
            csvFile = None or <filename.csv>.
                      None will not create a CSV file.
                      Provide a <filename>.csv to record all stats to a CSV file.
                      Example: getStats(sessionUrl, csvFile='Flow_Statistics.csv')

            csvEnableFileTimestamp = True or False. If True, timestamp will be appended to the filename.

            displayStats: True or False. True=Display stats.

            ignoreError: True or False.  Returns None if viewName is not found.

            viewObject: The view object: http://{apiServerIp:port}/api/v1/sessions/2/ixnetwork/statistics/view/13
                        A view object handle could be obtained by calling getViewObject().

            viewName options (Not case sensitive):
               NOTE: Not all statistics are listed here.
                  You could get the statistic viewName directly from the IxNetwork GUI in the statistics.

            'Port Statistics'
            'Tx-Rx Frame Rate Statistics'
            'Port CPU Statistics'
            'Global Protocol Statistics'
            'Protocols Summary'
            'Port Summary'
            'BGP Peer Per Port'
            'OSPFv2-RTR Drill Down'
            'OSPFv2-RTR Per Port'
            'IPv4 Drill Down'
            'L2-L3 Test Summary Statistics'
            'Flow Statistics'
            'Traffic Item Statistics'
            'IGMP Host Drill Down'
            'IGMP Host Per Port'
            'IPv6 Drill Down'
            'MLD Host Drill Down'
            'MLD Host Per Port'
            'PIMv6 IF Drill Down'
            'PIMv6 IF Per Port'
            'Flow View'

         Note: Not all of the viewNames are listed here. You have to get the exact names from
               the IxNetwork GUI in statistics based on your protocol(s).

         Return a dictionary of all the stats: statDict[rowNumber][columnName] == statValue
           Get stats on row 2 for 'Tx Frames' = statDict[2]['Tx Frames']
        """
        try:
            TrafficItemStats = StatViewAssistant(self.ixNetObj, viewName)
        except:
            raise Exception('getStats: Failed to get stats values')

        trafficItemStatsDict = {}
        columnCaptions = TrafficItemStats.ColumnHeaders

        if csvFile != None:
            csvFileName = csvFile.replace(' ', '_')
            if csvEnableFileTimestamp:
                import datetime
                timestamp = datetime.datetime.now().strftime('%H%M%S')
                if '.' in csvFileName:
                    csvFileNameTemp = csvFileName.split('.')[0]
                    csvFileNameExtension = csvFileName.split('.')[1]
                    csvFileName = csvFileNameTemp + '_' + timestamp + '.' + csvFileNameExtension
                else:
                    csvFileName = csvFileName + '_' + timestamp

            csvFile = open(csvFileName, 'w')
            csvWriteObj = csv.writer(csvFile)
            csvWriteObj.writerow(columnCaptions)
            for rowNumber, stat in enumerate(TrafficItemStats.Rows):
                rowStats = stat.RawData
            for row in rowStats:
                csvWriteObj.writerow(row)
            csvFile.close()

        for rowNumber, stat in enumerate(TrafficItemStats.Rows):
            if displayStats:
                self.ixnObj.logInfo('\nRow: {}'.format(rowNumber+1),timestamp=False)
            statsDict = {}
            for column in columnCaptions:
                statsDict[column] = stat[column]
                if displayStats:
                    self.ixnObj.logInfo('\t%s: %s' % (column, stat[column]), timestamp=False)
            trafficItemStatsDict[rowNumber + 1] = statsDict

        return trafficItemStatsDict

    def getStatsData(self, viewObject=None, viewName='Flow Statistics', csvFile=None, csvEnableFileTimestamp=False,
                     displayStats=True, silentMode=False, ignoreError=False):
        """
        Description
            For IxNetwork version >= 8.50.   
            Get stats by the statistic name or get stats by providing a view object handle.
            This method get stats using /api/v1/sessions/{id}/ixnetwork/statistics/view/{id}/data to get
            attributes columnCaptions, pageValues and totalPages. This method uses new API starting in 
            version 8.50.

        Parameters
            csvFile = None or <filename.csv>.
                      None will not create a CSV file.
                      Provide a <filename>.csv to record all stats to a CSV file.
                      Example: getStats(sessionUrl, csvFile='Flow_Statistics.csv')

            csvEnableFileTimestamp = True or False. If True, timestamp will be appended to the filename.
            displayStats: True or False. True=Display stats.
            ignoreError: True or False.  Returns None if viewName is not found.
            viewObject: The view object: http://{apiServerIp:port}/api/v1/sessions/2/ixnetwork/statistics/view/13
                        A view object handle could be obtained by calling getViewObject().

            viewName options (Not case sensitive):
               NOTE: Not all statistics are listed here.
                  You could get the statistic viewName directly from the IxNetwork GUI in the statistics.

            'Port Statistics'
            'Tx-Rx Frame Rate Statistics'
            'Port CPU Statistics'
            'Global Protocol Statistics'
            'Protocols Summary'
            'Port Summary'
            'BGP Peer Per Port'
            'OSPFv2-RTR Drill Down'
            'OSPFv2-RTR Per Port'
            'IPv4 Drill Down'
            'L2-L3 Test Summary Statistics'
            'Flow Statistics'
            'Traffic Item Statistics'
            'IGMP Host Drill Down'
            'IGMP Host Per Port'
            'IPv6 Drill Down'
            'MLD Host Drill Down'
            'MLD Host Per Port'
            'PIMv6 IF Drill Down'
            'PIMv6 IF Per Port'
            'Flow View'

         Note: Not all of the viewNames are listed here. You have to get the exact names from
               the IxNetwork GUI in statistics based on your protocol(s).

         Return a dictionary of all the stats: statDict[rowNumber][columnName] == statValue
           Get stats on row 2 for 'Tx Frames' = statDict[2]['Tx Frames']
        #Ignore vieobject,silentMode in Restpy as it is taken care by StatViewAssistant internally
        viewObject = None
        silentMode = False

        """

        try:
            TrafficItemStats = StatViewAssistant(self.ixNetObj, viewName)
        except:
            raise Exception('getStats: Failed to get stats values')

        trafficItemStatsDict = {}
        columnCaptions = TrafficItemStats.ColumnHeaders

        if csvFile != None:
            csvFileName = csvFile.replace(' ', '_')
            if csvEnableFileTimestamp:
                import datetime
                timestamp = datetime.datetime.now().strftime('%H%M%S')
                if '.' in csvFileName:
                    csvFileNameTemp = csvFileName.split('.')[0]
                    csvFileNameExtension = csvFileName.split('.')[1]
                    csvFileName = csvFileNameTemp + '_' + timestamp + '.' + csvFileNameExtension
                else:
                    csvFileName = csvFileName + '_' + timestamp

            csvFile = open(csvFileName, 'w')
            csvWriteObj = csv.writer(csvFile)
            csvWriteObj.writerow(columnCaptions)
            for rowNumber, stat in enumerate(TrafficItemStats.Rows):
                rowStats = stat.RawData
            for row in rowStats:
                csvWriteObj.writerow(row)
            csvFile.close()

        for rowNumber, stat in enumerate(TrafficItemStats.Rows):
            if displayStats:
                self.ixnObj.logInfo('\nRow: {}'.format(rowNumber+1),timestamp=False)
            statsDict = {}
            for column in columnCaptions:
                statsDict[column] = stat[column]
                if displayStats:
                    self.ixnObj.logInfo('\t%s: %s' % (column, stat[column]), timestamp=False)
            trafficItemStatsDict[rowNumber + 1] = statsDict

        return trafficItemStatsDict

    def removeAllTclViews(self):
        """
        Description
           Removes all created stat views.
        """
        self.ixnObj.logInfo("Remove all tcl views")
        self.ixNetObj.RemoveAllTclViews()

    def takeSnapshot(self, viewName='Flow Statistics', windowsPath=None, isLinux=False, localLinuxPath=None,
                     renameDestinationFile=None, includeTimestamp=False, mode='overwrite'):
        """
        Description
            Take a snapshot of the vieweName statistics.  This is a two step process.
            1> Take a snapshot of the statistics that you want and store it in the C: drive for Windows.
               For Linux, the snapshot goes to /home/ixia_logs.
            2> Copy the statistics from the snapshot locations to the local Linux where you ran the script..

        Parameters
            viewName: The name of the statistics to get.
            windowsPath: For Windows|WindowsConnectionMgr only.
                         The C: drive + path to store the snapshot: Example: c:\\Results.
            isLinux: <bool>: Defaults to False.  Set to True if you're getting the snapshot from Linux chassis.
            localLinuxPath: None|path. Provide the local Linux path to put the snapshot file.
                            If None, this API won't copy the stat file to local Linux.
                            The stat file will remain on Windows c: drive.
            renameDestinationFile: None or a name of the file other than the viewName.
            includeTimestamp: True|False: To include a timestamp at the end of the file.
            mode: append|overwrite: append=To append stats to an existing stat file.
                                    overwrite=Don't append stats. Create a new stat file.

        Example:
            For Windows:
               statObj.takeSnapshot(viewName='Flow Statistics', windowsPath='C:\\Results', localLinuxPath='/home/hgee',
                           renameDestinationFile='my_renamed_stat_file.csv', includeTimestamp=True)

            For Linux:
               statObj.takeSnapshot(viewName='Flow Statistics', isLinux=True, localLinuxPath='/home/hgee')
        """
        if mode == 'append':
            mode = 'kAppendCSVFile'

        if mode == 'overwrite':
            mode = 'kOverwriteCSVFile'

        if windowsPath:
            location = windowsPath

        if isLinux:
            location = '/home/ixia_logs'
        import pdb
        pdb.set_trace()
        self.ixNetObj.TakeViewCSVSnapshot(Arg1=[viewName],Arg2 = [
                            "Snapshot.View.Contents: \"allPages\"",
                            "Snapshot.View.Csv.Location: \"{0}\"".format(location),
                            "Snapshot.View.Csv.GeneratingMode: \"%s\"" % mode,
                            "Snapshot.View.Csv.StringQuotes: \"True\"",
                            "Snapshot.View.Csv.SupportsCSVSorting: \"False\"",
                            "Snapshot.View.Csv.FormatTimestamp: \"True\"",
                            "Snapshot.View.Csv.DumpTxPortLabelMap: \"False\"",
                            "Snapshot.View.Csv.DecimalPrecision: \"3\""
                            ])

        if isLinux:
            snapshotFile = location + '/' + viewName + '.csv'
            self.fileMgmtObj.copyFileLinuxToLocalLinux(linuxApiServerPathAndFileName=snapshotFile, localPath=localLinuxPath,
                                                        renameDestinationFile=renameDestinationFile,
                                                        includeTimestamp=includeTimestamp)

        if windowsPath and localLinuxPath:
            # Get the snapshot. Use the csvFilename that was specified and the location
            self.fileMgmtObj.copyFileWindowsToLocalLinux('{0}\\{1}.csv'.format(windowsPath, viewName), localLinuxPath,
                                                         renameDestinationFile=renameDestinationFile,
                                                         includeTimestamp=includeTimestamp)
        try:
            self.ixNetObj.CopyFile(Files(location + "\\" + viewName + ".csv"), localLinuxPath+"/" + viewName + ".csv")
        except:
            self.ixNetObj.CopyFile(Files(location + "/" + viewName + ".csv"), localLinuxPath+"/" + viewName + ".csv")

    def getViewObject(self, viewName='Flow Statistics'):
        """
        Not Rquired in Restpy
        """
        pass

    def clearStats(self):
        """
        Description
            Clear all stats and wait for API server to finish.
        """
        self.ixnObj.logInfo("Clearing all statistics")
        self.ixNetObj.ClearStats(Arg1= ['waitForPortStatsRefresh'])
