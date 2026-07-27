import enum


class PurchaseRequestStatus(str, enum.Enum):
    """Lifecycle status of a purchase request."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
