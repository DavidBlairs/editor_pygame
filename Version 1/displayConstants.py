"""
====================
displayContants V0.2
====================

This is the displayConstants module. It contains some functions relating to
surface manipulation. It is dependant on the default ctypes module used to acquire
screen dimensions and the pygame module which can be found at http://pygame.org/.

This module is part of a series of files to be entered into the march computing
competition which can be found at:

https://www.cambridge.org/ukschools/news/march-computing-competition?utm_source=
Cambridge+University+Press&utm_medium=email&utm_campaign=5504266_156+-+March+Compu
ting+Competition+eAlert&utm_content=UKnews-marchcomputingcomp&dm_i=2792,39Z4A,I8TB
9A,BQ8OH,1

"""

import pygame
import ctypes



#Function to create layer relative to screen size
def LayerSurface(Dimensions):
    Size = int(Dimensions[0]*ctypes.windll.user32.GetSystemMetrics(0)),\
           int(Dimensions[1]*ctypes.windll.user32.GetSystemMetrics(1)) #Decimal percentage of screen size
    return pygame.Surface(Size) #---> surface with relative sizes


#get the percentage coordinates of a destination
def GetPercentageCoordinates(Destination):
    return (int(Destination[0]*ctypes.windll.user32.GetSystemMetrics(0)),
            int(Destination[1]*ctypes.windll.user32.GetSystemMetrics(1)))


#get rect for a layer on a surface
def GetRect(Location, Surface):
    return pygame.Rect(Location, (Surface.get_width(), Surface.get_height()))


#returns a transparent line surface
def TransparentLine(Size, Colour, AlphaLevel):
    LineSurface = pygame.Surface(Size)
    LineSurface.set_alpha(128)
    LineSurface.fill(Colour)
    return LineSurface


#draws a border of a given colour around a given surface
def drawBorder(surface, colour):
    pygame.draw.rect(surface, colour, [
        0, 0,
        surface.get_width(), surface.get_height()
    ], 2)


#declare the layers present on the screen
IOFeatureLayer = LayerSurface((1, 1))
controlLayer = LayerSurface((0.17, 0.96))
textDisplayLayer = LayerSurface((0.78, 0.96))


#fill all layers with a white background
def clearIOLayer():
    IOFeatureLayer.fill((255, 255, 255))
    controlLayer.fill((255, 255, 255))
    textDisplayLayer.fill((255, 255, 255))
clearIOLayer()


#blit the updated layers to the IO feature Layer.
def UpdateIOLayer():
    IOFeatureLayer.blit(controlLayer, GetPercentageCoordinates((0.02, 0.02)))
    IOFeatureLayer.blit(textDisplayLayer, GetPercentageCoordinates((0.2, 0.02)))
UpdateIOLayer()


#declare the r# ects for the layers
controlRect = GetRect(GetPercentageCoordinates((0.02, 0.02)), controlLayer)
textDisplayRect = GetRect(GetPercentageCoordinates((0.2, 0.02)), textDisplayLayer)


#the onscreen location of each of the layers
controlCoordinate = GetPercentageCoordinates((0.02, 0.02))
textDisplayCoordinate = GetPercentageCoordinates((0.2, 0.02))
