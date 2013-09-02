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

from xml.dom.minidom import parse, parseString

TYPE_STRING_NODE = 'string'
TYPE_XLIFF_NODE = 'xliff:g'
TYPE_STRING_ARRAY_NODE = 'string-array'
TYPE_PLURALS_NODE = 'plurals'
TYPE_ITEM_NODE = 'item'
TYPE_B_NODE = 'b'
TYPE_I_NODE = 'i'
TYPE_U_NODE = 'u'

KEY_NODE_NAME = 'name'
KEY_QUANTITY = 'quantity'
KEY_PRODUCT = 'product'
KEY_TRANSLATABLE = 'translatable'
KEY_TRANSLATE = 'translate'
VALUE_TRANSLATABLE_FALSE = 'false'


SECOND_ID_PREFIX_PRODUCT = "product_"
SECOND_ID_PREFIX_PLURALS = "plurals_"
SECOND_ID_PREFIX_STRING_ARRAY = "string-array_"

DUMMY_NODE_START = '<dummy xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">'
DUMMY_NODE_END = '</dummy>'

STYLE_NODE_START_MAP = {TYPE_B_NODE:'<b>', TYPE_I_NODE:'<i>', TYPE_U_NODE:'<u>'}
STYLE_NODE_END_MAP = {TYPE_B_NODE:'</b>', TYPE_I_NODE:'</i>', TYPE_U_NODE:'</u>'}

COMMENT_FLAG_START = '<!--'
COMMENT_FLAG_END = '-->'

CHARSET = "UTF-8"

#for generate csv

def convertXMLText(value):
    return value.replace("<", "&lt;").replace(">", "&gt;")

#convert xliff node to string value
#warn: user isn't allowed to modify xliff part value, which may lead to build error
def convertXliffNodeToValue(xliffNode):
    if xliffNode.tagName != TYPE_XLIFF_NODE:
        return ''
    if len(xliffNode.childNodes) == 0:
        return ''
    #simply connect all the parts
    value = []
    value.append('<xliff:g')
    attributeKeys = xliffNode.attributes.keys()
    for attrName in attributeKeys:
        value.append(' ' + attrName + '="' + xliffNode.getAttribute(attrName) + '"')
    value.append('>' + convertXMLText(xliffNode.childNodes[0].nodeValue) + '</xliff:g>')
    return ''.join(value)

def convertCommentNodeToValue(commentNode):
    if commentNode.nodeType != commentNode.COMMENT_NODE:
        return ''
    return COMMENT_FLAG_START + commentNode.nodeValue + COMMENT_FLAG_END

def isTranslateFalseNode(node):
    if node.hasAttribute(KEY_TRANSLATABLE):
        if node.getAttribute(KEY_TRANSLATABLE) == VALUE_TRANSLATABLE_FALSE:
            return True
    if node.hasAttribute(KEY_TRANSLATE):
        if node.getAttribute(KEY_TRANSLATE) == VALUE_TRANSLATABLE_FALSE:
            return True
    return False

#get string value of common item
def getCommonNodeValue(itemNode):
    childNodes = itemNode.childNodes
    value = ''
    for node in childNodes:
        if node.nodeType == node.TEXT_NODE:
            value += convertXMLText(node.nodeValue)
        elif node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_XLIFF_NODE:
            value += convertXliffNodeToValue(node)
        elif node.nodeType == node.COMMENT_NODE:
            value += convertCommentNodeToValue(node)
        elif node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_B_NODE:
            value += getStyleNodeValue(node, TYPE_B_NODE)
        elif node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_I_NODE:
            value += getStyleNodeValue(node, TYPE_I_NODE)
        elif node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_U_NODE:
            value += getStyleNodeValue(node, TYPE_U_NODE)
    return value

#get string value of style node
def getStyleNodeValue(styleNode, style):
    childNodes = styleNode.childNodes
    value = STYLE_NODE_START_MAP[style]
    value += getCommonNodeValue(styleNode)
    value += STYLE_NODE_END_MAP[style]
    return value

#get value of string node (may contain xliff child nodes)
#format: (id, 2nd id, string_value)
def getStringNodeValue(stringNode):
    if stringNode.tagName != TYPE_STRING_NODE:
        return None
    if isTranslateFalseNode(stringNode):
        return None
    value = getCommonNodeValue(stringNode)
    #exception: some string nodes have 'product' attribute
    #so it is used as 2nd id
    secondId = ''
    if stringNode.hasAttribute(KEY_PRODUCT):
        secondId = SECOND_ID_PREFIX_PRODUCT + stringNode.getAttribute(KEY_PRODUCT)
    return (stringNode.getAttribute(KEY_NODE_NAME), secondId, value)

#get value list of string-array node, list item format: (id, 2nd id, string_value)
def getStringArrayNodeValueList(stringArrayNode):
    name = stringArrayNode.getAttribute(KEY_NODE_NAME)
    if stringArrayNode.tagName != TYPE_STRING_ARRAY_NODE:
        return []
    if isTranslateFalseNode(stringArrayNode):
        return []
    childNodes = stringArrayNode.childNodes
    valueList = []
    i = 1
    for node in childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_ITEM_NODE:
            value = getCommonNodeValue(node)
            if len(value) != 0:
                #for this type of item, no extra attribute to use as 2nd id so just record the index
                #so 'string-array_1' to indicate the first item under string-array node
                valueList.append((name, SECOND_ID_PREFIX_STRING_ARRAY + str(i), value))
                i += 1
    return valueList

#get value list of plurals node, list item format: (id, 2nd id, string_value)
def getPluralsNodeValueList(pluralsNode):
    name = pluralsNode.getAttribute(KEY_NODE_NAME)
    if pluralsNode.tagName != TYPE_PLURALS_NODE:
        return []
    if isTranslateFalseNode(pluralsNode):
        return []
    childNodes = pluralsNode.childNodes
    valueList = []
    for node in childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_ITEM_NODE:
            value = getCommonNodeValue(node)
            if len(value) != 0:
                #for this type of item, attribute 'quantity' can be used as 2nd id
                #'plurals_item_one' to indicate the item with quantity='one' under plurals node 
                valueList.append((name, SECOND_ID_PREFIX_PLURALS + node.getAttribute(KEY_QUANTITY), value))
    return valueList

#ELEMENT_NODE filter for DOM node type
def isElementNode(node):
    return node.nodeType == node.ELEMENT_NODE

def getElementNodeListFromXMLFile(fileName):
    try:
        xmlFile = open(fileName)
    except IOError:
        print "Open file: " + fileName + " error ."
        return ([], None)
    xmlDom = parse(xmlFile)
    root = xmlDom.documentElement
    return (filter(isElementNode, root.childNodes), xmlDom)

#generate baseline contents map, item format: (id, 2nd id)->[baseLineValue, dstValue1, dstValue2, ...]
#map element value (at index 0) is the baseline string value, map element value (at index 1,2,...) is the dst string value
#in this method, only element value at index 0 is set
def generateBaseLineContentsMapFromXMLFile(fileName, dstCount):
    (elementNodes, dom) = getElementNodeListFromXMLFile(fileName)
    if len(elementNodes) == 0 or dstCount < 1:
        return []
    contentsMap = {}
    #since sequence of the keys in contentsMap may be disordered, this is recorded for keeping the order of keys
    keyList = []
    for node in elementNodes:
        if node.tagName == TYPE_STRING_NODE:
            value = getStringNodeValue(node)
            if value is not None:
                key = (value[0], value[1])
                contentsMap[key] = [u''] * (dstCount + 1)
                contentsMap[key][0] = value[2]
                keyList.append(key)
        elif node.tagName == TYPE_STRING_ARRAY_NODE:
            for value in getStringArrayNodeValueList(node):
                key = (value[0], value[1])
                contentsMap[key] = [u''] * (dstCount + 1)
                contentsMap[key][0] = value[2]
                keyList.append(key)
        elif node.tagName == TYPE_PLURALS_NODE:
            for value in getPluralsNodeValueList(node):
                key = (value[0], value[1])
                contentsMap[key] = [u''] * (dstCount + 1)
                contentsMap[key][0] = value[2]
                keyList.append(key)
    print "scan length is " + str(len(keyList))
    return (contentsMap, keyList)

#generate destnation contents
#in this method, element value at index 1,2,... is set
def generateDstContentsIntoContentsMapFromXMLFile(contentsMap, fileName, index):
    if index < 1:
        return False
    (elementNodes, dom) = getElementNodeListFromXMLFile(fileName)
    if len(elementNodes) == 0:
        return False
    allKeys = contentsMap.keys()
    for node in elementNodes:
        if node.tagName == TYPE_STRING_NODE:
            value = getStringNodeValue(node)
            if value is not None:
                key = (value[0], value[1])
                if key in allKeys:
                    contentsMap[key][index] = value[2]
        elif node.tagName == TYPE_STRING_ARRAY_NODE:
            for value in getStringArrayNodeValueList(node):
                key = (value[0], value[1])
                if key in allKeys:
                    contentsMap[key][index] = value[2]
        elif node.tagName == TYPE_PLURALS_NODE:
            for value in getPluralsNodeValueList(node):
                key = (value[0], value[1])
                if key in allKeys:
                    contentsMap[key][index] = value[2]
    return True

#for write back

#update text, delete all child nodes and append 
def updateNodeText(node, value, dom):
    if len(value) <= 0:
        return
    childNodes = node.childNodes
    #remove all child nodes
    while len(childNodes) > 0:
        node.removeChild(childNodes[0])
    value = DUMMY_NODE_START + value + DUMMY_NODE_END
    tempDom = parseString(value)
    for newNode in tempDom.documentElement.childNodes:
        #clone a node, otherwise newNode will be unlinked from original childNodes
        node.appendChild(newNode.cloneNode(True))

#for string node, update dst language value, if no value, keep the baseline value
def updateStringNodeText(stringNode, contentsMap, index, dom):
    if stringNode.tagName != TYPE_STRING_NODE:
        return False
    key1 = stringNode.getAttribute(KEY_NODE_NAME)
    key2 = ''
    if stringNode.hasAttribute(KEY_PRODUCT):
        key2 = SECOND_ID_PREFIX_PRODUCT + stringNode.getAttribute(KEY_PRODUCT)
    key = (key1.encode(), key2.encode())
    if key not in contentsMap.keys():
        return False
    value = contentsMap[key][index]
    updateNodeText(stringNode, value, dom)
    return True

#for string-array node, update dst language value, if no value, keep the baseline value
def updateStringArrayNodeText(stringArrayNode, contentsMap, index, dom):
    if stringArrayNode.tagName != TYPE_STRING_ARRAY_NODE:
        return False
    itemNodes = stringArrayNode.childNodes
    key1 = stringArrayNode.getAttribute(KEY_NODE_NAME)
    i = 1
    for node in itemNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_ITEM_NODE:
            key2 = SECOND_ID_PREFIX_STRING_ARRAY + str(i)
            key = (key1.encode(), key2.encode())
            if key not in contentsMap.keys():
                return False
            value = contentsMap[key][index]
            updateNodeText(node, value, dom)
            i += 1
    return True

#for plurals node, update dst language value, if no value, keep the baseline value
def updatePluralsNodeText(pluralsNode, contentsMap, index, dom):
    if pluralsNode.tagName != TYPE_PLURALS_NODE:
        return False
    itemNodes = pluralsNode.childNodes
    key1 = pluralsNode.getAttribute(KEY_NODE_NAME)
    for node in itemNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == TYPE_ITEM_NODE:
            key2 = SECOND_ID_PREFIX_PLURALS + node.getAttribute(KEY_QUANTITY)
            key = (key1.encode(), key2.encode())
            if key not in contentsMap.keys():
                return False
            value = contentsMap[key][index]
            updateNodeText(node, value, dom)
    return True

#hard code
#set this attribute since this is set in all the none-english version
def updateRootAttribute(node):
    node.setAttribute('xmlns:android', 'http://schemas.android.com/apk/res/android')

#write back xml file
#note that the output xml file has some spacial strings that has been converted from
# < > "
def writeBackDstXMLFile(contentsMap, index, writer, baselineName):
    (elementNodeList, dom) = getElementNodeListFromXMLFile(baselineName)
    root = dom.documentElement
    updateRootAttribute(root)
    if len(elementNodeList) == 0 or dom is None:
        return
    for node in elementNodeList:
        if node.tagName == TYPE_STRING_NODE:
            result = updateStringNodeText(node, contentsMap, index, dom)
            if not result:
                #note that this is ok because elementNodeList is a copy
                root.removeChild(node)
        elif node.tagName == TYPE_STRING_ARRAY_NODE:
            result = updateStringArrayNodeText(node, contentsMap, index, dom)
            if not result:
                root.removeChild(node)
        elif node.tagName == TYPE_PLURALS_NODE:
            result = updatePluralsNodeText(node, contentsMap, index, dom)
            if not result:
                root.removeChild(node)
    dom.writexml(writer, encoding=CHARSET)
    writer.close()
