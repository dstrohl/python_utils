__author__ = 'dstrohl'



#===============================================================================
# counter function
#===============================================================================

class clicker():
    '''
    Arguments:
        initial = initial counter number
        echo = print each set to console
        step = print only on increments of x
        name = name of clicker
        max = max number (when set, echo will return %xx)
        format = format to use for echo, default = '{name} : {counter}'
    '''

    def __init__(self, **kwargs):
        self.counter = kwargs.get('initial', 0)
        self.echo = kwargs.get('echo', False)
        self.step = kwargs.get('step', 1)
        self.name = kwargs.get('name', '')
        self.max_value = kwargs.get('max', 0)
        self.format = kwargs.get('format', '{name} : {counter}')

        if self.echo:
            print('{}... initialized...'.format(self.name))

    def __call__(self, check):
        if check:
            self.counter = self.counter + 1
            self._echoif()
            return self.counter

    def perc(self):
        return ( self.counter / self.max_value ) * 100

    def _echoif(self):
        if self.echo:
            if self.counter % self.step == 0:
                if self.max_value:
                    perc = ( self.counter / self.max_value ) * 100
                    print(format.format(name=self.name, counter=perc))
                else:
                    print(format.format(name=self.name, counter=self.counter))

    def addif(self, check):
        if check:
            self.counter = self.counter + 1
            self._echoif()
            return self.counter

    def remif(self, check):
        if check:
            self.counter = self.counter - 1
            self._echoif()
            return self.counter

    def get(self):
        return self.counter

    def clear(self):
        self.counter = 0
        self._echoif()
        return self.counter

    def set(self, initial):
        self.counter = initial
        self._echoif()
        return self.counter

