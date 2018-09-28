from configparser import ConfigParser


class Config(object):
    def __init__(self, filename='env.ini'):
        self.filename = filename
        self.parser = ConfigParser()
        # read config file
        self.parser.read(filename)

    def sections(self):
        # get section, default to postgresql
        section_return = {}
        params = self.parser.items()
        for param in params:
            section_return[param[0]] = param[1]

        return section_return

    def item(self, section='database'):
        # get section, default to postgresql
        section_return = {}
        if self.parser.has_section(section):
            for param in self.parser.items(section):
                section_return[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, self.filename))

        return section_return
