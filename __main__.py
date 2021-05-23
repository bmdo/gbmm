import logging
import sys


class GBDLError(RuntimeError):
    def __init__(self):
        self.msg = 'An unknown error occurred.'


class FilterError(GBDLError):
    def __init__(self, filter_str: str):
        self.msg = f'Invalid filter: {filter_str}.'


class ArgumentError(GBDLError):
    def __init__(self, arg: str = None, msg: str = None):
        self.msg = 'Invalid arguments: '
        if arg is None and msg is None:
            self.msg += 'Unknown argument error.'
        if arg is not None:
            self.msg = f'Invalid argument {arg}: '
        if msg is not None:
            self.msg += msg


class ArgumentSet:
    def __init__(self, series: list[str]):
        if len(series) < 1:
            raise ArgumentError()
        self.option: str = series[0]
        self.values: list[str] = series[1:]


class GeneralSwitches:
    def __init__(self):
        self.console_log_level: int = logging.INFO


class CommandLineInterface:
    def __init__(self, args: list):
        self.args = args
        self.command: str = ''
        self.command_opts: list[str] = []
        self.general_switches = GeneralSwitches()
        self.logger = self.set_up_logging()

        try:
            self.command, self.command_opts, general_switches = self.parse_arguments()
            self.process_general_switches(general_switches)
            self.logger.debug(f'Command: {self.command}')
            self.logger.debug(f'Command options: {self.command_opts}')
            self.logger.debug(f'General options: {general_switches}')
            self.logger.debug(f'Running command.')
            self.run_command()

        except GBDLError as e:
            self.logger.error(e.msg)
            sys.exit(1)

    def set_up_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.general_switches.console_log_level)
        console_handler.name = 'console'
        logging.getLogger().handlers.clear()
        logger = logging.getLogger('gbdl-cli')
        logger.addHandler(console_handler)
        return logger

    def parse_arguments(self):
        options = []
        series = []
        for arg in self.args[1:]:
            if arg.startswith('-'):
                if len(series) > 0:
                    options.append(series)
                series = [arg]
            else:
                series.append(arg)
        options.append(series)
        if len(options) < 1 or len(options[0]) < 1:
            raise ArgumentError(msg='No command provided.')
        return options[0][0], options[0][1:], options[1:]

    def process_general_switches(self, general_switches: list[list[str]]):
        for series in general_switches:
            for item in series:
                if item == '--critical':
                    self.general_switches.console_log_level = logging.CRITICAL
                elif item == '--error':
                    self.general_switches.console_log_level = logging.ERROR
                elif item == '--warn' or item == '--warning':
                    self.general_switches.console_log_level = logging.WARNING
                elif item == '--info':
                    self.general_switches.console_log_level = logging.INFO
                elif item == '--debug':
                    self.general_switches.console_log_level = logging.DEBUG

    @staticmethod
    def filter_value_generator(filter_values: list):
        for v in filter_values:
            if isinstance(v, range):
                for rv in v:
                    yield rv
            else:
                yield v

    @staticmethod
    def parse_filter(filter_str: str):
        filter_strings = filter_str.split(';')
        filters = []
        for f in filter_strings:
            try:
                key, value = f.split('=')
            except ValueError:
                raise FilterError(f)
            values = []
            for v in value.split(','):
                rng = [int(limit) for limit in v.split('-')]
                if len(rng) == 1:
                    values.append(rng[0])
                elif len(rng) == 2:
                    values.append(range(rng[0], rng[1] + 1))
                else:
                    raise ArgumentError(f'Invalid range {v}.')
            filters.append((key, CommandLineInterface.filter_value_generator(values)))
        return filters

    # region Commands

    def run_command(self):
        if self.command == 'start':
            self.start_server()
        elif self.command == 'download':
            self.download()
        elif self.command == 'download-recent':
            self.get_and_download_most_recent()
        else:
            raise ArgumentError()

    def start_server(self):
        print('Starting server.')
        # Do something to start the server like run a shell command
        print('Server started.')

    def download(self):
        if len(self.command_opts) < 2:
            raise ArgumentError()
        object_type = self.command_opts[0]
        object_filters = self.parse_filter(self.command_opts[1])

        self.check_object_type(object_type)

        try:
            for name, value_generator in [f for f in object_filters]:
                if name == 'id':
                    for v in value_generator:
                        print(f'Would download {v}.')
                        # video = self.controller.get_video(v)
                        # if video is None:
                        #     logging.warning(f'No {object_type} with {name}={v} found. Skipping.')
                        # else:
                        #     self.controller.download_video_with_images(video)
                else:
                    raise ArgumentError(msg=f'Invalid filter name: {name}')
        except IndexError:
            raise ArgumentError(msg=f'Invalid filter string: {object_filters}')

    def get_and_download_most_recent(self):
        if len(self.command_opts) < 1:
            raise ArgumentError('Item type required.')
        object_type = self.command_opts[0]
        self.check_object_type(object_type)
        print(f'Would download {object_type}.')
        # res = self.controller.get_collection_resource(object_type)
        # new = self.controller.get_most_recent(res)
        # for obj in new:
        #     self.controller.download_video_with_images(obj)

    # endregion Commands


def main():
    CommandLineInterface(sys.argv)
    sys.exit(0)


if __name__ == '__main__':
    main()
