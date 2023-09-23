"""
============
ControlPanel
============

This is the module used to display a control panel from which the user can search
for a limited number of keywords. This class interacts with the Text Editor module
to display highlighted boxes over the found keywords in the queried text. It is
dependant on the default systems module to terminate the process, the default
tkinter module to handle the clipboard functionality, the time module to handle
the flashing cursor, the local displayConstants module which contains the layers
and rects used by the ControlPanel module, the surface manipulation module found
locally at "surfaceManipulation.py", the complex events module found locally at
""complexEvents.py" and finally the pygame module used to display the GUI for the
 program which can be found at the address http://pygame.org/.

This file is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import sys
import time
import tkinter

import pygame
import complexEvents
import displayConstants
import surfaceManipulation

class controlPanel(object):
    def __init__(self, textEditor, borderColour=(224, 224, 224), fontType="agencyfb", fontSize=22):
        # the control panel requires a text editor for gathering text for analysis
        # and highlighting the text allowing the user to find occurrences of words.
        self.textEditor = textEditor

        # when using custom fonts, pygame will return an error if the font cannot be
        # found. Its best to use system fonts because if the font cannt be found, it
        # will default to monospace.
        self.controlPanelFont = pygame.font.SysFont(fontType, fontSize)

        self.borderColour = borderColour
        self.currentlyEditing = False

        # the text that will be display to the screen and used in the analysis process,
        # the rendered version of this text that will be blit to the screen and the line
        # rects allowing the user to click near the end of a line and still move the cursor.
        self.textUnrendered = ["***", "ControlPanel", "***"]
        self.textRendered = []
        self.lineRects = []

        # the cursor visaility only changes when the currently editing variable changes
        # the cursor flash interval counts up to 2 slowly every iteration and the cursor
        # location changes when the user moves the cursor.
        self.cursorVisibility = False
        self.cursorFlashIntervalCount = 0
        self.cursorLocation = [0, 0]

        # because the check button acts as both an input and output box, it has a feature
        # that means they can only press the button once and then must stop clicking until
        # they press it again.
        self.checkButtonState  = True

        # the colours of each of the buttons backgrounds
        self.buttonBackgroundColours = [self.borderColour for button in range(3)]

        # each complex event buffer period must is accounted for. Pygame handles around 330
        # events so a list of 330 will suffice.
        self.eventBufferPeriod = [0 for event in range(330)]

        # the base height of all lines as a capital M is the tallest letter
        self.lineHeight = self.renderText("M").get_height()

        # each complex event corresponds to a function to update the text
        self.eventToFunction = {
            pygame.K_RETURN: complexEvents.returnInput,
            pygame.K_BACKSPACE: complexEvents.backspaceInput,
            pygame.K_UP: complexEvents.moveCursorUp,
            pygame.K_RIGHT: complexEvents.moveCursorRight,
            pygame.K_DOWN: complexEvents.moveCursorDown,
            pygame.K_LEFT: complexEvents.moveCursorLeft,
            pygame.K_DELETE: complexEvents.deleteInput,
        }


    def loopUpdate(self):
        # due to the unfortunately limited capabilities of my text editor, this
        # line must add space margins on either side of each line to make cursor
        # manipulation much easier.
        tempTextUnrendered = [str(line) + " " for line in list(self.textUnrendered)]

        self.surfaceUpdate()
        self.tertiarySurfaceUpdate()

        # the user is only allowed to interact with the editor if the mouse is inside the
        # editing box and has has clicked at least once. Otherwise, currently editing is
        # equal to false. If the user moves out of the editing box and clicks, they are
        # no longer editing.
        if pygame.mouse.get_pressed()[0]:
            if displayConstants.controlRect.collidepoint(pygame.mouse.get_pos()):
                self.currentlyEditing = True
            else:
                # the cursor location is also set to None so it isn't visible unless the
                # user is editing.
                self.currentlyEditing = False
                self.cursorLocation = None

        # blit the unrendered text to the screen
        self.blitText(self.textUnrendered)

        # generate the collision boundaries for the text
        tempLatestRects = self.generateRects(tempTextUnrendered)

        # by creating rects around each letter, I can detect mouse collision tracking where the
        # mouse is on the screen as is done so below using the rects generated above.
        tempMouseCollisions = 0

        if self.currentlyEditing:
            for lineRect in tempLatestRects:
                for letterRect in lineRect:

                    # pygame rects have many functions such as the collidepoint function
                    # which detects if a given set of coordinates in within the rect.
                    if letterRect[1].collidepoint(pygame.mouse.get_pos()):
                        if pygame.mouse.get_pressed()[0]:

                            # the cursor location is set to the letter where rect collison
                            # has been detected.
                            self.cursorLocation = letterRect[0]
                            self.cursorVisibility = True

                            tempMouseCollisions += 1

        # the line collision only works when the user if making collision beyond the end
        # of the line. When they click, the cursor location will move to the end of the line.
        for line in range(len(self.lineRects)):
            if self.lineRects[line].collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    if self.currentlyEditing:

                        # the tempMouseCollisions is equal to zero, if the user is not clicking
                        # any letters.
                        if tempMouseCollisions == 0:
                            self.cursorLocation = [line, len(str(self.textUnrendered[line]))]
                            self.cursorVisibility = True

        # the cursor mechanic can't simply use the time.sleep function as this will halt
        # to the loop causing there to be a lag every iteration of a half a second. We can
        # however use the time.time to track a progression in time every iteration.
        if self.cursorFlashIntervalCount == 0:
            self.cursorFlashIntervalCount = time.time()

            # essentially just means to invert the variable
            self.cursorVisibility = not self.cursorVisibility

        # another extension on the cursor flash mechanic
        if time.time() - self.cursorFlashIntervalCount > 0.5:
            self.cursorFlashIntervalCount = 0

        # will return True is the user wants to close the current instance of the process.
        # Simplest way to do this is to use the systems module and call a sys.exit method
        if self.closeRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                sys.exit()

        # when the user wants to check for a set of key words in the text, the
        # program collects all the words together and then proceeds to locate
        # each word and how many times is appears.
        if self.checkRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if self.checkButtonState:

                    # list of all the phrases to be searched
                    tempSearchPhrases = "".join(self.textUnrendered).split(",")[:-1]

                    tempFileTextUnrendered = []
                    tempHighlightedRegions = []

                    # this will go over every phrase and search for where the first letter
                    # in that phrase occurs. That is, where this words is found, the function
                    # will return a list of the location of the first letter.
                    for phrase in tempSearchPhrases:
                        tempFileTextUnrendered.append(phrase + "( " + str(len(self.findText(phrase))) + ") found,")

                        # since it only returns the first letter location we must calculate where
                        # the other letters are by using the length of the phrase.
                        for textLocation in self.findText(phrase):
                            for length in range(len(phrase)):
                                tempHighlightedRegions.append((textLocation[0], textLocation[1] + length))

                    # reset the cursor location. We reset it to 0, 0 as the rect boundaries
                    # are guaranteed to have a rect at this location and so no errors will occur.
                    self.cursorLocation = [0, 0]

                    # this will set the regions in the text editor to the regions to be highlighted.
                    self.textEditor.highlightingRegions = tempHighlightedRegions

                    if len(tempFileTextUnrendered) >= 1:
                        self.textUnrendered = list(tempFileTextUnrendered)
                    self.checkButtonState = False
            else:
                # means that the check button can only be pressed once until
                # the first mouse button is released.
                self.checkButtonState = True

        # when the user wants to clear the screen, it clears both the editor
        # and the control panel.
        if self.clearRect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:

                # the highlighted regions, the cursor location and the unrendered text
                # are all cleared with their default settings. Editor variables first.
                self.textEditor.highlightingRegions = []
                self.textEditor.cursorLocation = [0, 0]
                self.textEditor.textUnrendered = ["", "", ""]

                # then the control panel variables
                self.textUnrendered = ["", "", ""]
                self.cursorLocation = [0, 0]

        # this handles the complex events as they require monitoring to ensure
        # the user can hold down the buttons to activate them multiple times
        tempKeyPressedState = pygame.key.get_pressed()

        for event in range(len(tempKeyPressedState)):
            if event in list(self.eventToFunction.keys()):
                if tempKeyPressedState[event] and self.eventBufferPeriod[event] == 15:

                    # the event will be given the current unrendered text list and
                    # and the cursor location to do some analysis and then return a
                    # new cursor location and text list.
                    self.eventBufferPeriod[event] = 0

                    if self.currentlyEditing:
                        # all events are handled using the complex functions module that handles events deciding what
                        # to do for certain types of events like the return key or the backspace button.
                        if self.eventToFunction[event] not in [complexEvents.moveCursorDown, complexEvents.moveCursorUp]:
                            self.textUnrendered, self.cursorLocation = self.eventToFunction[event](
                                self.textUnrendered, self.cursorLocation)
                        else:
                            self.textUnrendered, self.cursorLocation = self.eventToFunction[event](
                                self.textUnrendered, self.cursorLocation, self.renderText)
                    self.cursorVisibility = True


                # the buffer period could not have ended and so will need to be increased
                # by 1 unit (arbitrary)
                elif tempKeyPressedState[event]:
                    self.eventBufferPeriod[event] += 1

                # otherwise it resets the buffer call by setting it to 15
                else:
                    self.eventBufferPeriod[event] = 15

        # the background colour for the buttons are all kept in an array which holds each
        # colour in an a certain order. We can compare a list of button rects to this list
        # to change the colours accordingly.
        tempButtonRects = [self.checkRect, self.clearRect, self.closeRect]

        for buttonRect in range(len(tempButtonRects)):
            if tempButtonRects[buttonRect].collidepoint(pygame.mouse.get_pos()):
                self.buttonBackgroundColours[buttonRect] = (180, 180, 180)
            else:
                self.buttonBackgroundColours[buttonRect] = self.borderColour

        # the cursor is blit at the cursor location (line, letter)
        self.blitCursor(tempLatestRects)

        # clear all the lists that update every iteration
        self.textRendered.clear()
        self.lineRects.clear()

        self.surfaceBlit()

    def checkEvent(self, event):
        # for some reason, pygame can't handle calling two or more pygame.event.get()
        # calls and so I have done it from one location but allow the checking for
        # each event to stem out into each class.
        if event.key >= 0 and event.key <= 127:
            if self.currentlyEditing:
                if event.key not in self.eventToFunction.keys():

                    # this isn't for the complex events but just appending text
                    # to the current cursor location.
                    tempKeysPressed = pygame.key.get_pressed()

                    if not tempKeysPressed[pygame.K_LCTRL]:
                        if not tempKeysPressed[pygame.K_RCTRL]:
                            if event.key != pygame.K_TAB:

                                # uses the complexEvent function to handle all the exceptions
                                # that come with appending text to the control panel
                                self.textUnrendered, self.cursorLocation = complexEvents.appendLetter(
                                            self.textUnrendered, self.cursorLocation, event.unicode)

                                self.cursorVisibility = True
                                return

                    # paste text occurs when the user is holding the control key
                    # and the v key. the v key is represented as \x16 in unicode
                    if event.unicode == "\x16":
                        self.textUnrendered, self.cursorLocation = complexEvents.pasteText(
                            self.textUnrendered, self.cursorLocation)

    def findText(self, text):
        # this function locates a word in the text and returns a list of all the locations
        # where this word was found. This is, where this word was found, a list containing
        # the first letter of this occurrence is returned.
        tempFoundLocations = []

        for line in range(len(self.textEditor.textUnrendered)):
            # This algorithm formulates a list containing all possible collection of letters
            # that could be the text the user is looking for.
            tempTextPermutations = ["".join([self.textEditor.textUnrendered[line][i + l] for l in range(len(text))])
                                   for i in range(len(self.textEditor.textUnrendered[line]) - len(text) + 1)]

            for permutation in range(len(tempTextPermutations)):
                if tempTextPermutations[permutation] == text:
                    tempFoundLocations.append((line, permutation))

        return tempFoundLocations

    def generateRects(self, text, margins=(5, 5)):
        # isn't placed as a common function as both editors have different offsets
        # and so it is just easier to deal with each one separately.
        tempRectBoundaries = []

        # use this "currentlocation" to follow the position of each letter as it is
        # rendered.
        currentLocation = [0, 0]

        for line in range(len(text)):
            tempLineBoundaries = []
            for letter in range(len(text[line])):

                # this is an example of how the render function can be used without
                # actually defining a colour but rather to judge text dimensions.
                renderedLetter = self.renderText(text[line][letter])

                # pygame rects can't be made relative to the surface location but rather
                # to the entire screen dimensions. They are somewhat difficult to make but
                # very useful in practice.
                rectBoundary = pygame.Rect(
                    (displayConstants.controlRect.x + margins[0] + currentLocation[0],
                     displayConstants.controlRect.y + margins[1] + currentLocation[1] +
                     35), (renderedLetter.get_width(), renderedLetter.get_height())
                )
                currentLocation[0] += renderedLetter.get_width()

                tempLineBoundaries.append(((line, letter), rectBoundary))
            currentLocation[0] = 0

            tempRectBoundaries.append(tempLineBoundaries)
            currentLocation[1] += self.lineHeight

        return tempRectBoundaries

    def blitText(self, text):
        # while bliting the text, we also generate line rects t allow the user to click
        # beyond the end of the line and move the cursor to the end of the line.

        for line in range(len(text)):
            renderedText = self.renderText(text[line], colour=(0, 0, 0))
            self.textRendered.append(renderedText)

            self.searchSurface.blit(renderedText, (5, 5 + (line * self.lineHeight)))

            # this rect allows the user to click "near" the end of the line to move the
            # cursor to that location.
            tempLineRect = pygame.Rect((displayConstants.controlRect.x + 5, displayConstants.controlRect.y
                                        + (line * self.lineHeight) + 5 + self.buttonSurface.get_height()
                                       ), (self.searchSurface.get_width(), self.lineHeight))
            self.lineRects.append(tempLineRect)

    def blitCursor(self, tempRects):
        # A cursor looks like it is between two letters but its actually assigned a letter and
        # then appears at the left side of the letters rect. This is not really the way I
        # should do it but this was one of the first features and everything was built around
        # this functionality.
        if self.cursorLocation != None:
            cursorRect = tempRects[self.cursorLocation[0]][self.cursorLocation[1]][1]

            if self.cursorVisibility == True:
                pygame.draw.rect(self.searchSurface, (0, 0, 0), [cursorRect.x - displayConstants.controlRect.x
                , cursorRect.y - 35 - displayConstants.controlRect.y, 2, cursorRect.height])


    def tertiarySurfaceUpdate(self):
        # this function generates the quaternary surfaces for the buttons. We dont generate
        # surfaces but simply draw rectangles to the screen.
        pygame.draw.rect(self.buttonSurface, self.buttonBackgroundColours[0], [5, 5,
                         self.buttonSurface.get_width() / 3 - 7.5, self.buttonSurface.get_height() - 10])

        pygame.draw.rect(self.buttonSurface, self.buttonBackgroundColours[1], [(self.buttonSurface.get_width() / 3) + 2.5, 5,
                        (self.buttonSurface.get_width() / 3) - 7.5, self.buttonSurface.get_height() - 10])

        pygame.draw.rect(self.buttonSurface, self.buttonBackgroundColours[2], [((2 * self.buttonSurface.get_width()) / 3) + 2.5, 5,
                        (self.buttonSurface.get_width() / 3) - 7.5, self.buttonSurface.get_height() - 10])

        # generate the rects for the surfaces to allow for mouse detection or at least make
        # it a much easier process.
        self.checkRect = pygame.Rect((displayConstants.controlRect.x + 5, displayConstants.controlRect.y + 5),
                                     ((self.buttonSurface.get_width() / 3) - 7.5, self.buttonSurface.get_height() - 10))

        self.clearRect = pygame.Rect((displayConstants.controlRect.x + (self.buttonSurface.get_width() / 3) + 2.5
                                     , displayConstants.controlRect.y + 5), ((self.buttonSurface.get_width() / 3) - 7.5,
                                     self.buttonSurface.get_height() - 10))

        self.closeRect = pygame.Rect((displayConstants.controlRect.x + ((2 * self.buttonSurface.get_width()) / 3) + 2.5,
                                     displayConstants.controlRect.y + 5), ((self.buttonSurface.get_width() / 3) - 7.5,
                                     self.buttonSurface.get_height() - 10))

        # each button has some text to tell the user what its function is
        self.checkTextSurface = self.renderText("check", colour=(255, 255, 255))
        self.clearTextSurface = self.renderText("clear", colour=(255, 255, 255))
        self.closeTextSurface = self.renderText("close", colour=(255, 255, 255))

        # te centre function will take an object and blit it to the centre
        # of a rect making the process much easier.
        surfaceManipulation.centreControl(self.buttonSurface, self.checkRect, self.checkTextSurface, displayConstants.controlRect)
        surfaceManipulation.centreControl(self.buttonSurface, self.clearRect, self.clearTextSurface, displayConstants.controlRect)
        surfaceManipulation.centreControl(self.buttonSurface, self.closeRect, self.closeTextSurface, displayConstants.controlRect)

    def surfaceUpdate(self):
        # the surfaces are "refreshed" every iteration to ensure all text is up to dat
        # with the latest unrendered text array.
        self.searchSurface = pygame.Surface((
            displayConstants.controlRect.width,
            displayConstants.controlRect.height - 35
        ))

        self.buttonSurface = pygame.Surface((
            displayConstants.controlRect.width, 35
        ))

        # the surfaces are "cleared" by making every pixel white.
        self.searchSurface.fill((255, 255, 255))
        self.buttonSurface.fill((255, 255, 255))

        # every surface has a border drawn on it to distinguish between them
        surfaceManipulation.drawBorder(self.searchSurface, self.borderColour)
        surfaceManipulation.drawBorder(self.buttonSurface, self.borderColour)

    def surfaceBlit(self):
        # the tertiary surfaces are blit onto the secondary surfaces and the
        # secondary surfaces are blit onto the primary surfaces.
        displayConstants.controlSurface.blit(self.searchSurface, (0, 35))
        displayConstants.controlSurface.blit(self.buttonSurface, (0, 0))

    def renderText(self, text, colour=(0, 0, 0)):
        # the colour argument is not compulsory as the text
        # isn't always blit to the screen but used to judge
        # dimensions of line width, for example.
        return self.controlPanelFont.render(text, 1, colour)