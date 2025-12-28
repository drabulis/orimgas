"""
Script to create a sample PDF and attach it to all instructions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orimgas.settings')
django.setup()

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from django.core.files import File
from orimgasapp import models

# Create the PDF
pdf_filename = 'media/sample_instruction.pdf'
os.makedirs('media', exist_ok=True)

doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
story = []
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor='darkblue',
    spaceAfter=30,
    alignment=TA_CENTER
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor='darkgreen',
    spaceAfter=12,
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    alignment=TA_JUSTIFY,
    spaceAfter=12,
)

# Page 1
story.append(Paragraph("Darbuotojų Saugos Instrukcija", title_style))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("1. Įvadas", heading_style))
story.append(Paragraph(
    "Ši instrukcija skirta užtikrinti saugią darbo aplinką ir sumažinti darbo nelaimingų "
    "atsitikimų riziką. Visi darbuotojai privalo susipažinti su šia instrukcija ir "
    "laikytis joje nurodytų reikalavimų.",
    body_style
))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("1.1. Instrukcijos tikslas", heading_style))
story.append(Paragraph(
    "Šios instrukcijos tikslas - nustatyti pagrindinius saugaus darbo principus, "
    "darbuotojų pareigas ir atsakomybę darbo saugos srityje. Instrukcija taikoma "
    "visiems įmonės darbuotojams, nepriklausomai nuo jų pareigų ar darbo stažo.",
    body_style
))
story.append(PageBreak())

# Page 2
story.append(Paragraph("2. Bendrosios nuostatos", heading_style))
story.append(Paragraph(
    "Darbuotojai privalo:<br/>"
    "• Atidžiai susipažinti su darbo saugos instrukcijomis<br/>"
    "• Laikytis nustatytų darbo saugos reikalavimų<br/>"
    "• Naudoti asmenines apsaugos priemones<br/>"
    "• Nedelsiant pranešti vadovui apie pastebėtus pažeidimus<br/>"
    "• Dalyvauti periodiniuose darbo saugos mokymuose",
    body_style
))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("2.1. Darbuotojų teisės", heading_style))
story.append(Paragraph(
    "Darbuotojas turi teisę atsisakyti dirbti pavojingomis sąlygomis, kurios kelia "
    "grėsmę jo gyvybei ar sveikatai. Apie tokią situaciją darbuotojas privalo "
    "nedelsiant informuoti tiesioginį vadovą ir darbo saugos specialistą.",
    body_style
))
story.append(PageBreak())

# Page 3
story.append(Paragraph("3. Asmeninės apsaugos priemonės", heading_style))
story.append(Paragraph(
    "Asmeninės apsaugos priemonės (AAP) yra būtinos darbuotojų saugai užtikrinti. "
    "Darbdavys privalo suteikti darbuotojams reikalingas AAP nemokamai.",
    body_style
))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("3.1. AAP rūšys", heading_style))
story.append(Paragraph(
    "Priklausomai nuo atliekamo darbo pobūdžio, gali būti naudojamos šios AAP:<br/>"
    "• Apsauginiai drabužiai<br/>"
    "• Apsauginiai batai<br/>"
    "• Apsauginiai pirštinės<br/>"
    "• Apsauginiai akiniai<br/>"
    "• Kvėpavimo takų apsaugos priemonės<br/>"
    "• Klausos apsaugos priemonės<br/>"
    "• Galvos apsaugos priemonės (šalmai)",
    body_style
))
story.append(PageBreak())

# Page 4
story.append(Paragraph("4. Priešgaisrinė sauga", heading_style))
story.append(Paragraph(
    "Kiekvienas darbuotojas privalo žinoti priešgaisrinės saugos taisykles ir "
    "gebėti jomis pasinaudoti kritinėje situacijoje. Darbo vietoje turi būti "
    "aiškiai pažymėtos evakuacijos išėjimai ir priešgaisrinės apsaugos priemonės.",
    body_style
))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("4.1. Veiksmai gaisro atveju", heading_style))
story.append(Paragraph(
    "Pastebėjus gaisrą arba jo požymius:<br/>"
    "1. Nedelsiant pranešti apie gaisrą telefonais 112 arba 01<br/>"
    "2. Informuoti kitus darbuotojus ir pradėti evakuaciją<br/>"
    "3. Jei įmanoma, bandyti gesinti gaisrą pirminėmis gesinimo priemonėmis<br/>"
    "4. Užtikrinti, kad visi darbuotojai saugiai evakuoti<br/>"
    "5. Laukti gelbėjimo tarnybų atvykimo saugioje vietoje",
    body_style
))
story.append(PageBreak())

# Page 5
story.append(Paragraph("5. Baigiamosios nuostatos", heading_style))
story.append(Paragraph(
    "Ši instrukcija peržiūrima ir prireikus atnaujinama kartą per metus arba "
    "pasikeitus darbo sąlygoms, technologijoms ar teisės aktų reikalavimams.",
    body_style
))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("5.1. Atsakomybė", heading_style))
story.append(Paragraph(
    "Už šios instrukcijos vykdymą atsakingi visi įmonės darbuotojai. "
    "Pažeidus darbo saugos reikalavimus, darbuotojams gali būti taikomos "
    "drausminės nuobaudos pagal galiojančius teisės aktus ir įmonės darbo "
    "tvarkos taisykles.",
    body_style
))
story.append(Spacer(1, 2*cm))
story.append(Paragraph(
    "Instrukcija patvirtinta: 2025-12-26<br/>"
    "Kitas peržiūros terminas: 2026-12-26",
    body_style
))

# Build PDF
doc.build(story)
print(f"✓ Created PDF: {pdf_filename}")

# Now attach to all instructions
print("\nAttaching PDF to instructions...")

# Instruction model
instructions = models.Instruction.objects.all()
count = 0
with open(pdf_filename, 'rb') as f:
    for instruction in instructions:
        instruction.pdf.save('sample_instruction.pdf', File(f), save=True)
        count += 1
print(f"✓ Updated {count} Instruction records")

# PriesgiasrinesInstrukcijos
priesgiasrines = models.PriesgiasrinesInstrukcijos.objects.all()
count = 0
with open(pdf_filename, 'rb') as f:
    for instrukcija in priesgiasrines:
        instrukcija.pdf.save('sample_instruction.pdf', File(f), save=True)
        count += 1
print(f"✓ Updated {count} PriesgiasrinesInstrukcijos records")

# CivilineSauga
civiline = models.CivilineSauga.objects.all()
count = 0
with open(pdf_filename, 'rb') as f:
    for sauga in civiline:
        sauga.pdf.save('sample_instruction.pdf', File(f), save=True)
        count += 1
print(f"✓ Updated {count} CivilineSauga records")

# Mokymai
mokymai = models.Mokymai.objects.all()
count = 0
with open(pdf_filename, 'rb') as f:
    for mokymas in mokymai:
        mokymas.pdf.save('sample_instruction.pdf', File(f), save=True)
        count += 1
print(f"✓ Updated {count} Mokymai records")

# KitiDokumentai
kiti = models.KitiDokumentai.objects.all()
count = 0
with open(pdf_filename, 'rb') as f:
    for doc in kiti:
        doc.pdf.save('sample_instruction.pdf', File(f), save=True)
        count += 1
print(f"✓ Updated {count} KitiDokumentai records")

# AsmeninesApsaugosPriemones (AAP)
aap = models.AsmeninesApsaugosPriemones.objects.all()
count = 0
with open(pdf_filename, 'rb') as f:
    for priemone in aap:
        if hasattr(priemone, 'pdf'):
            priemone.pdf.save('sample_instruction.pdf', File(f), save=True)
            count += 1
print(f"✓ Updated {count} AsmeninesApsaugosPriemones records")

print("\n✅ All done! PDFs attached to all instructions.")
