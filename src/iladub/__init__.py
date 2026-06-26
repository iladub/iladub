"""iladub — semantic document compiling, the reference implementation of ET(K)L."""
from .contract import SemanticDataContract
from .validate import ValidationResult, validate

__version__ = "0.0.2"

__all__ = [
    "SemanticDataContract",
    "ValidationResult",
    "validate",
    "__version__",
]
