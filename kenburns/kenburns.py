from PIL import Image, ImageFont, ImageDraw
from subprocess import Popen, PIPE, STDOUT
import StringIO
import time
import random

def add1(img, text, font, size, f, t, i):
    if not f<=i<=t: return img
    ox, oy =  img.size
    txt = Image.new('RGBA', img.size, (255,255,255,0))
    font = ImageFont.truetype(font, size)
    draw = ImageDraw.Draw(txt)
    tw, th = draw.textsize(text, font=font)
    edge = min(i-f, t-i)
    if 1.0*edge/(t-f) < .15: opacity = int(255*edge/(.15*(t-f)))
    else: opacity = 255
    draw.text(((ox-tw)/2, (oy-th)/3), text, fill=(255, 255, 255, opacity), font=font)
    return Image.alpha_composite(img, txt)

def add2(img, text, font, size, f, t, i):
    back_file = 'resources/back.png'
    if not f<=i<=t: return img
    ox, oy =  img.size
    txt = Image.new('RGBA', img.size, (255,255,255,0))
    back = Image.open(back_file)
    font = ImageFont.truetype(font, size)
    tw, th = ImageDraw.Draw(back).textsize(text, font=font)
    back = back.resize((img.size[0], th*3))
    draw = ImageDraw.Draw(back)
    draw.text(((back.size[0]-tw)/2, (back.size[1]-th)/2), text, fill="black", font=font)
    txt.paste(back, ((img.size[0] - back.size[0]) / 2, 5*(img.size[1] - back.size[1]) / 6))
    empty = Image.new('RGBA', txt.size, (255,255,255,0))
    edge = min(i-f, t-i)
    if 1.0*edge/(t-f) < .15: opacity = edge/(.15*(t-f))
    else: opacity = 1
    txt = Image.blend(empty, txt, opacity)
    return Image.alpha_composite(img, txt)
    

def make(layers, dst, img_files, duration, fps):

    width = 1080
    height = 720
    # width = 720
    # height = 576

    factor = 1.0*width/height

    
    
    cmd = ['ffmpeg', '-loglevel', 'info', '-y', '-threads', 'auto', '-f', 'image2pipe', '-vcodec', 'ppm', '-s', '%sx%s' % (width, height), '-r', str(fps), '-i', '-', '-vcodec', 'libx264', dst]

    p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)

    X = 0
    Y = 0

    bg_image = Image.new('RGB', (width, height))
    curr_img_file = None
    for i in range(duration*fps):
        result = bg_image.copy()
        # img = image.copy().convert('RGBA')

        for img_file, f, t in img_files:
            if f<=i+1<=t:
                if curr_img_file!=img_file:
                    counter = -1
                    image = Image.open(img_file).convert('RGBA')
                    w, h = image.size
                    if 1.0*w/h<factor: image = image.resize((w*height/h, height), Image.ANTIALIAS)
                    else: image = image.resize((width, width*h/w), Image.ANTIALIAS)
                    cw, ch = image.size
                curr_img_file = img_file
                break
                
        
        if i-f<(t-f)/2: counter += 1 
        else: counter -= 1        
        x, y, w, h = counter, counter, 1.0*cw*(ch-2*counter)/ch, ch-2*counter 
        img = image.crop((x, y, min(x+int(w), cw), min(y+h, ch)))
        print((int(w), h), img.size)
        img = img.resize((cw, ch), Image.ANTIALIAS)

        funcs = {'add1': add1, 'add2': add2}
        for func, text, font, size, f, t in layers:
            if not func: continue
            func = funcs[func]
            img = func(img, text, font, size, f, t, i)
        
        result.paste(img, ((result.size[0] - img.size[0]) / 2, (result.size[1] - img.size[1]) / 2))        
        output = StringIO.StringIO()
        result.save(output, 'ppm')
        p.stdin.write(output.getvalue())
    out, err = p.communicate()
    
if __name__=='__main__':

    make([
        ['add1', 'Title', 'DejaVuSerif', 50, 10, 100],
        ['add2', 'Text 1', 'DejaVuSans', 30, 110, 200],
        ['add2', 'Text 2', 'LiberationSans-Regular', 30, 201, 291],
        ['add2', 'Text 2', 'LiberationSans-Regular', 30, 201, 291],
        ['add2', 'Text 3', 'LiberationSans-Regular', 30, 292, 380],
    ], dst='resources/out.mp4', img_files=[('resources/a.jpg', 0, 50), ('resources/b.jpg', 51, 375)] , duration=15, fps=25)