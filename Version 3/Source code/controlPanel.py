"""
=================
ControlPanel V0.1
=================

This is the module used to display a control panel from which the user can search
for a limited number of keywords. This class interacts with the Text Editor module
to display highlighted boxes over the found keywords in the queried text. It is
dependant on the default systems module to terminate the process, the default
tkinter module to handle the clipboard functionality, the time module to handle
the flashing cursor, the local displayConstants module which contains the layers
and rects used by the ControlPanel module and finally the pygame module used to
display the GUI for the program which can be found at the address http://pygame.org/.

This class is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import sys
import pygame
import displayConstants
import tkinter
import time




class keywordSearch(object):
    def __init__(self, textEditor, borderColour=(224, 224, 224), font="agencyfb"):
        #the editor which all text will be display on
        self.textEditor = textEditor

        #the border colour for all the  layers
        self.borderColour = borderColour

        #buffer between event call. Pygame has just under 330 events
        self.eventBufferPeriod = [0 for event in range(330)]

        #font for the controls
        self.controlPanelFont = pygame.font.SysFont(font, 22)

        #whether the user is in or out of the control box
        self.currentlyEditing = False

        #the unrendered and rendered text for the input box
        self.unrenderedText = ["***", "ControlPanel", "***"]
        self.renderedText = []
        self.lineRects = []

        #maximum height of each line
        self.maximumLineHeight = self.renderText("M").get_height()

        #whether the cursor is visable and the flash interval
        self.cursorVisibility = False
        self.cursorFlashIntervals = 0
        self.cursorLocation = [0, 0]

        #only allow check to be pressed once and then wait until the button is let go
        self.checkButtonState = True

        #dynamic background colours for the buttons
        self.checkBackgroundColour = self.borderColour
        self.clearBackgroundColour = self.borderColour
        self.closeBackgroundColour = self.borderColour

        #convert a pygame event to a function call
        self.eventToFunction = {
            pygame.K_RETURN: self.returnInput,
            pygame.K_BACKSPACE: self.backspaceInput,
            pygame.K_UP: self.moveCursorUp,
            pygame.K_RIGHT: self.moveCursorRight,
            pygame.K_DOWN: self.moveCursorDown,
            pygame.K_LEFT: self.moveCursorLeft,
            pygame.K_DELETE: self.deleteInput,
        }


    def loopUpdate(self):
        #update file display layers
        self.updateSurfaces()

        #as not to alter the self.unrenderedText which remains constant during execution
        tempUnrenderedText = [str(line) + " " for line in list(self.unrenderedText)]

        #draw each button starting with the check
        pygame.draw.rect(self.buttonLayer, self.checkBackgroundColour, [5, 5,
                        (self.buttonLayer.get_width() / 3) - 7.5, self.buttonLayer.get_height() - 10])

        #the rect for the check button
        self.checkRect = pygame.Rect((displayConstants.controlCoordinate[0] + 5, displayConstants.controlCoordinate[1] + 5),
                                        ((self.buttonLayer.get_width() / 3) - 7.5, self.buttonLayer.get_height() - 10))

        #draw the button for the clear function
        pygame.draw.rect(self.buttonLayer, self.clearBackgroundColour, [(self.buttonLayer.get_width() / 3) + 2.5, 5,
                        (self.buttonLayer.get_width() / 3) - 7.5, self.buttonLayer.get_height() - 10])

        #the rect for the clear button
        self.clearRect = pygame.Rect((displayConstants.controlCoordinate[0] + (self.buttonLayer.get_width() / 3) + 2.5
                                     , displayConstants.controlCoordinate[1] + 5), ((self.buttonLayer.get_width() / 3)
                                        - 7.5, self.buttonLayer.get_height() - 10))

        #drae the button for the close
        pygame.draw.rect(self.buttonLayer, self.closeBackgroundColour, [((2 * self.buttonLayer.get_width()) / 3) + 2.5, 5,
                        (self.buttonLayer.get_width() / 3) - 7.5, self.buttonLayer.get_height() - 10])

        #the rect for the close button
        self.closeRect = pygame.Rect((displayConstants.controlCoordinate[0] + ((2 * self.buttonLayer.get_width()) / 3) + 2.5
                                     , displayConstants.controlCoordinate[1] + 5), ((self.buttonLayer.get_width() / 3)
                                        - 7.5, self.buttonLayer.get_height() - 10))

        #blit text for the buttons on the screen
        #firstly for the check button
        self.checkText = self.renderText("check", colour=(255, 255, 255))
        self.clearText = self.renderText("clear", colour=(255, 255, 255))
        self.closeText = self.renderText("close", colour=(255, 255, 255))

        #blit the rendered text function
        def centreControl(rect, object):
             self.buttonLayer.blit(object, (rect.centerx - displayConstants.controlCoordinate[0] -
                                (object.get_width() / 2), rect.centery - displayConstants.controlCoordinate[1]
                                - (object.get_height() / 2)))

        #apply function on each layer
        centreControl(self.checkRect, self.checkText)
        centreControl(self.clearRect, self.clearText)
        centreControl(self.closeRect, self.closeText)

        #check if the user is currently editing
        if pygame.mouse.get_pressed()[0]: #--> left mouse pressed
            if displayConstants.controlRect.collidepoint(pygame.mouse.get_pos()):
                self.currentlyEditing = True #--> editing the text
            else:
                self.currentlyEditing = False #--> elsewhere
                self.cursorLocation = None #--> prevent cursor viability

        #render the lines for blit to the screen
        for unrenderedLine in tempUnrenderedText:
            renderedText = self.renderText(unrenderedLine, colour=(0, 0, 0))
            self.renderedText.append(renderedText)

        #blit the text to the screen
        for renderedLine in range(len(self.renderedText)):
            self.searchLayer.blit(self.renderedText[renderedLine],
                (5, 5 + (renderedLine * self.maximumLineHeight)))

        #generate the collision boundaries of the text
        tempLatestRects = self.generateRects(tempUnrenderedText)

        #blit the text to the screen
        for renderedLine in range(len(self.renderedText)):
            self.searchLayer.blit(self.renderedText[renderedLine],
                (5, 5 + (renderedLine * self.maximumLineHeight)))

            renderedRect = pygame.Rect((displayConstants.controlCoordinate[0] + 5,
                                        displayConstants.controlCoordinate[1] + self.buttonLayer.get_height() + 5 +
                                        (renderedLine * self.maximumLineHeight)),
                                        (self.searchLayer.get_width(), self.maximumLineHeight))

            self.lineRects.append(renderedRect)

        #count the rect with which we are colliding
        tempCollisions = 0

        #check whether the user is using the mouse to navigate the letter
        if self.currentlyEditing:
            for line in tempLatestRects:
                for letter in line:
                    if letter[1].collidepoint(pygame.mouse.get_pos()):
                        if pygame.mouse.get_pressed()[0]:
                            self.cursorLocation = letter[0]
                            self.cursorVisibility = True
                            tempCollisions += 1

        #check for line collision
        for line in range(len(self.lineRects)):
            if self.lineRects[line].collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    if self.currentlyEditing:
                        if tempCollisions == 0:
                            self.cursorLocation = [line, len(str(self.unrenderedText[line]))]
                            self.cursorVisibility = True

        #reset the timeRegister
        if self.cursorFlashIntervals == 0:
            self.cursorFlashIntervals = time.time()

            #invert hte cursorVisiblity
            self.cursorVisibility = not self.cursorVisibility

        #blit the cursor to the screen
        if self.cursorLocation != None:
            cursorRect = tempLatestRects[self.cursorLocation[0]][self.cursorLocation[1]][1]

            #only when cursor visablility is true
            if self.cursorVisibility == True:
                #draw over the top of all text
                pygame.draw.rect(self.searchLayer, (0, 0, 0), [cursorRect.x - displayConstants.controlCoordinate[0]
                    , - 35 + cursorRect.y - displayConstants.controlCoordinate[1], 2, cursorRect.height])

        #update the time register
        if time.time() - self.cursorFlashIntervals > 0.5:
            self.cursorFlashIntervals = 0

        #check if the user wants to close the window
        if self.closeRect.collidepoint(pygame.mouse.get_pos()):
            self.closeBackgroundColour = (215, 215, 215)
            if pygame.mouse.get_pressed()[0]:
                sys.exit()
        else:
            self.closeBackgroundColour = (225, 225, 225)

        #check if the user wants to analyse the text
        if self.checkRect.collidepoint(pygame.mouse.get_pos()):
            self.checkBackgroundColour = (215, 215, 215)

            #if the user makes a check request
            if pygame.mouse.get_pressed()[0]:
                if self.checkButtonState:

                    #list containing all the words the user wants to request
                    searchThrases = "".join(self.unrenderedText).split(",")[:-1]

                    #the locations to highlight in the texteditor and new self.unrenderedText
                    finalUnrenderedText = []
                    highlightLocations = []

                    #go over each thrase
                    for thrase in searchThrases:
                        finalUnrenderedText.append(thrase + " ( " + str(len(self.findText(thrase))) + " found),")

                        #append locations for highlighting
                        for location in self.findText(thrase):
                            for length in range(len(thrase)):
                                highlightLocations.append((location[0], location[1] + length))

                    #reset the cursor location
                    self.cursorLocation = [0, 0]

                    #set the regions to highlight
                    self.textEditor.highlightingRegions = highlightLocations

                    #text version of the found words and frequency of each word
                    if len(finalUnrenderedText) >= 1:
                        self.unrenderedText = list(finalUnrenderedText)
                    self.checkButtonState = False
            else:
                self.checkButtonState = True
        else:
            self.checkBackgroundColour = (225, 225, 225)

        #called when the user wants to clear the input box
        if self.clearRect.collidepoint(pygame.mouse.get_pos()):
            self.clearBackgroundColour = (215, 215, 215)

            #the mouse is clicked
            if pygame.mouse.get_pressed()[0]:

                #reset the highlighted regions, unrenderedText and the cursor location
                self.textEditor.highlightingRegions = []
                self.textEditor.cursorLocation = [0, 0]
                self.textEditor.unrenderedText = ["", "", ""]

                self.unrenderedText = ["", "", ""]
                self.cursorLocation = [0, 0]
        else:
            self.clearBackgroundColour = (225, 225, 225)

        #allow the user to hold down the keys
        tempKeysPressed = pygame.key.get_pressed()

        #go over all events
        for event in range(len(tempKeysPressed)):
            if event in list(self.eventToFunction.keys()):
                if tempKeysPressed[event] and self.eventBufferPeriod[event] == 6:
                    self.eventBufferPeriod[event] = 0

                    #events will special function
                    if self.currentlyEditing:
                        self.eventToFunction[event]()
                    self.cursorVisibility = True

                elif tempKeysPressed[event]:
                    #increase the bufferperiod of the event by 1
                    self.eventBufferPeriod[event] += 1
                else:
                    #reset the buffer call
                    self.eventBufferPeriod[event] = 6

        #clear the rendered text list
        self.renderedText.clear()
        self.lineRects.clear()

        #blit the surfaces to the fileDisplayLayer
        self.blitSurfaces()


    def updateSurfaces(self):
        #update the surfaces

        #the text search layer
        self.searchLayer = pygame.Surface((
            displayConstants.controlLayer.get_width(),
            displayConstants.controlLayer.get_height() - 35
        ))

        #the layer containing all the necessary buttons for interaction
        self.buttonLayer = pygame.Surface((
            displayConstants.controlLayer.get_width(), 35
        ))

        #clear the layers by filling them with a white background
        self.searchLayer.fill((255, 255, 255))
        self.buttonLayer.fill((255, 255, 255))

        #draw the backgrounds on each layer
        displayConstants.drawBorder(self.searchLayer, self.borderColour)
        displayConstants.drawBorder(self.buttonLayer, self.borderColour)


    def blitSurfaces(self):
        #blit the surfaces to the controlLayer
        displayConstants.controlLayer.blit(self.searchLayer, (0, 35))
        displayConstants.controlLayer.blit(self.buttonLayer, (0, 0))


    #render the passed text with the given colour
    def renderText(self, text, colour=(0, 0, 0)):
        return self.controlPanelFont.render(text, 1, colour)


    def checkEvents(self, event):
        #used to handle events
        if event.key >= pygame.K_SPACE and event.key <= 127:
                    if self.currentlyEditing:
                        if event.key not in self.eventToFunction.keys():
                            #updated keys list to check for left and right control
                            tempKeysPressed = pygame.key.get_pressed()
                            if not tempKeysPressed[pygame.K_LCTRL]:
                                if not tempKeysPressed[pygame.K_RCTRL]:

                                    #append the unicode for the event.key
                                    if event.key != pygame.K_TAB:
                                        self.appendLetter(event.unicode)
                                        self.cursorVisibility = True
                                    self.cursorVisibility = True
                                else:
                                    if event.unicode == "\x16":
                                        self.pasteText()
                            else:
                                if event.unicode == "\x16":
                                    self.pasteText()


    def findText(self, text):
        #find a keyword in the unrendered text array
        foundLocations = []

        #go over every line in the document
        for line in range(len(self.textEditor.unrenderedText)):

            #create permutation tables to analyse
            textPermutations = ["".join([self.textEditor.unrenderedText[line][i + l] for l in range(len(text))])
                                for i in range(len(self.textEditor.unrenderedText[line]) - len(text) + 1)]

            #look for the text in the document
            for perm in range(len(textPermutations)):
                if textPermutations[perm] == text:
                    foundLocations.append((line, perm))

        #return any locations where the text was found
        return foundLocations


    def pasteText(self):
        #allows for pasting from clipboard
        clipboardText = list(tkinter.Tk().clipboard_get().split("\n"))

        if len(clipboardText) > 0:
            #append the first line at the cursor
            self.appendLetter(clipboardText[0])

            #append any other lines
            if len(clipboardText) > 1:
                for line in range(len(clipboardText) - 1):
                    self.returnInput()
                    self.appendLetter(clipboardText[line + 1])


    def generateRects(self, text, margins=(5, 5)):
        #list of all the collision rects
        rectBoundaries = []

        #updated according the width and height of letter
        currentLocation = [0, 0]
        for line in range(len(text)):
            lineBoundaries = [] #--> collision rects for current line
            for letter in range(len(text[line])):
                #render the letter as to acquire width and height
                renderedLetter = self.renderText(text[line][letter])

                #the rectBoundary for the letter
                rectBoundary = pygame.Rect(
                    (displayConstants.controlCoordinate[0] +
                     margins[0] + currentLocation[0],
                     displayConstants.controlCoordinate[1] + 35 + margins[1] + currentLocation[1]),
                    (renderedLetter.get_width(), renderedLetter.get_height())
                )
                currentLocation[0] += renderedLetter.get_width()

                #update the line boundaries
                lineBoundaries.append(([line, letter], rectBoundary))

            currentLocation[0] = 0

            #append the letter rect ro the line rect
            rectBoundaries.append(lineBoundaries)
            currentLocation[1] += self.maximumLineHeight

        #return the final rect boundaries
        return rectBoundaries


    def returnInput(self):
        #called when the enter key is pressed

        #enter called at the beginning of the line
        if self.cursorLocation[1] == 0:
            #insert new line and clear the old one
            self.unrenderedText.insert(self.cursorLocation[0] + 1, self.unrenderedText[self.cursorLocation[0]])
            self.unrenderedText[self.cursorLocation[0]] = ""

        #enter called at the end of the line
        elif self.cursorLocation[1] == len(str(self.unrenderedText[self.cursorLocation[0]])):
            #create a new line
            self.unrenderedText.insert(self.cursorLocation[0] + 1, "")

        #anywhere in the middle of the line
        else:
            #split the text at the cursor location
            splitText = str(self.unrenderedText[self.cursorLocation[0]])[self.cursorLocation[1]:]

            #insert the end portion of the split text on a new line and leave the rest on the current line
            self.unrenderedText.insert(self.cursorLocation[0] + 1, splitText)
            self.unrenderedText[self.cursorLocation[0]] = str(self.unrenderedText[self.cursorLocation[0]])[:
            len(str(self.unrenderedText[self.cursorLocation[0]])) - len(str(splitText))]

        #set the cursor location to the next line
        self.cursorLocation = [self.cursorLocation[0] + 1, 0]


    def moveCursorUp(self):
        #when the up key is pressed
        if self.cursorLocation[0] != 0:
            #primitive navigation through the text but will suffice
            if self.renderText(str(self.unrenderedText[self.cursorLocation[0]])[:self.cursorLocation[1]]).get_width() >\
                    self.renderText(str(self.unrenderedText[self.cursorLocation[0] - 1])).get_width():

                #cursor location to the last letter on the previous line
                self.cursorLocation = [self.cursorLocation[0] - 1,
                len(str(self.unrenderedText[self.cursorLocation[0] - 1]))]
            else:
                #cursor location to the 1st letter on the previous line
                self.cursorLocation = [self.cursorLocation[0] - 1, 0]


    def moveCursorRight(self):
        #called when the user wants to navigate to the right
        if self.cursorLocation[1] == len(str(self.unrenderedText[self.cursorLocation[0]])):
            #at the end of the line and not the last line in the text
            if self.cursorLocation[0] != len(self.unrenderedText) - 1:
                self.cursorLocation = [self.cursorLocation[0] + 1, 0]
        else:
            #simply move to the right
            self.cursorLocation = [self.cursorLocation[0], self.cursorLocation[1] + 1]


    def moveCursorDown(self):
        #similar to what happens when navigating up but with negative values
        if self.cursorLocation[0] != len(self.unrenderedText) - 1:
            #primitive navigation through the text but will suffice
            if self.renderText(self.unrenderedText[self.cursorLocation[0]][:self.cursorLocation[1]]).get_width() >\
                    self.renderText(self.unrenderedText[self.cursorLocation[0] + 1]).get_width():

                #cursor location to the last letter on the next line
                self.cursorLocation = [self.cursorLocation[0] + 1,
                len(str(self.unrenderedText[self.cursorLocation[0] + 1]))]
            else:
                #cursor location to the first letter on the next line
                self.cursorLocation = [self.cursorLocation[0] + 1, 0]


    def moveCursorLeft(self):
        #called when the user wants to navigate to the left
        if self.cursorLocation[1] == 0:
                #at the beginning of the line and not the first line
                if self.cursorLocation[0] != 0:
                    self.cursorLocation = [self.cursorLocation[0] - 1, len(str(self.unrenderedText[self.cursorLocation[0] - 1]))]
        else:
            #move one letter to the left
            self.cursorLocation = [self.cursorLocation[0], self.cursorLocation[1] - 1]


    def backspaceInput(self):
        #if the cursor isnt in the top left corner most letter
        if self.cursorLocation != [0, 0]:
            #at the beginning of the line ( > line 1)
            if self.cursorLocation[0] != 0:
                if self.cursorLocation[1] == 0:
                    #move the text from one line to another
                    self.cursorLocation = [self.cursorLocation[0], len(str(self.unrenderedText[self.cursorLocation[0] - 1]))]
                    self.unrenderedText[self.cursorLocation[0] - 1] += str(self.unrenderedText[self.cursorLocation[0]])

                    #delete the current line
                    del self.unrenderedText[self.cursorLocation[0]]

                    #change the current cursor location reference
                    self.cursorLocation = [self.cursorLocation[0] - 1, self.cursorLocation[1]]

                    #end function call
                    return

            #expand the unrendered text to delete single letters
            unrenderedChars = [[character for character in str(line)] for line in self.unrenderedText] #--> expand the line elements

            #delete the letter at new cursor location
            del unrenderedChars[self.cursorLocation[0]][self.cursorLocation[1] - 1]

            #update the cursor location and unrendered text
            self.cursorLocation = [self.cursorLocation[0], self.cursorLocation[1] - 1]
            self.unrenderedText = ["".join(line) for line in unrenderedChars]


    def deleteInput(self):
        #called when the delete key is pressed
        if self.cursorLocation[1] == len(str(self.unrenderedText[self.cursorLocation[0]])):
            #not the last line in the text
            if self.cursorLocation[0] != len(self.unrenderedText) - 1:
                self.unrenderedText[self.cursorLocation[0]] = str(self.unrenderedText[self.cursorLocation[0]])

                #move the next line text to the current line and delete
                self.unrenderedText[self.cursorLocation[0]] += str(self.unrenderedText[self.cursorLocation[0] + 1])
                del self.unrenderedText[self.cursorLocation[0] + 1]
        else:
            #python cannot delete individual letters in words so must be expanded
            unrenderedChars = [char for char in str(self.unrenderedText[self.cursorLocation[0]])]
            del unrenderedChars[self.cursorLocation[1]]
            self.unrenderedText[self.cursorLocation[0]] = "".join(unrenderedChars)


    def appendLetter(self, letter):
        for character in letter:
            #called when foreign keyboard event is found
            unrenderedChars = [letter for letter in str(self.unrenderedText[self.cursorLocation[0]])]

            #exception for the beginning of the text
            if self.cursorLocation[1] != 0:
                unrenderedChars.insert(self.cursorLocation[1], character)
            else:
                unrenderedChars.insert(0, character)

            #check if the text exceeds the screen boundaries
            if self.renderText("".join(unrenderedChars)).get_width() > 0.90 * self.searchLayer.get_width():
                unrenderedChars.clear()
                self.returnInput()
                return

            #reconfigure the cursor location and join the list of updated characters
            self.cursorLocation = [self.cursorLocation[0], self.cursorLocation[1] + len(character)]
            self.unrenderedText[self.cursorLocation[0]] = "".join(unrenderedChars)
