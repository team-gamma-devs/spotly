class InvalidCSVException(Exception):
    pass

class MissingColumnsException(Exception):
    def __init__(self, missing_columns):
        self.missing_columns = missing_columns
        super().__init__(f"Faltan columnas requeridas: {missing_columns}")
