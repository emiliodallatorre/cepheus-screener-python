class DeviceModel:
    name: str
    height: int
    width: int

    def __init__(self, width: int, height: int, name: str) -> None:
        self.height = height
        self.width = width
        self.name = name

    def __repr__(self) -> str:
        return f"Dimensioni {self.width}x{self.height}"
