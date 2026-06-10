from app.config import get_settings
from app.services.data_repository import DataRepository
from app.services.gap_service import GapService


def test_resource_gaps_match_demo_numbers():
    service = GapService(DataRepository(get_settings()))

    result, mode = service.calculate_resource_gaps("INC-2026-0529-MARIN-014")

    assert mode == "mock"
    gaps = {gap["resource"]: gap for gap in result["gaps"]}
    assert gaps["Burn kits"]["needed"] == 420
    assert gaps["Burn kits"]["available"] == 180
    assert gaps["Burn kits"]["gap"] == 240
    assert gaps["Albuterol doses"]["gap"] == 120
    assert gaps["Oxygen cylinders"]["gap"] == 36
    assert gaps["ICU beds"]["gap"] == 5
    assert gaps["ER nurses"]["gap"] == 8
