from PIL import Image, ImageFont, ImageDraw
from sys import argv
import csv

imagenumber = 0
previoustime = ''
color_bg = (255,255,255)   # white
color_norm = (125,125,125) # grey
color_high = (0,0,0)       # black
# fontszie_credit = 18
# font_credit = 'baskervilleboldbt.ttf'
# font_norm = 'bookerly.ttf'
# font_high = 'bookerlybold.ttf'
# def add_credits(drawobj, author:str, title:str):

def TurnQuoteIntoImage(time:str, quote:str, timestring:str, author:str, title:str):
    global imagenumber, previoustime
    imagesize = (600,800)
    quoteheight = 720
    quotelength = 570
    credtlength = 500
    v_anchor = 0
    h_anchor = 14
    credt_v_anchor = 740
    credt_h_anchor = 575
    fntname_norm = 'bookerly.ttf'
    fntname_high = 'bookerlybold.ttf'
    fntname_credt = 'baskervilleboldbt.ttf'
    fntsize_credt = 25

    ariandel = Image.new(mode='RGB', size=(imagesize), color=color_bg)
    paintedworld = ImageDraw.Draw(ariandel)

    quote, fntsize = calc_fntsize(quotelength, quoteheight, quote, fntname_high)
    font_norm = ImageFont.FreeTypeFont(fntname_norm, fntsize)
    font_high = ImageFont.FreeTypeFont(fntname_high, fntsize)
    font_credt = ImageFont.FreeTypeFont(fntname_credt, fntsize_credt)
    highlight_substr(paintedworld, (h_anchor,v_anchor), quote,
                            timestring, font_norm, font_high)

    credtext = f'—{title.strip()}, {author.strip()}'
    if font_credt.getlength(credtext) > credtlength:
        credtext = wrap_lines(credtext, font_credt, credtlength - 30)
    # ImageDraw.multiline_text(xy, text, fill=None, font=None, anchor=None, spacing=4, align='left', direction=None, features=None, language=None, stroke_width=0, stroke_fill=None, embedded_color=False)
    # paintedworld.multiline_text((credt_h_anchor, credt_v_anchor), credtext, color_high, font_credt, align='right')
    for line in credtext.splitlines():
        paintedworld.text((credt_h_anchor, credt_v_anchor), line, color_high, font_credt, anchor='rm')
        credt_v_anchor += font_credt.getbbox("A")[3] + 4

    # if font

    if time == previoustime:
        imagenumber += 1
    else:
        imagenumber = 0
        previoustime = time
    savepath = f'images/metadata/quote_{time}_{author}.png'
    if not paintedworld == None:
        ariandel.save(savepath)
    else:
        print(f'WARNING: missing timestring for {savepath}, discarding')

def highlight_substr(drawobj, anchors:tuple, text:str, substr:str,
        font_norm: ImageFont.FreeTypeFont, font_high: ImageFont.FreeTypeFont):
    # all this function does is add text to the drawobj with the substr
    # highlighted. it doesn't check if it will fit the image or anything else
    h_anchor = anchors[0]
    v_anchor = anchors[1]

    # treat text as a single line and enforce lowercase for searching
    flattened = text.replace('\n',' ')
    substr_starts = 0
    try:
        substr_starts = flattened.lower().index(substr.lower())
    except ValueError:
        return None
    substr_ends = substr_starts + len(substr)
    head = '|'
    lines = text[:substr_starts]
    lines += f'{head}{text[substr_starts:substr_ends]}{head}'
    lines += text[substr_ends:]

    fntstyle_norm = (color_norm, font_norm)
    fntstyle_high = (color_high, font_high)
    current_style = fntstyle_norm
    heads_found = 0
    write = drawobj.text
    textlength = drawobj.textlength
    # wordnow = ''
    h_pos = h_anchor
    v_pos = v_anchor
    # this would be a LOT simpler if we didn't have to check the edges attached
    # to the substring. it might be easier to implement a char by char loop
    # in the future, using the kerning calculation method in this example:
    # https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont.getlength
    for line in lines.splitlines():
        for word in line.split():
            word += ' '
            # if the entire substr is one word, split the non-substr
            # bits stuck to it, and print the whole thing in 3 parts
            if word.count(head) == 2:
                wordnow = word.split(head)[0]
                write((h_pos, v_pos), wordnow, *fntstyle_norm)
                h_pos += textlength(wordnow, font_norm)
                wordnow = word.split(head)[1]
                write((h_pos, v_pos), wordnow, *fntstyle_high)
                h_pos += textlength(wordnow, font_high)
                wordnow = word.split(head)[2]
                write((h_pos, v_pos), wordnow, *fntstyle_norm)
                h_pos += textlength(wordnow, font_norm)
                word = ''
            # otherwise change the default font, and wait for the next head
            elif word.count(head) == 1:
                heads_found += 1
                wordnow = word.split(head)[0]
                word = word.split(head)[1]
                write((h_pos, v_pos), wordnow, *fntstyle_high)
                h_pos += textlength(wordnow, font_high)
                if heads_found == 1:
                    current_style = fntstyle_high
                else:# if heads_found == 1:
                    current_style = fntstyle_norm
            # this is the bit that actually does most of the writing
            write((h_pos, v_pos), word, *current_style)
            h_pos += textlength(word, current_style[1])
        # the offset calculated by multiline_text (what we're trying to mimic)
        # is based on uppercase letter A plus 4 pixels for whatever fucking
        # reason. see: https://github.com/python-pillow/Pillow/discussions/6620
        v_pos += font_norm.getbbox("A")[3] + 4
        h_pos = h_anchor


def wrap_lines(text:str, font:ImageFont.FreeTypeFont, line_length:int):
    # wraps lines to maximize the number of words within line_length. note
    # that lines *can* exceed line_length, this is intentional, as text looks
    # better if the font is rescaled afterwards. adapted from Chris Collett
    # https://stackoverflow.com/a/67203353/8225672
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) <= line_length:
                lines[-1] = line
            else:
                lines.append(word)
        return '\n'.join(lines)


def calc_fntsize(length:int, height:int, text:str, fntname:str, basesize=2,
                                                              maxsize=800):
    # this will dynamically wrap and scale text with the optimal font size to
    # fill a given textbox, both length and height wise. manually setting
    # basesize and maxsize can speed up calculating very large batches of text.
    # returns wrapped text and fontsize, doesn't actually draw anything

    # these are just for calculating the textbox size, they're discarded
    louvre = Image.new(mode='RGB', size=(0,0))
    monalisa = ImageDraw.Draw(louvre)

    lines = ''
    fntsize = basesize
    fnt = ImageFont.truetype(fntname, fntsize)
    boxheight = 0
    while not boxheight > height and not fntsize > maxsize:
        fntsize += 1
        fnt = fnt.font_variant(size=fntsize)
        lines = wrap_lines(text, fnt, length)
        boxheight = monalisa.multiline_textbbox((0,0), lines, fnt)[3]

    fntsize -= 1
    fnt = fnt.font_variant(size=fntsize)
    lines = wrap_lines(text, fnt, length)
    boxlength = monalisa.multiline_textbbox((0,0), lines, fnt)[2]
    while boxlength > length:
        # note: this is a sanity check. we intentionally don't reformat lines
        # here, as wrap_lines only checks if its output is *longer* than length,
        # which can produce a recursive loop where lines always get wrapped
        # into something longer, leading to overly small and unreadable fonts
        fntsize -= 1
        fnt = fnt.font_variant(size=fntsize)
        boxlength = monalisa.multiline_textbbox((0,0), lines, fnt)[2]
    return lines, fntsize

if __name__ == '__main__':
    if len(argv) > 2:
        jobs = int(argv[1])
    else:
        jobs = 50
    with open('litclock_annotated_br2.csv', newline='\n') as csvfile:
        quotereader = csv.DictReader(csvfile, delimiter='|')
        i = 0
        for row in quotereader:
            if i >= jobs:
            # if i >= 100:
                break
            else:
                i += 1
                TurnQuoteIntoImage(row['time'],row['quote'], row['timestring'], row['author'], row['title'])
    # text = "Midnight, and there was frost on the fields and patches of black ice on a road notorious for its accidents—there were bunches of dead flowers tied to fence posts and telegraph poles, and torn gaps in hedges, like some kind of failed crop."
    # font = ImageFont.FreeTypeFont('bookerly.ttf', 53)
    # print("...\n\n\n...")
    # print(wrap_lines(text, font, 570))
