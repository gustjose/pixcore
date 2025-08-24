import configparser
from pathlib import Path
import typer

APP_NAME = "pixcore"
CONFIG_DIR = Path(typer.get_app_dir(APP_NAME))
CONFIG_FILE = CONFIG_DIR / "config.ini"

def _ensure_config_exists():
    """Garante que o diretório e o arquivo de configuração existam."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.is_file():
        CONFIG_FILE.touch()

def read_config() -> configparser.ConfigParser:
    """Lê o arquivo de configuração e retorna um objeto ConfigParser."""
    _ensure_config_exists()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def write_config(config: configparser.ConfigParser):
    """Escreve o objeto ConfigParser de volta no arquivo."""
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def set_value(section: str, key: str, value: str):
    """Define um valor em uma determinada seção do arquivo de configuração."""
    config = read_config()
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, value)
    write_config(config)

def get_config_as_dict() -> dict:
    """Retorna todas as configurações como um dicionário."""
    config = read_config()
    return {section: dict(config.items(section)) for section in config.sections()}