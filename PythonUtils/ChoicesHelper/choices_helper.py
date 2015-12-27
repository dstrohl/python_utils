from PythonUtils import slugify
from decimal import Decimal

__author__ = 'Dan Strohl'


def make_slug(text_in):
    tmp_str = slugify(text_in, allowed='_')
    # tmp_str = tmp_str.replace('-', '_')
    return tmp_str


class ChoiceBaseException(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


class ChoiceInvalidPropertyNameError(ChoiceBaseException):
    def __init__(self, property_name):
        self.message = 'ChoiceHelper Error, invalid property name: {}'.format(property_name)


class ChoiceDuplicateParameterError(ChoiceBaseException):
    def __init__(self, parameter_type, parameter_name):
        self.message = 'ChoiceHelper Error, duplicate {} name {}'.format(parameter_type, parameter_name)


class ChoiceInvalidChoiceError(ChoiceBaseException):
    def __init__(self, choice, choices):
        self.message = 'ChoiceHelper Error, choice %s not in %r' % (choice, choices)


class Choice(object):
    """
    Choice object for each choice used in the ChoiceHelper
    """

    def __init__(self,
                 stored,
                 display=None,
                 prop=None,
                 call=None,
                 stored_synonyms=None,
                 default=False,
                 **kwargs
                 ):
        """
        :param str stored: The text to be stored in the database
        :param str display_text: The text to be displayed to the user (can also be overdidden by subclassing and
            changing the Choice.get_display() method.  If no display_text is passed, a capalized version of the stored
            text will be used.
        :param str property_name: The property name to be used in programatic access to this object.  if No property
            name is passed, a cleaned up version of the stored text will be used.
        :param function call: A function or method that can be called if this choice is selected.  See documentation for
            further description and examples.
        :param list stored_synonyms: A list of synonyms of the stored text, this can be used when converting from one
            lookup approach to another... See documentation for more information and examples.
        :param bool parameter_validity_check: [True|False] Defaults to True, if True, the parameter name will be
            checked for validity using str.isidentifier() and an exception will be raised if it failes the check,
        :param kwargs: If additional keyword args are passed, these will be available like a dictionary from the choice
            object.  This can be used when additional information is needed based on a specific choice.
        """
        self._stored = stored
        self._stored_synonyms = stored_synonyms or []
        self._data = kwargs
        self._call = call
        self._default = default
        self._stored_list = []

        if prop:
            if not isinstance(prop, str):
                raise ChoiceInvalidPropertyNameError(prop)
            self._property_name = make_slug(prop)
        else:
            if not isinstance(self._stored, str):
                self._property_name = '_'+make_slug(str(self._stored))
            else:
                self._property_name = make_slug(self._stored)

        if display:
            self._display_text = str(display)
        else:
            self._display_text = str(stored).replace('_', ' ').capitalize()

        if not self._property_name.isidentifier():
            raise ChoiceInvalidPropertyNameError(self._property_name)

        if self._property_name in self.__dir__():
            raise ChoiceInvalidPropertyNameError(self._property_name)

        if call:
            if callable(self._call):
                self._callable = True
            else:
                self._callable = False

    @property
    def choice_tuple(self):
        return self.stored, self.display_text

    def get_display(self):
        """
        Can be overridden in order to control the returned display text for this option.
        """
        return self._display_text

    @property
    def is_default(self):
        return self._default

    @property
    def property_name(self):
        return self._property_name

    @property
    def stored(self):
        return self._stored

    def stored_list(self):
        if not self._stored_list:
            self._stored_list.append(self.stored)
            self._stored_list.extend(self._stored_synonyms)
        return self._stored_list

    @property
    def display_text(self):
        return self.get_display()

    def __getitem__(self, item):
        try:
            return self._data[item]
        except KeyError:
            if item in ('display_text', 'property_name', 'stored'):
                return getattr(self, item)
            else:
                raise

    def __setitem__(self, key, value):
        self._data[key] = value

    def __call__(self, *args, **kwargs):
        if self._call:
            if self._callable:
                return self._call(*args, **kwargs)
            else:
                return self._call
        else:
            raise ChoiceBaseException('{} Choice does not have any functions defined'.format(self.stored))

    def __str__(self):
        return self.display_text

    def __repr__(self):
        return 'Choice: ({}/{})'.format(self.stored, self.display_text)

    def __contains__(self, stored):
        return stored == self.stored or stored in self._stored_synonyms


class ChoicesHelper(object):
    """
    This can be called in the following ways:

    ChoiceHelper.property_name : returns the Choice object for that property name.
    ChoiceHelper['stored'] : returns the Choice object for that stored text or synonym
    ChoiceHelper('stored') : returns the display text for the stored text or synonym, raises an exception if
        unmatched.
    ChoiceHelper

    """

    def __init__(self, *choices,
                 parameter_validity_check=True,
                 duplicate_display_check=False,
                 duplicate_stored_check=False,
                 no_default=True
                 ):
        """
        helps choices options.  In the below formats, there are three types of data that are handled:

        property_string: this is the string that is used to access the info programatically, so this would be when the
            class is called with ChoiceHelper.parameter_string.

        stored_string: this is the string that is stored in the database

        display_string: this is the string that is shown to the users

        :param choices: this can be a list or set of items in one of three formats:
            strings: ('stored1', 'stored2', 'stored3'): In this format this will take each item and that string will be
                used for all three string types.
            two item tuples: ( ('stored1', 'display string 1'), ('stired2', 'display string 2') ):  In this format the
                first item will be used for both the parameter string and stored string, the second will be the display
                string
            three item tuples: ( ('stored1', 'display1', 'property1'), ('stored2', 'display2', 'property2')):
                in this format the items will be used as labeled in the example.

        examples:

        ChoiceHelper.property_string
        returns stored

        ChoiceHelper['property_string']
        returns display_text

        """
        self.parameter_validity_check = parameter_validity_check
        self.duplicate_display_check = duplicate_display_check
        self.duplicate_stored_check = duplicate_stored_check

        self._choices = []
        self._choices_list = []
        self._stored_lookup = {}
        self._parameter_lookup = {}
        self._display_lookup = {}
        self._default = None
        self._no_default = no_default

        if choices:
            self.add(*choices)

    def add(self, *choices):
        """
        Adds choice objects to the Choice Helper
        :param choices: Accepts any of the following:

        * Choices.add( (stored_value, displayed_value), ... )

        * Choices.add( string_stored_value, string_stored_value, ... )

        * Choices.Add( Choice(<parameters>), Choice(<parameters>), ... )

        * Choices.Add( choice_args_dict, choice_args_dict, ... )

        """

        for choice in choices:
            if isinstance(choice, (list, tuple)):
                choice = Choice(*choice, parameter_validity_check=self.parameter_validity_check)
            elif isinstance(choice, (str, int, bool, float, Decimal)):
                choice = Choice(choice, parameter_validity_check=self.parameter_validity_check)
            elif isinstance(choice, dict):
                choice = Choice(parameter_validity_check=self.parameter_validity_check, **choice)

            if not isinstance(choice, Choice):
                raise TypeError('%r could not be determined to be a valid choice object, '
                                'or could not be converted to one' % choice)

            if choice.property_name in self._parameter_lookup:
                raise ChoiceDuplicateParameterError('parameter name', choice.property_name)

            if self.duplicate_display_check:
                if choice.display_text in self._display_lookup:
                    raise ChoiceDuplicateParameterError('display name', choice.display_text)

            if self.duplicate_stored_check:
                if choice.stored in self._stored_lookup:
                    raise ChoiceDuplicateParameterError('stored name', choice.stored)

            self._choices_list.append(choice.choice_tuple)
            self._choices.append(choice)

            for st in choice.stored_list():
                self._stored_lookup[st] = choice

            self._parameter_lookup[choice.property_name] = choice
            self._display_lookup[choice.display_text] = choice

            if not self._no_default and (self._default is None or choice.is_default):
                self._default = choice.stored

    def choices(self, selected=None):
        """
        :param selected:
        :return:
        """
        if selected is None:
            return self._choices_list
        tmp_ret = []
        for c in self._choices_list:
            if c[0] == selected:
                tmp_sel = selected
            else:
                tmp_sel = ''
            tmp_ret.append((tmp_sel, c[0], c[1]))
        return tmp_ret

    def __iter__(self):
        """
        :return: An iterator for the choices, used by Django.
        """
        return iter(self._choices_list)

    def __getitem__(self, stored):
        """ `
        :param stored: The stored text to search for.
        :return: The Choice object for the "stored" passed
        """
        return self._stored_lookup[stored]

    def __getattr__(self, parameter_name):
        """
        :param parameter_name: the parameter name passed
        :return: The Choice object for the parameter name used
        """
        if parameter_name not in self._parameter_lookup:
            tmp_msg = 'ChoiceHelper Error: {} not in the list of choices'.format(parameter_name)
            raise AttributeError(tmp_msg)
        return self._parameter_lookup[parameter_name]

    def get(self, stored, default=None, is_display=False):
        if is_display:
            try:
                return self._display_lookup[stored].stored
            except KeyError:
                return default
        else:
            try:
                return self(stored)
            except KeyError:
                return default

    @property
    def default(self):
        return self._default

    @property
    def display_list(self, fieldname=None):
        """
        :param fieldname: The field to add to the list.
        :return: a list of display text objects, can be used to create drop down lists.
        """
        tmp_ret = []
        if fieldname is None:
            fieldname = 'display_text'

        for c in self._choices:
            tmp_ret.append(getattr(c, fieldname))

        return tmp_ret

    def validate(self, choice):
        if choice not in self:
            raise ChoiceInvalidChoiceError(choice, self._stored_lookup)

    def __repr__(self):
        tmp_msg = 'Choice Helper: %s', self._choices
        return tmp_msg

    def __call__(self, stored):
        return str(self._stored_lookup[stored])

    def __contains__(self, item):
        return item in self._stored_lookup
