#!/usr/bin/env python3
"""Render a narrated, exam-focused ECEN 304 whiteboard review from two approved voice tracks."""
import io, os, math, subprocess, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties

ROOT=Path(__file__).parent
OUT=ROOT/"ECEN304_Narrated_Whiteboard_Review.mp4"
FRAMES=ROOT/"frames"; FRAMES.mkdir(parents=True,exist_ok=True)
URLS=[
"https://d8j0ntlcm91z4.cloudfront.net/user_3LRh4TPp8mCZ65o0n7020vFWTSz/hf_20261031_052237_17adfa68-f776-44cd-8397-4658c127fd30.mp3",
"https://d8j0ntlcm91z4.cloudfront.net/user_3LRh4TPp8mCZ65o0n7020vFWTSz/hf_20261031_052410_b02b9a33-e9ef-47e7-bed9-3edbc8ab14f5.mp3"
]
W,H=1280,720
BG="#121923"; PANEL="#1D2834"; WHITE="#F1F5FA"; SOFT="#B9C7D5"
MINT="#76DED1"; YELLOW="#FFD17C"; CORAL="#FFAB9E"; MUTED="#70899C"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def text(d,xy,s,size=24,color=WHITE,bold=False):
    d.text(xy,s,font=ft(size,bold),fill=color)
def box(d,r,fill=PANEL,outline=None,radius=17):
    d.rounded_rectangle(r,radius=radius,fill=fill,outline=outline,width=2 if outline else 1)
def mathline(im,xy,expr,maxw=1130,base=35,color=WHITE):
    if not expr.startswith("$"):
        text(ImageDraw.Draw(im),xy,expr,26,color);return
    buf=io.BytesIO()
    math_to_image(expr,buf,prop=FontProperties(size=base),dpi=126,format="png",color="black")
    buf.seek(0)
    gray=Image.open(buf).convert("L")
    mask=ImageOps.invert(gray)
    bb=mask.getbbox()
    if bb: mask=mask.crop(bb)
    if mask.width>maxw:
        fac=maxw/mask.width
        mask=mask.resize((int(mask.width*fac),int(mask.height*fac)),Image.Resampling.LANCZOS)
    rgb=Image.new("RGBA",mask.size,color);rgb.putalpha(mask)
    im.paste(rgb,xy,rgb)
def chart(im,kind):
    d=ImageDraw.Draw(im)
    area=(742,214,1225,568)
    box(d,area,fill="#16222D",outline="#344C5C")
    x0,x1=780,1193; y0,y1=248,515
    d.line([(x0,y1),(x1,y1)],fill="#668091",width=2)
    if kind in ("coeff","filter"):
        text(d,(774,226),"HARMONIC MAGNITUDES",19,MINT,True)
        cx=986
        for k in range(-4,5):
            xx=cx+k*47
            d.line([(xx,y1-6),(xx,y1+6)],fill=MUTED,width=1)
            if k%2==0:text(d,(xx-11,y1+13),str(k),16,SOFT)
        vals={-2:1,-1:2,0:2,1:2,2:1} if kind=="coeff" else {-2:.143,-1:.25,0:1/3,1:.25,2:.143}
        for k,v in vals.items():
            xx=cx+k*47
            live=(kind=="coeff" or abs(k)<=1)
            col=MINT if live else MUTED
            ht=(91*v if kind=="coeff" else 350*v)
            d.line([(xx,y1),(xx,y1-ht)],fill=col,width=5)
            d.ellipse((xx-5,y1-ht-5,xx+5,y1-ht+5),fill=col)
        if kind=="filter":
            d.rounded_rectangle((cx-67,255,cx+67,519),radius=10,outline=YELLOW,width=2)
            text(d,(805,260),"Only k = -1, 0, 1 pass",17,YELLOW,True)
    elif kind=="spectrum":
        text(d,(760,228),"MAGNITUDE SPECTRUM",19,MINT,True)
        yy=465
        d.line([(770,yy),(1200,yy)],fill=SOFT,width=2)
        def fx(f):return 985+f*(210/3000)
        for freq,h,co in [(-2000,75,CORAL),(0,140,MINT),(2000,75,CORAL)]:
            lo,hi=fx(freq-500),fx(freq+500)
            d.rectangle((lo,yy-h,hi,yy),fill=co)
            text(d,(fx(freq)-29,yy+11),str(freq),14,SOFT)
        text(d,(1000,546),"frequency  f  (Hz)",17,SOFT)
    elif kind=="time":
        text(d,(770,227),"PERIODIC INPUT IN TIME",19,MINT,True)
        import numpy as np
        pts=[]
        for i in range(350):
            t=0.04*i/349
            val=2+4*math.cos(100*math.pi*t-math.pi/3)+2*math.sin(200*math.pi*t)
            pts.append((780+i*1.16,397-val*19))
        d.line(pts,fill=MINT,width=4)
        d.line([(780,397),(1195,397)],fill=MUTED,width=2)
        text(d,(1110,528),"time (s)",17,SOFT)
    elif kind=="passband":
        text(d,(768,230),"IDEAL LOW-PASS FILTER",18,MINT,True)
        yy=480
        d.line([(774,yy),(1200,yy)],fill=MUTED,width=2)
        d.rectangle((928,313,1042,yy),fill=MINT)
        text(d,(760,505),"-1000",16,SOFT)
        text(d,(1140,505),"+1000",16,SOFT)
        text(d,(810,267),"Shifted bands are removed",18,YELLOW)

SCENES=[
 dict(title="One idea, four exam moves",tag="THE BIG PICTURE",
      lines=["Fourier series = describe periodic signals with harmonics",
             "Fourier transform = describe the full frequency content",
             "An LTI filter multiplies each frequency by its response",
             "Modulation shifts copies of the spectrum"],
      key="First identify the type of operation. Then choose the property.",weight=22),
 dict(title="Every harmonic has a job",tag="FOURIER SERIES",
      lines=[r"$x(t)=\sum_{k=-\infty}^{\infty} a_k e^{jk\omega_0t}$",
             r"$\omega_0=\frac{2\pi}{T}\quad\mathrm{(harmonic\ spacing)}$",
             r"$a_0=\mathrm{DC\ component}\quad \qquad k=\pm1,\pm2,\ldots$",
             "Each coefficient sets the amplitude and phase of one tone."],
      key="Connect stems at discrete k-values to oscillations in time.",kind="coeff",weight=37),
 dict(title="2026 review: identify the tones",tag="QUESTION 2 — STEP 0",
      lines=[r"$x(t)=2+4\cos(\omega_0t-\pi/3)+2\sin(2\omega_0t)$",
             r"$\omega_0=2\pi(50)=100\pi\ \mathrm{rad/s}$",
             r"$T=\frac{2\pi}{100\pi}=\frac{1}{50}\ \mathrm{s}$",
             "Only DC, first harmonics, and second harmonics appear."],
      key="Predict the nonzero coefficients before touching the algebra.",kind="time",weight=46),
 dict(title="Euler's identity: expand cosine",tag="QUESTION 2 — STEP 1",
      lines=[r"$\cos(\theta)=\frac{e^{j\theta}+e^{-j\theta}}{2}$",
             r"$4\cos(\omega_0t-\pi/3)$",
             r"$=2e^{-j\pi/3}e^{j\omega_0t}+2e^{j\pi/3}e^{-j\omega_0t}$",
             r"$a_{1}=2e^{-j\pi/3}\qquad a_{-1}=2e^{j\pi/3}$"],
      key="The two signs are conjugate partners for this real signal.",weight=50),
 dict(title="Sine has a different sign",tag="QUESTION 2 — STEP 2",
      lines=[r"$\sin(\theta)=\frac{e^{j\theta}-e^{-j\theta}}{2j}$",
             r"$2\sin(2\omega_0t)=\frac{e^{j2\omega_0t}-e^{-j2\omega_0t}}{j}$",
             r"$\frac{1}{j}=-j$",
             r"$a_2=-j\qquad a_{-2}=+j$"],
      key="Missing the minus sign is a common exam mistake.",weight=48),
 dict(title="Collect the Fourier coefficients",tag="QUESTION 2 — STEP 3",
      lines=[r"$a_0=2,\quad a_{\pm1}=2e^{\mp j\pi/3}$",
             r"$a_2=-j,\quad a_{-2}=+j$",
             r"$a_k=0\quad\mathrm{for\ all\ remaining}\ k$",
             "Draw stems to visualize which frequencies exist."],
      key="DC is k=0. The negative-frequency tones are real-signal partners.",kind="coeff",weight=45),
 dict(title="A delay changes phase, not size",tag="QUESTION 2 — STEP 4",
      lines=[r"$y(t)=x(t-t_0)\ \Longrightarrow\ b_k=a_ke^{-jk\omega_0t_0}$",
             r"$t_0=0.005\ \mathrm{s},\quad\omega_0=100\pi$",
             r"$\omega_0t_0=\pi/2 \ \Longrightarrow\ b_k=a_ke^{-jk\pi/2}$",
             r"$|b_k|=|a_k|$"],
      key="Every harmonic rotates in phase by an amount proportional to k.",weight=42),
 dict(title="2019 exam: what gets through?",tag="QUESTION 1 — FILTERING",
      lines=[r"$a_k=\frac{1}{3+k^2},\qquad \omega_0=\frac{\pi}{2}$",
             r"$H(\omega)=1\ \mathrm{for}\ |\omega|<0.6\pi$",
             r"$k=0:\ 0,\quad k=\pm1:\ \pm\pi/2$",
             r"$k=\pm2:\ \pm\pi\quad\mathrm{(blocked)}$"],
      key="Evaluate the filter only at the harmonic frequencies k omega naught.",kind="filter",weight=51),
 dict(title="Reconstruct the surviving tones",tag="2019 EXAM — OUTPUT",
      lines=[r"$y(t)=a_{-1}e^{-j\pi t/2}+a_0+a_1e^{j\pi t/2}$",
             r"$a_0=\frac13,\qquad a_{\pm1}=\frac14$",
             r"$y(t)=\frac13+\frac14(e^{j\pi t/2}+e^{-j\pi t/2})$",
             r"$y(t)=\frac13+\frac12\cos(\pi t/2)$"],
      key="Filtering in frequency replaces a much harder convolution integral.",weight=50),
 dict(title="2026 review: modulation",tag="QUESTION 3 — SHIFTING SPECTRA",
      lines=[r"$y(t)=x(t)\cos^2(2000\pi t)$",
             r"$\cos^2(\theta)=\frac12+\frac12\cos(2\theta)$",
             r"$Y(\omega)=\frac12X(\omega)+\frac14X(\omega-4000\pi)$",
             r"$\quad\qquad\qquad+\frac14X(\omega+4000\pi)$"],
      key="A cosine in time creates two shifted spectral copies.",kind="spectrum",weight=53),
 dict(title="Low-pass filtering recovers the baseband",tag="QUESTION 3 — FINAL OUTPUT",
      lines=[r"$H(\omega)=1\quad\mathrm{for}\ |\omega|<2000\pi$",
             r"$X(\omega):\quad |f|<500\ \mathrm{Hz}$",
             "Shifted copies are centered at plus and minus 2000 Hz.",
             r"$z(t)=\frac12x(t)=\frac{\sin(1000\pi t)}{2t}$"],
      key="The filter passes only the centered half-amplitude copy.",kind="passband",weight=43)
]
def draw(idx,stage):
    s=SCENES[idx];im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((44,35,62,70),radius=5,fill=MINT)
    text(d,(80,39),"ECEN 304  /  SIGNALS AND SYSTEMS",21,SOFT,True)
    text(d,(1133,38),f"{idx+1:02d} / 11",20,SOFT)
    text(d,(48,90),s["title"],42,WHITE,True)
    text(d,(50,151),s["tag"],21,MINT,True)
    d.line((50,192,1230,192),fill="#354858",width=2)
    side=bool(s.get("kind"))
    right=715 if side else 1225
    maxw=right-100
    for j,line in enumerate(s["lines"][:stage]):
        y=213+j*93
        box(d,(48,y,right,y+78),fill=PANEL)
        text(d,(64,y+9),f"STEP {j+1}",13,MINT,True)
        mathline(im,(65,y+32),line,maxw=maxw,base=28 if side else 33,color=YELLOW if j==3 else WHITE)
    if side and stage>=2:chart(im,s["kind"])
    if stage>=4:
        box(d,(47,594,1230,650),fill="#233641",outline="#375767",radius=12)
        text(d,(64,604),"KEY IDEA",15,MINT,True)
        text(d,(174,604),s["key"],20,WHITE)
    d.line((48,675,1232,675),fill="#354858",width=3)
    d.line((48,675,48+1184*(idx+1)/len(SCENES),675),fill=MINT,width=4)
    text(d,(50,685),"Exam sources: Fall 2026 review and Fall 2019 Test 2",14,SOFT)
    return im

def sh(*args):subprocess.run(args,check=True)
def duration(p):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(p)]))
def main():
    tracks=[]
    for i,url in enumerate(URLS):
        path=ROOT/f"voice_{i+1}.mp3"
        if not path.exists():
            urllib.request.urlretrieve(url,path)
        tracks.append(path)
    d1,d2=map(duration,tracks)
    print("Voice segment durations",d1,d2,flush=True)
    sh("ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(tracks[0]),"-i",str(tracks[1]),
       "-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ac","2","-ar","48000",str(ROOT/"voice.wav"))
    weights1=sum(s["weight"] for s in SCENES[:6])
    weights2=sum(s["weight"] for s in SCENES[6:])
    ds=[s["weight"]/weights1*d1 if i<6 else s["weight"]/weights2*d2 for i,s in enumerate(SCENES)]
    ffcat=["ffconcat version 1.0"]
    fractions=[.12,.19,.20,.20,.29]
    last=None
    for i,dur in enumerate(ds):
        for st,fraction in enumerate(fractions):
            p=FRAMES/f"scene_{i:02}_{st}.png"
            draw(i,st).save(p,optimize=True)
            ffcat.append(f"file '{p.as_posix()}'")
            ffcat.append(f"duration {dur*fraction:.5f}")
            last=p
        print(f"Scene {i+1}: {dur:.1f}s",flush=True)
    ffcat.append(f"file '{last.as_posix()}'")
    listfile=ROOT/"frames.ffconcat"
    listfile.write_text("\n".join(ffcat)+"\n")
    sh("ffmpeg","-hide_banner","-loglevel","error","-y","-safe","0","-f","concat","-i",str(listfile),
       "-i",str(ROOT/"voice.wav"),"-r","24","-c:v","libx264","-preset","medium","-crf","21",
       "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",
       "-shortest",str(OUT))
    print("SUCCESS",OUT,OUT.stat().st_size,duration(OUT),flush=True)
if __name__=="__main__":main()
