import reportlab.pdfgen.canvas as pdfgcanvas
from reportlab.lib.pagesizes import LETTER, landscape, A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
import PIL


class TuckBoxGenerator:
    def __init__(self,
                 width,
                 height,
                 depth,
                 fname=None,
                 sideImage=None,
                 frontImage=None,
                 backImage=None,
                 endImage=None,
                 pagesize=LETTER,
                 fillColour=None,
                 preserveSideAspect=False,
                 preserveEndAspect=False,
                 endVerticalMargin=0,
                 endHorizontalMargin=0,
                 canvas=None):
        self.pagesize = landscape(pagesize)
        if canvas is None:
            assert fname
            self.canvas = pdfgcanvas.Canvas(fname, pagesize=self.pagesize)
        else:
            self.canvas = canvas
        self.filename = fname
        self.pageMargin = 2 * cm
        self.width = width
        self.height = height
        self.depth = depth
        self.flapDepth = self.depth * 0.6
        self.dash = (3, 5)
        self.sideImage = sideImage
        self.endImage = endImage
        self.frontImage = frontImage
        self.backImage = backImage
        self.fillColour = fillColour
        self.preserveSideAspect = preserveSideAspect
        self.preserveEndAspect = preserveEndAspect
        self.endVerticalMargin = endVerticalMargin
        self.endHorizontalMargin = endHorizontalMargin

    @staticmethod
    def fromRawData(raw_width,
                    raw_height,
                    raw_depth,
                    fname,
                    fIm,
                    sIm,
                    bIm,
                    eIm,
                    fillColour,
                    preserveSideAspect,
                    preserveEndAspect,
                    pagesize='letter'):
        fImRead = ImageReader(PIL.Image.open(fIm)) if fIm else None
        sImRead = ImageReader(PIL.Image.open(sIm)) if sIm else None
        bImRead = ImageReader(PIL.Image.open(bIm)) if bIm else None
        eImRead = ImageReader(PIL.Image.open(eIm)) if eIm else None

        ps = LETTER
        if pagesize == 'A4':
            ps = A4
        return TuckBoxGenerator(raw_width * cm, raw_height * cm,
                                raw_depth * cm, fname, sImRead, fImRead,
                                bImRead, eImRead,
                                fillColour=fillColour,
                                preserveSideAspect=preserveSideAspect,
                                preserveEndAspect=preserveEndAspect,
                                pagesize=ps)

    def drawEnd(self, isTop=False, isGlue=False):
        if self.fillColour:
            if len(self.fillColour) == 4:
                self.canvas.setFillColorCMYK(*self.fillColour)
            else:
                self.canvas.setFillColorRGB(*self.fillColour)
            self.canvas.rect(
                0,
                self.flapDepth,
                self.depth,
                self.width,
                fill=True,
                stroke=False)
        self.canvas.saveState()
        if isGlue:
            margin = 7
            self.canvas.setFillColorCMYK(0, 0, 0, 0.1)
            self.canvas.setStrokeColorCMYK(0, 0, 0, 0.1)
            self.canvas.rect(
                margin,
                self.flapDepth + margin,
                self.depth - 2 * margin,
                self.width - 2 * margin,
                fill=True)
            self.canvas.setFillColorCMYK(0, 0, 0, 1)
            self.canvas.rotate(-90)
            self.canvas.scale(1, -1)
            self.canvas.setFontSize(7)
            self.canvas.drawCentredString(
                -self.width / 2 - self.flapDepth, -self.depth / 2 - 5,
                "Cut Solid. Fold Dashed. Glue This.")
        elif self.sideImage:
            if isTop:
                self.canvas.scale(1, -1)
                self.canvas.translate(0, -self.width - 2 * self.flapDepth)
            self.canvas.rotate(-90)
            self.canvas.drawImage(
                self.sideImage,
                -self.width - self.flapDepth + self.endHorizontalMargin,
                self.endVerticalMargin,
                self.width - self.endHorizontalMargin,
                self.depth - 2 * self.endVerticalMargin,
                preserveAspectRatio=self.preserveEndAspect,
                mask='auto')
        self.canvas.restoreState()
        if not isGlue:
            self.canvas.line(0, 0, self.depth, 0)
            self.canvas.line(0, 0, 0, self.flapDepth)
        if not isTop:
            self.canvas.line(0, self.flapDepth, 0, self.flapDepth + self.width)
        if not isGlue:
            self.canvas.arc(
                0,
                self.width,
                self.depth,
                2 * self.flapDepth + self.width,
                startAng=180,
                extent=-90)
            self.canvas.line(self.depth / 2, self.width + 2 * self.flapDepth,
                             self.depth, self.width + 2 * self.flapDepth)
        self.canvas.setDash(*self.dash)
        if isTop:
            self.canvas.line(0, self.flapDepth, 0, self.flapDepth + self.width)
        self.canvas.line(self.depth, self.flapDepth, self.depth,
                         self.flapDepth + self.width)
        if isGlue:
            self.canvas.setDash()
        self.canvas.line(0, self.flapDepth, self.depth, self.flapDepth)
        self.canvas.line(0, self.width + self.flapDepth, self.depth,
                         self.width + self.flapDepth)

    def drawSide(self, hasFlap=False, isGlue=False):
        self.canvas.saveState()
        if self.fillColour:
            if len(self.fillColour) == 4:
                self.canvas.setFillColorCMYK(*self.fillColour)
            else:
                self.canvas.setFillColorRGB(*self.fillColour)
            self.canvas.rect(
                0, 0, self.height, self.depth, fill=True, stroke=False)
        if isGlue:
            self.canvas.setFillColorCMYK(0, 0, 0, 0.1)
            self.canvas.setStrokeColorCMYK(0, 0, 0, 0.1)
            margin = 7
            self.canvas.rect(
                margin,
                margin,
                self.height - 2 * margin,
                self.depth - 2 * margin,
                fill=True)
            self.canvas.setFillColorCMYK(0, 0, 0, 1)
            # self.canvas.rotate(-90)
            # self.canvas.scale(1,-1)
            self.canvas.setFontSize(8)
            self.canvas.drawCentredString(
                self.height / 2, self.depth / 2 - 5,
                "Cut Solid. Fold Dashed. Glue This.")
        elif self.endImage or self.sideImage:
            if self.endImage:
                image = self.endImage
            else:
                image = self.sideImage
            margin = 0
            if hasFlap:
                self.canvas.rotate(180)
                self.canvas.scale(1, -1)
                self.canvas.translate(-self.height, 0)
            self.canvas.drawImage(
                image,
                margin,
                margin,
                self.height - 2 * margin,
                self.depth - 2 * margin,
                preserveAspectRatio=self.preserveSideAspect,
                mask='auto')
        self.canvas.restoreState()
        arcWidth = 0.5 * self.flapDepth
        self.canvas.line(0, 0, 0, self.depth)
        if not hasFlap:
            self.canvas.line(0, 0, self.height, 0)
        else:
            extraFlap = 0.5 * cm
            self.canvas.setDash(*self.dash)
            self.canvas.setDash()
            self.canvas.line(0, 0, 0, -extraFlap)
            self.canvas.line(self.height, 0, self.height, -extraFlap)
            self.canvas.line(0, 0, arcWidth, 0)
            self.canvas.line(self.height - arcWidth, 0, self.height, 0)
            self.canvas.arc(0, -arcWidth - extraFlap, arcWidth * 2,
                            arcWidth - extraFlap, 180)
            self.canvas.line(arcWidth, -arcWidth - extraFlap,
                             self.height - arcWidth, -arcWidth - extraFlap)
            self.canvas.arc(self.height - arcWidth * 2, -arcWidth - extraFlap,
                            self.height, arcWidth - extraFlap, -90)
        self.canvas.line(self.height, 0, self.height, self.depth)
        self.canvas.setDash(*self.dash)
        self.canvas.line(0, self.depth, self.height, self.depth)
        if hasFlap:
            self.canvas.line(arcWidth, 0, self.height - arcWidth, 0)

    def drawFront(self):
        if self.frontImage:
            margin = 0
            self.canvas.saveState()
            # self.canvas.rotate(90)
            self.canvas.drawImage(
                self.frontImage,
                margin,
                margin,
                self.height - 2 * margin,
                self.width - 2 * margin,
                preserveAspectRatio=False,
                mask='auto')
            self.canvas.restoreState()

    def drawBack(self):
        if self.backImage:
            margin = 0
            self.canvas.saveState()
            # if self.backImage == self.frontImage:
            #     self.canvas.translate(self.height-2*margin,self.width-2*margin)
            #     self.canvas.rotate(180)
            # self.canvas.rotate(90)
            self.canvas.drawImage(
                self.backImage,
                margin,
                margin,
                self.height - 2 * margin,
                self.width - 2 * margin,
                preserveAspectRatio=False,
                mask='auto')
            self.canvas.restoreState()
        fingerWidth = min(self.depth / 1.5, 1.25 * cm)
        centre = self.height / 2.0
        self.canvas.line(0, self.width, centre - fingerWidth / 2.0, self.width)
        self.canvas.line(centre + fingerWidth / 2.0, self.width, self.height,
                         self.width)
        self.canvas.arc(
            centre - fingerWidth / 2.0,
            self.width - fingerWidth / 2.0,
            centre + fingerWidth / 2.0,
            self.width + fingerWidth / 2.0,
            startAng=180,
            extent=180)
        self.canvas.setFillColorCMYK(0, 0, 0, 0)
        self.canvas.wedge(
            centre - fingerWidth / 2.0,
            self.width - fingerWidth / 2.0,
            centre + fingerWidth / 2.0,
            self.width + fingerWidth / 2.0,
            startAng=180,
            extent=180,
            stroke=0,
            fill=1)

    def generate(self):
        if self.filename:
            print('generating {}'.format(self.filename))
        self.canvas.saveState()
        self.canvas.translate(self.pageMargin, self.pageMargin)

        # draw front
        self.canvas.saveState()
        self.canvas.translate(self.depth, self.depth)
        self.drawFront()
        self.canvas.restoreState()

        # complete the back
        self.canvas.saveState()
        self.canvas.translate(2 * self.depth + self.height, self.depth)
        self.drawBack()
        self.canvas.restoreState()

        # bottom flap
        self.canvas.saveState()
        self.canvas.translate(0, self.depth - self.flapDepth)
        self.drawEnd()
        self.canvas.restoreState()

        # top flap
        self.canvas.saveState()
        self.canvas.translate(2 * self.depth + self.height,
                              self.depth - self.flapDepth)
        self.canvas.scale(-1, 1)
        self.drawEnd(True)
        self.canvas.restoreState()

        # right flap
        self.canvas.saveState()
        self.canvas.translate(self.depth, 0)
        self.drawSide()
        self.canvas.restoreState()

        # left flap
        self.canvas.saveState()
        self.canvas.translate(self.depth, 2 * self.depth + self.width)
        self.canvas.scale(1, -1)
        self.drawSide(True)
        self.canvas.restoreState()

        # side glue flap
        self.canvas.saveState()
        self.canvas.translate(2 * self.depth + self.height, 0)
        self.drawSide(isGlue=True)
        self.canvas.restoreState()

        # bottom glue flap
        self.canvas.saveState()
        self.canvas.translate(2 * self.depth + 2 * self.height,
                              self.depth - self.flapDepth)
        self.canvas.scale(0.6, 1)
        self.canvas.translate(self.depth, 0)
        self.canvas.scale(-1, 1)
        self.drawEnd(False, True)
        self.canvas.restoreState()

        self.canvas.restoreState()

        # in case more will be drawn:
        self.canvas.translate(*self.pagesize)
        # self.canvas.line(0, 0, 10, 10)
        # self.canvas.translate(2*self.height+2*self.depth+self.flapDepth,2*self.width + 2*self.depth+self.flapDepth)
        self.canvas.rotate(180)
        return self.canvas

    def close(self):
        self.canvas.save()


def main():
    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.6 * cm,
        '7Wonders_age_2_3.pdf',
        sideImage='7W_logo.png',
        frontImage='7W_wallpapper_1440x900_zeus.jpg',
        backImage='age3.jpg',
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.77, 0.74, 0.1, 0.1))
    c = tuck.generate()

    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.6 * cm,
        sideImage='7W_logo.png',
        frontImage='7W_wallpapper_1440x900_alexandrie.jpg',
        backImage='age2.jpg',
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.96, 0.35, 0.0, 0.06),
        canvas=c)
    tuck.generate()
    tuck.close()

    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.6 * cm,
        '7Wonders_age_1_leaders.pdf',
        sideImage='7W_logo.png',
        frontImage='7W_wallpapper_1440x900_babylone.jpg',
        backImage='age1.jpg',
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.0, 0.45, 0.78, 0.30))
    c = tuck.generate()
    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.2 * cm,
        sideImage='7W_logo.png',
        frontImage='leaders.jpg',
        backImage='leaders_back.jpg',
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.0, 0.0, 0.0, 0.0),
        canvas=c)
    tuck.generate()
    tuck.close()
    tuck = TuckBoxGenerator(
        6.8 * cm,
        9.9 * cm,
        2.4 * cm,
        'Modern_Art.pdf',
        sideImage='MA_title.jpg',
        frontImage='MA_Jester.jpg',
        backImage='MA_Koriko.jpg',
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.29, 0.89, 0.54, 0.35))
    tuck.generate()
    tuck.close()
    tuck = TuckBoxGenerator(
        6.4 * cm,
        8.8 * cm,
        2 * cm,
        'Claustrophobia_tuckbox.pdf',
        sideImage='claustrophobia_side.jpg',
        endImage='claustrophobia_end.jpg',
        frontImage='claustrophobia_front.jpg',
        backImage='claustrophobia_back.jpg',
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50))
    tuck.generate()
    tuck.close()
    # monuments
    tuck = TuckBoxGenerator(
        4.2 * cm,
        5.2 * cm,
        2.3 * cm,
        'tzolkin_monuments_starttile_tuckbox.pdf',
        sideImage='tzolkin_title.jpg',
        endImage='tzolkin_title.jpg',
        frontImage='tzolkin_monument.jpg',
        backImage='tzolkin_monument.jpg',
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50))
    c = tuck.generate()
    # starting tiles
    tuck = TuckBoxGenerator(
        2.7 * cm,
        5.2 * cm,
        2.6 * cm,
        sideImage='tzolkin_title.jpg',
        endImage='tzolkin_title.jpg',
        frontImage='tzolkin_starttile.jpg',
        backImage='tzolkin_starttile.jpg',
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
        canvas=c)
    tuck.generate()
    tuck.close()
    # Age 1
    tuck = TuckBoxGenerator(
        4.2 * cm,
        5.2 * cm,
        2.5 * cm,
        'tzolkin_ages_tuckboxes.pdf',
        sideImage='tzolkin_title.jpg',
        endImage='tzolkin_title.jpg',
        frontImage='tzolkin_age1.jpg',
        backImage='tzolkin_age1.jpg',
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50))
    c = tuck.generate()
    # Age 2
    tuck = TuckBoxGenerator(
        4.2 * cm,
        5.2 * cm,
        3.1 * cm,
        sideImage='tzolkin_title.jpg',
        endImage='tzolkin_title.jpg',
        frontImage='tzolkin_age2.jpg',
        backImage='tzolkin_age2.jpg',
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
        canvas=c)
    c = tuck.generate()
    tuck.close()

    # Istanbul
    tuck = TuckBoxGenerator(
        6.8 * cm,
        4.5 * cm,
        0.8 * cm,
        'istanbul_tuckbox.pdf',
        sideImage='istanbul_side.png',
        endImage='istanbul_side.png',
        frontImage='istanbul_front.jpg',
        backImage='istanbul_front.jpg',
        preserveSideAspect=True,
        preserveEndAspect=True,
        endVerticalMargin=0,
        fillColour=(0.9, 0.75, 0.29, 0.6))
    tuck.generate()
    tuck.close()


if __name__ == '__main__':
    main()
