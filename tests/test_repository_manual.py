from core.constants import ScanType
from core.database.database import database_manager
from core.database.repository import ScanRepository


database_manager.initialize()

repository = ScanRepository()

scan_id = repository.create_scan(
    target="127.0.0.1",
    scan_type=ScanType.QUICK,
    port_range="1-1000",
)

print("Created scan ID:", scan_id)
print(repository.get_by_id(scan_id))