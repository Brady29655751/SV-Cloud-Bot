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

def append_char(string_list, character, newline=''):
    if not string_list:
        return character
    new_list = []
    for x in string_list:
        new_str = ('\n') if (x == newline) else (x + character)
        new_list.append(new_str)
            
    new_list[-1] = string_list[-1]
    return new_list

def concate_content_with_character(string_list, character, newline=''):
    if not string_list:
        return ''
    if len(string_list) == 1:
        return string_list[0]
        
    new_string = ''
    new_list = append_char(string_list, character, newline)
    for x in new_list:
        new_string += x
    return new_string

def is_parsed_int(num, stop=-1):
    return (not isinstance(num, bool)) and ((num in range(stop)) if stop != -1 else True)

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
    if error:
        for r in result:
            if isinstance(r, bool) and not r:
                return False
    return result

def list_reader(list_repr):
    content = list_repr.replace('[', '').replace(']', '').replace(', ', ' ').replace(',',' ')
    content = content.replace("'",'').replace('"', '').split()
    return content
 