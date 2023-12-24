
class FileError(Exception):
    """File handling error"""
    message = "File error! Invalid file type."

    def __init__(self, message: str = None) -> None:
        if self.message:
            self.message = message

    def __str__(self):
        return self.message if self.message else self.__doc__
