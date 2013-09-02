#
# Copyright (C) 2012, Code Aurora Forum. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     # Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     # Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     # Neither the name of Code Aurora Forum, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import csv

COL_PATH_INDEX = 0
COL_ID_INDEX = 1
COL_2ND_ID_INDEX = 2
BASELINE_VALUE_INDEX = 3

COLUMN_NAME_PATH = "Path"
COLUMN_NAME_ID = "ID"
COLUMN_NAME_2ND_ID = '2nd ID'
LEAST_INDEX_COUNT = 5

#write one row
def writeCsvContentRow(key, contentsMap, writer, baselineFileName, dstLangList):
    row = []
    row.append(baselineFileName)
    row.append(key[0])
    row.append(key[1])
    row.append(contentsMap[key][0].encode())
    for i in range(0, len(dstLangList)):
        row.append(contentsMap[key][i+1].encode())
    writer.writerow(row)

#write rows according to the keyList
def writeCsvContentRows(keyList, contentsMap, writer, baselineFileName, dstLangList):
    for key in keyList:
        writeCsvContentRow(key, contentsMap, writer, baselineFileName, dstLangList)

#split csv rows and generate contents map list,for each map item format: (id, 2nd id)->[baselineValue, dstValue1, dstValue2, ...]
def generateContentsMapListFromCSVFile(csvFileName):
    contentsMapList = []
    pathList = []
    dstLangList = []

    #since sequence of the keys in contentsMap may be disordered, this is recorded for keeping the order of keys
    keyLists = []
    baselineLang = ''
    try:
        csvFile = open(csvFileName, 'rb')
        reader = csv.reader(csvFile)
    except IOError, (errno, strerror):
        print "IOError: " + strerror
        print "CSV file: '" + csvFileName + "' invalid"
        return([], [], [], [], '')
    dstLangCount = 0
    #first time empty string
    curPath = ''
    curContentsMap = {}
    curKeyList = []
    for row in reader:
        if len(row) < LEAST_INDEX_COUNT:
            print "Invalid column count in csv file: line " + str(row.line_num)
            return ([], [], [], [], '')
        if reader.line_num == 1:
            baselineLang = row[BASELINE_VALUE_INDEX]
            dstLangCount = len(row) - BASELINE_VALUE_INDEX - 1
            #validate if the column name is valid
            for i in range(BASELINE_VALUE_INDEX+1, len(row)):
                dstLangList.append(row[i])
        else:
            thisDstLangCount = len(row) - BASELINE_VALUE_INDEX - 1
            if thisDstLangCount != dstLangCount:
                print "Invalid column count in csv file: line " + str(row.line_num)
                return ([], [], [], [], '')
            thisPath = row[COL_PATH_INDEX]
            if thisPath != curPath:
                if len(curContentsMap.keys()) != 0:#a group of strings.xml
                    contentsMapList.append(curContentsMap)
                    keyLists.append(curKeyList)
                    pathList.append(curPath)
                curPath = thisPath
                curContentsMap = {}
                curKeyList = []
            key = (row[COL_ID_INDEX], row[COL_2ND_ID_INDEX])
            curContentsMap[key] = [''] * (dstLangCount+1)
            curContentsMap[key][0] = row[BASELINE_VALUE_INDEX]
            for i in range(BASELINE_VALUE_INDEX+1, len(row)):
                curContentsMap[key][i-BASELINE_VALUE_INDEX] = row[i]
            curKeyList.append(key)
    if len(curContentsMap) != 0:
        contentsMapList.append(curContentsMap)
        pathList.append(curPath)
        keyLists.append(curKeyList)
    return (contentsMapList, keyLists, pathList, dstLangList, baselineLang)

#write the 1st row
def writeFirstRow(baselineLang, dstLangList, writer):
    firstRow = []
    firstRow.append(COLUMN_NAME_PATH)
    firstRow.append(COLUMN_NAME_ID)
    firstRow.append(COLUMN_NAME_2ND_ID)
    firstRow.append(baselineLang)
    for dstLang in dstLangList:
        firstRow.append(dstLang)
    writer.writerow(firstRow)
