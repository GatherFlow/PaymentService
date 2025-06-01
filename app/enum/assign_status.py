
import enum


class AssignStatus(enum.Enum):
    pending = "pending"
    success = "success"
    expired = "expired"
    cancelled = "cancelled"
