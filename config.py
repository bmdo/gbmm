import yaml
import logging
import os
from marshmallow import Schema, fields

CONFIG_FILE_PATH = 'config.yaml'


class ConfigError(IOError):
    pass


class ConfigValueError(ConfigError):
    pass


def _convert_log_level(log_level: str):
    if log_level == 'CRITICAL' or log_level == '50':
        return logging.CRITICAL
    elif log_level == 'ERROR' or log_level == '40':
        return logging.ERROR
    elif log_level == 'WARNING' or log_level == '30':
        return logging.WARNING
    elif log_level == 'INFO' or log_level == '20':
        return logging.INFO
    elif log_level == 'DEBUG' or log_level == '10':
        return logging.DEBUG
    else:
        return logging.NOTSET


class ConfigStatic:
    SERVER_NAME = 'gbmm'
    SERVER_VERSION = '0.1.0'

    SECRET_KEY = 'jMEFOn8volBpq2Q1efuZsRjpy51g4ix4WYx4if2g3h4vDElVT9uBsCtu5nv8AAm8'

    API_BASE_URL = 'https://www.giantbomb.com/api/'
    API_KEY_FIELD = 'api_key'
    API_KEY_REGEX = '^([0-9]|[a-f]){40}$'

    HEADERS = {'user-agent': f'{SERVER_NAME}/{SERVER_VERSION}'}


class ConfigFile:
    @staticmethod
    def load(config_file_path: str):
        with open(config_file_path, 'r') as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def save(c: 'Config', config_file_path: str):
        with open(config_file_path, 'w') as stream:
            yaml.safe_dump(c.dump_values(), stream)


class ConfigItemType:
    def __init__(self, name: str, pytype: type):
        self.name: str = name
        self.pytype: type = pytype


class ConfigItem:
    def __init__(self,
                 t: ConfigItemType,
                 default: any,
                 mutable_runtime: bool = False,
                 helptext: str = None):
        self.t: ConfigItemType = t
        self.helptext: str = helptext
        self.mutable_runtime: bool = mutable_runtime

        self.__value: any = None
        self.update(default)

    @property
    def value(self):
        return self.__value

    def update(self, value):
        try:
            self.__value = self.t.pytype(value)
        except ValueError or TypeError:
            raise ConfigValueError(f'Invalid type for configuration item: {type(value)}')


class ConfigItemSchema(Schema):
    type = fields.Str(attribute='t.name')
    helptext = fields.Str()
    value = fields.Str()


class CInt(ConfigItem):
    __type = ConfigItemType('int', int)

    def __init__(self,
                 default: any,
                 *,
                 mutable_runtime: bool = False,
                 helptext: str = None):
        super().__init__(
            self.__type,
            default,
            mutable_runtime,
            helptext
        )


class CStr(ConfigItem):
    __type = ConfigItemType('str', str)

    def __init__(self,
                 default: any,
                 *,
                 mutable_runtime: bool = False,
                 helptext: str = None):
        super().__init__(
            self.__type,
            default,
            mutable_runtime,
            helptext
        )


class CBool(ConfigItem):
    __type = ConfigItemType('bool', bool)

    def __init__(self,
                 default: any,
                 *,
                 mutable_runtime: bool = False,
                 helptext: str = None):
        super().__init__(
            self.__type,
            default,
            mutable_runtime,
            helptext
        )


class CSelect(ConfigItem):
    __type = ConfigItemType('select', str)

    def __init__(self,
                 default: any,
                 options: list[str],
                 *,
                 mutable_runtime: bool = False,
                 helptext: str = None):
        super().__init__(
            self.__type,
            default,
            mutable_runtime,
            helptext
        )
        self.options = options


class Config:
    @property
    def SERVER_NAME(self):
        return ConfigStatic.SERVER_NAME

    @property
    def SERVER_VERSION(self):
        return ConfigStatic.SERVER_VERSION

    @property
    def SECRET_KEY(self):
        return ConfigStatic.SECRET_KEY

    @property
    def API_BASE_URL(self):
        return ConfigStatic.API_BASE_URL

    @property
    def API_KEY_FIELD(self):
        return ConfigStatic.API_KEY_FIELD

    @property
    def API_KEY_REGEX(self):
        return ConfigStatic.API_KEY_REGEX

    @property
    def HEADERS(self):
        return ConfigStatic.HEADERS

    @property
    def SERVER_ROOT(self):
        """
        The root directory used for the gbmm server. Contains web application files and optionally databases and logs.
        """
        v = self.get('server root').value
        return os.path.abspath(v)

    @property
    def API_VERSION(self):
        """The API version. This should be 1.0."""
        return self.get('api.version').value

    @property
    def API_KEY(self):
        """Your Giant Bomb API key. https://www.giantbomb.com/api"""
        return self.get('api.key').value

    @property
    def DATABASE_DIR(self):
        """
        The directory where gbmm stores sqlite databases. If not an absolute path, this is relative to SERVER_ROOT.
        """
        v = self.get('database.directory').value
        return v if os.path.isabs(v) else os.path.join(self.SERVER_ROOT, v)

    @property
    def DATABASE_NAME(self):
        """The name of the database file."""
        v = self.get('database.name').value
        return v if v.endswith('.db') else f'{v}.db'

    @property
    def FILE_ROOT(self):
        """The root directory used to store files like videos and images."""
        v = self.get('file root').value
        return v if os.path.isabs(v) else os.path.join(self.SERVER_ROOT, v)

    @property
    def LOG_DIR(self):
        """The directory where gbmm stores logs. If not an absolute path, this is relative to SERVER_ROOT."""
        v = self.get('logging.directory').value
        return v if os.path.isabs(v) else os.path.join(self.SERVER_ROOT, v)

    @property
    def LOG_FILE(self):
        """The name of the log file for the server. Stored in LOG_DIR."""
        v = self.get('logging.name').value
        return v if v.endswith('.log') else f'{v}.log'

    @property
    def LOG_LEVEL(self):
        """
        The logging level to use for the server. Must be one of `the string or numeric logging levels understood by
        Python's logging library <https://docs.python.org/3/library/logging.html#logging-levels>`_.
        """
        return _convert_log_level(self.get('logging.level').value)

    @property
    def LOG_MAX_SIZE(self):
        """Integer. The maximum size a log file grows to before it is rotated. Units are kilobytes."""
        return self.get('logging.max size').value

    @property
    def LOG_BACKUP_COUNT(self):
        """Integer. The maximum number of rotated logs to keep."""
        return self.get('logging.backup count').value

    def dump_values(self) -> dict:
        return self.__to_nested_value_dict(self.__dict)

    def dump_ui(self):
        """
        Dumps a structured representation of the configuration that includes information for presenting in a user
        interface.
        """
        return self.__to_nested_ui_list(self.__dict)

    def __init__(self, *,
                 config_dict: dict = None,
                 server_root: str = None,
                 file_root: str = None,
                 db_dir: str = None,
                 log_dir: str = None):
        self.__dict = {}
        self.__init_defaults(server_root, file_root, db_dir, log_dir)
        if config_dict is not None:
            self.__from_nested_value_dict(config_dict)

    def __init_defaults(self,
                        server_root: str = None,
                        file_root: str = None,
                        db_dir: str = None,
                        log_dir: str = None):

        if server_root is None:
            server_root = './'
        if file_root is None:
            file_root = 'files/'
        if db_dir is None:
            db_dir = 'db/'
        if log_dir is None:
            log_dir = 'log/'

        self.__dict = {
            'api': {
                'key':
                    CStr('', mutable_runtime=True,
                         helptext='Your Giant Bomb API key. https://www.giantbomb.com/api.'),
                'version':
                    CStr('1.0', mutable_runtime=True,
                         helptext='The Giant Bomb API version. This should be 1.0.')
                },
            'file root':
                CStr(file_root,
                     helptext='The root directory used to store files like videos and images. If not an absolute path, '
                              'this is relative to the server root.'),
            'database': {
                'directory':
                    CStr(db_dir,
                         helptext='The directory where gbmm stores sqlite databases. If not an absolute path, this is '
                                  'relative to the server root.'),
                'name':
                    CStr(f'{ConfigStatic.SERVER_NAME}.db',
                         helptext='The name of the database file.')
                },
            'logging': {
                'directory':
                    CStr(log_dir, mutable_runtime=True,
                         helptext='The directory where gbmm stores logs. If not an absolute path, this is relative to '
                                  'the server root.'),
                'name':
                    CStr(f'{ConfigStatic.SERVER_NAME}.log', mutable_runtime=True,
                         helptext='The name of the log file for the server. Stored in under the logging directory.'),
                'level':
                    CSelect('INFO', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], mutable_runtime=True,
                         helptext='The logging level to use for the server. Must be one of the string or numeric '
                                  'logging levels understood by Python\'s logging library: '
                                  'https://docs.python.org/3/library/logging.html#logging-levels.'),
                'max size':
                    CInt(1000, mutable_runtime=True,
                         helptext='The maximum size a log file grows to before it is rotated. Units are kilobytes.'),
                'backup count':
                    CInt(1000, mutable_runtime=True,
                         helptext='The maximum number of rotated logs to keep.')
                }
        }

    @staticmethod
    def __build_address(*stops: str):
        return '.'.join([s for s in stops if s is not None])

    def __to_nested_value_dict(self, node: dict) -> dict:
        d = {}
        for k, v in node.items():
            if isinstance(v, dict):
                m = self.__to_nested_value_dict(v)
                d[k] = m
            else:  # An actual configuration value
                d[k] = v.value
        return d

    def __to_nested_ui_list(self, node: dict, address: str = None) -> list:
        d = []
        for k, v in node.items():
            if isinstance(v, dict):
                a = self.__build_address(address, k)
                m = self.__to_nested_ui_list(v, a)
                d.append({
                    'group': {
                        'address': a,
                        'name': k,
                        'items': m
                    }
                })
            else:  # An actual configuration value
                if v.mutable_runtime:
                    item = ConfigItemSchema().dump(v)
                    item['address'] = self.__build_address(address, k)
                    item['name'] = k
                    d.append({'item': item})
        return d

    def __from_nested_value_dict(self, node: dict, path: str = ''):
        for k, v in node.items():
            working_path = path
            if working_path == '':
                working_path = k
            else:
                working_path = f'{working_path}.{k}'

            if isinstance(v, dict):
                self.__from_nested_value_dict(v, working_path)
            else:  # An actual configuration value
                self.modify(working_path, v)

    def update(self, address: str, value: any):
        """Update a configuration item without saving to disk."""
        self.get(address).update(value)

    def modify(self, address: str, value: any):
        """Update and save a configuration item."""
        self.get(address).update(value)
        ConfigFile.save(self, CONFIG_FILE_PATH)

    @staticmethod
    def __get_address_from_dict(d: dict, address: str) -> ConfigItem:
        for stop in address.split('.'):
            d = d.get(stop, None)
            if d is None:
                raise ValueError(f'Invalid address part "{stop}" in address {address}.')
        return d

    def get(self, address: str) -> ConfigItem:
        return self.__get_address_from_dict(self.__dict, address)



__server_root = None
__file_root = None
__db_dir = None
__log_dir = None
config = None

try:
    __config_dict = ConfigFile.load(CONFIG_FILE_PATH)
    config = Config(config_dict=__config_dict)
except OSError:
    config = Config(
        server_root=__server_root,
        file_root=__file_root,
        db_dir=__db_dir,
        log_dir=__log_dir
    )
    ConfigFile.save(config, CONFIG_FILE_PATH)
repr(config)
