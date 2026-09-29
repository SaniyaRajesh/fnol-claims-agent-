from typing import List, Tuple
from fnol_agent.models import ExtractedFields, ClaimProcessingResult

class ClaimRouter:
    """
    Evaluates extracted FNOL fields against missing field checks and business routing rules.
    """

    MANDATORY_FIELDS = [
        ("policyInformation.policyNumber", lambda f: f.policyInformation.policyNumber),
        ("policyInformation.policyholderName", lambda f: f.policyInformation.policyholderName),
        ("incidentInformation.date", lambda f: f.incidentInformation.date),
        ("incidentInformation.description", lambda f: f.incidentInformation.description),
        ("involvedParties.claimant", lambda f: f.involvedParties.claimant),
        ("involvedParties.contactDetails", lambda f: f.involvedParties.contactDetails),
        ("assetDetails.assetType", lambda f: f.assetDetails.assetType),
        ("assetDetails.estimatedDamage", lambda f: f.assetDetails.estimatedDamage),
        ("otherMandatoryFields.claimType", lambda f: f.otherMandatoryFields.claimType),
    ]

    FRAUD_KEYWORDS = ["fraud", "inconsistent", "staged", "suspicious", "fabricated", "fake"]

    def evaluate(self, extracted: ExtractedFields) -> ClaimProcessingResult:
        missing_fields = self._detect_missing_fields(extracted)
        route, reasoning = self._determine_route(extracted, missing_fields)

        return ClaimProcessingResult(
            extractedFields=extracted,
            missingFields=missing_fields,
            recommendedRoute=route,
            reasoning=reasoning
        )

    def _detect_missing_fields(self, extracted: ExtractedFields) -> List[str]:
        missing = []
        for field_path, getter in self.MANDATORY_FIELDS:
            val = getter(extracted)
            if val is None:
                missing.append(field_path)
            elif isinstance(val, str) and not val.strip():
                missing.append(field_path)
        return missing

    def _determine_route(self, extracted: ExtractedFields, missing_fields: List[str]) -> Tuple[str, str]:
        desc = (extracted.incidentInformation.description or "").lower()
        claim_type = (extracted.otherMandatoryFields.claimType or "").lower()
        damage = extracted.assetDetails.estimatedDamage

        # 1. Investigation Flag Rule (Fraud / Inconsistency Detection)
        triggered_fraud_words = [kw for kw in self.FRAUD_KEYWORDS if kw in desc]
        if triggered_fraud_words:
            words_str = ", ".join(f"'{w}'" for w in triggered_fraud_words)
            return (
                "Investigation Flag",
                f"Incident description contains fraud/inconsistency keyword(s): {words_str}. Flagged for Special Investigation Unit (SIU) review."
            )

        # 2. Specialist Queue Rule (Claim Type = Injury)
        if "injury" in claim_type or "medical" in claim_type or "bodily injury" in desc:
            display_claim_type = extracted.otherMandatoryFields.claimType or "Injury"
            return (
                "Specialist Queue",
                f"Claim type or description indicates personal injury ('{display_claim_type}'). Routed to Injury Specialist Queue for clinical review."
            )

        # 3. Manual Review Rule (Missing Mandatory Fields)
        if missing_fields:
            missing_str = ", ".join(missing_fields)
            return (
                "Manual Review",
                f"Document is missing mandatory field(s): {missing_str}. Routed for manual review and field verification."
            )

        # 4. Fast-track Rule (Estimated Damage < 25,000)
        if damage is not None and damage < 25000:
            return (
                "Fast-track",
                f"Estimated damage (${damage:,.2f}) is below the $25,000 threshold and all mandatory fields are complete."
            )

        # 5. Standard Review Rule (Estimated Damage >= 25,000 or Default)
        if damage is not None:
            return (
                "Standard Review",
                f"Estimated damage (${damage:,.2f}) meets or exceeds the $25,000 fast-track threshold. Routed for standard adjuster assessment."
            )

        return (
            "Manual Review",
            "Unable to verify estimated damage amount. Routed for manual adjuster assessment."
        )
