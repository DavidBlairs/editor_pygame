"""
===============
TextEditor V0.3
===============

This is the TextEditor module used to display the text editor on the screen.
it contains all the functionality. It is dependant on the default time module,
the default tkinter module, displayConstants found locally as "displayConstants.py"
and the pygame module found at http://pygame.org/.

This class is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import displayConstants
import tkinter
import pygame
import time



class textEditor(object):
    def __init__(self, borderColour=(244, 244, 244), fontType="agencyfb", fontSize=22):
        #default system fonts will be used as pygame defaults to monospace if no font is found
        self.editorFont = pygame.font.SysFont(fontType, fontSize)

        #dynamic variables for relative text layer adjustment
        self.lineNumberLayerWidth = 30

        #arrays for the rendered, unrendered text and collision boundaries for the text
        self.unrenderedText = [1, 2, 3, 4, 55325135]
        self.renderedText = []
        self.textRects = []
        self.lineRects = []

        #convert unrendered text to strings
        self.unrenderedText = [str(line) for line in self.unrenderedText]

        #used for all borders as primary colour
        self.borderColour = borderColour

        #the default line spacing judged by the capital letter M
        self.maximumLineHeight = self.renderText("M").get_height()

        #if the user is currently editing text
        self.currentlyEditing = False

        #current location of the cursor and visibility
        self.cursorLocation = [0, 0]
        self.cursorVisibility = False
        self.cursorFlashIntervals = 0

        #offset for the scrolling
        self.slidebarOffsetY = 0
        self.slidebarOffsetX = 0

        #buffer between event call
        self.eventBufferPeriod = [0 for event in range(330)]

        #regions for highlighting
        self.highlightingRegions = []

        #function for the event calls
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
        #as not to alter the self.unrenderedText which remains contant during execution
        tempUnrenderedText = [str(line) + " " for line in list(self.unrenderedText)]

        #reset the surfaces with default borders
        self.surfaceUpdate()

        #blit the line numbers to the surface
        newLineWidth = self.renderText(str(len(self.unrenderedText))).get_width()

        #make the line margins aesthetically pleasing
        if newLineWidth + (5 * 3) > 30: #--> minimum margin width of 20
            self.lineNumberLayerWidth = newLineWidth + (5 * 3)

        #blit the line numbers to the screen
        for number in range(len(self.unrenderedText)):
            renderedNumber = self.renderText(str(number), colour=(215, 215, 215))

            #align to the left and use default line spacing defined above
            self.lineNumbersLayer.blit(renderedNumber, (self.lineNumberLayerWidth - renderedNumber.get_width() - 5,
                                                     (self.maximumLineHeight * number) + 5 + self.slidebarOffsetY))

        #generate the collision boundaries of the text
        tempLatestRects = self.generateRects(tempUnrenderedText)

        #blit the highlighted regions
        for region in self.highlightingRegions:
            if not region[0] >= len(tempLatestRects):
                if not region[1] >= len(tempLatestRects[region[0]]):
                    tempCharacterRect = tempLatestRects[region[0]][region[1]][1]

                    pygame.draw.rect(self.textEditingLayer, (255, 0, 0), [tempCharacterRect.x + 3 - displayConstants.textDisplayCoordinate[0]
                                    - self.lineNumberLayerWidth, tempCharacterRect.y - displayConstants.textDisplayCoordinate[1],
                                    tempCharacterRect.width, tempCharacterRect.height])

        #render the lines for blit to the screen
        for unrenderedLine in tempUnrenderedText:
            renderedText = self.renderText(unrenderedLine, colour=(0, 0, 0))
            self.renderedText.append(renderedText)

        #blit the text to the screen
        for renderedLine in range(len(self.renderedText)):
            self.textEditingLayer.blit(self.renderedText[renderedLine],
                (5 + self.slidebarOffsetX, 5 + (renderedLine * self.maximumLineHeight) + self.slidebarOffsetY))

            renderedRect = pygame.Rect((displayConstants.textDisplayCoordinate[0] + 5 + self.slidebarOffsetX,
                                        displayConstants.textDisplayCoordinate[1] +
                                        (renderedLine * self.maximumLineHeight) + self.slidebarOffsetY),
                                        (self.textEditingLayer.get_width(), self.maximumLineHeight))

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
                pygame.draw.rect(self.textEditingLayer, (0, 0, 0), [cursorRect.x - displayConstants.textDisplayCoordinate[0]
                    - self.maximumLineHeight, cursorRect.y - displayConstants.textDisplayCoordinate[1], 2, cursorRect.height])

        #update the time register
        if time.time() - self.cursorFlashIntervals > 0.5:
            self.cursorFlashIntervals = 0

        #detect whether the user is editing
        if pygame.mouse.get_pressed()[0]: #--> left mouse pressed
            if displayConstants.textDisplayRect.collidepoint(pygame.mouse.get_pos()): #--> mouse within the text editor boundaries
                self.currentlyEditing = True #--> editing the text
            else:
                self.currentlyEditing = False #--> elsewhere
                self.cursorLocation = None #--> prevent cursor viability

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

        #move the text down or up depending on request
        self.moveUpLayer = pygame.Surface((30, 30))
        self.moveUpLayer.fill((200, 200, 200))

        #draw the up arrow on the surface
        pygame.draw.line(self.moveUpLayer, (225, 225, 225), (15, 5), (5, 25), 2)
        pygame.draw.line(self.moveUpLayer, (225, 225, 225), (15, 5), (25, 25), 2)

        #blit it to the screen
        self.slidebarLayer.blit(self.moveUpLayer, (0, 0))

        #setup the down button layer
        self.moveDownLayer = pygame.Surface((30, 30))
        self.moveDownLayer.fill((200, 200, 200))

        #draw the down arrow on the surface (not relative positioning)
        pygame.draw.line(self.moveDownLayer, (225, 225, 225), (15, 25), (5, 5), 2)
        pygame.draw.line(self.moveDownLayer, (225, 225, 225), (15, 25), (25, 5), 2)

        #blit it to the screen
        self.slidebarLayer.blit(self.moveDownLayer, (0, self.slidebarLayer.get_height() - 30))

        #estalish the rects for the button surfaces
        self.moveUpRect = pygame.Rect((self.lineNumbersLayer.get_width() + self.textEditingLayer.get_width()
                + displayConstants.textDisplayCoordinate[0], displayConstants.textDisplayCoordinate[1]), (30, 30))
        self.moveDownRect = pygame.Rect((self.lineNumbersLayer.get_width() + self.textEditingLayer.get_width()
                       + displayConstants.textDisplayCoordinate[0], displayConstants.textDisplayCoordinate[1] +
                        self.slidebarLayer.get_height() - 30), (30, 30))

        #check if the user is moving up or down
        if self.moveUpRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if self.slidebarOffsetY < 0:
                    self.slidebarOffsetY += 4
                else:
                    self.slidebarOffsetY = 0

        #check for movement down
        if self.moveDownRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if self.slidebarOffsetY > -(self.maximumLineHeight * (len(self.unrenderedText) - 5)):
                    self.slidebarOffsetY -= 4
                else:
                    #limit of 5 lines visible
                    if len(self.unrenderedText) > 5:
                        self.slidebarOffsetY = -(self.maximumLineHeight * (len(self.unrenderedText) - 5)) + 1

        #moving the screen to the left and right
        self.moveLeftLayer = pygame.Surface((30, 30))
        self.moveRightLayer = pygame.Surface((30, 30))

        #fill with a slightly dark grey
        self.moveLeftLayer.fill((200, 200, 200))
        self.moveRightLayer.fill((200, 200, 200))

        #draw the left arrow on the left layer
        pygame.draw.line(self.moveLeftLayer, (225, 225, 225), (5, 15), (25, 5), 2)
        pygame.draw.line(self.moveLeftLayer, (225, 225, 225), (5, 15), (25, 25), 2)

        #draw the right arrow on the right layer
        pygame.draw.line(self.moveRightLayer, (225, 225, 225), (5, 5), (25, 15), 2)
        pygame.draw.line(self.moveRightLayer, (225, 225, 225), (5, 25), (25, 15), 2)

        #blit these layers to the horizontal slide layer
        self.horizontalSlidebarLayer.blit(self.moveLeftLayer, (0, 0))
        self.horizontalSlidebarLayer.blit(self.moveRightLayer, (self.horizontalSlidebarLayer.get_width() - 30, 0))

        #the rects for the layers to detect mouse collision
        self.moveLeftRect = pygame.Rect((displayConstants.textDisplayCoordinate[0], displayConstants.textDisplayCoordinate[1]
                                        + self.lineNumbersLayer.get_height()), (30, 30))
        self.moveRightRect = pygame.Rect((displayConstants.textDisplayCoordinate[0] + self.lineNumbersLayer.get_width() +
                                          self.textEditingLayer.get_width() - 30, displayConstants.textDisplayCoordinate[1]
                                        + self.lineNumbersLayer.get_height()), (30, 30))

        #check if user wants to move left
        if self.moveLeftRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if self.slidebarOffsetX < 0:
                    self.slidebarOffsetX += 4
                else:
                    self.slidebarOffsetX = 0

        #check if user wants to go right
        if self.moveRightRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:

                #find the line with the greatest width
                tempGreatestWidth = 0
                for renderedLine in self.renderedText:
                    if renderedLine.get_width() > tempGreatestWidth:
                        tempGreatestWidth = renderedLine.get_width()

                #buffer for easy viewing
                tempGreatestWidth -= 50

                #only when within the boundaries
                if tempGreatestWidth + 50 > self.textEditingLayer.get_width() * 0.5:
                    if self.slidebarOffsetX > -tempGreatestWidth:
                        self.slidebarOffsetX -= 4
                    else:
                        self.slidebarOffsetX = -tempGreatestWidth


       #reset the renderedText array and line rects
        self.renderedText.clear()
        self.lineRects.clear()

        #blit the surfaces to the screen
        self.blitSurfaces()


    def checkEvent(self, event):
        #pygame can only handle one location handeling events
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
                    (displayConstants.textDisplayCoordinate[0] + self.maximumLineHeight +
                     margins[0] + currentLocation[0] + self.slidebarOffsetX,
                     displayConstants.textDisplayCoordinate[1] + margins[1] + currentLocation[1] + self.slidebarOffsetY),
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


    def surfaceUpdate(self):
        #resizing the three sub-surfaces. Begin with slide bar layer as it has a fixed with
        self.slidebarLayer = pygame.Surface((
            30, displayConstants.textDisplayLayer.get_height() - 30
        ))

        #text editing layer is only dependant on the width of the line numbers
        self.textEditingLayer = pygame.Surface((
            displayConstants.textDisplayLayer.get_width() - self.lineNumberLayerWidth - self.slidebarLayer.get_width(),
            displayConstants.textDisplayLayer.get_height() - 30
        ))

        #line number layer is dependant on the width of the maximum number
        self.lineNumbersLayer = pygame.Surface((
            self.lineNumberLayerWidth,
            displayConstants.textDisplayLayer.get_height() - 30
        ))

        #the second slidebar layer for horizontal movement
        self.horizontalSlidebarLayer = pygame.Surface((
            self.lineNumbersLayer.get_width() + self.textEditingLayer.get_width(),
            30
        ))

        #clear the layers as (255, 255, 255) or white.
        self.slidebarLayer.fill((255, 255, 255))
        self.textEditingLayer.fill((255, 255, 255))
        self.lineNumbersLayer.fill((255, 255, 255))
        self.horizontalSlidebarLayer.fill((255, 255, 255))

        #draw the borders
        displayConstants.drawBorder(self.slidebarLayer, self.borderColour)
        displayConstants.drawBorder(self.textEditingLayer, self.borderColour)
        displayConstants.drawBorder(self.lineNumbersLayer, self.borderColour)
        displayConstants.drawBorder(self.horizontalSlidebarLayer, self.borderColour)


    def blitSurfaces(self):
        #the self.updateSurfaces function clears and draw all the default aspects.
        #this is designed to be run after all the other aspects are appended.

        displayConstants.textDisplayLayer.blit(self.lineNumbersLayer, (0, 0))
        displayConstants.textDisplayLayer.blit(self.textEditingLayer, (self.lineNumbersLayer.get_width(), 0))
        displayConstants.textDisplayLayer.blit(self.slidebarLayer, (self.lineNumbersLayer.get_width() + self.textEditingLayer.get_width(), 0))
        displayConstants.textDisplayLayer.blit(self.horizontalSlidebarLayer, (0, self.lineNumbersLayer.get_height()))

    def returnInput(self):
        #called when the enter key is pressed

        #enter called at the beginning of the line
        if self.cursorLocation[1] == 0:
            #insert new line and cleae the old one
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
        #called when foreign keyboard event is found
        unrenderedChars = [letter for letter in str(self.unrenderedText[self.cursorLocation[0]])]

        #exception for the beginning of the text
        if self.cursorLocation[1] != 0:
            unrenderedChars.insert(self.cursorLocation[1], letter)
        else:
            unrenderedChars.insert(0, letter)

        #reconfigure the cursor location and join the list of updated characters
        self.cursorLocation = [self.cursorLocation[0], self.cursorLocation[1] + len(letter)]
        self.unrenderedText[self.cursorLocation[0]] = "".join(unrenderedChars)


    #render the passed text with the given colour
    def renderText(self, text, colour=(0, 0, 0)):
        return self.editorFont.render(text, 1, colour)
