"""
==================
Display Constants
==================

This file contains some constants regarding surface dimensions in respect
to the ctypes system metrics. It's dependant on surfaceManipulation.py for some
functions regarding surface manipulation, the default module ctypes to get the
system metrics and the pygame module which can be found at http://pygame.org/.

This file is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import surfaceManipulation
import pygame
import ctypes



# It's best to keep all the primary layers available for both the control panel
# to use to make accessing these surfaces much easier. All values for the surface
# dimensions are relative to the complete screen dimensions as a decimal fraction.

IOFeatureSurface = surfaceManipulation.layerSurface((1, 1))
controlSurface = surfaceManipulation.layerSurface((0.17, 0.96))
editorSurface = surfaceManipulation.layerSurface((0.78, 0.96))

controlRect = surfaceManipulation.getRect(surfaceManipulation.getPercentageCoordinates((0.02, 0.02)), controlSurface)
editorRect = surfaceManipulation.getRect(surfaceManipulation.getPercentageCoordinates((0.2, 0.02)), editorSurface)

# these functions allow the program to reset and update the surfaces much easier
def clearIOSurface():
    IOFeatureSurface.fill((255, 255, 255))
    controlSurface.fill((255, 255, 255))
    editorSurface.fill((255, 255, 255))
clearIOSurface()

def updateIOSurface():
    IOFeatureSurface.blit(controlSurface, surfaceManipulation.getPercentageCoordinates((0.02, 0.02)))
    IOFeatureSurface.blit(editorSurface, surfaceManipulation.getPercentageCoordinates((0.2, 0.02)))
updateIOSurface()