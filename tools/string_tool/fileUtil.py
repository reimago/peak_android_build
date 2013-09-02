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

import os
from os import path

FILE_SEPERATOR = "/"
FLAG_IS_STRINGS_XML = "values/strings.xml"
SYMBOL_CONNECT = "-"
FLAG_VALUES = "values"
FLAG_STRINGS_XML = "strings.xml"
DEFAULT_BASELINE_LANG = 'en'

#DFS to get the values/strings.xml list
def getBaselineXMLFileNameListFromSearchPath(baselineLang, searchPath, fileNameList):
    if baselineLang == DEFAULT_BASELINE_LANG:
        baselineSuffix = FLAG_IS_STRINGS_XML
    else:
        baselineSuffix = path.join(FLAG_VALUES + SYMBOL_CONNECT + baselineLang, FLAG_STRINGS_XML)
    searchPath = path.normpath(searchPath)
    if path.exists(searchPath):
        if path.isdir(searchPath):
            curFileNameList = os.listdir(searchPath)
            for tempFileName in curFileNameList:
                getBaselineXMLFileNameListFromSearchPath(baselineLang, path.join(searchPath, tempFileName), fileNameList)
        elif path.isfile(searchPath):
            if searchPath.endswith(baselineSuffix):
                fileNameList.append(searchPath)
    else:
        print "Search path: '" + searchPath + "' doesn't exist."
        return

#get dst filename with language 'dstLang'if exists
def getDstXMLFileNameFromBaselineXMLFileName(fileNameBaseline, dstLang):
    searchPath = FILE_SEPERATOR.join(fileNameBaseline.split(FILE_SEPERATOR)[0:-2])
    searchPath = path.normpath(searchPath)
    dirNameDst = path.join(searchPath, FLAG_VALUES + SYMBOL_CONNECT + dstLang)
    fileNameDst = path.join(dirNameDst, FLAG_STRINGS_XML)
    fileNameDst = path.normpath(fileNameDst)
    if path.exists(dirNameDst):
        if path.exists(fileNameDst):
            return (True, fileNameDst)
    else:
        print "Mkdir :'" + dirNameDst + "'"
        os.mkdir(dirNameDst)
    return (False, fileNameDst)
