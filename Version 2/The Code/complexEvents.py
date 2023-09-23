"""
======================
complexEvents Handler
======================

 This files contains some internal functions for text manipulation. These
 functions are used by both the textEditor class and the controlPanel class
 to power their text interaction functionality. It is dependant on the default
 tkinter module used for clipboard manipulation and the pygame module which
 can be found at http://pygame.org/.

This file is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import tkinter
import pygame


def returnInput(interactionText, cursorLocation):
    if cursorLocation == None: return interactionText, cursorLocation
    # python can't ignore split functions called at the end of the line
    # or at  the beginning of the line so exceptions are made.

    # shouldn't edit arguements as if they were variables
    # for some reason, without type declaration, the variable
    # acts as if it where the argument.
    tempInteractionText = list(interactionText)
    tempCursorLocation = list(cursorLocation)

    # first exception is at the beginning of the line
    if tempCursorLocation[1] == 0:
        tempInteractionText.insert(tempCursorLocation[0] + 1, tempInteractionText[tempCursorLocation[0]])
        tempInteractionText[tempCursorLocation[0]] = ""

    # second exception is at the end of the line
    elif tempCursorLocation[1] == len(str(tempInteractionText[tempCursorLocation[0]])):
        tempInteractionText.insert(tempCursorLocation[0] + 1, "")

    # final case is anywhere in the rest of the line
    else:
        tempSplitText = str(tempInteractionText[tempCursorLocation[0]])[tempCursorLocation[1]:]
        tempInteractionText.insert(tempCursorLocation[0] + 1, tempSplitText)

        # there isn't an easy way to acquire the leftover text from the subscription of text
        # so worked around it with a longer script
        tempInteractionText[tempCursorLocation[0]] = str(tempInteractionText[tempCursorLocation[0]])[:
                    len(str(tempInteractionText[tempCursorLocation[0]])) - len(str(tempSplitText))]

    tempCursorLocation = (tempCursorLocation[0] + 1, 0)

    return tempInteractionText, tempCursorLocation


def appendLetter(interactionText, cursorLocation, letter):
    if cursorLocation == None: return interactionText, cursorLocation
    # Can't simply define a variable as another variable as python sometimes doesn't
    # correctly work with the newly declared variable. To work around this problem,
    # I declared the variable with the data type.

    tempInteractionText = list(interactionText)
    tempCursorLocation = tuple(cursorLocation)
    tempLetter = str(letter)

    # strings are not subscriptable so the line is converted to a list
    tempInteractionLine = [letter for letter in str(tempInteractionText[tempCursorLocation[0]])]

    tempInteractionLine.insert(tempCursorLocation[1], tempLetter)
    tempCursorLocation = (tempCursorLocation[0], tempCursorLocation[1] + len(tempLetter))

    # take the list of letters and put them into a string that can be
    # rendered.
    tempInteractionText[tempCursorLocation[0]] = "".join(tempInteractionLine)

    return tempInteractionText, tempCursorLocation



def pasteText(interactionText, cursorLocation):
    if cursorLocation == None: return interactionText, cursorLocation
    # tkinter seems to  be the only module with reasonable clipboard
    # manipulation functionality so while it isn't used for this primarily,
    # it will be used for this purpose in my script.

    tempInteractionText = list(interactionText)
    tempCursorLocation = tuple(cursorLocation)

    try:
        tempClipboardText = list(tkinter.Tk().clipboard_get().split("\n"))
    except: return tempInteractionText, tempCursorLocation

    if len(tempClipboardText) > 0:
        tempInteractionText, tempCursorLocation = appendLetter(
            tempInteractionText, tempCursorLocation, tempClipboardText[0])

        if len(tempClipboardText) > 1:
            # iterate over the len of the range to easily work with elements
            # at different locations relative to each index.
            for line in range(len(tempClipboardText) - 1):
                tempInteractionText, tempCursorLocation = \
                    returnInput(tempInteractionText, tempCursorLocation)
                tempInteractionText, tempCursorLocation = appendLetter(
                    tempInteractionText, tempCursorLocation, tempClipboardText[line + 1])

    return tempInteractionText, tempCursorLocation



def backspaceInput(interactionText, cursorLocation):
    if cursorLocation == None: return interactionText, cursorLocation
    # like with the other functions, we can't just simply define one variable
    # as another and so must declare the data type along side them

    tempInteractionText = list(interactionText)
    tempCursorLocation = tuple(cursorLocation)

    #first exception made for the 1st line and 1st letter
    if tempCursorLocation != (0, 0):
        if tempCursorLocation[0] != 0:
            #second exception is at the beginning of the line
            if tempCursorLocation[1] == 0:
                tempCursorLocation = (tempCursorLocation[0], len(str(tempInteractionText[tempCursorLocation[0] - 1])))
                tempInteractionText[tempCursorLocation[0] - 1] += str(tempInteractionText[tempCursorLocation[0]])

                del tempInteractionText[tempCursorLocation[0]]
                tempCursorLocation = (tempCursorLocation[0] - 1, tempCursorLocation[1])
                return tempInteractionText, tempCursorLocation

        tempInteractionLine = [[letter for letter in str(line)] for line in tempInteractionText]

        #third exception is when deleting anywhere in the middle of the line
        del tempInteractionLine[tempCursorLocation[0]][tempCursorLocation[1] - 1]

        tempCursorLocation = (tempCursorLocation[0], tempCursorLocation[1] - 1)
        tempInteractionText = ["".join(line) for line in tempInteractionLine]

    return tempInteractionText, tempCursorLocation



def moveCursorUp(interactionText, cursorLocation, renderFunction):
    if cursorLocation == None: return interactionText, cursorLocation
    # like with the other functions, we can't just simply define one variable
    # as another and so must declare the data type along side them

    tempCursorLocation = tuple(cursorLocation)
    tempInteractionText = list(interactionText)

    # first exception is cursor located on the first line
    if tempCursorLocation[0] != 0:
        if renderFunction(str(tempInteractionText[tempCursorLocation[0]][:tempCursorLocation[1]])).get_width() >\
            renderFunction(str(tempInteractionText[tempCursorLocation[0] - 1])).get_width():

            tempCursorLocation = [tempCursorLocation[0] - 1,
            len(str(tempInteractionText[tempCursorLocation[0] - 1]))]

        else:
            tempCursorLocation = [tempCursorLocation[0] - 1, 0]

    return tempInteractionText, tempCursorLocation



def moveCursorRight(interactionText, cursorLocation):
    if cursorLocation == None: return interactionText, cursorLocation
    # like with the other functions, we can't just simply define one variable
    # as another and so must declare the data type along side them

    tempCursorLocation = tuple(cursorLocation)
    tempInteractionText = list(interactionText)

    # exception at the end of the line where it moves to the next
    if tempCursorLocation[1] == len(str(tempInteractionText[tempCursorLocation[0]])):
        # a sort of sub exception, if not at the end of the document
        if tempCursorLocation[0] != len(tempInteractionText) -1:
            tempCursorLocation = (tempCursorLocation[0] + 1, 0)
    else:
        tempCursorLocation = (tempCursorLocation[0], tempCursorLocation[1] + 1)

    return tempInteractionText, tempCursorLocation



def moveCursorDown(interactionText, cursorLocation, renderFunction):
    if cursorLocation == None: return interactionText, cursorLocation
    # mainly just a replica of the up function but with negative values
    # like with the other functions, we can't just simply define one variable
    # as another and so must declare the data type along side them

    tempCursorLocation = tuple(cursorLocation)
    tempInteractionText = list(interactionText)

    # first exception is cursor located on the last line
    if tempCursorLocation[0] != len(tempInteractionText) - 1:
        if renderFunction(str(tempInteractionText[tempCursorLocation[0]][:tempCursorLocation[1]])).get_width() >\
            renderFunction(str(tempInteractionText[tempCursorLocation[0] + 1])).get_width():

            tempCursorLocation = [tempCursorLocation[0] + 1,
            len(str(tempInteractionText[tempCursorLocation[0] + 1]))]

        else:
            tempCursorLocation = [tempCursorLocation[0] + 1, 0]

    return tempInteractionText, tempCursorLocation



def moveCursorLeft(interactionText, cursorLocation):
    if cursorLocation == None: return interactionText, cursorLocation
    # like with the other functions, we can't just simply define one variable
    # as another and so must declare the data type along side them

    tempCursorLocation = tuple(cursorLocation)
    tempInteractionText = list(interactionText)

    # exception at the end of the line where it moves to the next
    if tempCursorLocation[1] == 0:
        # a sort of sub exception, if not at the end of the document
        if tempCursorLocation[0] != 0:
            tempCursorLocation = (tempCursorLocation[0] - 1, len(str(tempInteractionText[tempCursorLocation[0] - 1])))
    else:
        tempCursorLocation = (tempCursorLocation[0], tempCursorLocation[1] - 1)

    return tempInteractionText, tempCursorLocation



def deleteInput(interactionText, cursorLocation):
    if cursorLocation == None: return interactionText, cursorLocation
    # sort of like the backspace function which makes it easy to represent the event
    # like with the other functions, we can't just simply define one variable
    # as another and so must declare the data type along side them

    tempCursorLocation = tuple(cursorLocation)
    tempInteractionText = list(interactionText)

    # the only exception is if the cursor is at the end of the line. If it is, the
    # text from the next line is moved to the end of the current line.
    if tempCursorLocation[1] == len(str(tempInteractionText[tempCursorLocation[0]])):
        if tempCursorLocation[0] != len(tempInteractionText) - 1:
            tempInteractionText[tempCursorLocation[0]] = str(tempInteractionText[tempCursorLocation[0]])

            # combine the lines and delete the next line
            tempInteractionText[tempCursorLocation[0]] += str(tempInteractionText[tempCursorLocation[0] + 1])
            del tempInteractionText[tempCursorLocation[0] + 1]
    else:
        # occurs when the cursor is not at the end of the line. It simply
        # requires the letter to the left of the cursor to be deleted
        tempInteractionLine = [letter for letter in str(tempInteractionText[tempCursorLocation[0]])]

        del tempInteractionLine[tempCursorLocation[1]]
        tempInteractionText[tempCursorLocation[0]] = "".join(tempInteractionLine)

    return tempInteractionText, tempCursorLocation