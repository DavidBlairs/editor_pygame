#import pygame to display the instance
import pygame

#import the constants from the displayConstants
from displayConstants import *

#import the editor class
import textEditorV03
import controlPanelV01


#initiate and setup screen layer
pygame.init()
screenDimensions = GetPercentageCoordinates((1, 1))
displaySurface = pygame.display.set_mode(screenDimensions, pygame.FULLSCREEN)

#setup the time handling
instanceClock = pygame.time.Clock()

#setup the editorLayer
editorInstance = textEditorV03.textEditor()

#setup the controlPanel Layer
controlDisplay = controlPanelV01.keywordSearch(editorInstance)

#run the main loop
while True:
    #check for events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            #text appending
            editorInstance.checkEvent(event)

            #text analysing
            controlDisplay.checkEvents(event)

    #reset the layout and update all layers
    clearIOLayer()
    editorInstance.loopUpdate()
    controlDisplay.loopUpdate()

    #place all layers onto the IO feature layer
    UpdateIOLayer()
    displaySurface.blit(IOFeatureLayer, (0, 0))

    #update pygame settings
    pygame.display.flip()
    instanceClock.tick(60)