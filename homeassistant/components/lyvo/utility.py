import subprocess  # noqa: D100

from .const import DEV_SN


def get_serial_number() -> str:
    """Extract hardware serial number."""
    serial_number = subprocess.run(  # noqa: S602
        ["cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2"],
        shell=True,
        check=True,
        text=True,
        capture_output=True,
    ).stdout
    if not serial_number:
        serial_number = DEV_SN
    return serial_number


def get_mac_serial_number() -> str:
    """Get serial number of a macOS based system."""
    cmd = "/usr/sbin/system_profiler SPHardwareDataType | awk '/Serial Number/ {print $4}'"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)  # noqa: S602
    return result.stdout.strip()
