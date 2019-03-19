#!/usr/bin/env python3

#####################################################################
# NsCDE: nscde_palette_colorgen.py
#
# Purpose: Generate Motif/CDE colorset definitions from CDE palettes
#          for fvwm Colorsets, X defaults, dynamic pixmaps and for
#          CDE/CDE-style backdrops
#
# Based on: motifcolors.py from Jos Van Riswick
# Adapted by: M. Z.
#####################################################################

import re
import os
import sys
import shutil
import getopt

bg=[0,0,0,0,0,0,0,0,0]
fg=[0,0,0,0,0,0,0,0,0]
bs=[0,0,0,0,0,0,0,0,0]
ts=[0,0,0,0,0,0,0,0,0]
sel=[0,0,0,0,0,0,0,0,0]

# Exact Motif color values from Xm.h
XmCOLOR_LITE_SEL_FACTOR=15
XmCOLOR_LITE_BS_FACTOR=40
XmCOLOR_LITE_TS_FACTOR=20
XmCOLOR_LO_SEL_FACTOR=15
XmCOLOR_LO_BS_FACTOR=60
XmCOLOR_LO_TS_FACTOR=50
XmCOLOR_HI_SEL_FACTOR=15
XmCOLOR_HI_BS_FACTOR=40
XmCOLOR_HI_TS_FACTOR=60
XmCOLOR_DARK_SEL_FACTOR=15
XmCOLOR_DARK_BS_FACTOR=30
XmCOLOR_DARK_TS_FACTOR=50
XmRED_LUMINOSITY=0.30
XmGREEN_LUMINOSITY=0.59
XmBLUE_LUMINOSITY=0.11
XmINTENSITY_FACTOR=75
XmLIGHT_FACTOR=0
XmLUMINOSITY_FACTOR=25
XmMAX_SHORT=65535
XmDEFAULT_DARK_THRESHOLD=20
XmDEFAULT_LIGHT_THRESHOLD=93
XmDEFAULT_FOREGROUND_THRESHOLD=70
XmCOLOR_PERCENTILE = (XmMAX_SHORT / 100)
XmCOLOR_LITE_THRESHOLD = XmDEFAULT_LIGHT_THRESHOLD* XmCOLOR_PERCENTILE
XmCOLOR_DARK_THRESHOLD = XmDEFAULT_DARK_THRESHOLD* XmCOLOR_PERCENTILE
XmFOREGROUND_THRESHOLD = XmDEFAULT_FOREGROUND_THRESHOLD* XmCOLOR_PERCENTILE

HEX=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
HEXNUM=[4096,256,16,1]

def int2hex(n):
    if n==0: return '0000'
    h=''
    for a in HEXNUM:
        i=int(float(n)/a)
        h+=HEX[i]
        n-=i*a
    return h

def encode16bpp(color):
    match=re.search('#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$',color)
    if match:
        a=match.group(1)
        b=match.group(2)
        c=match.group(3)
        return """#{a}{a}{b}{b}{c}{c}""".format(**locals())
    match=re.search('#[0-9a-fA-F]{12}$',color)
    if match:
        return color
    return "#888888888888";

# convert to rgb array
def bbpToRGB(hexcolor):
    rgb=[]
    match=re.search('#(....)(....)(....)',hexcolor)
    if match:
        rgb.append(int(match.group(1),16))
        rgb.append(int(match.group(2),16))
        rgb.append(int(match.group(3),16))
        return rgb
    match=re.search('#(..)(..)(..)',hexcolor)
    if match:
        rgb.append(int(match.group(1),16))
        rgb.append(int(match.group(2),16))
        rgb.append(int(match.group(3),16))
        return rgb
    return [0,0,0]

def Brightness(color):
    red = color[0]
    green = color[1]    
    blue = color[2]
    intensity = (red + green + blue) / 3.0
    luminosity = int ((XmRED_LUMINOSITY * red) + (XmGREEN_LUMINOSITY * green) + (XmBLUE_LUMINOSITY * blue))
    ma=0
    if red>green:
        if red>blue: ma=red
        else: ma=blue
    else:
        if green>blue: ma=green
        else: ma=blue
    mi=0
    if red<green:
        if red<blue:mi=red
        else: mi=blue
    else:
        if green<blue:mi=green
        else: mi=blue
    light = (mi+ ma) / 2.0
    brightness = ( (intensity * XmINTENSITY_FACTOR) + (light * XmLIGHT_FACTOR) + (luminosity * XmLUMINOSITY_FACTOR) ) / 100.0
    return brightness

def CalculateColorsForDarkBackground(bg_color):
    fg_color=[0,0,0]
    sel_color=[0,0,0]
    bs_color=[0,0,0]
    ts_color=[0,0,0]
    brightness=Brightness(bg_color)
    if brightness > XmFOREGROUND_THRESHOLD:
        fg_color[0]= 0 
        fg_color[1]= 0 
        fg_color[2]= 0
    else:
        fg_color[0]= XmMAX_SHORT 
        fg_color[1]= XmMAX_SHORT 
        fg_color[2]= XmMAX_SHORT
    color_value = bg_color[0] 
    color_value += XmCOLOR_DARK_SEL_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    sel_color[0] = color_value
    color_value = bg_color[1] 
    color_value += XmCOLOR_DARK_SEL_FACTOR * (XmMAX_SHORT - color_value) / 100.0    
    sel_color[1] = color_value
    color_value = bg_color[2] 
    color_value += XmCOLOR_DARK_SEL_FACTOR * (XmMAX_SHORT - color_value) / 100.0
    sel_color[2] = color_value
    color_value = bg_color[0] 
    color_value += XmCOLOR_DARK_BS_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    bs_color[0] = color_value
    color_value = bg_color[0]
    color_value += XmCOLOR_DARK_BS_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    bs_color[1] = color_value
    color_value = bg_color[2]
    color_value += XmCOLOR_DARK_BS_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    bs_color[2] = color_value
    color_value = bg_color[0]
    color_value += XmCOLOR_DARK_TS_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    ts_color[0] = color_value
    color_value = bg_color[1]
    color_value += XmCOLOR_DARK_TS_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    ts_color[1] = color_value
    color_value = bg_color[2]
    color_value += XmCOLOR_DARK_TS_FACTOR * (XmMAX_SHORT - color_value) / 100.0 
    ts_color[2] = color_value
    return fg_color,sel_color,bs_color,ts_color

def CalculateColorsForLightBackground(bg_color):
    fg_color=[0,0,0]
    sel_color=[0,0,0]
    bs_color=[0,0,0]
    ts_color=[0,0,0]
    brightness=Brightness(bg_color)
    if (brightness > XmFOREGROUND_THRESHOLD):
        fg_color[0] = 0
        fg_color[1] = 0
        fg_color[2] = 0
    else:
        fg_color[0] = XmMAX_SHORT
        fg_color[1] = XmMAX_SHORT
        fg_color[2] = XmMAX_SHORT
    color_value = bg_color[0]
    color_value -= (color_value * XmCOLOR_LITE_SEL_FACTOR) / 100.0
    sel_color[0] = color_value
    color_value = bg_color[1]
    color_value -= (color_value * XmCOLOR_LITE_SEL_FACTOR) / 100.0
    sel_color[1] = color_value
    color_value = bg_color[2]
    color_value -= (color_value * XmCOLOR_LITE_SEL_FACTOR) / 100.0
    sel_color[2] = color_value
    color_value = bg_color[0]
    color_value -= (color_value * XmCOLOR_LITE_BS_FACTOR) / 100.0
    bs_color[0] = color_value
    color_value = bg_color[1]
    color_value -= (color_value * XmCOLOR_LITE_BS_FACTOR) / 100.0
    bs_color[1] = color_value
    color_value = bg_color[2]
    color_value -= (color_value * XmCOLOR_LITE_BS_FACTOR) / 100.0
    bs_color[2] = color_value
    color_value = bg_color[0]
    color_value -= (color_value * XmCOLOR_LITE_TS_FACTOR) / 100.0
    ts_color[0] = color_value
    color_value = bg_color[1]
    color_value -= (color_value * XmCOLOR_LITE_TS_FACTOR) / 100.0
    ts_color[1] = color_value
    color_value = bg_color[2]
    color_value -= (color_value * XmCOLOR_LITE_TS_FACTOR) / 100.0
    ts_color[2] = color_value
    return (fg_color,sel_color,bs_color,ts_color)

def CalculateColorsForMediumBackground(bg_color):
    fg_color=[0,0,0]
    sel_color=[0,0,0]
    bs_color=[0,0,0]
    ts_color=[0,0,0]
    brightness=Brightness(bg_color)
    if (brightness > XmFOREGROUND_THRESHOLD):
        fg_color[0] = 0
        fg_color[1] = 0
        fg_color[2] = 0
    else:
        fg_color[0] = XmMAX_SHORT
        fg_color[1] = XmMAX_SHORT
        fg_color[2] = XmMAX_SHORT
    f = XmCOLOR_LO_SEL_FACTOR + (brightness * ( XmCOLOR_HI_SEL_FACTOR - XmCOLOR_LO_SEL_FACTOR ) / XmMAX_SHORT)
    color_value = bg_color[0]
    color_value -= (color_value * f) / 100.0
    sel_color[0] = color_value
    color_value = bg_color[1]
    color_value -= (color_value * f) / 100.0
    sel_color[1] = color_value
    color_value = bg_color[2]
    color_value -= (color_value * f) / 100.0
    sel_color[2] = color_value
    f = XmCOLOR_LO_BS_FACTOR + (brightness * ( XmCOLOR_HI_BS_FACTOR - XmCOLOR_LO_BS_FACTOR ) / XmMAX_SHORT)
    color_value = bg_color[0]
    color_value -= (color_value * f) / 100.0
    bs_color[0] = color_value
    color_value = bg_color[1]
    color_value -= (color_value * f) / 100.0
    bs_color[1] = color_value
    color_value = bg_color[2]
    color_value -= (color_value * f) / 100.0
    bs_color[2] = color_value
    f = XmCOLOR_LO_TS_FACTOR + (brightness * ( XmCOLOR_HI_TS_FACTOR - XmCOLOR_LO_TS_FACTOR ) / XmMAX_SHORT)
    color_value = bg_color[0]
    color_value += f * ( XmMAX_SHORT - color_value ) / 100.0
    ts_color[0] = color_value
    color_value = bg_color[1]
    color_value += f * ( XmMAX_SHORT - color_value ) / 100.0
    ts_color[1] = color_value
    color_value = bg_color[2]
    color_value += f * ( XmMAX_SHORT - color_value ) / 100.0
    ts_color[2] = color_value
    return (fg_color,sel_color,bs_color,ts_color)


def rgbToHex(rgb):
    a=int2hex(rgb[0])
    b=int2hex(rgb[1])
    c=int2hex(rgb[2])
    return """#{a}{b}{c}""".format(**locals())

def equal_colors_ab(a,b):
    bg[a]=bg[b]
    fg[a]=fg[b]
    bs[a]=bs[b]
    ts[a]=ts[b]
    sel[a]=sel[b]
    

def initcolors(palette):
    for a in range(1,9):
        color16=encode16bpp(palette[a-1])
        bg_color=bbpToRGB(color16)
        backgroundbrightness=Brightness(bg_color)
        if backgroundbrightness< XmCOLOR_DARK_THRESHOLD:
            (fg_color,sel_color,bs_color,ts_color)= CalculateColorsForDarkBackground(bg_color)
        elif backgroundbrightness> XmCOLOR_LITE_THRESHOLD:
            (fg_color,sel_color,bs_color,ts_color)= CalculateColorsForLightBackground(bg_color)
        else:
            (fg_color,sel_color,bs_color,ts_color)= CalculateColorsForMediumBackground(bg_color)
        # bg[a]=encode16bpp(palette[a-1])
        bg[a]=color16
        fg[a]=rgbToHex(fg_color)
        bs[a]=rgbToHex(bs_color)
        ts[a]=rgbToHex(ts_color)
        sel[a]=rgbToHex(sel_color)
    if use_4_colors:
        equal_colors_ab(5,2)
        equal_colors_ab(6,2)
        equal_colors_ab(8,2)
        equal_colors_ab(7,2)

def round_colors_6():
    for a in range(1,9):
        bg[a]='#'+bg[a][1:3]+bg[a][5:7]+bg[a][9:11]
        fg[a]='#'+fg[a][1:3]+fg[a][5:7]+fg[a][9:11]
        bs[a]='#'+bs[a][1:3]+bs[a][5:7]+bs[a][9:11]
        ts[a]='#'+ts[a][1:3]+ts[a][5:7]+ts[a][9:11]
        sel[a]='#'+sel[a][1:3]+sel[a][5:7]+sel[a][9:11]

def readPalette(filename):
    with open(filename) as f:lines=f.read().splitlines() 
    return lines
    
use_4_colors=False

def readMotifColors2(n,filename):
    global use_4_colors
    palette=readPalette(filename)
    if n==4: 
        use_4_colors=True
    else: 
        use_4_colors=False
    initcolors(palette)
    # round_colors_6()
    colors={}
    for a in range(1,9):
        colors['bg_color_'+str(a)]=bg[a]
        colors['fg_color_'+str(a)]=fg[a]
        colors['ts_color_'+str(a)]=ts[a]
        colors['bs_color_'+str(a)]=bs[a]
        colors['sel_color_'+str(a)]=sel[a]
    return colors

#######################
# End program functions
#######################
def genfvwmcolorset(palettefile,ncolors):
    palette=readPalette(palettefile)
    global use_4_colors
    if ncolors == 4: 
        use_4_colors=True
    else: 
        use_4_colors=False
    initcolors(palette)
    bgg=bg
    tsg=ts
    bsg=bs
    fgg=fg
    selg=sel
    basename=os.path.basename(palettefile)
    palettename=basename.split(".dp")
    lines=''
    lines+="""##############################################
# NsCDE - Not so Common Desktop Environment
# Theme: {palettename[0]}, Colors: {ncolors}
##############################################

UnsetEnv NSCDE_PALETTE
SetEnv NSCDE_PALETTE {basename}

UnsetEnv NSCDE_PALETTE_NCOLORS
SetEnv NSCDE_PALETTE_NCOLORS {ncolors}

# Bare default (should not be seen at all)
Colorset 0 fg {fgg[3]}, bg {selg[8]}

# Inactive windows and default widget fg/bg/sh/hi, regular menu, window borders
Colorset 1 fg {fgg[2]}, bg {bgg[2]}, hi {tsg[2]}, sh {bsg[2]}, fgsh {selg[2]}, Plain, NoShape

# Active, focused windows, titlebar of FrontPanelPager, active window borders
Colorset 2 fg {fgg[1]}, bg {bgg[1]}, hi {tsg[1]}, sh {bsg[1]}, fgsh {selg[1]}, Plain, NoShape

# Hilight menu (main menu selected), Subpanels of front panel selected, mousover baloons
Colorset 4 fg {fgg[2]}, bg {selg[2]}, hi {tsg[2]}, sh {bsg[2]}, fgsh {bsg[2]}, Plain, NoShape

# Grayed / disabled menu
Colorset 5 fg grey40, bg {bgg[2]}

############################
# NsCDE additional Colorsets
############################

# For FvwmScript: TextField and List widgets
Colorset 20 fg {fgg[4]}, bg {bgg[4]}, hi {tsg[4]}, sh {bsg[4]}, fgsh {selg[4]}, Plain, NoShape

# 2nd windows color when Colors == 8
# Colorset 21 fg {fgg[2]}, bg {bgg[5]}, hi {tsg[5]}, sh {bsg[5]}, fgsh {selg[5]}, Plain, NoShape
# Colorset 21 fg {fgg[2]}, bg {bgg[5]}, hi {tsg[2]}, sh {bsg[2]}, fgsh {selg[2]}, Plain, NoShape
Colorset 21 fg #ffffffffffff, bg {bgg[5]}, hi {tsg[5]}, sh {bsg[5]}, fgsh {selg[5]}, Plain, NoShape

# 2nd Color for transient windows when Colors == 8
Colorset 22 fg {fgg[6]}, bg {bgg[6]}, hi {tsg[6]}, sh {bsg[6]}, fgsh {bsg[6]}, Plain, NoShape

# FrontPanel Press Indicator Large
Colorset 24 Pixmap $[FVWM_USERDIR]/icons/NsCDE/SelectedL.xpm
# FrontPanel Press Indicator Small
Colorset 25 Pixmap $[FVWM_USERDIR]/icons/NsCDE/SelectedS.xpm
# FrontPanel Menus Press Indicator
Colorset 26 Pixmap $[FVWM_USERDIR]/icons/NsCDE/SelectedXL.xpm
# FrontPanel Subpanel Launcher Press Indicator
Colorset 27 Pixmap $[FVWM_USERDIR]/icons/NsCDE/PressedFPL.xpm
# Pressed Button on Colorset 21 (Style Manager)
Colorset 28 fg {fgg[5]}, bg {selg[5]}, hi {bsg[5]}, sh {tsg[5]}, fgsh {selg[5]}, Plain, NoShape
# Last Pressed Button on Front Panel
Colorset 29 Pixmap $[FVWM_USERDIR]/icons/NsCDE/LastPressedFPB.xpm
    """.format(**locals())

    if ncolors == 8:
        lines+="""
# Workspace Manager Buttons: Even - pressed/active, Odd - inactive
# One, Five ...
Colorset 40 fg #ffffffffffff, bg {bgg[3]}, hi {tsg[3]}, sh {bsg[3]}, fgsh #330033003300, Plain, NoShape
Colorset 41 fg #ffffffffffff, bg {bgg[3]}, hi {bsg[3]}, sh {tsg[3]}, fgsh #330033003300, Plain, NoShape
# Two, Six ...
Colorset 42 fg #ffffffffffff, bg {bgg[5]}, hi {tsg[5]}, sh {bsg[5]}, fgsh #330033003300, Plain, NoShape
Colorset 43 fg #ffffffffffff, bg {bgg[5]}, hi {bsg[5]}, sh {tsg[5]}, fgsh #330033003300, Plain, NoShape
# Three, Seven ...
Colorset 44 fg #ffffffffffff, bg {bgg[6]}, hi {tsg[6]}, sh {bsg[6]}, fgsh #330033003300, Plain, NoShape
Colorset 45 fg #ffffffffffff, bg {bgg[6]}, hi {bsg[6]}, sh {tsg[6]}, fgsh #330033003300, Plain, NoShape
# Four, Eight ...
Colorset 46 fg #ffffffffffff, bg {bgg[7]}, hi {tsg[7]}, sh {bsg[7]}, fgsh #330033003300, Plain, NoShape
Colorset 47 fg #ffffffffffff, bg {bgg[7]}, hi {bsg[7]}, sh {tsg[7]}, fgsh #330033003300, Plain, NoShape

# Exception from Colorset 1: BorderColorset of FrontPanel to be as close as possible to CDE FrontPanel
Colorset 48 fg {fgg[2]}, bg {bgg[2]}, hi {tsg[2]}, sh {bgg[2]}, fgsh {selg[2]}, Plain, NoShape

# Exception from Colorset 1: Panel SubMenus Font Shadow darker (fgsh == sel_color_3)
Colorset 49 fg #ffffffffffff, bg {bgg[5]}, hi {tsg[2]}, sh {bsg[2]}, fgsh #330033003300, Plain, NoShape
        """.format(**locals())

    elif ncolors == 4:
        lines+="""
# Workspace Manager Buttons: Even - pressed/active, Odd - inactive
# One, Five ...
Colorset 40 fg #ffffffffffff, bg {bgg[3]}, hi {tsg[3]}, sh {bsg[3]}, fgsh #330033003300, Plain, NoShape
Colorset 41 fg #ffffffffffff, bg {bgg[3]}, hi {bsg[3]}, sh {tsg[3]}, fgsh #330033003300, Plain, NoShape
# Two, Six ...
Colorset 42 fg #ffffffffffff, bg {bgg[3]}, hi {tsg[3]}, sh {bsg[3]}, fgsh #330033003300, Plain, NoShape
Colorset 43 fg #ffffffffffff, bg {bgg[3]}, hi {bsg[3]}, sh {tsg[3]}, fgsh #330033003300, Plain, NoShape
# Three, Seven ...
Colorset 44 fg #ffffffffffff, bg {bgg[3]}, hi {tsg[3]}, sh {bsg[3]}, fgsh #330033003300, Plain, NoShape
Colorset 45 fg #ffffffffffff, bg {bgg[3]}, hi {bsg[3]}, sh {tsg[3]}, fgsh #330033003300, Plain, NoShape
# Four, Eight ...
Colorset 46 fg #ffffffffffff, bg {bgg[3]}, hi {tsg[3]}, sh {bsg[3]}, fgsh #330033003300, Plain, NoShape
Colorset 47 fg #ffffffffffff, bg {bgg[3]}, hi {bsg[3]}, sh {tsg[3]}, fgsh #330033003300, Plain, NoShape

# Exception from Colorset 1: BorderColorset of FrontPanel to be as close as possible to CDE FrontPanel
Colorset 48 fg {fgg[2]}, bg {bgg[2]}, hi {tsg[2]}, sh {bgg[2]}, fgsh {selg[2]}, Plain, NoShape

# Exception from Colorset 1: Panel SubMenus Font Shadow darker (fgsh == sel_color_3)
Colorset 49 fg #ffffffffffff, bg {bgg[5]}, hi {tsg[2]}, sh {bsg[2]}, fgsh #330033003300, Plain, NoShape
        """.format(**locals())

    lines+="""
# Transparent handler (WSM, MonthDayApplet, CheckMailApplet ...)
Colorset 52 fg #ffffffffffff, Transparent

# For ItemDraw Widget of FvwmScript (used in WSM)
Colorset 53 fg #000000000000, bg #000000000000, hi #000000000000, sh #000000000000

# Colorset for test indicators
Colorset 50 fg red, bg green, hi blue, sh yellow
    """.format(**locals())

    print (lines)

def gencdebackdrop(palettefile,ncolors,infile,palettepart):
    palette=readPalette(palettefile)
    global use_4_colors
    if ncolors == 4: 
        use_4_colors=True
    else: 
        use_4_colors=False
    initcolors(palette)
    bgg=bg
    tsg=ts
    bsg=bs
    fgg=fg
    selg=sel
    basename=os.path.basename(palettefile)

    buf_infile = open(infile, 'r')
    for line in buf_infile:
        line = re.sub('s background(.*) m(.*) c (.*)', r's background \1 m \2 c ' + bgg[palettepart] + '",', line)
        line = re.sub('s foreground(.*) m(.*) c (.*)', r's foreground \1 m \2 c ' + fgg[palettepart] + '",', line)
        line = re.sub('s topShadowColor(.*) m(.*) c (.*)', r's topShadowColor \1 m \2 c ' + tsg[palettepart] + '",', line)
        line = re.sub('s bottomShadowColor(.*) m(.*) c (.*)', r's bottomShadowColor \1 m \2 c ' + bsg[palettepart] + '",', line)
        line = re.sub('s selectColor(.*) m(.*) c (.*)', r's selectColor \1 m \2 c ' + selg[palettepart] + '",', line)
        sys.stdout.write (line)
    buf_infile.close()
    sys.stdout.flush()

def gencdecolors(palettefile,n,infile,shorten_colorhex):
    palette=readPalette(palettefile)
    global use_4_colors
    if n==4: 
        use_4_colors=True
    else: 
        use_4_colors=False
    initcolors(palette)
    if shorten_colorhex is 1:
        round_colors_6()
    bgg=bg
    tsg=ts
    bsg=bs
    fgg=fg
    selg=sel
    basename=os.path.basename(palettefile)

    replacement_dict = {'NSCDE_BG_COLOR_1':bgg[1], 'NSCDE_BG_COLOR_2':bgg[2],
                        'NSCDE_BG_COLOR_3':bgg[3], 'NSCDE_BG_COLOR_4':bgg[4],
                        'NSCDE_BG_COLOR_5':bgg[5], 'NSCDE_BG_COLOR_6':bgg[6],
                        'NSCDE_BG_COLOR_7':bgg[7], 'NSCDE_BG_COLOR_8':bgg[8],
                        'NSCDE_FG_COLOR_1':fgg[1], 'NSCDE_FG_COLOR_2':fgg[2],
                        'NSCDE_FG_COLOR_3':fgg[3], 'NSCDE_FG_COLOR_4':fgg[4],
                        'NSCDE_FG_COLOR_5':fgg[5], 'NSCDE_FG_COLOR_5':fgg[5],
                        'NSCDE_FG_COLOR_6':fgg[6], 'NSCDE_FG_COLOR_6':fgg[6],
                        'NSCDE_FG_COLOR_7':fgg[7], 'NSCDE_FG_COLOR_8':fgg[8],
                        'NSCDE_TS_COLOR_1':tsg[1], 'NSCDE_TS_COLOR_2':tsg[2],
                        'NSCDE_TS_COLOR_3':tsg[3], 'NSCDE_TS_COLOR_4':tsg[4],
                        'NSCDE_TS_COLOR_5':tsg[5], 'NSCDE_TS_COLOR_5':tsg[5],
                        'NSCDE_TS_COLOR_6':tsg[6], 'NSCDE_TS_COLOR_6':tsg[6],
                        'NSCDE_TS_COLOR_7':tsg[7], 'NSCDE_TS_COLOR_8':tsg[8],
                        'NSCDE_BS_COLOR_1':bsg[1], 'NSCDE_BS_COLOR_2':bsg[2],
                        'NSCDE_BS_COLOR_3':bsg[3], 'NSCDE_BS_COLOR_4':bsg[4],
                        'NSCDE_BS_COLOR_5':bsg[5], 'NSCDE_BS_COLOR_5':bsg[5],
                        'NSCDE_BS_COLOR_6':bsg[6], 'NSCDE_BS_COLOR_6':bsg[6],
                        'NSCDE_BS_COLOR_7':bsg[7], 'NSCDE_BS_COLOR_8':bsg[8],
                        'NSCDE_SEL_COLOR_1':selg[1], 'NSCDE_SEL_COLOR_2':selg[2],
                        'NSCDE_SEL_COLOR_3':selg[3], 'NSCDE_SEL_COLOR_4':selg[4],
                        'NSCDE_SEL_COLOR_5':selg[5], 'NSCDE_SEL_COLOR_5':selg[5],
                        'NSCDE_SEL_COLOR_6':selg[6], 'NSCDE_SEL_COLOR_6':selg[6],
                        'NSCDE_SEL_COLOR_7':selg[7], 'NSCDE_SEL_COLOR_8':selg[8]}

    buf_infile = open(infile, 'r')
    for line in buf_infile:
        for colorkey in replacement_dict:
            line = line.replace(colorkey, replacement_dict[colorkey])
        sys.stdout.write (line)
    buf_infile.close()
    sys.stdout.flush()

def usage():
    print ("Used to generate colorsets for fvwm, Xresources, backdrops and element pixmaps")

def main():
    shorten_colorhex = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cfbp:i:n:sP:lh", ["palette=", "infile", "fvwm-colorsets", "backdrop", "colorgen", "ncolors=", "shortencolorhex", "palettepart=", "list-colors"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o in ("-f", "--fvwm-colorsets"):
            genfvwmcolorset(palettefile,ncolors)
        elif o in ("-b", "--backdrop"):
            gencdebackdrop(palettefile,ncolors,infile,palettepart)
        elif o in ("-c", "--colorgen"):
            gencdecolors(palettefile,ncolors,infile,shorten_colorhex)
        elif o in ("-p", "--palette"):
            palettefile = a
        elif o in ("-i", "--infile"):
            infile = a
        elif o in ("-n", "--ncolors"):
            ncolors = int(a)
        elif o in ("-s", "--shortencolorhex"):
            shorten_colorhex = 1
        elif o in ("-P", "--palettepart"):
             palettepart = int(a)
        elif o in ("-l", "--list-colors"):
            # Debug: print colors out
            motifcolors=readMotifColors2(ncolors,palettefile)
            for key in motifcolors:
                print (key, motifcolors[key])
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        else:
            assert False, "getopt: unhandled option"

# Action ...
if __name__ == '__main__':
    main()

