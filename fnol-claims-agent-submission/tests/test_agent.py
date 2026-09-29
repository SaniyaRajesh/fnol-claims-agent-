import unittest
import os
from pathlib import Path
from fnol_agent.agent import ClaimsProcessingAgent

class TestClaimsProcessingAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.agent = ClaimsProcessingAgent()
        cls.samples_dir = Path(__file__).parent.parent / "samples"

    def test_sample_1_fasttrack_txt(self):
        file_path = self.samples_dir / "sample_1_fasttrack.txt"
        res = self.agent.process_file(str(file_path))
        self.assertEqual(res.recommendedRoute, "Fast-track")
        self.assertEqual(len(res.missingFields), 0)
        self.assertEqual(res.extractedFields.policyInformation.policyNumber, "POL-994821")
        self.assertEqual(res.extractedFields.assetDetails.estimatedDamage, 3200.0)
        self.assertIn("below the $25,000 threshold", res.reasoning)

    def test_sample_1_fasttrack_pdf(self):
        file_path = self.samples_dir / "sample_1_fasttrack.pdf"
        res = self.agent.process_file(str(file_path))
        self.assertEqual(res.recommendedRoute, "Fast-track")
        self.assertEqual(len(res.missingFields), 0)
        self.assertEqual(res.extractedFields.policyInformation.policyNumber, "POL-994821")

    def test_sample_2_manual_review(self):
        file_path = self.samples_dir / "sample_2_manual_review.txt"
        res = self.agent.process_file(str(file_path))
        self.assertEqual(res.recommendedRoute, "Manual Review")
        self.assertTrue(len(res.missingFields) > 0)
        self.assertIn("policyInformation.policyNumber", res.missingFields)
        self.assertIn("contactDetails", str(res.missingFields))

    def test_sample_3_investigation(self):
        file_path = self.samples_dir / "sample_3_investigation.txt"
        res = self.agent.process_file(str(file_path))
        self.assertEqual(res.recommendedRoute, "Investigation Flag")
        self.assertIn("staged", res.reasoning.lower())

    def test_sample_4_injury_specialist(self):
        file_path = self.samples_dir / "sample_4_injury_specialist.txt"
        res = self.agent.process_file(str(file_path))
        self.assertEqual(res.recommendedRoute, "Specialist Queue")
        self.assertIn("Personal Injury", res.extractedFields.otherMandatoryFields.claimType)

    def test_sample_5_high_value(self):
        file_path = self.samples_dir / "sample_5_high_value.txt"
        res = self.agent.process_file(str(file_path))
        self.assertEqual(res.recommendedRoute, "Standard Review")
        self.assertEqual(res.extractedFields.assetDetails.estimatedDamage, 185000.0)
        self.assertIn("exceeds the $25,000", res.reasoning)

if __name__ == '__main__':
    unittest.main()
