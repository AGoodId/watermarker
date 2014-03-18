#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
except:
    import Image, ImageDraw, ImageFont, ImageEnhance

class ImpropertlyConfigured(Exception):
    pass



def ReduceOpacity(im, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def Imprint(im, inputtext, font=None, color=None, outline=None, opacity=0.6, margin=(30,30),
            position='bottom-left', antialias=True):
    """
    imprints a PIL image with the indicated text in lower-right corner
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")

    # For anti-aliasing use twice the size and scale down
    size = im.size
    if antialias:
        size = [2*s for s in size]

    textlayer = Image.new("RGBA", size, (0,0,0,0))
    textdraw = ImageDraw.Draw(textlayer)
    textsize = textdraw.textsize(inputtext, font=font)

    # Use relative margins for values < 1
    margin = [round(margin[i]*size[i]) if margin[i] < 1 else margin[i] for i in [0,1]]

    # Calculate positions for text from position and margins
    textpos = [0, 0]
    if 'left' in position:
        textpos[0] = margin[0]
    else:
        textpos[0] = size[0]-textsize[0]-margin[0]
    if 'top' in position:
        textpos[1] = margin[1]
    else:
        textpos[1] = size[1]-textsize[1]-margin[1]

    # Draw an outline of the text if specified
    if outline:
        s = 2 if antialias else 1
        textdraw.text((textpos[0], textpos[1]-s), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0], textpos[1]+s), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0]-s, textpos[1]), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0]+s, textpos[1]), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0]-s, textpos[1]-s), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0]+s, textpos[1]-s), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0]-s, textpos[1]+s), inputtext, font=font, fill=outline)
        textdraw.text((textpos[0]+s, textpos[1]+s), inputtext, font=font, fill=outline)

    # Draw the text
    textdraw.text(textpos, inputtext, font=font, fill=color)

    if antialias:
        textlayer = textlayer.resize(im.size, resample=Image.ANTIALIAS)

    if opacity != 1:
        textlayer = ReduceOpacity(textlayer, opacity)

    return Image.composite(textlayer, im, textlayer)


def watermark(image, text, font_path, font_scale=None, font_size=None, color=(0,0,0), outline=(0,0,0),
              opacity=0.6, margin=(30, 30), position='bottom-left', antialias=True):
    """
    image - PIL Image instance
    text - text to add over image
    font_path - font that will be used
    font_scale - font size will be set as percent of image height
    """
    if font_scale and font_size:
        raise ImpropertlyConfigured("You should provide only font_scale or font_size option, but not both")
    elif font_scale:
        width, height = image.size
        font_size = int(font_scale*height)
    elif not (font_size or font_scale):
        raise ImpropertlyConfigured("You should provide font_scale or font_size option")

    if antialias:
        font_size = 2 * font_size

    font = ImageFont.truetype(font_path, font_size)
    im0 = Imprint(image, text, font=font, opacity=opacity, color=color, outline=outline, margin=margin, position=position, antialias=antialias)
    return im0
