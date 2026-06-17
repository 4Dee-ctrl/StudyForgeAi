from __future__ import annotations

from app.schemas.models import StudyAidType
from app.services.format_validator import missing_expected_sections
from app.services.local_generator import LocalStudyAidGenerator


SAMPLE_TEXT = """
Photosynthesis is the process plants use to convert light energy into chemical energy.
Chlorophyll captures sunlight inside chloroplasts. Water and carbon dioxide are transformed
into glucose and oxygen. The light-dependent reactions produce energy carriers, and the Calvin
cycle uses carbon dioxide to build sugars. Photosynthesis supports plant growth and supplies
oxygen used by many living organisms.
"""


def main() -> None:
	generator = LocalStudyAidGenerator()
	for study_aid_type in StudyAidType:
		result = generator.generate(text=SAMPLE_TEXT, study_aid_type=study_aid_type)
		missing = missing_expected_sections(content=result.content, study_aid_type=study_aid_type)
		if missing:
			raise SystemExit(f"{study_aid_type}: missing {missing}")
		print(f"{study_aid_type}: ok")


if __name__ == "__main__":
	main()
