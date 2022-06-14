
def int_parser(string, error=False):
    num = string
    try:
        num = int(string)
    except Exception:
        num = string
        if error:
            return False
    return num

def int_list_parser(string_list, error=False):
    result = [int_parser(x, error) for x in string_list]
    if error and (False in result):
        return False
    return result

def list_reader(list_repr):
    content = list_repr.replace('[', '').replace(']', '').replace(', ', ' ')
    content = content.replace("'",'').replace('"', '').split()
    return content
 