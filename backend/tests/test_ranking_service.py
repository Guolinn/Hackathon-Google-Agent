from app.config import get_settings
from app.services.data_repository import DataRepository
from app.services.supplier_service import SupplierService


def test_best_supplier_for_burn_kits_is_oakland():
    service = SupplierService(DataRepository(get_settings()))

    result, _ = service.search("Burn kits", 240, "HOSP-SFGH")

    assert result["candidates"][0]["supplier_name"] == "MedSupply Oakland"
    assert result["candidates"][0]["recommendation"] == "Best"


def test_best_supplier_for_albuterol_is_ucsf():
    service = SupplierService(DataRepository(get_settings()))

    result, _ = service.search("Albuterol doses", 120, "HOSP-SFGH")

    assert result["candidates"][0]["supplier_name"] == "UCSF Storage"


def test_best_supplier_for_oxygen_is_norcal():
    service = SupplierService(DataRepository(get_settings()))

    result, _ = service.search("Oxygen cylinders", 36, "HOSP-SFGH")

    assert result["candidates"][0]["supplier_name"] == "NorCal Oxygen"
