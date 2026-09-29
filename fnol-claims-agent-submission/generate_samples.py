import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLES_DIR = Path("samples")
SAMPLES_DIR.mkdir(exist_ok=True)

SAMPLE_DATA = [
    {
        "filename": "sample_1_fasttrack",
        "title": "FIRST NOTICE OF LOSS (FNOL) - AUTOMOTIVE CLAIM",
        "policy_number": "POL-994821",
        "policyholder_name": "Sarah Jenkins",
        "effective_dates": "2026-01-01 to 2026-12-31",
        "date": "2026-03-10",
        "time": "08:45 AM",
        "location": "Corner of 5th Ave and Main St, Austin, TX",
        "description": "Vehicle A was stopped at red light when Vehicle B bumped rear bumper at low speed. Minor bumper cover dent.",
        "claimant": "Sarah Jenkins",
        "third_parties": "Michael Scott (Driver of Honda Civic)",
        "contact_details": "555-0199 / sjenkins@example.com",
        "asset_type": "Automobile (2023 Toyota Camry)",
        "asset_id": "VIN 4T1B11HK5NW123456",
        "estimated_damage": "$3,200.00",
        "claim_type": "Vehicle Collision",
        "attachments": "bumper_photo_1.jpg, police_report_austin.pdf",
        "initial_estimate": "$3,200.00"
    },
    {
        "filename": "sample_2_manual_review",
        "title": "FIRST NOTICE OF LOSS (FNOL) - PROPERTY DAMAGE",
        "policy_number": "",  # Missing policy number
        "policyholder_name": "Robert Vance",
        "effective_dates": "2025-06-01 to 2026-06-01",
        "date": "2026-02-14",
        "time": "11:20 PM",
        "location": "456 Elm Street, Dallas, TX",
        "description": "Water pipe burst in upstairs bathroom causing ceiling collapse in kitchen below.",
        "claimant": "Robert Vance",
        "third_parties": "None",
        "contact_details": "",  # Missing contact details
        "asset_type": "Residential Property",
        "asset_id": "PROP-8821",
        "estimated_damage": "$14,500.00",
        "claim_type": "Property Damage",
        "attachments": "plumbing_repair_invoice.pdf",
        "initial_estimate": "$14,500.00"
    },
    {
        "filename": "sample_3_investigation",
        "title": "FIRST NOTICE OF LOSS (FNOL) - AUTO INCIDENT",
        "policy_number": "POL-332910",
        "policyholder_name": "David Miller",
        "effective_dates": "2026-02-01 to 2027-02-01",
        "date": "2026-03-22",
        "time": "02:15 AM",
        "location": "Industrial Park Lot, Houston, TX",
        "description": "Claimant states vehicle was parked when struck. However witness statements are inconsistent and physical damage looks staged.",
        "claimant": "David Miller",
        "third_parties": "Unknown",
        "contact_details": "555-0144 / dmiller@example.com",
        "asset_type": "Automobile (2021 BMW M3)",
        "asset_id": "VIN WBS8M9C58M5678901",
        "estimated_damage": "$18,000.00",
        "claim_type": "Vehicle Collision",
        "attachments": "scene_photo_1.png",
        "initial_estimate": "$18,000.00"
    },
    {
        "filename": "sample_4_injury_specialist",
        "title": "FIRST NOTICE OF LOSS (FNOL) - LIABILITY INJURY",
        "policy_number": "POL-771092",
        "policyholder_name": "Metro Supermarket Inc",
        "effective_dates": "2026-01-15 to 2027-01-15",
        "date": "2026-03-18",
        "time": "05:30 PM",
        "location": "Supermarket Store #4, San Antonio, TX",
        "description": "Customer slipped on wet floor near produce section causing severe wrist sprain and head injury.",
        "claimant": "Elena Rostova",
        "third_parties": "Metro Supermarket Store",
        "contact_details": "555-0822 / elena.rostova@example.com",
        "asset_type": "Commercial Store Premises",
        "asset_id": "STORE-SAN-04",
        "estimated_damage": "$12,000.00",
        "claim_type": "Personal Injury",
        "attachments": "medical_report_er.pdf, incident_report.pdf",
        "initial_estimate": "$12,000.00"
    },
    {
        "filename": "sample_5_high_value",
        "title": "FIRST NOTICE OF LOSS (FNOL) - COMMERCIAL LOSS",
        "policy_number": "POL-550119",
        "policyholder_name": "Apex Logistics LLC",
        "effective_dates": "2026-01-01 to 2026-12-31",
        "date": "2026-03-01",
        "time": "04:00 AM",
        "location": "Warehouse B, 789 Logistics Way, Fort Worth, TX",
        "description": "Electrical fire originated in storage rack section B destroying commercial inventory and structural roof trusses.",
        "claimant": "Apex Logistics LLC",
        "third_parties": "None",
        "contact_details": "555-0900 / claims@apexlogistics.com",
        "asset_type": "Commercial Property & Inventory",
        "asset_id": "BLDG-FW-02",
        "estimated_damage": "$185,000.00",
        "claim_type": "Commercial Property",
        "attachments": "fire_dept_report.pdf, inventory_loss_sheet.xlsx",
        "initial_estimate": "$185,000.00"
    }
]

def create_txt_sample(data: dict):
    txt_path = SAMPLES_DIR / f"{data['filename']}.txt"
    content = f"""====================================================================
{data['title']}
====================================================================

--- POLICY INFORMATION ---
Policy Number: {data['policy_number']}
Policyholder Name: {data['policyholder_name']}
Effective Dates: {data['effective_dates']}

--- INCIDENT INFORMATION ---
Date of Incident: {data['date']}
Time of Incident: {data['time']}
Incident Location: {data['location']}
Incident Description: {data['description']}

--- INVOLVED PARTIES ---
Claimant Name: {data['claimant']}
Third Parties Involved: {data['third_parties']}
Contact Details: {data['contact_details']}

--- ASSET DETAILS ---
Asset Type: {data['asset_type']}
Asset ID: {data['asset_id']}
Estimated Damage Amount: {data['estimated_damage']}

--- OTHER CLAIM MANDATORY FIELDS ---
Claim Type: {data['claim_type']}
Attachments: {data['attachments']}
Initial Estimate: {data['initial_estimate']}
====================================================================
"""
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created TXT: {txt_path}")

def create_pdf_sample(data: dict):
    pdf_path = SAMPLES_DIR / f"{data['filename']}.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#1E3A8A'), spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#2563EB'), spaceBefore=8, spaceAfter=4)
    normal_style = styles['Normal']

    elements = []
    elements.append(Paragraph(data['title'], title_style))
    elements.append(Spacer(1, 10))

    def field_row(label, val):
        return [Paragraph(f"<b>{label}:</b>", normal_style), Paragraph(val if val else "[NOT PROVIDED]", normal_style)]

    table_data = [
        [Paragraph("<b>Section</b>", heading_style), Paragraph("<b>Field Information</b>", heading_style)],
        field_row("Policy Number", data['policy_number']),
        field_row("Policyholder Name", data['policyholder_name']),
        field_row("Effective Dates", data['effective_dates']),
        field_row("Date of Incident", data['date']),
        field_row("Time of Incident", data['time']),
        field_row("Incident Location", data['location']),
        field_row("Incident Description", data['description']),
        field_row("Claimant Name", data['claimant']),
        field_row("Third Parties", data['third_parties']),
        field_row("Contact Details", data['contact_details']),
        field_row("Asset Type", data['asset_type']),
        field_row("Asset ID", data['asset_id']),
        field_row("Estimated Damage", data['estimated_damage']),
        field_row("Claim Type", data['claim_type']),
        field_row("Attachments", data['attachments']),
        field_row("Initial Estimate", data['initial_estimate']),
    ]

    t = Table(table_data, colWidths=[150, 380])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#111827')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    doc.build(elements)
    print(f"Created PDF: {pdf_path}")

def main():
    print("Generating sample FNOL documents (PDF & TXT)...")
    for sample in SAMPLE_DATA:
        create_txt_sample(sample)
        create_pdf_sample(sample)
    print("All sample FNOL documents created successfully in samples/")

if __name__ == "__main__":
    main()
