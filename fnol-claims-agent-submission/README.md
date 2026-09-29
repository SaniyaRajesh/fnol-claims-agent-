# Autonomous Insurance Claims Processing Agent

A lightweight end-to-end agent for processing **First Notice of Loss (FNOL)** insurance claim documents.

The system accepts PDF or TXT FNOL documents, extracts structured claim information, identifies missing mandatory fields, classifies the claim using deterministic business rules, routes it to the appropriate workflow, and provides a short explanation for the routing decision.

## 1. Problem Statement

The objective is to automate the first stage of insurance claims processing:

1. Extract key fields from an FNOL document.
2. Identify missing or incomplete mandatory information.
3. Detect suspicious/inconsistent indicators in the incident description.
4. Classify the claim.
5. Route the claim to the appropriate workflow.
6. Provide a concise explanation for the routing decision.

## 2. Approach

The project uses a two-level extraction strategy:

### A. Rule-based extraction

A deterministic regex/heuristic extractor is used by default. It can extract:

- Policy number
- Policyholder name
- Policy effective dates
- Incident date and time
- Incident location
- Incident description
- Claimant
- Third parties
- Contact details
- Asset type
- Asset ID / VIN / plate
- Estimated damage
- Claim type
- Attachments
- Initial estimate

This approach works without an external API key.

### B. Optional LLM-assisted extraction

If `GEMINI_API_KEY` is configured, the application can use **Gemini 2.5 Flash** with structured JSON output to extract the FNOL fields.

If the LLM call fails or no API key is configured, the system automatically falls back to the local rule-based extractor.

This makes the application usable both with and without an external LLM service.

## 3. Processing Workflow

```text
FNOL PDF / TXT
       |
       v
Document Loader
       |
       v
Text Extraction
       |
       v
FNOL Field Extractor
   /           \
LLM          Regex/Heuristics
   \           /
       v
Structured Pydantic Model
       |
       v
Mandatory Field Validation
       |
       v
Claim Routing Rules
       |
       +--> Investigation Flag
       +--> Specialist Queue
       +--> Manual Review
       +--> Fast-track
       +--> Standard Review
       |
       v
Routing Explanation + JSON Result
```

## 4. Routing Logic

The routing rules are evaluated in the following order:

### Investigation Flag

Triggered when the incident description contains indicators such as:

- `fraud`
- `inconsistent`
- `staged`
- `suspicious`
- `fabricated`
- `fake`

The claim is routed for Special Investigation Unit (SIU) review.

### Specialist Queue

Triggered when the claim type or incident description indicates:

- injury
- medical treatment
- bodily injury

The claim is routed to an Injury Specialist Queue.

### Manual Review

Triggered when one or more mandatory fields are missing or blank.

### Fast-track

Triggered when:

- all mandatory fields are present, and
- estimated damage is below **$25,000**.

### Standard Review

Triggered when estimated damage is **$25,000 or higher**.

## 5. Mandatory Fields

The current validation checks:

```text
policyInformation.policyNumber
policyInformation.policyholderName
incidentInformation.date
incidentInformation.description
involvedParties.claimant
involvedParties.contactDetails
assetDetails.assetType
assetDetails.estimatedDamage
otherMandatoryFields.claimType
```

Values such as `N/A`, `Unknown`, `Missing`, and `[NOT PROVIDED]` are treated as unavailable.

## 6. Project Structure

```text
fnol-claims-agent/
│
├── fnol_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── document_loader.py
│   ├── extractor.py
│   ├── models.py
│   └── router.py
│
├── samples/
│   ├── sample_1_fasttrack.pdf
│   ├── sample_1_fasttrack.txt
│   ├── sample_2_manual_review.pdf
│   ├── sample_2_manual_review.txt
│   ├── sample_3_investigation.pdf
│   ├── sample_3_investigation.txt
│   ├── sample_4_injury_specialist.pdf
│   ├── sample_4_injury_specialist.txt
│   ├── sample_5_high_value.pdf
│   └── sample_5_high_value.txt
│
├── tests/
│   └── test_agent.py
│
├── app.py
├── cli.py
├── generate_samples.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 7. Technologies Used

- Python
- FastAPI
- Pydantic
- PyPDF
- Uvicorn
- Google GenAI / Gemini 2.5 Flash (optional)
- HTML + JavaScript + Tailwind CSS for the web dashboard
- unittest for automated verification

## 8. Installation

### Clone the repository

```bash
git clone https://github.com/<YOUR-USERNAME>/fnol-claims-agent.git
cd fnol-claims-agent
```

### Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 9. Optional Gemini Configuration

The project works without an API key.

To enable Gemini-assisted extraction, set:

Windows Command Prompt:

```cmd
set GEMINI_API_KEY=your_api_key_here
```

PowerShell:

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

Do not commit API keys to GitHub.

## 10. Run the Web Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:8000
```

The dashboard supports:

- Uploading PDF/TXT FNOL documents
- Loading the five preset sample claims
- Viewing extracted structured fields
- Viewing missing mandatory fields
- Viewing the recommended workflow
- Viewing routing reasoning
- Copying the raw JSON response

## 11. Run from the CLI

Process one document:

```bash
python cli.py process samples/sample_1_fasttrack.pdf
```

Batch process the sample directory:

```bash
python cli.py batch samples/
```

## 12. Run Tests

```bash
python -m unittest discover -s tests -v
```

The included test suite verifies:

| Scenario | Expected Route |
|---|---|
| Minor auto collision | Fast-track |
| Missing mandatory fields | Manual Review |
| Suspicious/staged claim | Investigation Flag |
| Personal injury claim | Specialist Queue |
| High-value property claim | Standard Review |

The current test suite contains **6 automated tests**, including PDF and TXT processing for the fast-track scenario.

## 13. Example Result

A processed claim returns structured JSON similar to:

```json
{
  "extractedFields": {
    "policyInformation": {
      "policyNumber": "POL-994821",
      "policyholderName": "Sarah Jenkins",
      "effectiveDates": "2026-01-01 to 2026-12-31"
    },
    "incidentInformation": {
      "date": "2026-03-10",
      "time": "08:45 AM",
      "location": "Corner of 5th Ave and Main St, Austin, TX",
      "description": "Vehicle A was stopped at red light when Vehicle B bumped rear bumper..."
    },
    "assetDetails": {
      "assetType": "Automobile (2023 Toyota Camry)",
      "estimatedDamage": 3200.0
    },
    "otherMandatoryFields": {
      "claimType": "Vehicle Collision"
    }
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Estimated damage ($3,200.00) is below the $25,000 threshold and all mandatory fields are complete."
}
```

## 14. Design Notes

The routing layer is intentionally deterministic so that each routing decision can be traced to an explicit business rule.

The LLM is optional and is used only for structured field extraction. The final workflow routing is performed by the application's business-rule engine rather than relying on an unconstrained LLM decision.

This provides predictable, explainable routing behavior while still allowing LLM-assisted document understanding.

## 15. Limitations

- The extractor is designed for the supplied FNOL-style documents and similar structured documents.
- Scanned/image-only PDFs would require OCR before text extraction.
- The current routing rules are demonstration/business rules for the assessment and are not intended for production insurance adjudication.
- The suspicious-claim rule uses explicit indicators in the incident description; it is not a comprehensive fraud-detection system.
