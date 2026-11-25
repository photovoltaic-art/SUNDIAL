from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import sys
out=sys.argv[1]
F="Arial"
blue=Font(name=F,color="0000FF"); black=Font(name=F); bold=Font(name=F,bold=True)
hdr=Font(name=F,bold=True,color="FFFFFF"); hfill=PatternFill("solid",fgColor="3A3A3A")
yfill=PatternFill("solid",fgColor="FFF2B3"); gfill=PatternFill("solid",fgColor="EEEEEE")
EUR='€#,##0;(€#,##0);-'; EUR2='€#,##0.00;(€#,##0.00);-'
thin=Side(style="thin",color="BBBBBB")

Q="Quote"; L="Listed price"; E="Estimate"
Q="Quote"; L="Listed price"; E="Estimate"
lines=[
("Panels and boards","Retired PV panel, Trina TSM-185DC01 class (9 + artist's proof + 1 spare)",11,30,E,"Second-hand / end-of-life; may be donated. Source still to confirm","Yes"),
("Panels and boards","ELEGOO ESP32 30-pin USB-C (10 sets + 1 spare)",11,10,L,"Sold in 3-packs, about €28 a pack (Nov 2026)","Yes"),
("Panels and boards","Screw-terminal breakout, 30-pin ESP32 (10 + 1 spare)",11,6,E,"Many makers; check the ELEGOO's row spacing on the first before buying the rest","Yes"),
("Panels and boards","Buck converter module, 8–60 V in, 5 V out",11,8,E,"Generic modules widely available","Yes"),
("Panels and boards","MC4 inline fuse holder (10x38) + 2 A gPV fuse",10,15,E,"Holders usually ship with 10–30 A fuses: buy 2 A gPV 10x38 fuses separately (e.g. Eaton PV-2A10F)","Yes"),
("Panels and boards","Sun cell: ANYSOLAR KXOB25-05X3F, 23 x 8 mm (on the gnomon mount)",11,4,L,"DigiKey, about €3 + VAT each (Nov 2026)","Yes"),
("Panels and boards","DS3231 clock module + CR2032 (10 + 1 spare)",11,5,E,"Remove the charging parts on ZS-042 modules","Yes"),
("Panels and boards","DS18B20 waterproof probe",10,4,E,"","Yes"),
("Panels and boards","Air probe: Adafruit 4099 SHT-30 weatherproof, 1 m cable (10 + 1 spare)",11,26,L,"DigiKey Italy €21.21 + VAT, in stock Nov 2026; lead time up to 18 weeks when out: order early","Yes"),
("Panels and boards","Radiation shield, small multi-plate",10,25,E,"About €5 each if printed in ASA instead of bought","Yes"),
("Panels and boards","BME280 module, from a reputable seller",10,12,E,"Cheap 'BME280' modules are often BMP280 (no humidity): check the square chip","Yes"),
("Panels and boards","microSD module, SPI, 3.3 V",10,3,E,"","Yes"),
("Panels and boards","microSD 32 GB, SanDisk High Endurance SDSQQNR-032G-GN6IA (−25 to 85 °C) (10 + 1 spare)",11,28,L,"Amazon Italy €28 (Nov 2026). If tests fail, industrial cards at about €42–65 instead","Yes"),
("Panels and boards","Small parts: 1000 µF cap, divider resistors, R_cell 39 Ω, pull-up, 100 nF",10,2,E,"","Yes"),
("Panels and boards","IP65 box, 5 glands, breather vent, desiccant, tamper screws",10,25,E,"About 115 x 90 x 55 mm","Yes"),
("Panels and boards","Wire, ferrules, standoffs",10,8,E,"","Yes"),
("Carrier board (on hold)","Board designer: schematic review, layout, files (CARRIER.md brief)",1,1000,E,"On hold: the MVP build replaces it (hardware/MVP.md)","No"),
("Carrier board (on hold)","Carrier v1, small run of 5, assembled",5,100,E,"On hold","No"),
("Carrier board (on hold)","Carrier v2, run of 10, assembled",10,60,E,"On hold","No"),

("Sundial hardware","Gnomon: 15 mm aluminium tube, 45 cm, TIG-welded to its mount",9,40,E,"Local fabrication; GNOMON.md","Yes"),
("Sundial hardware","Hour lines and date marks: UV-stable vinyl pinstripe tape, per panel",9,10,E,"No numbers, no brackets; GNOMON.md","Yes"),
("Sundial hardware","Stand-offs (aluminium angle) and M6 stainless fixings",9,30,E,"","Yes"),
("Sundial hardware","Hour-line tape test (pilot panel)",1,20,E,"README to-do","Yes"),

("Mounting and plates","Wall fixings (anchors, brackets)",9,25,E,"","Yes"),
("Mounting and plates","Wall plate: number and QR code",9,20,E,"","Yes"),

("The event (2027)","Girasole: dwarf sunflowers, pots, soil",1,40,E,"","Yes"),
("The event (2027)","Girasole: chalkboard, stand, ochre and blue chalk",1,90,E,"","Yes"),
("The event (2027)","Flyers",1,100,E,"","Yes"),
("The event (2027)","Screen print set-up: four screens and films",1,400,E,"Awaiting the print shop's answer (texts/print-enquiry.md)","Yes"),
("The event (2027)","Screen print run",50,10,E,"Edition size and price per print still open; sales may cover it","Yes"),

("Website, permissions, insurance","Domain photovoltaic.art, first year",1,30,E,"Check the renewal price (PVA TASKS.md)","Yes"),
("Website, permissions, insurance","Public liability insurance, first year",1,400,E,"Get a quote","Yes"),
("Website, permissions, insurance","Permission costs (applications, stamps)",1,100,E,"Depends on the route: patto di collaborazione or authorisation","Yes"),

("Shared and spares","Spares: coin cells, DS18B20, fixings, desiccant",1,40,E,"Board, air probe, card and clock spares are in the lines above","Yes"),
("Shared and spares","Bench supply and test leads",1,60,E,"If not already owned","Yes"),
("Shared and spares","Shipping (several suppliers, incl. Voltaic's own fee)",1,150,E,"","Yes"),

("Post option","Steel post and base",1,450,E,"Only where no wall works (POST.md)","No"),
("Post option","Structural engineer's sign-off",1,400,E,"","No"),
("Post option","USB-C PD charger module, sockets, shelf, plate",1,110,E,"","No"),

("Running, each year","Insurance renewal",1,400,E,"","Yes"),
("Running, each year","Domain renewal",1,30,E,"","Yes"),
("Running, each year","Upkeep: coin cells, desiccant, cleaning, a replacement air probe",1,60,E,"","Yes"),
("Running, each year","Screen print set-up for the year's print",1,400,E,"Each event makes a new print","Yes"),
]
nodes=["Panels and boards","Sundial hardware","Mounting and plates","The event (2027)","Website, permissions, insurance","Shared and spares"]
wb=Workbook()
S=wb.active; S.title="Summary"
Lw=wb.create_sheet("Lines")
heads=["Node","Item","Qty","Unit (€)","Total (€)","Basis","Source / note","Include"]
for i,h in enumerate(heads,1):
    c=Lw.cell(1,i,h); c.font=hdr; c.fill=hfill
for r,(n,it,q,u,b,note,inc) in enumerate(lines,2):
    Lw.cell(r,1,n).font=black; Lw.cell(r,2,it).font=black
    c=Lw.cell(r,3,q); c.font=blue
    c=Lw.cell(r,4,u); c.font=blue; c.number_format=EUR2 if u<5 else EUR
    c=Lw.cell(r,5,f"=C{r}*D{r}"); c.font=black; c.number_format=EUR
    Lw.cell(r,6,b).font=black; Lw.cell(r,7,note).font=black
    c=Lw.cell(r,8,inc); c.font=blue
last=len(lines)+1
for col,w in zip("ABCDEFGH",[30,62,7,11,12,14,70,9]): Lw.column_dimensions[col].width=w
Lw.freeze_panes="A2"

S["A1"]="SUNDIAL: budget to build the nine panels"; S["A1"].font=Font(name=F,bold=True,size=14)
S["A2"]="Draft, 25 Nov 2026 (MVP v1). Hardware, the first event, and yearly running costs (Sole and the event)."; S["A2"].font=black
S["A4"]="Node"; S["B4"]="Cost (€)"; S["C4"]="Share"
for c in ("A4","B4","C4"): S[c].font=hdr; S[c].fill=hfill
rng=f"Lines!$E$2:$E${last}"; nr=f"Lines!$A$2:$A${last}"; ir=f"Lines!$H$2:$H${last}"
r=5
for n in nodes:
    S.cell(r,1,n).font=black
    c=S.cell(r,2,f'=SUMIFS({rng},{nr},A{r},{ir},"Yes")'); c.font=black; c.number_format=EUR
    r+=1
first,lastn=5,r-1
S.cell(r,1,"Build subtotal").font=bold
c=S.cell(r,2,f"=SUM(B{first}:B{lastn})"); c.font=bold; c.number_format=EUR; sub=r
for rr in range(first,lastn+1):
    c=S.cell(rr,3,f"=IFERROR(B{rr}/$B${sub},0)"); c.font=black; c.number_format='0.0%'
r+=1
S.cell(r,1,"Contingency").font=black
cont=r
r+=1
S.cell(r,1,"Build total").font=bold
c=S.cell(r,2,f"=B{sub}+B{cont}"); c.font=bold; c.number_format=EUR; build=r
r+=1
S.cell(r,1,"Each following year: insurance, domain, upkeep, the year's print").font=black
c=S.cell(r,2,f'=SUMIFS({rng},{nr},"Running, each year",{ir},"Yes")'); c.font=black; c.number_format=EUR; run=r
r+=1
S.cell(r,1,"Total to build and run the first year").font=Font(name=F,bold=True,size=12)
c=S.cell(r,2,f"=B{build}"); c.font=Font(name=F,bold=True,size=12); c.number_format=EUR; tot=r
for rr in (sub,build,tot):
    for cc in (1,2,3): S.cell(rr,cc).border=Border(top=thin)
r+=2
S.cell(r,1,"Contingency rate").font=black
c=S.cell(r,2,0.15); c.font=blue; c.fill=yfill; c.number_format='0%'
c=S.cell(cont,2,f"=B{sub}*B{r}"); c.font=black; c.number_format=EUR
r+=2
S.cell(r,1,"Option, not in the total:").font=bold; r+=1
S.cell(r,1,"Post panel (in place of one wall)").font=black
c=S.cell(r,2,f'=SUMIFS({rng},{nr},"Post option")'); c.font=black; c.number_format=EUR
r+=1
S.cell(r,1,"Carrier board (on hold; would replace some MVP parts)").font=black
c=S.cell(r,2,f'=SUMIFS({rng},{nr},"Carrier board (on hold)")'); c.font=black; c.number_format=EUR
r+=2
notes=["How to use it",
"Edit only the blue cells: quantities, unit prices and Include (Yes/No) on the Lines sheet, and the contingency rate above (yellow).",
"Basis on each line: Quote (from the supplier), Listed price (seen online, Nov 2026), Estimate (to be confirmed).",
"Prices include VAT. The first year's insurance, domain and print are in the build cost; the yearly figure starts from the second year.",
"To include a post panel, set its lines' Include to Yes on the Lines sheet.",
"Not included: PVA's labour and travel; the print's sale income."]
S.cell(r,1,notes[0]).font=bold
for t in notes[1:]:
    r+=1; S.cell(r,1,t).font=black
S.column_dimensions["A"].width=40; S.column_dimensions["B"].width=14; S.column_dimensions["C"].width=10
wb.save(out)
