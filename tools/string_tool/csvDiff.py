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

import sys
import csv
import csvUtil
import optparse

CHARSET = "UTF-8"
CONFIG_FLAG_CSVFILE_1 = "csvfile_1 = "
CONFIG_FLAG_CSVFILE_2 = "csvfile_2 = "
CONFIG_FLAG_OUTPUT_CSV_DIFF = "output_csv_diff = "
BASELINE_VALUE_INDEX = 0
SYMBOL_LINE_BREAK = "\n"

DEFAULT_OUTPUT_CSV_DIFF = "output.csv.diff"


def parseConfigFile(configFileName, csvFileName1, csvFileName2, outputFileName):
    try:
        configFile = open(configFileName, 'rb')
    except IOError, (errno, strerror):
        print "IOError: " + strerror
        print "Config file: '" + configFileName + "' invalid."
        return False
    lines = configFile.readlines()
    configFile.close()
    for line in lines:
        line = line.strip(SYMBOL_LINE_BREAK)
        if line.startswith(CONFIG_FLAG_CSVFILE_1):
            csvFileName1.append(line[len(CONFIG_FLAG_CSVFILE_1)-len(line):])
        elif line.startswith(CONFIG_FLAG_CSVFILE_2):
            csvFileName2.append(line[len(CONFIG_FLAG_CSVFILE_2)-len(line):])
        elif line.startswith(CONFIG_FLAG_OUTPUT_CSV_DIFF):
            outputFileName.append(line[len(CONFIG_FLAG_OUTPUT_CSV_DIFF)-len(line):])
    if len(csvFileName1) == 0:
        print "Config item 'csvfile_1' not set."
        return False
    if len(csvFileName2) == 0:
        print "Config item 'csvfile_2' not set."
        return False
    return True

def process(csvFileName1, csvFileName2, outputFileName):
    (contentsMapList1, keyLists1, pathList1, dstLangList1, baselineLang1) = csvUtil.generateContentsMapListFromCSVFile(csvFileName1)
    (contentsMapList2, keyLists2, pathList2, dstLangList2, baselineLang2) = csvUtil.generateContentsMapListFromCSVFile(csvFileName2)
    if len(pathList1) == 0 or len(pathList2) == 0:
        return
    if baselineLang1 != baselineLang2:
        print "Baseline language of csv1 isn't equal to that of csv2."
        return
    try:
        outputFile = open(outputFileName, 'wb')
    except IOError, (errno, strerror):
        print "IOError: " + strerror
        print "OutputFile: '" + outputFileName + "' invalid"
        return
    writer = csv.writer(outputFile)
    csvUtil.writeFirstRow(baselineLang2, dstLangList2, writer)
    for i in range(0, len(pathList2)):
        baselineFileName2 = pathList2[i]
        contentsMap2 = contentsMapList2[i]
        if baselineFileName2 in pathList1:
            index = pathList1.index(baselineFileName2)
            contentsMap1 = contentsMapList1[index]
            keyList2 = keyLists2[i]
            for key in keyList2:
                if not contentsMap1.has_key(key) or contentsMap2[key][BASELINE_VALUE_INDEX].encode() != contentsMap1[key][BASELINE_VALUE_INDEX].encode():
                    csvUtil.writeCsvContentRow(key, contentsMap2, writer, baselineFileName2, dstLangList2)



if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding(CHARSET)
    parser = optparse.OptionParser(
        usage = "python csvDiff.py <diff config file>\n"
                        + "config file format:\n"
                        + "\tcsvfile_1 = [old csv file name]\n"
                        + "\tcsvfile_2 = [new csv file name]\n"
                        + "\toutput_csv_diff = [output diff file name]",
        description = "Print the diff of two csv files.\n"
    )
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print parser.usage
        sys.exit(-1)
    configFileName = args[0]
    csvFileName1 = []
    csvFileName2 = []
    outputFileName = []
    if parseConfigFile(configFileName, csvFileName1, csvFileName2, outputFileName):
        csvFileName1 = csvFileName1[0]
        csvFileName2 = csvFileName2[0]
        if len(outputFileName) == 0:
            outputFileName = DEFAULT_OUTPUT_CSV_DIFF
        else:
            outputFileName = outputFileName[0]
        process(csvFileName1, csvFileName2, outputFileName)
