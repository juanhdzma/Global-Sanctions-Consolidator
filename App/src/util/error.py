class CustomError(Exception):
    """Excepción personalizada con mensaje opcional."""

    def __init__(self, message="Se ha producido un error desconocido"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return "❌  Error durante: " + self.message
