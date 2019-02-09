__author__ = 'dstrohl'


class ColorWrap(object):

    color_dict = {
                    'default' : '\033[1;m',
                    'grey' : '\033[1;30m' ,
                    'red' :  '\033[1;31m' ,
                    'green' : '\033[1;32m' ,
                    'yellow' : '\033[1;33m' ,
                    'blue' : '\033[1;34m' ,
                    'magenta' : '\033[1;35m' ,
                    'cyan' : '\033[1;36m',
                    'white' : '\033[1;37m', }

    hightlight_dict = {
                    'default' : '\033[1;m',
                    'grey' : '\033[1;40m' ,
                    'red' :  '\033[1;41m' ,
                    'green' : '\033[1;42m' ,
                    'yellow' : '\033[1;43m' ,
                    'blue' : '\033[1;44m' ,
                    'magenta' : '\033[1;45m' ,
                    'cyan' : '\033[1;46m',
                    'white' : '\033[1;47m', }

    is_tty = True

    '''
    def __init__(self):

        if stdout.isatty():
            self.is_tty = True
        else:
            self.is_tty = False



        #self.highlight_dict = {}
        #self.color_dict = {}
        for c, s in iter(self.color_dict.items()):
            if c != 'default':
                tmp_highlight = s + self.highlight
                self.highlight_dict[c] = self.base_color.format(tmp_highlight)
                self.color_dict[c] = self.base_color.format(s)
    '''

    def _wrap(self, c_dict, color, content, sep):
        if isinstance(content, (list, tuple)):
            tmp_list = []
            for con in content:
                tmp_list.append(str(con))
            content = sep.join(tmp_list)
            if self.is_tty:
                return '{}{}{}'.format(c_dict[color], content, c_dict[self.default])
            else:
                return content

    def wrap(self, color, content, sep = ' '):
        return self._wrap(self.color_dict, color, content, sep)

    def h_wrap(self, color, content, sep = ''):
        return self._wrap(self.highlight_dict, color, content, sep)

    def __getitem__(self, key):
        if self.is_tty:
            try:
                return self.color_dict[key]
            except KeyError:
                return ''
        else:
            return ''

    def __getattr__(self, name):
        if self.is_tty:
            try:
                return self.color_dict[name]
            except KeyError:
                raise AttributeError()
        else:
            return ''

