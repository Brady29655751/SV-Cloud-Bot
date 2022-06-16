def replace_dot(string):
    return string.replace('·', '．').replace('‧', '．').replace('﹒', '．').replace('・','．').replace('•', '．')

def strip_quote(string):
    return string.replace("'",'').replace('"','')

def append_newline(string_list):
    if not string_list:
        return ['\n']

    new_list = [x + '\n' for x in string_list]
    new_list[-1] = string_list[-1]
    return new_list

def concate_content_with_newline(string_list):
    new_string = ''
    new_list = append_newline(string_list)
    for x in new_list:
        new_string += x
    return new_string

def append_char(string_list, character):
    if not string_list:
        return character
    new_list = [x + character for x in string_list]
    new_list[-1] = string_list[-1]
    return new_list

def concate_content_with_character(string_list, character):
    if not string_list:
        return ''
    if len(string_list) == 1:
        return string_list[0]
        
    new_string = ''
    new_list = append_char(string_list, character)
    for x in new_list:
        new_string += x
    return new_string

def int_parser(string, error=False):
    num = string
    try:
        num = int(string)
    except Exception:
        num = string
        if error or not string:
            return False
    return num

def int_list_parser(string_list, error=False, use_list_reader=False):
    if use_list_reader:
        string_list = list_reader(string_list)    
    result = [int_parser(x, error) for x in string_list]
    if error and (False in result):
        return False
    return result

def list_reader(list_repr):
    content = list_repr.replace('[', '').replace(']', '').replace(', ', ' ').replace(',',' ')
    content = content.replace("'",'').replace('"', '').split()
    return content
 