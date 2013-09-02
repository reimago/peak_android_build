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

import xmlUtil
import fileUtil
import csvUtil
import optparse
import sys
import csv
import codecs
import os

CHARSET = "UTF-8"
CONFIG_FLAG_BASELINE = "baseline = "
CONFIG_FLAG_DST_LANG = "to_language = "
CONFIG_FLAG_SEARCH_PATH = "search_path = "
CONFIG_FLAG_OUTPUT = "output_filename = "
CONFIG_FLAG_BACKUP = "backup_filename = "
SYMBOL_LINE_BREAK = "\n"
SYMBOL_COMMA = ","
DEFAULT_BASELINE_LANG = "en"
DEFAULT_OUTPUT_FILENAME = "output.csv"
DEFAULT_BACK_FILENAME = "backup.zip"
COLUMN_NAME_PATH = "Path"
COLUMN_NAME_ID = "ID"
COLUMN_NAME_2ND_ID = '2nd ID'

def isNotEmpty(s):
    return len(s) > 0

#parse config file
def parseConfigFile(configFileName, pathList, dstLangList, baselineLang, outputFileName, bakFileName):
    try:
        configFile = open(configFileName, 'r')
    except IOError:
        print "Config file: '" + configFileName + "' doesn't exist or can't be opened."
        return False
    lines = configFile.readlines()
    configFile.close()
    for line in lines:
        line = line.strip(SYMBOL_LINE_BREAK)
        if line.startswith(CONFIG_FLAG_BASELINE):
            lang = line[len(CONFIG_FLAG_BASELINE)-len(line):]
            baselineLang.append(lang)
        elif line.startswith(CONFIG_FLAG_SEARCH_PATH):
            searchPathListString = line[len(CONFIG_FLAG_SEARCH_PATH)-len(line):]
            pathList += filter(isNotEmpty, searchPathListString.split(SYMBOL_COMMA))
        elif line.startswith(CONFIG_FLAG_DST_LANG):
            dstLangListString = line[len(CONFIG_FLAG_DST_LANG)-len(line):]
            dstLangList += filter(isNotEmpty, dstLangListString.split(SYMBOL_COMMA))
        elif line.startswith(CONFIG_FLAG_OUTPUT):
            outputFileName.append(line[len(CONFIG_FLAG_OUTPUT)-len(line):])
        elif line.startswith(CONFIG_FLAG_BACKUP):
            bakFileName.append(line[len(CONFIG_FLAG_BACKUP)-len(line):])
    #validation
    if len(pathList) == 0:
        print "Config item 'search_path' not set."
        return False
    if len(dstLangList) == 0:
        print "Config item 'to_language' not set."
    if len(baselineLang) > 0 and baselineLang[0] in dstLangList:
        print "In config item 'baseline', language code '" + baselineLang[0] + "' shouldn't exist in 'to_language' list."
        return False
    return True

def backupFileList(bakFileList, bakFileName):
    if len(bakFileList) > 0:
        os.system('rm ' + bakFileName)
        cmd = 'zip ' + bakFileName
        for fileName in bakFileList:
            temp = ' ' + fileName
            cmd += temp
        os.system(cmd)

#main process
def process(baselineLang, dstLangList, pathList, outputFileName, bakFileName):
    bakFileList = []
    try:
        outFile = open(outputFileName, 'wb')
    except IOError, (errno, strerror):
        print "IOError: " + strerror
        print "Output file: '" + outputFileName + "' invalid"
        return
    #tell excel UTF-8 is used
    outFile.write(codecs.BOM_UTF8)
    writer = csv.writer(outFile)
    csvUtil.writeFirstRow(baselineLang, dstLangList, writer)
    for path in pathList:
        baselineFileNameList = []
        fileUtil.getBaselineXMLFileNameListFromSearchPath(baselineLang, path, baselineFileNameList)
        for filename in baselineFileNameList:
            print "Processing: " + filename
            (contentsMap, keyList) = xmlUtil.generateBaseLineContentsMapFromXMLFile(filename, len(dstLangList))
            for i in range(0, len(dstLangList)):
                dstLang = dstLangList[i]
                (flag, fileNameDst) = fileUtil.getDstXMLFileNameFromBaselineXMLFileName(filename, dstLang)
                if flag:#means that the dst language strings.xml exists
                    result = xmlUtil.generateDstContentsIntoContentsMapFromXMLFile(contentsMap, fileNameDst, i+1)
                    if result:
                        bakFileList.append(fileNameDst)
            csvUtil.writeCsvContentRows(keyList, contentsMap, writer, filename, dstLangList)
    print "CSV file " + outputFileName + " is generated."
    backupFileList(bakFileList, bakFileName)
    print "Backup file " + bakFileName + " is generated."

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding(CHARSET)
    parser = optparse.OptionParser(
        usage = "python generateCSV.py <config file>\n"
                + "config file format:\n"
                + "\tto_language = [to languge list, splitted by comma]\n"
                + "\tsearch_path = [search path, splittd by comma]\n"
                + "\toutput_filename = [output csv filename, default: output.csv]\n"
                + "\tbackup_filename = [backup zip filename, default: backup.zip]",
        description = "Get all the related strings and generate csv file."
    )
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print parser.usage
        sys.exit(-1)
    configFileName = args[0]
    pathList = []
    dstLangList = []
    baselineLang = []
    outputFileName = []
    bakFileName = []
    if parseConfigFile(configFileName, pathList,dstLangList, baselineLang, outputFileName, bakFileName):
        # 'en' as default baseline
        if len(baselineLang) == 0:
            baselineLang = DEFAULT_BASELINE_LANG
        else:
            baselineLang = baselineLang[0]
        if len(outputFileName) == 0:
            outputFileName = DEFAULT_OUTPUT_FILENAME
        else:
            outputFileName = outputFileName[0]
        if len(bakFileName) == 0:
            bakFileName = DEFAULT_BACK_FILENAME
        else:
            bakFileName = bakFileName[0]
        process(baselineLang, dstLangList, pathList, outputFileName, bakFileName)
