__all__ = ['validator_format_list', 'validator_format_line', 'validator_format_lines', 'validator_format_table']

from PythonUtils.BaseUtils import max_len


PF_MESSAGE = {True: 'PASSED', False: 'FAILED'}


def validator_format_list(**kwargs):
    results = kwargs['results']
    passed = kwargs.get('passed', True)
    failed = kwargs.get('failed', True)
    tmp_ret = []
    for key, res in results.items():
        if not res['passed'] and failed:
            tmp_ret.append(res['message'])
        elif res['passed'] and passed:
            tmp_ret.append(res['message'])
    return tmp_ret


def validator_format_line(**kwargs):
    tmp_ret = validator_format_list(**kwargs)
    return '{fieldname} [{pf_message}]: {messages}'.format(
            fieldname=kwargs.get('fieldname', 'Field'),
            pf_message=PF_MESSAGE[kwargs['pf']],
            messages=', '.join(tmp_ret))


def validator_format_lines(**kwargs):
    tmp_ret = validator_format_list(**kwargs)
    return '{fieldname} [{pf_message}]:\n\n    {messages}'.format(
            fieldname=kwargs.get('fieldname', 'Field'),
            pf_message=PF_MESSAGE[kwargs['pf']],
            messages='\n    '.join(tmp_ret))


def _make_line(field_strs, field_lens, len_plus=0, fill=' '):
    tmp_ret = (
        field_strs[0].ljust(field_lens[0]+len_plus, fill),
        field_strs[1].ljust(field_lens[1]+len_plus, fill),
        field_strs[2].ljust(field_lens[2]+len_plus, fill))
    return tmp_ret


def validator_format_table(**kwargs):

    results = kwargs['results']
    pf = kwargs['pf']
    fieldname = kwargs.get('fieldname', 'Field')
    passed = kwargs.get('passed', True)
    failed = kwargs.get('failed', True)

    name_max_len = max_len(results.values(), ({'validator': 'Validator'},), field_key='validator')
    msg_max_len = max_len(results.values(), ({'message': 'Message'},), field_key='message')

    header_info = ('PF', 'Validator', 'Message')

    pf_flag = {True: ' P', False: '*F'}

    size_tuple = (2, name_max_len, msg_max_len)

    sep_format = '+{}+{}+{}+'
    line_format = '| {} | {} | {} |'

    main_sep = sep_format.format(*_make_line(('', '', ''), size_tuple, 2, '-'))
    head_sep = sep_format.format(*_make_line(('', '', ''), size_tuple, 2, '='))
    title_line = line_format.format(*_make_line(header_info, size_tuple))

    tmp_ret = [
        fieldname+' ['+PF_MESSAGE[pf]+']',
        '',
        main_sep,
        title_line,
        head_sep]

    for key, res in results.items():
        if not res['passed'] and failed:
            line_info = _make_line((
                pf_flag[res['passed']],
                res['validator'],
                res['message']),
                size_tuple)
            tmp_ret.append(line_format.format(*line_info))
        elif res['passed'] and passed:
            line_info = _make_line((
                pf_flag[res['passed']],
                res['validator'],
                res['message']),
                size_tuple)
            tmp_ret.append(line_format.format(*line_info))
        tmp_ret.append(main_sep)

    return '\n'.join(tmp_ret)

