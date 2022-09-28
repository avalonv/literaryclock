from PIL import Image, ImageFont, ImageDraw
from sys import argv
import csv

# constants
csvpath = 'litclock_annotated_br2.csv'
imgformat = 'png'       # jpeg is faster but lossy
include_metadata = True # whether to include author and title name
imagesize = (600,800)   # width/height
color_bg = 255          # white
color_norm = 125        # grey
color_high = 0          # black
fntname_norm = 'bookerly.ttf'
fntname_high = 'bookerlybold.ttf'
fntname_cite = 'baskervilleboldbt.ttf'
fntsize_cite = 25
# don't touch
imagenumber = 0
previoustime = ''


def TurnQuoteIntoImage(index:int, time:str, quote:str, timestring:str,
                                               author:str, title:str):
    global imagenumber, previoustime
    quoteheight = 720
    quotelength = 570
    quotestart_y = 0
    quotestart_x = 20

    paintedworld = Image.new(mode='L', size=(imagesize), color=color_bg)
    ariandel = ImageDraw.Draw(paintedworld)

    # draw credits
    if include_metadata:
        font_cite = ImageFont.FreeTypeFont(fntname_cite, fntsize_cite)
        citation = f'—{title.strip()}, {author.strip()}'
        citelength = 500
        citestart_y = 785
        citestart_x = 585
        if font_cite.getlength(citation) > citelength:
            citation = wrap_lines(citation, font_cite, citelength - 30)
        # the more lines there are, the higher the credits start,
        # this limits where the quote is allowed to end
        for line in citation.splitlines():
            citestart_y -= font_cite.getbbox("A")[3] + 4
        quoteheight = citestart_y - 35
        cite_y = citestart_y
        for line in citation.splitlines():
            ariandel.text((citestart_x, cite_y), line, color_high,
                                                    font_cite, anchor='rm')
            cite_y += font_cite.getbbox("A")[3] + 4

    # draw quote
    quote, fntsize = calc_fntsize(quotelength, quoteheight, quote, fntname_high)
    font_norm = ImageFont.FreeTypeFont(fntname_norm, fntsize)
    font_high = ImageFont.FreeTypeFont(fntname_high, fntsize)
    try:
        draw_quote(ariandel, (quotestart_x,quotestart_y), quote,
                                timestring, font_norm, font_high)
    except LookupError:
        print(f"WARNING: missing timestring at csv line {index+1}, skipping")
        return

    if time == previoustime:
        imagenumber += 1
    else:
        imagenumber = 0
        previoustime = time
    savepath = f'images/metadata/quote_{time}_{imagenumber}.{imgformat}'
    paintedworld.save(savepath)


def draw_quote(drawobj, anchors:tuple, text:str, substr:str,
        font_norm:ImageFont.FreeTypeFont, font_high:ImageFont.FreeTypeFont):
    # all this function does is add text to the drawobj with the substr
    # highlighted. it doesn't check if it will fit the image or anything else
    start_x = anchors[0]
    start_y = anchors[1]

    # treat text as a single line and enforce lowercase for searching
    flattened = text.replace('\n',' ')
    substr_starts = 0
    try:
        substr_starts = flattened.lower().index(substr.lower())
    except ValueError:
        raise LookupError
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
    x = start_x
    y = start_y
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
                write((x,y), wordnow, *fntstyle_norm)
                x += textlength(wordnow, font_norm)
                wordnow = word.split(head)[1]
                write((x,y), wordnow, *fntstyle_high)
                x += textlength(wordnow, font_high)
                wordnow = word.split(head)[2]
                write((x,y), wordnow, *fntstyle_norm)
                x += textlength(wordnow, font_norm)
                word = ''
            # otherwise change the default font, and wait for the next head
            elif word.count(head) == 1:
                heads_found += 1
                wordnow = word.split(head)[0]
                word = word.split(head)[1]
                write((x,y), wordnow, *fntstyle_high)
                x += textlength(wordnow, font_high)
                if heads_found == 1:
                    current_style = fntstyle_high
                else: # if heads_found == 1:
                    current_style = fntstyle_norm
            # this is the bit that actually does most of the writing
            write((x,y), word, *current_style)
            x += textlength(word, current_style[1])
        # the offset calculated by multiline_text (what we're trying to mimic)
        # is based on uppercase letter A plus 4 pixels for whatever fucking
        # reason. see https://github.com/python-pillow/Pillow/discussions/6620
        y += font_norm.getbbox("A")[3] + 4
        x = start_x


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


def calc_fntsize(length:int, height:int, text:str, fntname:str, basesize=50,
                                                              maxsize=800):
    # this will dynamically wrap and scale text with the optimal font size to
    # fill a given textbox, both length and height wise.
    # manually setting basesize to just below the mean of a sample will
    # massively reduce processing time with large batches of text, at the risk
    # of potentially wasting it with strings much larger than the mean
    # returns wrapped text and fontsize, doesn't actually draw anything

    # these are just for calculating the textbox size, they're discarded
    louvre = Image.new(mode='1', size=(0,0))
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
    # recursive call in case original basesize was too low
    boxheight = monalisa.multiline_textbbox((0,0), lines, fnt)[3]
    if boxheight > height:
        return calc_fntsize(length, height, text, fntname, basesize-5)
    return lines, fntsize


if __name__ == '__main__':
    if len(argv) > 2:
        jobs = int(argv[1])
    else:
        jobs = 0
    with open(csvpath, newline='\n') as csvfile:
        quotereader = csv.DictReader(csvfile, delimiter='|')
        i = 0
        for row in quotereader:
            if jobs and i >= jobs:
                break
            else:
                i += 1
                TurnQuoteIntoImage(i, row['time'],row['quote'], row['timestring'], row['author'], row['title'])
