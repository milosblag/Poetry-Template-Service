import os
import socket
import time
from typing import Optional

from pydantic import BaseModel, Field

# Application startup time
startup_time = time.time()


class SystemStats(BaseModel):
    """Model for system statistics."""

    process_id: int = Field(..., description="Current process ID")
    hostname: str = Field(..., description="Server hostname")

    # These will require psutil which we'll add to dependencies
    cpu_usage: Optional[float] = Field(
        None,
        description="CPU usage percentage"
    )
    memory_usage: Optional[float] = Field(
        None,
        description="Memory usage percentage"
    )
    disk_usage: Optional[float] = Field(
        None,
        description="Disk usage percentage"
    )


class ServiceHealth(BaseModel):
    """Model for service health information."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime_seconds: int = Field(..., description="Uptime in seconds")
    uptime_human: str = Field(..., description="Human readable uptime")
    system: SystemStats = Field(..., description="System statistics")


def format_uptime(seconds: int) -> str:
    """Format uptime in human readable format."""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


def get_system_stats() -> SystemStats:
    """Get current system statistics."""
    stats = SystemStats(
        process_id=os.getpid(),
        hostname=socket.gethostname(),
        cpu_usage=None,
        memory_usage=None,
        disk_usage=None,
    )

    # Try to get additional stats if psutil is available
    try:
        import psutil

        stats.cpu_usage = psutil.cpu_percent()
        stats.memory_usage = psutil.virtual_memory().percent
        stats.disk_usage = psutil.disk_usage("/").percent
    except ImportError:
        pass

    return stats


def get_service_health(version: str = "1.0.0") -> ServiceHealth:
    """Get comprehensive service health information."""
    uptime_seconds = int(time.time() - startup_time)

    return ServiceHealth(
        status="ok",
        version=version,
        uptime_seconds=uptime_seconds,
        uptime_human=format_uptime(uptime_seconds),
        system=get_system_stats(),
    )
