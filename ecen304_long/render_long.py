#!/usr/bin/env python3
"""Long-form ECEN 304 tutorial with free natural TTS and progressive chalk writing.
Own educational material based on supplied Fall 2026 review & Fall 2019 test.
"""
import os, io, json, math, asyncio, random, subprocess, textwrap
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
from matplotlib.mathtext import math_to_image
from matplotlib.font_manager import FontProperties
from pydub import AudioSegment
import edge_tts

ROOT=Path(__file__).resolve().parent
PAGES=json.loads((ROOT/"lesson.json").read_text())
OUT=ROOT/"ECEN304_Slow_Step_by_Step_Tutorial.mp4"
M=ROOT/"media";M.mkdir(exist_ok=True)
W,H=1280,720
COLORS=["#f0e9df","#f5e7d8","#8fe1cf","#f0e9df","#f5d277","#8fe1cf","#f0e9df"]
BKG="#07090d";INK="#eeeae4"; GOLD="#f6dc70";CYAN="#78daca";MUTED="#a6b0be";RED="#e9a6a6"
FONT=next((x for x in ["/usr/share/fonts/opentype/comic-neue/ComicNeue-Regular.otf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if os.path.exists(x)))
BOLD=next((x for x in ["/usr/share/fonts/opentype/comic-neue/ComicNeue-Bold.otf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if os.path.exists(x)))
def ff(*args):
 return subprocess.check_output(["ffprobe","-v","error",*args],text=True).strip()
def tm(sec):
 n=int(sec);return f"{n//3600:02}:{n%3600//60:02}:{n%60:02},000"
def font(sz,b=False):return ImageFont.truetype(BOLD if b else FONT,sz)
def say(draw,xy,s,sz=28,col=INK,b=False):
 draw.text(xy,s,font=font(sz,b),fill=col,stroke_width=0)
def mathmask(expr,size=40):
 buf=io.BytesIO()
 math_to_image(expr,buf,prop=FontProperties(size=size),dpi=114,format="png",color="black")
 buf.seek(0);im=Image.open(buf).convert("RGBA")
 # Retain alpha if mathtext supplies it; otherwise extract black ink on white.
 alpha=im.getchannel("A")
 if alpha.getextrema()[0] == 255:
  from PIL import ImageOps
  alpha=ImageOps.invert(im.convert("L"))
 bb=alpha.getbbox()
 return alpha.crop(bb) if bb else Image.new("L",(2,2))
CACHE={}
def ink_layer(expr,size,target_w,target_h,color):
 k=(expr,size,target_w,target_h)
 if k not in CACHE:
  if expr.startswith("$"):
   mask=mathmask(expr,size)
  else:
   # Scale prose to available width without wrapping into next row.
   sz=33
   while sz>16 and ImageDraw.Draw(Image.new("L",(1,1))).textbbox((0,0),expr,font=font(sz))[2]>target_w: sz-=1
   bbox=ImageDraw.Draw(Image.new("L",(1,1))).textbbox((0,0),expr,font=font(sz))
   mask=Image.new("L",(max(1,bbox[2]+3),max(1,bbox[3]-bbox[1]+4)),0)
   ImageDraw.Draw(mask).text((0,-bbox[1]),expr,font=font(sz),fill=255)
  factor=min(1.0,target_w/max(1,mask.width),target_h/max(1,mask.height))
  if factor<1:mask=mask.resize((max(1,int(mask.width*factor)),max(1,int(mask.height*factor))),Image.Resampling.LANCZOS)
  CACHE[k]=mask
 mask=CACHE[k]
 rgba=Image.new("RGBA",mask.size,color)
 rgba.putalpha(mask)
 return rgba
def plot(board,kind):
 d=ImageDraw.Draw(board)
 R=(780,260,1210,600)
 d.rounded_rectangle(R,radius=10,fill="#111923",outline="#293b49",width=2)
 if kind=="coeff":
  say(d,(802,271),"|a_k|  magnitude",24,CYAN)
  cx,yy=1002,535
  d.line((810,yy,1185,yy),fill=MUTED,width=2)
  for k in range(-3,4):
   x=cx+51*k;v={-2:1,-1:2,0:2,1:2,2:1}.get(k,0)
   say(d,(x-15,547),str(k),19,INK)
   if v:
    h=78*v
    d.line((x,yy,x,yy-h),fill=CYAN,width=5)
    d.ellipse((x-6,yy-h-6,x+6,yy-h+6),fill=CYAN)
    say(d,(x-8,yy-h-31),str(v),21,GOLD)
  say(d,(1131,579),"k",17,MUTED)
 elif kind=="f19":
  say(d,(799,272),"Pass: k = 0, +/-1",25,CYAN)
  cx,yy=1002,531
  d.line((814,yy,1194,yy),fill=MUTED,width=2)
  d.rectangle((cx-73,334,cx+73,537),outline=GOLD,width=2)
  for k in range(-3,4):
   x=cx+48*k
   say(d,(x-14,548),str(k),19,INK)
   v=1/(3+k*k)
   ht=v*440
   c=CYAN if abs(k)<=1 else "#59636f"
   d.line((x,yy,x,yy-ht),fill=c,width=5)
   d.ellipse((x-5,yy-ht-5,x+5,yy-ht+5),fill=c)
  say(d,(832,595),"Filter keeps the three center stems",17,GOLD)
 elif kind=="baseband":
  say(d,(798,271),"Spectrum X(omega)",25,CYAN)
  x0,yy=996,533
  d.line((807,yy,1188,yy),fill=MUTED,width=2)
  d.rectangle((926,356,1066,533),fill="#2c9e92",outline=CYAN,width=2)
  say(d,(920,553),"-500",19,INK);say(d,(1038,553),"500 Hz",19,INK)
  say(d,(978,335),"pi",19,GOLD)
 elif kind=="shift":
  say(d,(789,271),"Y: original + shifted copies",21,CYAN)
  yy=526;d.line((806,yy,1190,yy),fill=MUTED,width=2)
  # plot in kHz
  def xx(f):return 995+f*72
  for lo,hi,height,c in [(-.5,.5,136,CYAN),(-2.5,-1.5,68,GOLD),(1.5,2.5,68,GOLD)]:
   d.rectangle((xx(lo),yy-height,xx(hi),yy),fill=c)
  for k in [-2,0,2]:say(d,(xx(k)-22,540),str(k)+"k",18,INK)
  say(d,(817,594),"Center: pi/2   Sidebands: pi/4",17,MUTED)
 elif kind=="cut":
  say(d,(800,272),"Filter passes only center",22,CYAN)
  yy=528; d.line((803,yy,1190,yy),fill=MUTED,width=2)
  x0=994
  d.rectangle((x0-40,370,x0+40,yy),fill=CYAN)
  for k in [-1,1]:
   x=x0+k*80;d.line((x,328,x,yy),fill=GOLD,width=2)
  say(d,(887,543),"-1 kHz",17,INK);say(d,(1061,543),"+1 kHz",17,INK)
  say(d,(905,592),"Passed height = pi/2",20,GOLD)
def render_page(pi,step_index,frac):
 page=PAGES[pi];n=len(page["steps"]);with_plot=bool(page.get("plot"))
 board=Image.new("RGB",(W,H),BKG);d=ImageDraw.Draw(board)
 # A deliberately minimal board: no slide-boxes or corporate UI.
 say(d,(50,26),"ECEN 304",24,CYAN,True)
 say(d,(200,22),page["title"],34,GOLD,True)
 d.line((49,86,1230,86),fill=GOLD,width=2)
 say(d,(51,99),page["topic"],20,CYAN)
 maxw=680 if with_plot else 1160
 # Writing lines stay on screen until this page ends.
 rows=page["steps"]
 top=151
 dy=65 if n>=7 else (75 if n==6 else (86 if n==5 else 105))
 for j,(expr,narr) in enumerate(rows):
  if j>step_index:break
  y=top+j*dy
  color=COLORS[j%len(COLORS)]
  # One intentionally legible line per teaching move.
  rgba=ink_layer(expr,41,maxw,49,color)
  if j==step_index and frac<1:
   target=max(1,int(rgba.width*frac))
   rgba=rgba.crop((0,0,target,rgba.height))
  board.paste(rgba,(59,y),rgba)
  if j==step_index and frac<1:
   x=60+rgba.width
   # Small chalk-tip cursor; no large distraction.
   ImageDraw.Draw(board).ellipse((x+3,y+rgba.height//2-4,x+9,y+rgba.height//2+2),fill=GOLD)
 if with_plot and step_index>=2:plot(board,page["plot"])
 d=ImageDraw.Draw(board)
 d.line((48,654,1230,654),fill="#35404d",width=1)
 say(d,(51,661),"F26 review + F19 exam  |  derived one line at a time",17,MUTED)
 say(d,(1125,661),f"{pi+1:02}/{len(PAGES):02}",18,MUTED)
 return board
async def speech():
 timings=[]
 for pi,page in enumerate(PAGES):
  for si,(_,narr) in enumerate(page["steps"]):
   path=M/f"audio_{pi:02}_{si:02}.mp3"
   if not path.exists() or path.stat().st_size<1000:
    for attempt in range(6):
     try:
      await edge_tts.Communicate(narr,voice="en-US-AvaNeural",rate="-13%",pitch="-1Hz").save(str(path))
      if path.stat().st_size<1000:raise ValueError("empty audio")
      break
     except Exception as e:
      print("TTS retry",pi,si,attempt,repr(e),flush=True)
      path.unlink(missing_ok=True)
      if attempt==5:raise
      await asyncio.sleep(3+attempt*5)
    await asyncio.sleep(.18)
   seconds=float(ff("-show_entries","format=duration","-of","default=nokey=1:noprint_wrappers=1",str(path)))
   timings.append((pi,si,path,seconds))
  print("Narrated page",pi+1,"/",len(PAGES),flush=True)
 return timings
def produce(timings):
 # Each spoken line has its own audio and a genuine post-line reading pause.
 audio=AudioSegment.silent(duration=400)
 index=[(0,0,400)]
 now=.4
 frames=["ffconcat version 1.0"]
    # Match the 400 ms of pre-roll audio with an initially empty board.
    pre=M/"frames"/"initial.jpg"; pre.parent.mkdir(exist_ok=True)
    render_page(0,0,0.0).save(pre,quality=86)
    frames.extend([f"file '{pre.resolve()}'","duration 0.4000"])
 frames_dir=M/"frames";frames_dir.mkdir(exist_ok=True)
 subs=[];chapters=[];prev_page=-1
 for pi,si,p,d in timings:
  if pi!=prev_page:
   if prev_page!=-1:
    audio+=AudioSegment.silent(duration=1800);now+=1.8
                frames.extend([f"file '{last_full.resolve()}'","duration 1.8000"])
   chapters.append((now,PAGES[pi]["title"]))
   prev_page=pi
  sound=AudioSegment.from_file(p)
  pause=1.65
  audio+=sound+AudioSegment.silent(duration=int(pause*1000))
  start,end=now,now+d
  subs.append((start,end,PAGES[pi]["steps"][si][1]))
  now=end+pause
  # Slow reveal while the tutor begins explaining the line.
  draw_time=min(3.0,max(1.5,d*.27))
  cuts=14
  for q in range(1,cuts+1):
   frac=q/cuts
   image_path=frames_dir/f"{pi:02}_{si:02}_{q:02}.jpg"
   if not image_path.exists():
    render_page(pi,si,frac).save(image_path,quality=86,subsampling=0)
   frames.append(f"file '{image_path.resolve()}'")
   frames.append(f"duration {draw_time/cuts:.4f}")
  # Reader retains the fully written line through narration and pause.
  image_path=frames_dir/f"{pi:02}_{si:02}_{cuts:02}.jpg"
  frames.append(f"file '{image_path.resolve()}'")
  frames.append(f"duration {max(1.0,d-draw_time+pause):.4f}")
        last_full=image_path
 # Close last frame.
 frames.append(frames[-2]); frames.append("duration 0.05")
 audio=audio.set_frame_rate(44100).set_channels(2)
 audio.export(M/"full_audio.mp3",format="mp3",bitrate="160k")
 (M/"frames.ffconcat").write_text("\n".join(frames)+"\n")
 srt=[]
 for k,(a,b,narr) in enumerate(subs,1):
  # Captions are optional and external; keep equations unobstructed in video itself.
  srt.extend([str(k),tm(a)+" --> "+tm(b),narr,""])
 (ROOT/"ECEN304_Long_Lesson_Captions.srt").write_text("\n".join(srt))
 (ROOT/"ECEN304_Long_Lesson_Chapters.txt").write_text("\n".join(f"{int(t)//60:02}:{int(t)%60:02} {title}" for t,title in chapters))
 print("Expected length",now,"frames",len(frames)//2,flush=True)
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
    "-safe","0","-f","concat","-i",str(M/"frames.ffconcat"),
    "-i",str(M/"full_audio.mp3"),"-r","16","-c:v","libx264","-preset","veryfast",
    "-crf","23","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
    "-movflags","+faststart","-shortest",str(OUT)],check=True)
 print("FINAL MP4",str(OUT),OUT.stat().st_size,flush=True)
def main():
 timings=asyncio.run(speech())
 produce(timings)
if __name__=="__main__":main()
