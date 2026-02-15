from fastapi import APIRouter

router = APIRouter(prefix="/dataloggers/{serial}/inverter", tags=["inverter"])


@router.get("/settings")
async def get_all_inverter_settings(serial: str) -> list[str]:
    """List all available inverter setting names."""
    return ["max_output_power", "startup_voltage", "shutdown_voltage", "grid_frequency"]


@router.get("/settings/{name}")
async def get_single_inverter_setting(serial: str, name: str) -> dict[str, str]:
    """Get a specific inverter setting by name."""
    return {"name": name, "value": "example_value"}


@router.put("/settings/{name}")
async def update_single_inverter_setting(serial: str, name: str, value: str) -> dict[str, str]:
    """Update a specific inverter setting by name."""
    return {"name": name, "value": value}


# Inverter register endpoints
@router.get("/registers/{register}")
async def read_single_inverter_register(serial: str, register: int) -> dict[str, int]:
    """Read a single register from the inverter."""
    return {"register": register, "value": 12345}


@router.get("/registers")
async def read_all_inverter_registers(serial: str, start: int, end: int) -> list[dict[str, int]]:
    """Read multiple registers from the inverter."""
    return [{"register": reg, "value": 12345 + reg} for reg in range(start, end + 1)]


@router.put("/registers/{register}")
async def write_single_inverter_register(serial: str, register: int, value: int) -> dict[str, int]:
    """Write a single register on the inverter."""
    return {"register": register, "value": value}


@router.put("/registers")
async def write_multiple_inverter_registers(
    serial: str, registers: list[dict[str, int]]
) -> list[dict[str, int]]:
    """Write multiple registers on the inverter.

    Body example:
    [
        {"register": 100, "value": 5000},
        {"register": 101, "value": 3000}
    ]
    """
    return registers


@router.post("/raw-frames")
async def send_raw_frame(
    serial: str, protocol_id: int, function_code: int, payload: str
) -> dict[str, str]:
    """Send a raw frame to the inverter."""
    return {"payload": payload}
