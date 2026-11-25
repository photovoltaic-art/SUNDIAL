"""Draws hardware/mvp-wiring.svg (MVP v1). Run from the repo root:
   python3 tools/mvp_wiring.py && rsvg-convert -w 1800 hardware/mvp-wiring.svg -o hardware/mvp-wiring.png
"""
import pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "hardware" / "mvp-wiring.svg"
R,O,K,B="#d62828","#f08c00","#222","#1f6feb"
o=[]
def a(s): o.append(s)
def pl(pts,c,w=3): a(f'<polyline points="{" ".join(f"{x},{y}" for x,y in pts)}" fill="none" stroke="{c}" stroke-width="{w}"/>')
def dot(x,y,c,r=4): a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')
def t(x,y,s,size=14,fill="#222",anchor="start",bold=False): a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{" font-weight=\"bold\"" if bold else ""}>{s}</text>')
def box(x,y,w,h,fill="#fff",rx=6): a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#334" stroke-width="2"/>')
W,H=1200,830
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="14">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
t(30,36,"SUNDIAL wall — MVP v1 wiring (with the logger layer)",22,bold=True)
t(30,58,"Modules on a screw-terminal breakout. No custom board; the only soldering is two leads on the reference cell. hardware/MVP.md",13,"#555")
for (x,y,c,l) in [(760,30,R,"panel voltage (up to ~48 V)"),(760,48,O,"5 V / 3.3 V"),(980,30,K,"GND"),(980,48,B,"signal")]:
    a(f'<line x1="{x}" y1="{y}" x2="{x+30}" y2="{y}" stroke="{c}" stroke-width="3"/>'); t(x+36,y+4,l,12,"#333")
# panel
box(30,100,150,110,"#e8eef7")
a('<g stroke="#9ab" stroke-width="1"><line x1="30" y1="137" x2="180" y2="137"/><line x1="30" y1="173" x2="180" y2="173"/><line x1="80" y1="100" x2="80" y2="210"/><line x1="130" y1="100" x2="130" y2="210"/></g>')
t(105,230,"PV panel",anchor="middle",bold=True); t(105,247,"Trina 185 W, V_oc 44.5 V",12,"#555","middle")
t(188,116,"+",12); t(188,190,"−",12)
box(225,105,70,30,rx=4); t(260,125,"MC4 fuse",12,anchor="middle"); t(260,152,"2 A",11,"#555","middle")
box(345,95,140,120,"#fff4e0"); t(415,150,"Buck converter",anchor="middle",bold=True)
t(415,167,"8–60 V in → 5.0 V",12,"#555","middle"); t(415,182,"check 5.0 V first",11,"#a00","middle")
t(352,122,"IN+",11); t(352,200,"IN−",11); t(450,122,"OUT+",11); t(450,200,"OUT−",11)
pl([(180,120),(225,120)],R); pl([(295,120),(345,120)],R); pl([(180,195),(345,195)],K)
# divider
dot(320,120,R); pl([(320,120),(320,300)],R)
box(300,300,40,70,rx=3); t(320,340,"100k",12,anchor="middle")
pl([(320,370),(320,430)],B); dot(320,415,B)
box(300,430,40,60,rx=3); t(320,465,"4.7k",12,anchor="middle")
pl([(320,490),(320,520)],K)
pl([(320,415),(270,415),(270,440)],B)
a('<line x1="255" y1="440" x2="285" y2="440" stroke="#334" stroke-width="3"/><line x1="255" y1="450" x2="285" y2="450" stroke="#334" stroke-width="3"/>')
pl([(270,450),(270,520)],K); t(205,448,"100 nF",12)
t(200,345,"divider:",12,"#555"); t(200,361,"panel voltage,",12,"#555"); t(200,377,"dawn and dusk",12,"#555")
pl([(320,415),(560,415)],B)
# ESP32
box(560,250,200,390,"#eef6ee",8); a('<rect x="600" y="270" width="120" height="330" rx="4" fill="#2b2b2b"/>')
t(660,300,"ESP32",fill="#fff",anchor="middle",bold=True); t(660,318,"ELEGOO 30-pin",11,"#ccc","middle")
t(660,570,"on screw-terminal",11,"#ccc","middle"); t(660,583,"breakout",11,"#ccc","middle")
for y,l in [(294,"5V"),(334,"GND"),(419,"G34"),(479,"G35")]: t(566,y,l,12)
for y,l in [(289,"3V3"),(319,"GND"),(359,"G4"),(404,"G21"),(429,"G22")]: t(755,y,l,12,anchor="end")
for x,l in [(610,"G18"),(645,"G19"),(680,"G23"),(715,"G5")]: t(x,632,l,11,"#222","middle")
# buck out + cap
pl([(485,120),(530,120),(530,290),(560,290)],O)
pl([(485,195),(510,195),(510,330),(560,330)],K)
pl([(530,240),(523,240)],O); pl([(517,240),(510,240)],K)
a('<line x1="523" y1="228" x2="523" y2="252" stroke="#334" stroke-width="3"/><line x1="517" y1="228" x2="517" y2="252" stroke="#334" stroke-width="3"/>')
dot(530,240,O); dot(510,240,K); t(505,272,"1000 µF",12,anchor="end"); t(505,286,"10 V",11,"#555","end")
# GND bus
pl([(270,520),(510,520)],K); pl([(510,330),(510,520)],K); dot(510,330,K); dot(320,520,K); dot(440,520,K)
t(345,512,"common GND",12,"#555")
# reference cell
box(40,440,130,80,"#e8eef7",4)
a('<g stroke="#9ab"><line x1="40" y1="480" x2="170" y2="480"/><line x1="105" y1="440" x2="105" y2="520"/></g>')
t(105,540,"Reference cell",anchor="middle",bold=True); t(105,556,"Voltaic P124, 6 V 1.2 W,",12,"#555","middle"); t(105,571,"on the panel frame",12,"#555","middle")
pl([(170,455),(200,455),(200,600),(490,600),(490,475),(560,475)],B); dot(200,600,B)
pl([(200,600),(200,610)],B); box(185,610,30,34,rx=3)
t(225,632,"R_cell = 1.0 V ÷ I_sc: 4.7 Ω for the P124",12)
pl([(170,505),(180,505),(180,652),(200,652),(200,644)],K); pl([(180,652),(440,652),(440,520)],K)
t(300,594,"sun → G35",12,B)
# rails
pl([(760,285),(800,285),(800,735),(760,735)],O); dot(800,285,O)
pl([(760,315),(820,315),(820,755),(760,755)],K); dot(820,315,K)
t(796,272,"3V3",11,O,"end"); t(826,272,"GND",11)
# I2C buses
t(780,396,"SDA",10,B,"middle"); t(780,421,"SCL",10,B,"middle")
pl([(760,400),(850,400),(850,605)],B); pl([(760,425),(870,425),(870,620)],B)
def module(y,h,title,lines,sig,pw):
    box(900,y,270,h)
    t(1035,y+20,title,anchor="middle",bold=True)
    for i,(s,c) in enumerate(lines): t(1035,y+38+i*15,s,12,c,"middle")
    for (yy,bus) in sig:
        pl([(bus,yy),(900,yy)],B,2.5); dot(bus,yy,B,3.5)
    for (yy,rail,c) in pw:
        pl([(rail,yy),(900,yy)],c,2); dot(rail,yy,c,3.5)
# DS18B20
box(900,330,270,62); t(1035,350,"DS18B20 probe",anchor="middle",bold=True)
t(1035,368,"panel back temperature",12,"#555","middle"); t(1035,383,"4.7 k pull-up from G4 to 3V3",12,"#555","middle")
pl([(760,355),(900,355)],B,2.5); pl([(800,342),(900,342)],O,2); dot(800,342,O,3.5); pl([(820,377),(900,377)],K,2); dot(820,377,K,3.5)
module(400,78,"DS3231 clock + CR2032",[("I2C 0x68 · time at dawn, offline","#555"),("remove the charging parts (ZS-042)","#a00")],[(412,850),(437,870)],[(455,800,O),(468,820,K)])
module(490,82,"SHT-30 probe, outside",[("air temperature + humidity · I2C 0x44","#555"),("in a radiation shield, on 1 m of cable","#555"),("under the panel, ≥ 10 cm from wall","#555")],[(505,850),(522,870)],[(545,800,O),(560,820,K)])
module(590,72,"BME280, inside the box",[("air pressure · I2C 0x76","#555"),("box temperature + humidity (maintenance)","#555")],[(605,850),(620,870)],[(640,800,O),(652,820,K)])
# SD
box(560,700,200,80,"#fff")
t(660,722,"microSD module (SPI)",anchor="middle",bold=True); t(660,740,"high-endurance 32 GB card",12,"#555","middle"); t(660,756,"years of raw data",12,"#555","middle")
for x,l in [(610,"SCK"),(645,"MISO"),(680,"MOSI"),(715,"CS")]:
    pl([(x,640),(x,700)],B,2.5); t(x+4,676,l,10,B)
t(30,800,"All grounds meet at the breakout's GND, the panel's − included. GPIO 34 and 35 are ADC1: the only analog inputs that work with Wi-Fi on.",12,"#555")
t(30,818,"One I2C bus at 100 kHz for three parts (0x68 + its EEPROM 0x57, 0x44, 0x76): no address clashes. Crossing wires without a dot are not joined.",12,"#555")
a('</svg>')
open(OUT,'w').write("\n".join(o)+"\n")
