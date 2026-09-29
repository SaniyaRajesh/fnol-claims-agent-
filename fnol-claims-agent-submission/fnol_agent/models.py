from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field

class PolicyInformation(BaseModel):
    policyNumber: Optional[str] = Field(None, description="Insurance policy number")
    policyholderName: Optional[str] = Field(None, description="Name of the policyholder")
    effectiveDates: Optional[str] = Field(None, description="Policy effective date range")

class IncidentInformation(BaseModel):
    date: Optional[str] = Field(None, description="Date of the incident")
    time: Optional[str] = Field(None, description="Time of the incident")
    location: Optional[str] = Field(None, description="Location/address of the incident")
    description: Optional[str] = Field(None, description="Detailed description of the incident")

class InvolvedParties(BaseModel):
    claimant: Optional[str] = Field(None, description="Name of the claimant")
    thirdParties: Optional[str] = Field(None, description="Third parties involved in the incident")
    contactDetails: Optional[str] = Field(None, description="Contact phone/email for parties")

class AssetDetails(BaseModel):
    assetType: Optional[str] = Field(None, description="Type of asset (e.g. Vehicle, Property)")
    assetId: Optional[str] = Field(None, description="Asset Identifier (e.g. VIN, License Plate, Property Address)")
    estimatedDamage: Optional[float] = Field(None, description="Estimated damage amount in USD/currency")

class OtherMandatoryFields(BaseModel):
    claimType: Optional[str] = Field(None, description="Type of claim (e.g. Vehicle Collision, Injury, Property)")
    attachments: List[str] = Field(default_factory=list, description="List of attached documents/photos")
    initialEstimate: Optional[float] = Field(None, description="Initial repair/loss estimate amount")

class ExtractedFields(BaseModel):
    policyInformation: PolicyInformation = Field(default_factory=PolicyInformation)
    incidentInformation: IncidentInformation = Field(default_factory=IncidentInformation)
    involvedParties: InvolvedParties = Field(default_factory=InvolvedParties)
    assetDetails: AssetDetails = Field(default_factory=AssetDetails)
    otherMandatoryFields: OtherMandatoryFields = Field(default_factory=OtherMandatoryFields)

class ClaimProcessingResult(BaseModel):
    extractedFields: ExtractedFields = Field(..., description="Extracted structured fields from FNOL document")
    missingFields: List[str] = Field(default_factory=list, description="List of missing mandatory fields")
    recommendedRoute: str = Field(..., description="Recommended workflow route")
    reasoning: str = Field(..., description="Explanation for the routing decision")

    def to_dict(self) -> dict:
        return self.model_dump()
