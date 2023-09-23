"""
===========
TextEditor
===========

This is the TextEditor class used to display the text editor on the screen.
It contains all the functionality for handling keys with specific text manipulation
functions. It is dependant on the default time module, the default tkinter module,
displayConstants found locally as "displayConstants.py", the pygame module
found at http://pygame.org/, the surface manipulation module found locally at
"surfaceManipulation.py" and the complex events module found at "complexEvents.py".

This file is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import displayConstants
import surfaceManipulation
import complexEvents

import tkinter
import pygame
import time


class textEditor(object):
    def __init__(self, borderColour=(224, 224, 224), fontType="agencyfb", fontSize=22):
        # Use default system fonts. Pygame doesn't always seem to find font files in relative
        # directory so its best to stay with fonts on windows
        self.editorFont = pygame.font.SysFont(fontType, fontSize)

        self.lineNumberSurfaceWidth = 30
        self.borderColour = borderColour
        self.currentlyEditing = False

        # the program doesn't allow you to add text to an empty editor so
        # there must be some sort of
        self.textUnrendered = ["***", "TextEditor", "***"]
        self.textRendered = [] #--> as type pygame.Surface

        # create a collision box around each letter for both highlighting and
        # mouse detection as type pygame.Rect
        self.textRects = []
        self.lineRects = []

        # one of the heighest letters in terms of pixels is a capital M so
        # this will be the line width
        self.lineHeight = self.renderText("M").get_height()

        # cursor location as type list to make line and letter manipulation much
        # quicker without any redefining of tuples
        self.cursorLocation = [0, 0]

        self.cursorVisibility = False

        # will count up to 0.5 seconds and then return to 0 to simulate a flash
        self.cursorFlashInterval = 0

        # each slidebar has an offset which the user can change to alter the position
        # of the text and rect boundaries.
        self.verticalSlidebarOffset = 0
        self.horizontalSlidebarOffset = 0

        # the background colours will change depending on whether the user to hovering
        # the mouse over the button.
        self.buttonBackgroundColours = [self.borderColour for button in range(4)]

        # used to track the time between event calls for all 330 events tracked
        # by pygame
        self.eventBufferPeriod = [0 for event in range(330)]

        # a region for highlighting is represented as a tuple
        # --> (lineNumber, letterNumber)
        self.highlightingRegions = []

        # the functions that correspond to the complex events eg the return key
        # or the backspace as apposed to the "a" key or "r" key.
        self.complexEventToFunction = {
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

        self.surfaceReset()

        # blit the line numbers to the line number surface and re-calculate line
        # number layer width taking into account any unrendered text updates.
        self.renewLineWidth(len(self.textUnrendered))
        self.lineNumberBlit()

        # the rects are generated every iteration as they change when ever an event
        # function is called or the vertical and horizontal arrouws are changed
        tempLatestRects = self.generateRects(tempTextUnrendered)

        # blit text and generate line rects for eas of detection
        self.blitText(self.textUnrendered)

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
        if self.cursorFlashInterval == 0:
            self.cursorFlashInterval = time.time()

            # essentially just means to invert the variable
            self.cursorVisibility = not self.cursorVisibility

        # blit the cursor to the left side of the rect assigned to it
        self.blitCursor(tempLatestRects)

        # another extension on the cursor flash mechanic
        if time.time() - self.cursorFlashInterval > 0.5:
            self.cursorFlashInterval = 0

        # the user is only allowed to interact with the editor if the mouse is inside the
        # editing box and has has clicked at least once. Otherwise, currently editing is
        # equal to false. If the user moves out of the editing box and clicks, they are
        # no longer editing.
        if pygame.mouse.get_pressed()[0]:
            if displayConstants.editorRect.collidepoint(pygame.mouse.get_pos()):
                self.currentlyEditing = True
            else:
                # the cursor location is also set to None so it isn't visible unless the
                # user is editing.
                self.currentlyEditing = False
                self.cursorLocation = None

        # all events ae handled by the complexEvents module which has some functions I
        # created for handling events like the enter key or the backspace key.
        tempKeyPressedState = pygame.key.get_pressed()

        for event in range(len(tempKeyPressedState)):
            if event in list(self.complexEventToFunction.keys()):
                if tempKeyPressedState[event] and self.eventBufferPeriod[event] == 15:

                    # the event will be given the current unrendered text list and
                    # and the cursor location to do some analysis and then return a
                    # new cursor location and text list.
                    self.eventBufferPeriod[event] = 0

                    if self.currentlyEditing:
                        if self.complexEventToFunction[event] not in [complexEvents.moveCursorDown, complexEvents.moveCursorUp]:
                            self.textUnrendered, self.cursorLocation = self.complexEventToFunction[event](
                                self.textUnrendered, self.cursorLocation)
                        else:
                            self.textUnrendered, self.cursorLocation = self.complexEventToFunction[event](
                                self.textUnrendered, self.cursorLocation, self.renderText)
                    self.cursorVisibility = True

                # the buffer period could not have ended and so will need to be increased
                # by 1 unit (arbitrary)
                elif tempKeyPressedState[event]:
                    self.eventBufferPeriod[event] += 1

                # otherwise it resets the buffer call by setting it to 15
                else:
                    self.eventBufferPeriod[event] = 15

        # we firstly generate the buttons and then detect any mouse collision
        self.surfaceButtons()

        # each button affects one of the slidebar offsets. the first button is the
        # left button which will affect the horizontal slidebar value.
        if self.moveLeftRect.collidepoint(pygame.mouse.get_pos()):

            if pygame.mouse.get_pressed()[0]:
                if self.horizontalSlidebarOffset < 0:
                    self.horizontalSlidebarOffset += 4
                else:
                    # the slidebar offset has it's restrictions to ensure the user
                    # can't break any important mechanics.
                    self.horizontalSlidebarOffset = 0

        # the right button will also affect the horizontal slidebar value
        if self.moveRightRect.collidepoint(pygame.mouse.get_pos()):

            if pygame.mouse.get_pressed()[0]:
                # we firstly find the line with the greatest width to
                # figure out how far the text can slide before the
                #restrictions apply.
                tempGreatestLineWidth = 0
                for line in self.textRendered:
                    if line.get_width() > tempGreatestLineWidth:
                        tempGreatestLineWidth = line.get_width()

                # 50 is set as the buffer which means that there is an extension on
                # the slidebar restrictions. This is more visible in the actually
                # execution of the program.
                tempGreatestLineWidth -= 50

                if tempGreatestLineWidth + 50 > self.textEditingSurface.get_width() * 0.5:
                    if self.horizontalSlidebarOffset > -tempGreatestLineWidth:
                        self.horizontalSlidebarOffset -= 4
                    else:
                        self.horizontalSlidebarOffset = -tempGreatestLineWidth

        # the up button will affect the vertical slidebar offset
        if self.moveUpRect.collidepoint(pygame.mouse.get_pos()):

            if pygame.mouse.get_pressed()[0]:
                if self.verticalSlidebarOffset < 0:
                    self.verticalSlidebarOffset += 4
                else:
                    # if the user decides to try and go beyond the boundaries
                    # restrictions are "enforced" to return the offset back
                    # within the boundaries
                    self.verticalSlidebarOffset = 0

        # the down button also affects the vertical slidebar offset
        if self.moveDownRect.collidepoint(pygame.mouse.get_pos()):

            if pygame.mouse.get_pressed()[0]:
                # this what the slidebar uses to judge the length of the text
                # and as such set the restrictions on the sliding functionality.
                tempTextWidth = -(self.lineHeight * (len(self.textUnrendered) - 5))

                if self.verticalSlidebarOffset > tempTextWidth:
                    self.verticalSlidebarOffset -= 4
                else:
                    # these is a limit of 5 lines before any changes can be
                    # made to the offset value.
                    if len(self.textUnrendered) > 5:
                        self.verticalSlidebarOffset = tempTextWidth + 1

        # the background colour for the buttons are all kept in an array which holds each
        # colour in an a certain order. We can compare a list of button rects to this list
        # to change the colours accordingly.
        tempButtonRects = [self.moveUpRect, self.moveRightRect, self.moveDownRect, self.moveLeftRect]

        for buttonRect in range(len(tempButtonRects)):
            if tempButtonRects[buttonRect].collidepoint(pygame.mouse.get_pos()):
                self.buttonBackgroundColours[buttonRect] = (180, 180, 180)
            else:
                self.buttonBackgroundColours[buttonRect] = self.borderColour

        # we then blit these updated buttons to the screen
        self.surfaceButtons()
        self.buttonBlit()

        # the rects list and the rendered text list are calculated each iteration
        # so they must be cleared at the end of the iteration for another cycle.
        self.textRendered.clear()
        self.lineRects.clear()

        self.surfaceBlit()


    def checkEvent(self, event):
        # for some reason, pygame can't handle calling two or more pygame.event.get()
        # calls and so I have done it from one location but allow the checking for
        # each event to stem out into each class.
        if event.key >= 0 and event.key <= 127:
            if self.currentlyEditing:
                if event.key not in self.complexEventToFunction.keys():

                    # this isn't for the complex events but just appending text
                    # to the current cursor location.
                    tempKeysPressed = pygame.key.get_pressed()

                    if not tempKeysPressed[pygame.K_LCTRL]:
                        if not tempKeysPressed[pygame.K_RCTRL]:
                            if event.key != pygame.K_TAB:

                                # uses the complexEvent function to handle all the exceptions
                                # that come with appending text to the text editor
                                self.textUnrendered, self.cursorLocation = complexEvents.appendLetter(
                                            self.textUnrendered, self.cursorLocation, event.unicode)

                                self.cursorVisibility = True
                                return

                    # paste text occurs when the user is holding the control key
                    # and the v key. the v key is represented as \x16 in unicode
                    if event.unicode == "\x16":
                        self.textUnrendered, self.cursorLocation = complexEvents.pasteText(
                            self.textUnrendered, self.cursorLocation)


    def surfaceButtons(self):
        # there are four buttons on the surface that need to be generated all with
        # their individual rects.
        self.moveUpSurface = pygame.Surface((30, 30))
        self.moveDownSurface = pygame.Surface((30, 30))
        self.moveLeftSurface = pygame.Surface((30, 30))
        self.moveRightSurface = pygame.Surface((30, 30))

        # we now clear these surfaces
        self.moveUpSurface.fill(self.buttonBackgroundColours[0])
        self.moveDownSurface.fill(self.buttonBackgroundColours[2])
        self.moveLeftSurface.fill(self.buttonBackgroundColours[3])
        self.moveRightSurface.fill(self.buttonBackgroundColours[1])

        # these are the rects for the surfaces
        self.moveUpRect = pygame.Rect((self.lineNumberSurface.get_width() + self.textEditingSurface.get_width() +
                                        displayConstants.editorRect.x, displayConstants.editorRect.y), (30, 30))

        self.moveDownRect = pygame.Rect((self.lineNumberSurface.get_width() + self.textEditingSurface.get_width() +
                                        displayConstants.editorRect.x, displayConstants.editorRect.y +
                                        self.verticalSlidebarSurface.get_height() - 30), (30, 30))

        self.moveRightRect = pygame.Rect((displayConstants.editorRect.x + self.lineNumberSurface.get_width() +
                                        self.textEditingSurface.get_width() - 30, displayConstants.editorRect.y
                                        + self.lineNumberSurface.get_height()), (30, 30))

        self.moveLeftRect = pygame.Rect((displayConstants.editorRect.x, displayConstants.editorRect.y +
                                        self.lineNumberSurface.get_height()), (30, 30))

        # we now draw the arrow shapes on each of the surfaces
        pygame.draw.line(self.moveLeftSurface, (255, 255, 255), (5, 15), (25, 5), 2)
        pygame.draw.line(self.moveLeftSurface, (255, 255, 255), (5, 15), (25, 25), 2)

        pygame.draw.line(self.moveRightSurface, (255, 255, 255), (5, 5), (25, 15), 2)
        pygame.draw.line(self.moveRightSurface, (255, 255, 255), (5, 25), (25, 15), 2)

        pygame.draw.line(self.moveUpSurface, (255, 255, 255), (15, 5), (5, 25), 2)
        pygame.draw.line(self.moveUpSurface, (255, 255, 255), (15, 5), (25, 25), 2)

        pygame.draw.line(self.moveDownSurface, (255, 255, 255), (15, 25), (5, 5), 2)
        pygame.draw.line(self.moveDownSurface, (255, 255, 255), (15, 25), (25, 5), 2)


    def buttonBlit(self):
        # each of the four buttons is placed on the vertical and horizontal slidebar layers.
        self.verticalSlidebarSurface.blit(self.moveUpSurface, (0, 0))
        self.horizontalSlidebarSurface.blit(self.moveLeftSurface, (0, 0))
        self.verticalSlidebarSurface.blit(self.moveDownSurface, (0, self.verticalSlidebarSurface.get_height() - 30))
        self.horizontalSlidebarSurface.blit(self.moveRightSurface, (self.horizontalSlidebarSurface.get_width() - 30, 0))


    def blitCursor(self, tempRects):
        # A cursor looks like it is between two letters but its actually assigned a letter and
        # then appears at the left side of the letters rect. This is not really the way I
        # should do it but this was one of the first features and everything was built around
        # this functionality.
        if self.cursorLocation != None:
            cursorRect = tempRects[self.cursorLocation[0]][self.cursorLocation[1]][1]

            if self.cursorVisibility == True:
                pygame.draw.rect(self.textEditingSurface, (0, 0, 0), [cursorRect.x - displayConstants.editorRect.x
                - self.lineHeight, cursorRect.y - displayConstants.editorRect.y, 2, cursorRect.height])


    def blitText(self, text):
        # while bliting the text, we also generate line rects t allow the user to click
        # beyond the end of the line and move the cursor to the end of the line.

        for line in range(len(text)):
            renderedText = self.renderTextSeperation(text[line], line, textColour=(0, 0, 0))

            # decreased the lag on the screen by only bliting what is seen
            self.textEditingSurface.blit(renderedText[0], (5 + self.horizontalSlidebarOffset, 5 +
                                        (line * self.lineHeight) + self.verticalSlidebarOffset))

            # this rect allows the user to click "near" the end of the line to move the
            # cursor to that location.
            tempLineRect = pygame.Rect((displayConstants.editorRect.x + 5 + self.horizontalSlidebarOffset, displayConstants.editorRect.y
                                        + (line * self.lineHeight) + self.verticalSlidebarOffset), (self.textEditingSurface.get_width(),
                                        self.lineHeight))
            self.lineRects.append(tempLineRect)


    def renderTextSeperation(self, text, index, textColour=(0, 0, 0)):
        # This function renders text by rendering each letter and then
        # placing each letter on a surface with a space  between each letter.
        tempCurrentHorizontalLocation = 0
        tempRenderedLetters  = []

        for letter in range(len(text)):
            tempRenderedLetter = self.renderText(text[letter], colour=textColour)
            tempSepLetterSurface = pygame.Surface((tempRenderedLetter.get_width(),
                                                   tempRenderedLetter.get_height()))

            # if the editor has registered the current letter as a highlighting region,
            # the background will be changed to a red colour otherwise it will change to
            # a default white.
            if (index, letter) in self.highlightingRegions:
                tempSepLetterSurface.fill((255, 0, 0))
            else:
                tempSepLetterSurface.fill((255, 255, 255))

            # the rendered letter is blit onto a surface with dimensions equal to that
            # of the letter and a colour to signify whether it is a highlighting region or
            # not.
            tempSepLetterSurface.blit(tempRenderedLetter, (0, 0))
            tempRenderedLetters.append(((tempCurrentHorizontalLocation, 0), tempSepLetterSurface))

            tempCurrentHorizontalLocation += tempRenderedLetter.get_width()

        # the tempCurrentHorizontalLocation changes every iteration y adding the width of the
        # previous letter. It is used as the end surface dimension as the length of the line.
        tempLetterSurface = pygame.Surface((tempCurrentHorizontalLocation, self.lineHeight))

        # blit each of the letters to the surface with their individual spacing
        for renderedLetter in tempRenderedLetters:
            tempLetterSurface.blit(renderedLetter[1], renderedLetter[0])

        return tempLetterSurface, tempRenderedLetters


    def renewLineWidth(self, number):
        # calculates a new line width based on the length of the unrendered text
        # list. May be smaller then the current length but doesn't really make a
        # difference.
        tempNewLineWidth = self.renderText(str(number)).get_width()

        if tempNewLineWidth + (5 * 3) > 30:
            self.lineNumberSurfaceWidth = tempNewLineWidth + (5 * 3)


    def lineNumberBlit(self):
        # no need to pre-render line numbers as its obvious what
        # text will be rendered.

        for number in range(len(self.textUnrendered)):
            renderedNumber = self.renderText(str(number), colour=(215, 215, 215))

            self.lineNumberSurface.blit(renderedNumber, (self.lineNumberSurfaceWidth - renderedNumber.get_width() - 5,
                                                         (self.lineHeight * number) + 5 + self.verticalSlidebarOffset))


    def surfaceReset(self):
        # for surfaces like the line number surface, the surface will need to
        # be redefined in accordance with the width of the largest number

        self.verticalSlidebarSurface = pygame.Surface ((
            30, displayConstants.editorRect.height - 30
        ))

        self.textEditingSurface = pygame.Surface((
            displayConstants.editorRect.width - self.lineNumberSurfaceWidth - 30,
            displayConstants.editorRect.height - 30
        ))

        self.lineNumberSurface = pygame.Surface((
            self.lineNumberSurfaceWidth,
            displayConstants.editorRect.height - 30
        ))

        self.horizontalSlidebarSurface = pygame.Surface((
            self.lineNumberSurfaceWidth + self.textEditingSurface.get_width(),
            30
        ))

        # the surfaces are "clear" by filling all the pixels with white to
        # and then placing all other updated aspects on the surface

        self.verticalSlidebarSurface.fill((255, 255, 255))
        self.textEditingSurface.fill((255, 255, 255))
        self.lineNumberSurface.fill((255, 255, 255))
        self.horizontalSlidebarSurface.fill((255, 255, 255))

        # all surfaces have borders drawn on them to distinguish them from one
        # one another.

        surfaceManipulation.drawBorder(self.verticalSlidebarSurface, self.borderColour)
        surfaceManipulation.drawBorder(self.textEditingSurface, self.borderColour)
        surfaceManipulation.drawBorder(self.lineNumberSurface, self.borderColour)
        surfaceManipulation.drawBorder(self.horizontalSlidebarSurface, self.borderColour)


    def surfaceBlit(self):
        # blits the surfaces to the editor surface after all updating has been
        # done in the loop to decrease rendering time for the aspects.

        displayConstants.editorSurface.blit(self.lineNumberSurface, (0, 0))
        displayConstants.editorSurface.blit(self.textEditingSurface, (self.lineNumberSurface.get_width(), 0))
        displayConstants.editorSurface.blit(self.verticalSlidebarSurface, (self.lineNumberSurface.get_width() + self.textEditingSurface.get_width(), 0))
        displayConstants.editorSurface.blit(self.horizontalSlidebarSurface, (0, self.lineNumberSurface.get_height()))


    def renderText(self, text, colour=(0, 0, 0)):
        # the colour argument is not compulsory as the text
        # isn't always blit to the screen but used to judge
        # dimensions of line width, for example.

        return self.editorFont.render(text, 1, colour)


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
                    (displayConstants.editorRect.x + self.lineHeight +
                    margins[0] + currentLocation[0] + self.horizontalSlidebarOffset,
                    displayConstants.editorRect.y + margins[1] + currentLocation[1] + self.verticalSlidebarOffset),
                    (renderedLetter.get_width(), renderedLetter.get_height())
                )
                currentLocation[0] += renderedLetter.get_width()

                tempLineBoundaries.append(((line, letter), rectBoundary))
            currentLocation[0] = 0

            tempRectBoundaries.append(tempLineBoundaries)
            currentLocation[1] += self.lineHeight

        return tempRectBoundaries




