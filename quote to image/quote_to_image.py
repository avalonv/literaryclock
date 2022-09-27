from PIL import Image, ImageFont, ImageDraw
import csv

jobs = 50
imagenumber = 0
previoustime = ''

def TurnQuoteIntoImage(time, quote, timestring, fname=None, title=None, author=None):
    global imagenumber, previoustime
    imagesize = (600,800)
    quoteheight = 745
    quotelength = 570
    v_anchor = 0
    h_anchor = 18
    c_fnt1 = (125,125,125) # grey
    c_fnt2 = (0,0,0)       # black
    c_bg = (255,255,255)   # white
    fntname1 = 'bookerly.ttf'
    fntname2 = 'bookerlybold.ttf'

    ariandel = Image.new(mode='RGB', size=(imagesize), color=c_bg)
    paintedworld = ImageDraw.Draw(ariandel)

    if time == previoustime:
        imagenumber += 1
    else:
        imagenumber = 0
        previoustime = time
    savepath = f'images/test2/quote_{time}_{fname}.png'

    # the case and timestring can be mismatched. Checking this is very important
    timestr_starts = 0
    try:
        timestr_starts = quote.lower().index(timestring.lower())
    except ValueError:
        print(f'WARNING: missing timestring for {savepath}, discarding')
        return

    timestr_ends = timestr_starts + len(timestring)

    quote, fntsize = calc_fntsize(quotelength, quoteheight, quote, fntname1)
    fnt1 = ImageFont.FreeTypeFont(fntname1, fntsize)
    fnt2 = ImageFont.FreeTypeFont(fntname2, fntsize)

    # sandwich timestring in heads so it's easy to to find later
    head = '<|*_*|>'
    lines = quote[:timestr_starts]
    lines += f'{head}{quote[timestr_starts:timestr_ends]}{head}'
    lines += quote[timestr_ends:]

    g_fnt = fnt1
    g_color = c_fnt1
    h_pos = h_anchor
    v_pos = v_anchor
    heads_found = 0
    in_timestring = False
    write = paintedworld.text
    textlength = paintedworld.textlength
    wordnow = ''
    for line in lines.splitlines():
        for word in line.split():
            word += ' '
            # if the entire timestring is one word, split the non-timestr
            # bits stuck to it, and print the whole thing in 3 parts
            if word.count(head) == 2:
                wordnow = word.split(head)[0]
                write((h_pos, v_pos), wordnow, c_fnt1, font=fnt1)
                h_pos += textlength(wordnow, fnt1)
                wordnow = word.split(head)[1]
                write((h_pos, v_pos), wordnow, c_fnt2, font=fnt2)
                h_pos += textlength(wordnow, fnt2)
                wordnow = word.split(head)[2]
                write((h_pos, v_pos), wordnow, c_fnt1, font=fnt1)
                h_pos += textlength(wordnow, fnt1)
                word = ''
                heads_found += 2
            # otherwise change the font, and wait for the next head
            elif word.count(head) == 1:
                if heads_found == 0:
                    in_timestring = True
                    g_fnt = fnt2
                    g_color = c_fnt2
                    wordnow = word.split(head)[0]
                    word = word.split(head)[1]
                if heads_found == 1:
                    in_timestring = False
                    wordnow = word.split(head)[0]
                    word = word.split(head)[1]
                write((h_pos, v_pos), wordnow, c_fnt2, font=fnt2)
                h_pos += textlength(wordnow, g_fnt)
                heads_found += 1
            if in_timestring:
                g_fnt = fnt2
                g_color = c_fnt2
            elif not in_timestring:
                g_fnt = fnt1
                g_color = c_fnt1
            # this is the bit that actually does most of the writing
            write((h_pos, v_pos), word, g_color, font=g_fnt)
            h_pos += textlength(word, g_fnt)
        # the offset calculated by multiline_text (what we're trying to mimic)
        # is based on uppercase letter A plus 4 pixels for whatever fucking
        # reason. see: https://github.com/python-pillow/Pillow/discussions/6620
        v_pos += fnt1.getbbox("A")[3] + 4
        h_pos = h_anchor

    ariandel.save(savepath)
    # ariandel.show()


def wrap_lines(text:str, font:ImageFont.FreeTypeFont, line_length:int,
                                                         strict=False):
    # wraps lines to maximize the number of words within line_length. note
    # that long words or a big font can easily exceed line_length, you still
    # need to check the bbox size elsewhere. adapted from Chris Collett
    # https://stackoverflow.com/a/67203353/8225672
        lines = ['']
        for word in text.split():
            line = f'{lines[-1]} {word}'.strip()
            if font.getlength(line) < line_length:
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

with open('litclock_annotated_br2.csv', newline='\n') as csvfile:
    quotereader = csv.DictReader(csvfile, delimiter='|')
    i = 0
    for row in quotereader:
        if i >= jobs:
        # if i >= 100:
            break
        else:
            i += 1
            TurnQuoteIntoImage(row['time'],row['quote'], row['timestring'], row['author'])
