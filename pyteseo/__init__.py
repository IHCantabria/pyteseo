"""Python package developed to simplify and facilitate the setup and processing of TESEO simulations (https://ihcantabria.com/en/specialized-software/teseo/)
"""
import os
from dotenv import load_dotenv

__version__ = "0.0.6"

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)
