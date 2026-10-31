
from ragsmith.evidence.models import Evidence


def check_evidence_eligibility(evidence: Evidence) -> tuple[bool, str]:
    """Check basic evidence provenance and content completeness."""

    if not isinstance(evidence, Evidence):
        return False, "Invalid evidence object"

    if not evidence.content.strip():
        return False, "Evidence content is empty"

    if not evidence.document_version.strip():
        return False, "Document version is missing"

    if not evidence.locator.strip():
        return False, "Evidence locator is missing"

    return True, "Evidence has basic provenance information"
