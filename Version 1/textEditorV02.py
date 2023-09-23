#import the constants and necessary function
from displayConstants import *

#import the GUI module and time module
import pygame
import time

#module used for the clipboard get
from tkinter import Tk


#establish the textEditor class
class textEditor(object):
    def __init__(self, borderColour=(224, 224, 224), fontType="agencyfb", fontSize=22):
        #The font used to render the text onto the screen
        self.font = pygame.font.SysFont(fontType, fontSize)

        #all rendered text uses the above font
        self.unrenderedText = ["if it works with multiple lines and letters", "testing the delete function"] #--> store the unrendered text
        self.renderedText = [] #--> store the rendered text
        self.TextRects = [] #--> store the collision boxes for each letter

        #colour of the border and other editor styles
        self.borderColour = borderColour
        self.textColour = (0, 0, 0)

        #split the layer into two sub-layers to make things easier
        self.numberedLayerWidth = 50

        #height spacing between the lines. Must remain the same for line numbers and text
        self.lineSpacing = self.renderText("M").get_height()

        #True when the user is editing
        self.currentlyEditing = False

        #the current location of the mouse cursor
        self.cursorLocation = None

        #the colour of the cursor and width
        self.cursorColour = (0, 0, 0)
        self.cursorWidth = 2

        self.cursorTimerState = 0
        self.cursonVisability = True

        #slide bar
        self.slidebarHeight = 100
        self.slidebarSpaceHeight = textDisplayLayer.get_height() - 8

        self.slideMaxLines = self.slidebarSpaceHeight / self.lineSpacing

        self.pause = 0

    #display the text editor at displayConstants.textDisplayCoordinate
    def updateText(self):
        #check for keyboard events
        for event in pygame.event.get(): #iterate over the current events

            if event.type == pygame.KEYDOWN: #check for keyboard event
                #enter key pressed
                if event.key == pygame.K_RETURN:
                    if self.currentlyEditing: #if in the editing box
                        self.returnLine() #new line for split text

                #the up key is pressed
                elif event.key == pygame.K_UP:
                    if self.currentlyEditing: #if in the editing box
                        self.moveCursor(0) #move mouse cursor up by 1 line

                #the right key is pressed
                elif event.key == pygame.K_RIGHT:
                    if self.currentlyEditing: #if in the editing box
                        self.moveCursor(1) #move the cursor to the right by 1

                #the down key is pressed
                elif event.key == pygame.K_DOWN:
                    if self.currentlyEditing:
                        self.moveCursor(2)

                #the right key pressed
                elif event.key == pygame.K_LEFT:
                    if self.currentlyEditing:
                        self.moveCursor(3)

                elif event.key == pygame.K_DELETE:
                    if self.currentlyEditing:
                        self.secondaryDelete()

                else:
                    if self.currentlyEditing:
                        if event.key >= pygame.K_SPACE and event.key <= 126:
                            self.addLetter(event.unicode)

        pressed = pygame.key.get_pressed()
        if self.pause == 3 and pressed[pygame.K_BACKSPACE]:
            self.pause = 0
            self.deleteLetter()
        elif pressed[pygame.K_BACKSPACE]:
            self.pause += 1
        else:
            self.pause = 0

        #local copy of the unrenderedText attribute
        unrenderedText = [line + " " for line in list(self.unrenderedText)]

        #must generate surface every iteration to keep the width dynamic
        self.textDisplayLayer = pygame.Surface(( #--will change depending on the self.numbered Layer
            textDisplayLayer.get_width() - self.numberedLayerWidth, textDisplayLayer.get_height()
        ))

        self.numberedLayer = pygame.Surface((self.numberedLayerWidth,
        textDisplayLayer.get_height())) #--> the width will remain dynamic

        #empty the layer (clear)
        self.numberedLayer.fill((255, 255, 255))

        #empty or clear the layer
        self.textDisplayLayer.fill((255, 255, 255))

        #draw a border around the line numbers
        pygame.draw.rect(self.numberedLayer, self.borderColour, [
            1, 1, #top right corner of the layer
            self.numberedLayer.get_width() - 1, self.numberedLayer.get_height() #--> bottom right hand corner
        ], 2)

        #render all the unrendered lines in the list
        for unrenderedline in unrenderedText:
            renderedText = self.renderText(unrenderedline, colour=self.textColour)

            #add these lines to the rendered
            self.renderedText.append(renderedText)

        #blit the text to the screen
        self.blitText(self.renderedText, margins=(10, 5))

        #blit the line numbers to the screen
        self.blitLineNumbers(len(self.renderedText),margin=5)

        #generate the rects for the given text
        latestTextRects = self.generateRects(unrenderedText, margins=(10, 5))

        #check whether the user is clicking on the letters
        if self.currentlyEditing:
            for rectX in latestTextRects:
                for rect in rectX:
                    #check the user is hovering over the letter
                    if rect[1].collidepoint(pygame.mouse.get_pos()):
                        #check the mouse button is pressed
                        if pygame.mouse.get_pressed()[0]:
                            self.cursorLocation = rect[0]
                            self.cursonVisability = True

        #reset the timeRegister
        if self.cursorTimerState == 0:
            self.cursorTimerState = time.time()
            self.cursonVisability = not self.cursonVisability

        #blit the cursor to the screen
        if self.cursorLocation != None:
            cursorRect = latestTextRects[self.cursorLocation[0]][self.cursorLocation[1]][1]

            #only when cursor visablility is true
            if self.cursonVisability == True:
                #draw over the top of all text
                pygame.draw.rect(self.textDisplayLayer, self.cursorColour, [cursorRect.x - textDisplayCoordinate[0] - self.numberedLayerWidth,
                            cursorRect.y - textDisplayCoordinate[1], self.cursorWidth, cursorRect.height])

        #update the time register
        if time.time() - self.cursorTimerState > 0.5:
            self.cursorTimerState = 0

        #blit the surfaces
        textDisplayLayer.blit(self.numberedLayer, (0, 0))
        textDisplayLayer.blit(self.textDisplayLayer, (self.numberedLayerWidth, 0))

        #draw the sldiebar
        if self.slideMaxLines != 0:
            self.slidebarHeight = self.slidebarSpaceHeight / (len(self.unrenderedText)/ (self.slideMaxLines - 2))

        slidebarLayer = pygame.Surface((30, textDisplayLayer.get_height() - 8))
        slidebarRect = pygame.Rect(((textDisplayLayer.get_width() - 30, 8)), ((30, textDisplayLayer.get_height() - 8)))
        slidebarLayer.fill((255, 255, 255))

        if self.slidebarHeight < slidebarLayer.get_height():
            pygame.draw.rect(slidebarLayer, (200, 200, 200), [10, 8, 10, self.slidebarHeight], 1)

        if slidebarRect.collidepoint(pygame.mouse.get_pos()):

        textDisplayLayer.blit(slidebarLayer, (textDisplayLayer.get_width() - 30, 8))
        pygame.draw.line(textDisplayLayer, self.borderColour, (textDisplayLayer.get_width() - 30, 0),
                         (textDisplayLayer.get_width() - 30, textDisplayLayer.get_height()), 2)

        #draw lines above and below the editor for asthetics
        pygame.draw.rect(textDisplayLayer, self.borderColour, [0, 0,
                          textDisplayLayer.get_width(), textDisplayLayer.get_height()], 4)

        #draw the border on textDisplayLayer with colour self.borderColour
        pygame.draw.rect(textDisplayLayer, self.borderColour, [
            1, 1, #--> top left hand corner of the layer
            textDisplayLayer.get_width() - 1, textDisplayLayer.get_height() - 1 #--> bottom right hand corner
        ], 2)

        #detect whether the user is editing
        if pygame.mouse.get_pressed()[0]: #--> left mouse pressed
            if textDisplayRect.collidepoint(pygame.mouse.get_pos()): #--> mouse within the text editor boundaries
                self.currentlyEditing = True #--> editing the text
            else:
                self.currentlyEditing = False #--> elsewhere
                self.cursorLocation = None #--> prevent cursor viability

        #clear the renderedText for re-analysis
        self.renderedText.clear()


    #blit line numbers to the screen
    def blitLineNumbers(self, quantity, margin=5):
        #update the line number layer width
        newLineWidth = self.renderText(str(quantity)).get_width()

        #make the line margins aesthetically pleasing
        if newLineWidth + (margin * 3) > 20: #--> minimum margin width of 20
            self.numberedLayerWidth = newLineWidth + (margin * 3)

        #blit the line numbers to the screen
        for number in range(quantity):
            renderedNumber = self.renderText(str(number), colour=(215, 215, 215))

            #align to the left and use default line spacing defined above
            self.numberedLayer.blit(renderedNumber, (self.numberedLayerWidth - renderedNumber.get_width() - margin,
                                                     (self.lineSpacing * number) + margin))


    #blit the text the the screen
    def blitText(self, text, margins=(5, 5)):
        for renderedline in range(len(text)):
            #blit them to the screen using their index
            self.textDisplayLayer.blit(text[renderedline], (margins[0],
            margins[1] + (renderedline*self.lineSpacing)))


    #create a list of collision rects over text
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
                    (textDisplayCoordinate[0] + self.numberedLayerWidth + margins[0] + currentLocation[0],
                     textDisplayCoordinate[1] + margins[1] + currentLocation[1]),
                    (renderedLetter.get_width(), renderedLetter.get_height())
                )
                currentLocation[0] += renderedLetter.get_width()

                #update the line boundaries
                lineBoundaries.append(([line, letter], rectBoundary))

            currentLocation[0] = 0

            #append the letter rect ro the line rect
            rectBoundaries.append(lineBoundaries)
            currentLocation[1] += self.lineSpacing

        #return the final rect
        return rectBoundaries


    #delete the current letter on the cursor
    def deleteLetter(self):
        #if the cursor isnt in the top left corner most letter
        if self.cursorLocation != (0, 0):
            #at the beginning of the line ( > line 1)
            if self.cursorLocation[0] != 0:
                if self.cursorLocation[1] == 0:
                    #move the text from one line to another
                    self.cursorLocation = (self.cursorLocation[0], len(self.unrenderedText[self.cursorLocation[0] - 1]))
                    self.unrenderedText[self.cursorLocation[0] - 1] += self.unrenderedText[self.cursorLocation[0]]

                    #delete the current line
                    del self.unrenderedText[self.cursorLocation[0]]

                    #change the current cursor location reference
                    self.cursorLocation = (self.cursorLocation[0] - 1, self.cursorLocation[1])

                    #end function call
                    return

            #expand the unrendered text to delete single letters
            unrenderedChars = [[character for character in line] for line in self.unrenderedText] #--> expand the line elements

            #delete the letter at new cursor location
            del unrenderedChars[self.cursorLocation[0]][self.cursorLocation[1] - 1]

            #update the cursor location and unrendered text
            self.cursorLocation = (self.cursorLocation[0], self.cursorLocation[1] - 1)
            self.unrenderedText = ["".join(line) for line in unrenderedChars]


    #simulate the delete button not the bachspace button
    def secondaryDelete(self):
        if self.cursorLocation[1] == len(self.unrenderedText[self.cursorLocation[0]]):
            if self.cursorLocation[0] != len(self.unrenderedText) - 1:
                self.unrenderedText[self.cursorLocation[0]] += self.unrenderedText[self.cursorLocation[0] + 1]
                del self.unrenderedText[self.cursorLocation[0] + 1]
        else:
            unrenderedChars = [char for char in self.unrenderedText[self.cursorLocation[0]]]
            del unrenderedChars[self.cursorLocation[1]]
            self.unrenderedText[self.cursorLocation[0]] = "".join(unrenderedChars)


    #move the line to the next
    def returnLine(self):
        #enter occures at the beginning of the line
        if self.cursorLocation[1] == 0:
            #insert new line and cleae the old one
            self.unrenderedText.insert(self.cursorLocation[0] + 1, self.unrenderedText[self.cursorLocation[0]])
            self.unrenderedText[self.cursorLocation[0]] = ""

        #enter occures at the end of the line
        elif self.cursorLocation[1] == len(self.unrenderedText[self.cursorLocation[0]]):
            #create a new line
            self.unrenderedText.insert(self.cursorLocation[0] + 1, "")

        #anywhere in the middle of the line
        else:
            #split the text at the cursor location
            splitText = self.unrenderedText[self.cursorLocation[0]][self.cursorLocation[1]:]

            #insert the end portion of the split text on a new line and leave the rest on the current line
            self.unrenderedText.insert(self.cursorLocation[0] + 1, splitText)
            self.unrenderedText[self.cursorLocation[0]] = self.unrenderedText[self.cursorLocation[0]][:
            len(self.unrenderedText[self.cursorLocation[0]]) - len(splitText)]

        #set the cursor location to the next line
        self.cursorLocation = [self.cursorLocation[0] + 1, 0]


    #move the cursor in the given direction
    def moveCursor(self, direction):
        self.cursonVisability = True
        if direction == 0:
            if self.cursorLocation[0] != 0:
                if self.renderText(self.unrenderedText[self.cursorLocation[0]][:self.cursorLocation[1]]).get_width() >\
                        self.renderText(self.unrenderedText[self.cursorLocation[0] - 1]).get_width():
                    self.cursorLocation = (self.cursorLocation[0] - 1,
                    len(self.unrenderedText[self.cursorLocation[0] - 1]))
                else:self.cursorLocation = (self.cursorLocation[0] - 1, 0)

        if direction == 1:
            if self.cursorLocation[1] == len(self.unrenderedText[self.cursorLocation[0]]):
                if self.cursorLocation[0] != len(self.unrenderedText) - 1:
                    self.cursorLocation = (self.cursorLocation[0] + 1, 0)
            else:
                self.cursorLocation = (self.cursorLocation[0], self.cursorLocation[1] + 1)

        if direction == 2:
            if self.cursorLocation[0] != len(self.unrenderedText) - 1:
                if self.renderText(self.unrenderedText[self.cursorLocation[0]][:self.cursorLocation[1]]).get_width() >\
                        self.renderText(self.unrenderedText[self.cursorLocation[0] + 1]).get_width():
                    self.cursorLocation = (self.cursorLocation[0] + 1,
                    len(self.unrenderedText[self.cursorLocation[0] + 1]))
                else:self.cursorLocation = (self.cursorLocation[0] + 1, 0)

        if direction == 3:
            if self.cursorLocation[1] == 0:
                if self.cursorLocation[0] != 0:
                    self.cursorLocation = (self.cursorLocation[0] - 1, len(self.unrenderedText[self.cursorLocation[0] - 1]))
            else:
                self.cursorLocation = (self.cursorLocation[0], self.cursorLocation[1] - 1)


    #add a letter to the current cursor location
    def addLetter(self, letter):
        unrenderedChars = [letter for letter in self.unrenderedText[self.cursorLocation[0]]]

        if self.cursorLocation[1] != 0:
            unrenderedChars.insert(self.cursorLocation[1], letter)
        else:
            unrenderedChars.insert(0, letter)

        self.cursorLocation = (self.cursorLocation[0], self.cursorLocation[1] + 1)
        self.unrenderedText[self.cursorLocation[0]] = "".join(unrenderedChars)

    #render the passed text with the given colour
    def renderText(self, text, colour=(0, 0, 0)):
        return self.font.render(text, 1, colour)
