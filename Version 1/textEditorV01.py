from displayConstants import *
import pygame, time

class TextAnalysisInstance(object):
    def __init__(self):
        pygame.init()

        self.screenDimensions = GetPercentageCoordinates((1, 1))
        self.displaySurface = pygame.display.set_mode(self.screenDimensions,
                                                      pygame.FULLSCREEN)
        self.instanceClock = pygame.time.Clock()
        self.fileTextSave = self.loadSavedText("SavedText")

        self.editorFont = pygame.font.SysFont("agencyfb", 24)
        self.editorTextOffset = 0
        self.editorCursor = [[-1, -1], [-1, -1], [-1, -1]]

        self.editorTextUnrendered = ["This is a test.", "----------", "\"\"\"\"\"\"\"\"", "((((((())))))", "MMMMMMMMM", "+++++++++", "===========", ":::::::::::", "@@@@@@@@@@@@"]
        self.editorTextRendered = []
        self.editorTextRect = []

        self.timeRegister = 0
        self.MouseState = 0

        self.x = True

    def analyseText(self, Sample, Specification):
        FoundWords = []
        for Word in Specification:
            FoundLocations = []
            possibleMatches = [
                "".join([Sample[Letter + Segment] for Segment in range(len(Word))])
                for Letter in range(len(Sample) - len(Word))
            ]
            for Possible in range(len(possibleMatches)):
                if possibleMatches[Possible] == Word:
                     FoundLocations.append(Possible)
            FoundWords.append((FoundLocations, Word))
        return FoundWords


    def Update(self):
        clearIOLayer()
        self.updateTextViewer()

        UpdateIOLayer()
        self.displaySurface.blit(IOFeatureLayer, (0, 0))

        pygame.display.flip()
        self.instanceClock.tick(60)


    def loadSavedText(self, FileReference):
        return [([line for line in open(SavedFile).read().splitlines()], SavedFile)
            for SavedFile in open(FileReference).read().splitlines()]


    def addTextToSaved(self, FileReference, fileToSave):
        open(FileReference, "a").write("\n" + str(fileToSave))
        self.fileTextSave = self.loadSavedText("SavedText")
        return True


    def updateTextViewer(self):
        pygame.draw.rect(textDisplayLayer, (224, 224, 224), [1, 1,
            textDisplayLayer.get_width() - 1, textDisplayLayer.get_height() - 1], 2)

        currentLocation = [0, 0]
        for line in range(len(self.editorTextUnrendered)):
            self.editorTextRendered.append(((0, currentLocation[1]), self.editorFont.render(
                str(self.editorTextUnrendered[line]), 1, (0, 0, 0))))

            numberLength = self.editorFont.render(str(len(self.editorTextUnrendered)),
                1, (96, 96, 96)).get_width() + 6

            for letter in range(len(self.editorTextUnrendered[line])):
                tempTextRendered = self.editorFont.render(self.editorTextUnrendered[line][letter], 1, (96, 96, 96))
                if self.editorTextUnrendered[line][letter] != "|":
                    self.editorTextRect.append(((line, letter), self.editorTextUnrendered[line][letter],
                    pygame.Rect((textDisplayCoordinate[0] + numberLength + 20 + currentLocation[0], textDisplayCoordinate[1] +
                    currentLocation[1] + self.editorTextOffset + 4), (tempTextRendered.get_width(),
                    tempTextRendered.get_height()))))

                currentLocation[0] += tempTextRendered.get_width()
            textDisplayLayer.blit(self.editorFont.render(str(line + 1), 1, (192, 192, 192)),
                (numberLength - self.editorFont.render(str(line + 1), 1, (192, 192, 192)).get_width(),
                 currentLocation[1] + self.editorTextOffset + 4))
            currentLocation[1] += self.editorFont.render("|", 1, (0, 0, 0)).get_height() - 4
            currentLocation[0] = 0

            textDisplayLayer.blit(self.editorTextRendered[line][1],
                (self.editorTextRendered[line][0][0] + numberLength + 20,
                 self.editorTextRendered[line][0][1] + 4 + self.editorTextOffset))

            pygame.draw.line(textDisplayLayer, (224, 224, 224), (numberLength + 4, 0),
                (numberLength + 4, textDisplayLayer.get_height()), 2)

        if textDisplayRect.collidepoint(pygame.mouse.get_pos()):
            for rect in self.editorTextRect:
                if rect[2].collidepoint(pygame.mouse.get_pos()):
                    if pygame.mouse.get_pressed()[0]:
                        self.editorCursor = [[rect[2].x, rect[2].y], [rect[2].width, rect[2].height], rect[0]]

        def getRect(Location):
            sumLetters = 0
            for lines in range(Location[0]):
                sumLetters += len(self.editorTextUnrendered[lines])
            return sumLetters + Location[1] + 1

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.x = False
                elif event.key == pygame.K_BACKSPACE:
                    if self.editorCursor[0][0] != -1:
                        listText = list(self.editorTextUnrendered[self.editorCursor[2][0]])
                        del listText[self.editorCursor[2][1] - 1]
                        self.editorTextUnrendered[self.editorCursor[2][0]] = "".join(listText)
                        self.editorCursor = [[self.editorTextRect[getRect((self.editorCursor[2][0], self.editorCursor[2][1] - 1))][2].x,
                                            self.editorTextRect[getRect((self.editorCursor[2][0], self.editorCursor[2][1] - 1))][2].y],
                                             [self.editorTextRect[getRect((self.editorCursor[2][0], self.editorCursor[2][1] - 1))][2].width,
                                              self.editorTextRect[getRect((self.editorCursor[2][0], self.editorCursor[2][1] - 1))][2]. height],
                                                [self.editorCursor[2][0], self.editorCursor[2][1] - 1]]
                elif event.key > 0 and event.key < 127:
                    pass
            if event.type == pygame.QUIT:
                self.x = False

        if self.timeRegister == 0:
            self.timeRegister = time.time()
            if self.MouseState == True:
                self.MouseState = False
            else: self.MouseState = True
        if self.editorCursor[0] != (-1, -1):
            if self.MouseState == True:
                    pygame.draw.rect(textDisplayLayer, (0, 0, 0), [self.editorCursor[0][0] - textDisplayCoordinate[0],
                                 self.editorCursor[0][1] - textDisplayCoordinate[1], 2, self.editorCursor[1][1]])
        if time.time() - self.timeRegister > 0.5:
            self.timeRegister = 0
        self.editorTextRect = []
        self.editorTextRendered = []


TextInstance = TextAnalysisInstance()

while TextInstance.x == True:
    TextInstance.Update()