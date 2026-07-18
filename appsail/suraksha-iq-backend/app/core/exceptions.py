class CatalystConnectionError(Exception):
    """Exception raised for errors in the connection to Zoho Catalyst SDK/Services."""
    def __init__(self, message: str = "Failed to connect to Catalyst services"):
        self.message = message
        super().__init__(self.message)


class RepositoryError(Exception):
    """Exception raised when a repository operation fails."""
    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)


class DataValidationError(Exception):
    """Exception raised when data fails validation before insertion/update."""
    def __init__(self, message: str = "Provided data is invalid"):
        self.message = message
        super().__init__(self.message)
