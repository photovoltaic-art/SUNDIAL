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
("Panels and boards","Retired PV panel, Trina TSM-185DC01 class (9 + 1 spare)",10,30,E,"Second-hand / end-of-life; may be donated. Source still to confirm","Yes"),
("Panels and boards","Board designer: schematic review, layout, files (CARRIER.md brief)",1,1000,E,"One-off; get quotes (Italian/European design house)","Yes"),
("Panels and boards","Carrier v1, small run of 5, assembled (bench test of the sun sensor)",5,100,E,"Small-run setup costs make v1 dear per board","Yes"),
("Panels and boards","Carrier v2, run of 10, assembled (9 panels + 1 spare)",10,60,E,"CARRIER.md: order 5 of v1, fix, then 10 of v2","Yes"),
("Panels and boards","ELEGOO ESP32 30-pin dev boards (v1 bench + v2)",15,9,E,"","Yes"),
("Panels and boards","Buck converter modules (8–60 V in, 5 V out)",15,5,E,"","Yes"),
("Panels and boards","Supercapacitor pairs (2 x 10 F), DS18B20 probe, CR2032",10,12,E,"","Yes"),
("Panels and boards","IP65 box, glands, breather vent, tamper screws",10,32,E,"CARRIER.md: about 150 x 110 x 70 mm","Yes"),
("Panels and boards","Cable, fuses, terminals",10,15,E,"","Yes"),

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

("Shared and spares","Spares: supercaps, coin cells, probe, fixings",1,60,E,"SUNDIAL.md 5","Yes"),
("Shared and spares","Bench supply and test leads",1,60,E,"If not already owned","Yes"),
("Shared and spares","Shipping",1,100,E,"","Yes"),

("Post option","Steel post and base",1,450,E,"Only where no wall works (POST.md)","No"),
("Post option","Structural engineer's sign-off",1,400,E,"","No"),
("Post option","USB-C PD charger module, sockets, shelf, plate",1,110,E,"","No"),

("Running, each year","Insurance renewal",1,400,E,"","Yes"),
("Running, each year","Domain renewal",1,30,E,"","Yes"),
("Running, each year","Upkeep: coin cells, supercaps over time, cleaning",1,60,E,"","Yes"),
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
S["A2"]="Draft, 25 Oct 2026. Hardware, the first event, and yearly running costs (Sole and the event)."; S["A2"].font=black
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
r+=2
notes=["How to use it",
"Edit only the blue cells: quantities, unit prices and Include (Yes/No) on the Lines sheet, and the contingency rate above (yellow).",
"Basis on each line: Quote (from the supplier), Listed price (seen online, Oct 2026), Estimate (to be confirmed).",
"Prices include VAT. The first year's insurance, domain and print are in the build cost; the yearly figure starts from the second year.",
"To include a post panel, set its lines' Include to Yes on the Lines sheet.",
"Not included: PVA's labour and travel; the print's sale income."]
S.cell(r,1,notes[0]).font=bold
for t in notes[1:]:
    r+=1; S.cell(r,1,t).font=black
S.column_dimensions["A"].width=40; S.column_dimensions["B"].width=14; S.column_dimensions["C"].width=10
wb.save(out)
