"""
====
Run
====

This is the run file which allows the user to interact with the classes and
display all the class aspects. It is dependant on the textEditor module found
locally at "textEditor.py", the controlPanel module found locally at "controlPanel.py"
the pygame module found at http://pygame.org/ and the displayConstants module found
locally at "displayConstants.py".

This file is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

#import pygame to display the instance
import pygame

#import the constants from the displayConstants
from displayConstants import *

#import the editor class
import textEditor
import controlPanel


#initiate and setup screen layer
pygame.init()
screenDimensions = GetPercentageCoordinates((1, 1))
displaySurface = pygame.display.set_mode(screenDimensions, pygame.FULLSCREEN)

#setup the time handling
instanceClock = pygame.time.Clock()

#setup the editorLayer
editorInstance = textEditor.textEditor()

#setup the controlPanel Layer
controlDisplay = controlPanel.keywordSearch(editorInstance)

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