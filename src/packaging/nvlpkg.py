from ..config import *
from .nvlrc import NVLRCParser
import zipfile

class NVLPKGBuilder:
    def __init__(self) -> None:
        self.parser = NVLRCParser()