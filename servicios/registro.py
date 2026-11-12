"""Registro local de errores; no expone detalles técnicos en la interfaz."""
import logging
from pathlib import Path
RUTA = Path(__file__).resolve().parent.parent / "datos" / "optiagro.log"
RUTA.parent.mkdir(exist_ok=True)
logging.basicConfig(filename=RUTA, level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("optiagro")
