def string_to_list(string):
    result = []
    i = 0
    while i < len(string):
        if string[i] == '[':
            i += 1
            inner_list = []
            while string[i] != ']':
                if string[i] == "'":
                    i += 1
                    start = i
                    while string[i] != "'":
                        i += 1
                    inner_list.append(string[start:i])
                    i += 1
                elif string[i].isdigit() or string[i] == '.':
                    start = i
                    while string[i].isdigit() or string[i] == '.':
                        i += 1
                    inner_list.append(float(string[start:i]))
                elif string[i] == ',':
                    i += 1
                else:
                    i += 1
            result.append(inner_list)
        i += 1
    return result