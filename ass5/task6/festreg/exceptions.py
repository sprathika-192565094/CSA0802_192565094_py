class FestError(Exception):
    """Base class for all fest-registration problems."""


class InvalidRecord(FestError):
    """A line is damaged or contains an invalid field (raised in validator, handled in pipeline)."""


class DuplicateRegistration(FestError):
    """The register number has already been registered (raised and handled in pipeline)."""
