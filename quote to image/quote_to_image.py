from PIL import Image, ImageFont, ImageDraw
import csv

imagenumber = 0
previoustime = ''

def TurnQuoteIntoImage(time, quote, timestring, fname=None, title=None, author=None):
    global imagenumber, previoustime
    imagesize = (600,800)
    quoteheight = 745
    quotelength = 570
    c_fnt1 = (125,125,125) # grey
    c_fnt2 = (0,0,0)       # black
    c_bg = (255,255,255)   # white
    fntname1 = 'bookerly.ttf'
    fntname2 = 'bookerlybold.ttf'

    ariandel = Image.new(mode='RGB', size=(imagesize), color=c_bg)
    paintedworld = ImageDraw.Draw(ariandel)

    timestr_lenght = len(timestring.split())
    timestr_starts = len(quote[0:quote.find(timestring)].split())
    timestr_ends = timestr_starts + timestr_lenght

    wrp_lines, fntsize = fill_textbox(quotelength, quoteheight, quote, fntname1)
    fnt1 = ImageFont.FreeTypeFont(fntname1, fntsize)
    fnt2 = ImageFont.FreeTypeFont(fntname2, fntsize)

    v_anchor = 0
    h_anchor = 18
    h_offset = h_anchor
    v_offset = v_anchor
    index = 0
    # for line in wrp_lines.splitlines():
    #     for word in line.split():
    #         word += ' '
    #         if index in range(timestr_starts, timestr_ends):
    #             fnt = fnt2
    #             color = c_fnt2
    #         else:
    #             fnt = fnt1
    #             color = c_fnt1
    #         paintedworld.text((h_offset, v_offset), word, color, font=fnt)
    #         h_offset += paintedworld.textlength(word, fnt)
    #         index += 1
    #     # the offset calculated by multiline_text (what we're trying to mimic)
    #     # is based on uppercase letter A plus 4 pixels for whatever fucking
    #     # reason. see: https://github.com/python-pillow/Pillow/discussions/6620
    #     v_offset += fnt1.getbbox("A")[3] + 4
    #     h_offset = h_anchor
    # # paintedworld.multiline_text((h_anchor, v_anchor), lines, color_normal, fnt)

    for line in wrp_lines.splitlines():
        word = ''
        for char in line:
            if char == ' ':
                word += ' '
                paintedworld.text((h_offset, v_offset), word, c_fnt1, font=fnt1)
                h_offset += paintedworld.textlength(word, fnt1)
                word = ''
            else:
                word += char
            index += 1
        paintedworld.text((h_offset, v_offset), word, c_fnt1, font=fnt1)
        h_offset = h_anchor
        v_offset += fnt1.getbbox("A")[3] + 4

    if time == previoustime:
        imagenumber += 1
    else:
        imagenumber = 0
        previoustime = time
    savepath = f'images/test/quote_{time}_{fname}.png'
    print(savepath)
    ariandel.save(savepath)
    # ariandel.show()


def wrap_lines(text:str, font:ImageFont.FreeTypeFont, line_length:int):
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


def fill_textbox(length:int, height:int, text:str, fntname:str, basesize=2,
                                                              maxsize=1000):
    # this will dynamically wrap and scale text with the optimal font size to
    # fill a given textbox, both length and height wise. manually setting
    # basesize and maxsize can speed up calculating very large batches of text.
    # returns wrapped text and a ImageFont.FreeTypeFont object

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
        if i >= 50:
        # if i >= 100:
            break
        else:
            i += 1
            TurnQuoteIntoImage(row['time'],row['quote'], row['timestring'], row['author'])
