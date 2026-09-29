import re
import os
import json
from typing import Optional, Dict, Any, List
from fnol_agent.models import (
    ExtractedFields,
    PolicyInformation,
    IncidentInformation,
    InvolvedParties,
    AssetDetails,
    OtherMandatoryFields,
)

class FNOLExtractor:
    """
    Field Extractor for FNOL (First Notice of Loss) documents.
    Uses pattern matching and structural heuristics with optional LLM augmentation.
    """

    IGNORED_VALUES = [
        'n/a', 'none', 'unknown', 'null', '[not provided]', '[missing]',
        '[blank]', 'not provided', 'missing', 'blank', '[n/a]'
    ]

    def extract(self, text: str) -> ExtractedFields:
        """Main extraction method. Tries LLM if configured, otherwise regex heuristic engine."""
        # Try LLM if API key exists
        if os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"):
            try:
                llm_result = self._extract_with_llm(text)
                if llm_result:
                    return llm_result
            except Exception:
                # Fallback silently to rule-based parser on any LLM error
                pass

        return self._extract_with_heuristics(text)

    def _extract_with_heuristics(self, text: str) -> ExtractedFields:
        """Regex and line-by-line key-value parser for FNOL fields."""
        cleaned_text = text.replace('\r', '')

        # 1. Policy Information
        policy_num = self._find_pattern(cleaned_text, [
            r"Policy[ \t]*(?:Number|#|No\.?)[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Policy[ \t]*ID[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"(\bPOL-\d+\b)"
        ])
        holder_name = self._find_pattern(cleaned_text, [
            r"Policyholder[ \t]*(?:Name)?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Insured[ \t]*(?:Name)?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Name[ \t]*of[ \t]*Insured[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        eff_dates = self._find_pattern(cleaned_text, [
            r"Effective[ \t]*(?:Dates?|Period)?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Policy[ \t]*Period[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Coverage[ \t]*Dates?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])

        # 2. Incident Information
        inc_date = self._find_pattern(cleaned_text, [
            r"Date[ \t]*of[ \t]*(?:Incident|Loss|Accident)[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Incident[ \t]*Date[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Date[ \t]*:[ \t]*(?:\n[ \t]*)?(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}|[A-Z][a-z]+\s+\d{1,2},\s*\d{4})"
        ])
        inc_time = self._find_pattern(cleaned_text, [
            r"Time[ \t]*of[ \t]*(?:Incident|Loss|Accident)[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Incident[ \t]*Time[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Time[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        location = self._find_pattern(cleaned_text, [
            r"(?:Incident|Loss)[ \t]*Location[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Location[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Address[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])

        # Multiline description extractor
        description = self._find_multiline_pattern(cleaned_text, [
            r"(?:Incident|Loss)[ \t]*Description[ \t]*:[ \t]*(?:\n[ \t]*)?((?:(?![A-Z][A-Za-z0-9 ]+:|\n[ \t]*---).|\n)+)",
            r"Description[ \t]*:[ \t]*(?:\n[ \t]*)?((?:(?![A-Z][A-Za-z0-9 ]+:|\n[ \t]*---).|\n)+)",
            r"Details[ \t]*:[ \t]*(?:\n[ \t]*)?((?:(?![A-Z][A-Za-z0-9 ]+:|\n[ \t]*---).|\n)+)"
        ])

        # 3. Involved Parties
        claimant = self._find_pattern(cleaned_text, [
            r"Claimant[ \t]*(?:Name)?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Reported[ \t]*By[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        third_parties = self._find_pattern(cleaned_text, [
            r"Third[ \t]*Parties[ \t]*(?:Involved)?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Third[ \t]*Party[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Other[ \t]*Drivers?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        contact_details = self._find_pattern(cleaned_text, [
            r"Contact[ \t]*Details[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Contact[ \t]*(?:Info|Information|Phone|Email)[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Phone/Email[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])

        # 4. Asset Details
        asset_type = self._find_pattern(cleaned_text, [
            r"Asset[ \t]*Type[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Property[ \t]*Type[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Vehicle[ \t]*Type[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        asset_id = self._find_pattern(cleaned_text, [
            r"Asset[ \t]*ID[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"VIN[ \t]*/?[ \t]*Plate[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"VIN[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Serial[ \t]*Number[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        raw_est_damage = self._find_pattern(cleaned_text, [
            r"Estimated[ \t]*Damage[ \t]*(?:Amount)?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Damage[ \t]*Estimate[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Est\.?[ \t]*Damage[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        est_damage = self._parse_amount(raw_est_damage)

        # 5. Other Mandatory Fields
        claim_type = self._find_pattern(cleaned_text, [
            r"Claim[ \t]*Type[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Type[ \t]*of[ \t]*Claim[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Loss[ \t]*Type[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        raw_attachments = self._find_pattern(cleaned_text, [
            r"Attachments?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Attached[ \t]*Files?[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        attachments = self._parse_attachments(raw_attachments)

        raw_init_est = self._find_pattern(cleaned_text, [
            r"Initial[ \t]*Estimate[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Initial[ \t]*Loss[ \t]*Estimate[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)",
            r"Initial[ \t]*Reserve[ \t]*:[ \t]*(?:\n[ \t]*)?([^\n]+)"
        ])
        init_est = self._parse_amount(raw_init_est)

        # Fallback for initial estimate if estimated damage present or vice versa
        if init_est is None and est_damage is not None:
            init_est = est_damage
        elif est_damage is None and init_est is not None:
            est_damage = init_est

        return ExtractedFields(
            policyInformation=PolicyInformation(
                policyNumber=policy_num,
                policyholderName=holder_name,
                effectiveDates=eff_dates
            ),
            incidentInformation=IncidentInformation(
                date=inc_date,
                time=inc_time,
                location=location,
                description=description
            ),
            involvedParties=InvolvedParties(
                claimant=claimant,
                thirdParties=third_parties,
                contactDetails=contact_details
            ),
            assetDetails=AssetDetails(
                assetType=asset_type,
                assetId=asset_id,
                estimatedDamage=est_damage
            ),
            otherMandatoryFields=OtherMandatoryFields(
                claimType=claim_type,
                attachments=attachments,
                initialEstimate=init_est
            )
        )

    def _find_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                val = match.group(1 if match.groups() else 0).strip()
                if val and val.lower() not in self.IGNORED_VALUES:
                    if not val.endswith(':') and not val.startswith('---') and not val.lower().startswith('section'):
                        if not re.match(r"^[A-Z][A-Za-z ]+:", val):
                            return val
        return None

    def _find_multiline_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                val_single = " ".join(val.split())
                if val_single and val_single.lower() not in self.IGNORED_VALUES:
                    return val_single
        return None

    def _parse_amount(self, text_val: Optional[str]) -> Optional[float]:
        if not text_val:
            return None
        matches = re.findall(r"[\d,]+(?:\.\d+)?", text_val)
        if matches:
            cleaned = matches[0].replace(',', '')
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _parse_attachments(self, raw_attachments: Optional[str]) -> List[str]:
        if not raw_attachments:
            return []
        if raw_attachments.lower() in self.IGNORED_VALUES:
            return []
        items = re.split(r'[,;\n]+', raw_attachments)
        return [item.strip() for item in items if item.strip() and item.strip().lower() not in self.IGNORED_VALUES]

    def _extract_with_llm(self, text: str) -> Optional[ExtractedFields]:
        """Optional LLM integration using google-genai or openai if API keys are available."""
        if os.getenv("GEMINI_API_KEY"):
            try:
                from google import genai
                client = genai.Client()
                prompt = (
                    "Extract the following FNOL insurance claims fields into structured JSON:\n"
                    "- policyInformation (policyNumber, policyholderName, effectiveDates)\n"
                    "- incidentInformation (date, time, location, description)\n"
                    "- involvedParties (claimant, thirdParties, contactDetails)\n"
                    "- assetDetails (assetType, assetId, estimatedDamage as float)\n"
                    "- otherMandatoryFields (claimType, attachments as list of strings, initialEstimate as float)\n\n"
                    f"Document Text:\n{text}"
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"response_mime_type": "application/json", "response_schema": ExtractedFields}
                )
                if response.text:
                    data = json.loads(response.text)
                    return ExtractedFields(**data)
            except Exception:
                pass
        return None
