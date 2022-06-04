import reportlab.pdfgen.canvas as pdfgcanvas
from reportlab.lib.pagesizes import LETTER, landscape, A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import PIL
import click


class TuckBoxGenerator:
    def __init__(
        self,
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
        canvas=None,
    ):
        self.pagesize = landscape(pagesize)
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
        self.is_sample = False

    @staticmethod
    def fromRawData(
        raw_width,
        raw_height,
        raw_depth,
        fname=None,
        fIm=None,
        sIm=None,
        bIm=None,
        eIm=None,
        fillColour=None,
        preserveSideAspect=False,
        preserveEndAspect=False,
        pagesize="letter",
    ):
        fImRead = ImageReader(PIL.Image.open(fIm)) if fIm else None
        sImRead = ImageReader(PIL.Image.open(sIm)) if sIm else None
        bImRead = ImageReader(PIL.Image.open(bIm)) if bIm else None
        eImRead = ImageReader(PIL.Image.open(eIm)) if eIm else None

        ps = LETTER
        if pagesize == "A4":
            ps = A4
        return TuckBoxGenerator(
            raw_width * cm,
            raw_height * cm,
            raw_depth * cm,
            fname,
            sImRead,
            fImRead,
            bImRead,
            eImRead,
            fillColour=fillColour,
            preserveSideAspect=preserveSideAspect,
            preserveEndAspect=preserveEndAspect,
            pagesize=ps,
        )

    def drawImage(self, image, x, y, w, h, preserveAspect, tag):
        self.canvas.saveState()
        if self.is_sample:
            if tag not in ["Side", "End"]:
                self.canvas.setFillColorRGB(1, 1, 1)
                self.canvas.rect(x, y, w, h, fill=1)
            self.canvas.setFillColorRGB(0.0, 0.0, 0.0)
            self.canvas.setFontSize(15)
            self.canvas.drawCentredString(x + w / 2.0, y + h / 2.0, tag)
        else:
            self.canvas.drawImage(
                image, x, y, w, h, preserveAspectRatio=preserveAspect, mask="auto"
            )
        self.canvas.restoreState()

    def drawEnd(self, isTop=False, isGlue=False):
        self.canvas.saveState()
        if self.fillColour:
            if self.fillColour[0] == "#":
                self.canvas.setFillColor(HexColor(self.fillColour))
            elif len(self.fillColour) == 4:
                self.canvas.setFillColorCMYK(*self.fillColour)
            else:
                self.canvas.setFillColorRGB(*self.fillColour)
            self.canvas.rect(
                0, self.flapDepth, self.depth, self.width, fill=True, stroke=False
            )
        if isGlue:
            margin = 7
            self.canvas.setFillColorCMYK(0, 0, 0, 0.1)
            self.canvas.setStrokeColorCMYK(0, 0, 0, 0.1)
            self.canvas.rect(
                margin,
                self.flapDepth + margin,
                self.depth - 2 * margin,
                self.width - 2 * margin,
                fill=True,
            )
            self.canvas.setFillColorCMYK(0, 0, 0, 1)
            self.canvas.rotate(-90)
            self.canvas.scale(1, -1)
            self.canvas.setFontSize(7)
            self.canvas.drawCentredString(
                -self.width / 2 - self.flapDepth,
                -self.depth / 2 - 5,
                "Cut Solid. Fold Dashed. Glue This.",
            )
        elif self.endImage or self.is_sample:
            if isTop:
                self.canvas.scale(1, -1)
                self.canvas.translate(0, -self.width - 2 * self.flapDepth)
            self.canvas.rotate(-90)
            x = -self.width - self.flapDepth + self.endHorizontalMargin
            y = self.endVerticalMargin
            w = self.width - self.endHorizontalMargin
            h = self.depth - 2 * self.endVerticalMargin
            self.drawImage(self.endImage, x, y, w, h, self.preserveEndAspect, "End")

        self.canvas.restoreState()
        self.canvas.saveState()

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
                extent=-90,
            )
            self.canvas.line(
                self.depth / 2,
                self.width + 2 * self.flapDepth,
                self.depth,
                self.width + 2 * self.flapDepth,
            )
        self.canvas.setDash(*self.dash)
        if isTop:
            self.canvas.line(0, self.flapDepth, 0, self.flapDepth + self.width)
        self.canvas.line(
            self.depth, self.flapDepth, self.depth, self.flapDepth + self.width
        )
        if isGlue:
            self.canvas.setDash()
        self.canvas.line(0, self.flapDepth, self.depth, self.flapDepth)
        self.canvas.line(
            0, self.width + self.flapDepth, self.depth, self.width + self.flapDepth
        )
        self.canvas.restoreState()

    def drawSide(self, hasFlap=False, isGlue=False):
        self.canvas.saveState()
        if self.fillColour:
            if self.fillColour[0] == "#":
                self.canvas.setFillColor(HexColor(self.fillColour))
            elif len(self.fillColour) == 4:
                self.canvas.setFillColorCMYK(*self.fillColour)
            else:
                self.canvas.setFillColorRGB(*self.fillColour)
            self.canvas.rect(0, 0, self.height, self.depth, fill=True, stroke=False)
        if isGlue:
            self.canvas.setFillColorCMYK(0, 0, 0, 0.1)
            self.canvas.setStrokeColorCMYK(0, 0, 0, 0.1)
            margin = 7
            self.canvas.rect(
                margin,
                margin,
                self.height - 2 * margin,
                self.depth - 2 * margin,
                fill=True,
            )
            self.canvas.setFillColorCMYK(0, 0, 0, 1)
            # self.canvas.rotate(-90)
            # self.canvas.scale(1,-1)
            self.canvas.setFontSize(8)
            self.canvas.drawCentredString(
                self.height / 2,
                self.depth / 2 - 5,
                "Cut Solid. Fold Dashed. Glue This.",
            )
        elif self.sideImage or self.is_sample:
            image = self.sideImage
            margin = 0
            if hasFlap:
                self.canvas.rotate(180)
                self.canvas.scale(1, -1)
                self.canvas.translate(-self.height, 0)

            self.drawImage(
                image,
                margin,
                margin,
                self.height - 2 * margin,
                self.depth - 2 * margin,
                self.preserveSideAspect,
                "Side",
            )

        self.canvas.restoreState()
        self.canvas.saveState()

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
            self.canvas.arc(
                0, -arcWidth - extraFlap, arcWidth * 2, arcWidth - extraFlap, 180
            )
            self.canvas.line(
                arcWidth,
                -arcWidth - extraFlap,
                self.height - arcWidth,
                -arcWidth - extraFlap,
            )
            self.canvas.arc(
                self.height - arcWidth * 2,
                -arcWidth - extraFlap,
                self.height,
                arcWidth - extraFlap,
                -90,
            )
        self.canvas.line(self.height, 0, self.height, self.depth)
        self.canvas.setDash(*self.dash)
        self.canvas.line(0, self.depth, self.height, self.depth)
        if hasFlap:
            self.canvas.line(arcWidth, 0, self.height - arcWidth, 0)
        self.canvas.restoreState()

    def drawFront(self):
        self.canvas.saveState()
        if self.frontImage or self.is_sample:
            margin = 0
            # self.canvas.rotate(90)
            self.drawImage(
                self.frontImage,
                margin,
                margin,
                self.height - 2 * margin,
                self.width - 2 * margin,
                False,
                "Front",
            )
        self.canvas.restoreState()

    def drawBack(self):
        self.canvas.saveState()
        if self.backImage or self.is_sample:
            margin = 0
            # if self.backImage == self.frontImage:
            #     self.canvas.translate(self.height-2*margin,self.width-2*margin)
            #     self.canvas.rotate(180)
            # self.canvas.rotate(90)
            self.drawImage(
                self.backImage,
                margin,
                margin,
                self.height - 2 * margin,
                self.width - 2 * margin,
                False,
                "Back",
            )
        fingerWidth = min(self.depth / 1.5, 1.25 * cm)
        centre = self.height / 2.0
        self.canvas.line(0, self.width, centre - fingerWidth / 2.0, self.width)
        self.canvas.line(
            centre + fingerWidth / 2.0, self.width, self.height, self.width
        )
        self.canvas.arc(
            centre - fingerWidth / 2.0,
            self.width - fingerWidth / 2.0,
            centre + fingerWidth / 2.0,
            self.width + fingerWidth / 2.0,
            startAng=180,
            extent=180,
        )
        self.canvas.setFillColorCMYK(0, 0, 0, 0)
        self.canvas.wedge(
            centre - fingerWidth / 2.0,
            self.width - fingerWidth / 2.0,
            centre + fingerWidth / 2.0,
            self.width + fingerWidth / 2.0,
            startAng=180,
            extent=180,
            stroke=0,
            fill=1,
        )
        self.canvas.restoreState()

    def generate(self):
        if self.filename:
            print("generating {}".format(self.filename))

        if self.canvas is None:
            assert self.filename
            self.canvas = pdfgcanvas.Canvas(self.filename, pagesize=self.pagesize)
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
        self.canvas.translate(2 * self.depth + self.height, self.depth - self.flapDepth)
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
        self.canvas.translate(
            2 * self.depth + 2 * self.height, self.depth - self.flapDepth
        )
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

    def generate_sample(self):
        import io
        from wand.image import Image

        buf = io.BytesIO()
        tmp_fname = self.filename
        self.filename = buf
        self.is_sample = True
        self.generate()
        self.close()
        self.filename = tmp_fname
        self.is_sample = False
        sample_out = io.BytesIO()
        with Image(blob=buf.getvalue(), resolution=75) as sample:
            sample.rotate(-90)
            sample.format = "png"
            sample.save(sample_out)
            return sample_out.getvalue()


@click.command()
@click.option("--width", default=6.4, help="width in centimers")
@click.option("--height", default=8.8, help="height in centimers")
@click.option("--depth", default=3.0, help="depth in centimers")
@click.option("--outfile", default="tuckbox.pdf")
@click.option("--front_image", help="file path")
@click.option("--back_image", help="file path")
@click.option("--side_image", help="file path")
@click.option("--end_image", help="file path")
@click.option("--preserve_end_aspect", default=False)
@click.option("--preserve_side_aspect", default=False)
@click.option("--fill_colour", default="#FFFFFF", help="RGB hex string for side/end background colour")
def main(
    width,
    height,
    depth,
    outfile,
    front_image,
    back_image,
    side_image,
    end_image,
    preserve_end_aspect,
    preserve_side_aspect,
    fill_colour,
):
    tuck = TuckBoxGenerator(
        width * cm,
        height * cm,
        depth * cm,
        outfile,
        frontImage=front_image,
        backImage=back_image,
        sideImage=side_image,
        endImage=end_image,
        preserveEndAspect=preserve_end_aspect,
        preserveSideAspect=preserve_side_aspect,
        fillColour=fill_colour,
    )
    tuck.generate()
    tuck.close()


def sample():
    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.6 * cm,
        "7Wonders_age_2_3.pdf",
        sideImage="7W_logo.png",
        frontImage="7W_wallpapper_1440x900_zeus.jpg",
        backImage="age3.jpg",
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.77, 0.74, 0.1, 0.1),
    )
    # tuck = TuckBoxGenerator.fromRawData(
    #     6.7 * cm,
    #     10.2 * cm,
    #     1.6 * cm,
    #     preserveEndAspect=True,
    #     preserveSideAspect=True,
    #     fillColour=(0.77, 0.74, 0.6))
    # with open('sample.png', 'wb') as f:
    #     d = tuck.generate_sample()
    #     f.write(d)
    # import sys
    # sys.exit()

    c = tuck.generate()

    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.6 * cm,
        sideImage="7W_logo.png",
        frontImage="7W_wallpapper_1440x900_alexandrie.jpg",
        backImage="age2.jpg",
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.96, 0.35, 0.0, 0.06),
        canvas=c,
    )
    tuck.generate()
    tuck.close()

    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.6 * cm,
        "7Wonders_age_1_leaders.pdf",
        sideImage="7W_logo.png",
        frontImage="7W_wallpapper_1440x900_babylone.jpg",
        backImage="age1.jpg",
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.0, 0.45, 0.78, 0.30),
    )
    c = tuck.generate()
    tuck = TuckBoxGenerator(
        6.7 * cm,
        10.2 * cm,
        1.2 * cm,
        sideImage="7W_logo.png",
        frontImage="leaders.jpg",
        backImage="leaders_back.jpg",
        preserveEndAspect=True,
        preserveSideAspect=True,
        fillColour=(0.0, 0.0, 0.0, 0.0),
        canvas=c,
    )
    tuck.generate()
    tuck.close()
    tuck = TuckBoxGenerator(
        6.8 * cm,
        9.9 * cm,
        2.4 * cm,
        "Modern_Art.pdf",
        sideImage="MA_title.jpg",
        frontImage="MA_Jester.jpg",
        backImage="MA_Koriko.jpg",
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.29, 0.89, 0.54, 0.35),
    )
    tuck.generate()
    tuck.close()
    tuck = TuckBoxGenerator(
        6.4 * cm,
        8.8 * cm,
        2 * cm,
        "Claustrophobia_tuckbox.pdf",
        sideImage="claustrophobia_side.jpg",
        endImage="claustrophobia_end.jpg",
        frontImage="claustrophobia_front.jpg",
        backImage="claustrophobia_back.jpg",
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
    )
    tuck.generate()
    tuck.close()
    # monuments
    tuck = TuckBoxGenerator(
        4.2 * cm,
        5.2 * cm,
        2.3 * cm,
        "tzolkin_monuments_starttile_tuckbox.pdf",
        sideImage="tzolkin_title.jpg",
        endImage="tzolkin_title.jpg",
        frontImage="tzolkin_monument.jpg",
        backImage="tzolkin_monument.jpg",
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
    )
    c = tuck.generate()
    # starting tiles
    tuck = TuckBoxGenerator(
        2.7 * cm,
        5.2 * cm,
        2.6 * cm,
        sideImage="tzolkin_title.jpg",
        endImage="tzolkin_title.jpg",
        frontImage="tzolkin_starttile.jpg",
        backImage="tzolkin_starttile.jpg",
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
        canvas=c,
    )
    tuck.generate()
    tuck.close()
    # Age 1
    tuck = TuckBoxGenerator(
        4.2 * cm,
        5.2 * cm,
        2.5 * cm,
        "tzolkin_ages_tuckboxes.pdf",
        sideImage="tzolkin_title.jpg",
        endImage="tzolkin_title.jpg",
        frontImage="tzolkin_age1.jpg",
        backImage="tzolkin_age1.jpg",
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
    )
    c = tuck.generate()
    # Age 2
    tuck = TuckBoxGenerator(
        4.2 * cm,
        5.2 * cm,
        3.1 * cm,
        sideImage="tzolkin_title.jpg",
        endImage="tzolkin_title.jpg",
        frontImage="tzolkin_age2.jpg",
        backImage="tzolkin_age2.jpg",
        preserveSideAspect=False,
        preserveEndAspect=False,
        endVerticalMargin=0,
        fillColour=(0.62, 0.76, 0.68, 0.50),
        canvas=c,
    )
    c = tuck.generate()
    tuck.close()

    # Istanbul
    tuck = TuckBoxGenerator(
        6.8 * cm,
        4.5 * cm,
        0.8 * cm,
        "istanbul_tuckbox.pdf",
        sideImage="istanbul_side.png",
        endImage="istanbul_side.png",
        frontImage="istanbul_front.jpg",
        backImage="istanbul_front.jpg",
        preserveSideAspect=True,
        preserveEndAspect=True,
        endVerticalMargin=0,
        fillColour=(0.9, 0.75, 0.29, 0.6),
    )
    tuck.generate()
    tuck.close()


if __name__ == "__main__":
    main()
