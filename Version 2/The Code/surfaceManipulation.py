"""
====================
Surface Manipulation
====================

This file contains some functions that help with surface creation and
manipulation. It is dependant on the pygame module which can be found at
http://pygame.org/ and the ctypes module for system metrics.

This file is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1
"""

import pygame
import ctypes

# Function to create layer relative to screen size
def layerSurface(dimensions):
    size = int(dimensions[0]*ctypes.windll.user32.GetSystemMetrics(0)),\
           int(dimensions[1]*ctypes.windll.user32.GetSystemMetrics(1)) #Decimal percentage of screen size
    return pygame.Surface(size) #---> surface with relative sizes


# get the percentage coordinates of a destination
def getPercentageCoordinates(destination):
    return (int(destination[0]*ctypes.windll.user32.GetSystemMetrics(0)),
            int(destination[1]*ctypes.windll.user32.GetSystemMetrics(1)))


# get rect for a layer on a surface
def getRect(location, surface):
    return pygame.Rect(location, (surface.get_width(), surface.get_height()))


# returns a transparent line surface
def transparentLine(Size, Colour, AlphaLevel):
    LineSurface = pygame.Surface(Size)
    LineSurface.set_alpha(128)
    LineSurface.fill(Colour)
    return LineSurface


# draws a border of a given colour around a given surface
def drawBorder(surface, colour):
    pygame.draw.rect(surface, colour, [
        0, 0,
        surface.get_width(), surface.get_height()
    ], 2)


# centres as object around a rect on a secondary surface
def centreControl(surface, rect, object, secondarySurfaceRect):
    surface.blit(object, (rect.centerx - secondarySurfaceRect.x -
                (object.get_width() / 2), rect.centery - secondarySurfaceRect.y
                - (object.get_height() / 2)))
