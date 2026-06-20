class EntityNotFound(Exception):
    def __init__(self, entity: str = "Entity", uuid: str = ""):
        self.message = f"{entity} with id '{uuid}' not found"
        super().__init__(self.message)


class AlreadyExistsError(Exception):
    def __init__(self, entity: str = "Entity"):
        self.message = f"{entity} already exists"
        super().__init__(self.message)


class InsufficientFundsError(Exception):
    def __init__(self):
        self.message = "Insufficient funds"
        super().__init__(self.message)


class InvalidCredentialsError(Exception):
    def __init__(self):
        self.message = "Invalid email or password"
        super().__init__(self.message)


class BudgetExceededError(Exception):
    def __init__(self, category: str = ""):
        self.message = f"Budget exceeded for category '{category}'"
        super().__init__(self.message)


class ValidationError(Exception):
    def __init__(self, detail: str = "Validation error"):
        self.message = detail
        super().__init__(self.message)


class InvalidResetTokenError(Exception):
    def __init__(self, detail: str = "Invalid or expired reset token"):
        self.message = detail
        super().__init__(self.message)
