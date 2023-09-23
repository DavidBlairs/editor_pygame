"""
This is a file used to text all the modules and what is run
to initiate the program.
"""
import pygame

from displayConstants import *
from surfaceManipulation import *

import textEditor
import controlPanel

pygame.init()
screenDimensions = getPercentageCoordinates((1, 1))
displaySurface = pygame.display.set_mode(screenDimensions, pygame.FULLSCREEN)

instanceClock = pygame.time.Clock()

editorInstance = textEditor.textEditor()
controlInstance = controlPanel.controlPanel(editorInstance)

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            editorInstance.checkEvent(event)
            controlInstance.checkEvent(event)

    clearIOSurface()
    editorInstance.loopUpdate()
    controlInstance.loopUpdate()

    updateIOSurface()
    displaySurface.blit(IOFeatureSurface, (0, 0))

    pygame.display.flip()
    instanceClock.tick(600)