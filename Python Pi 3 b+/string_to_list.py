import ast

def string_to_list(sequence_str):
    try:
        sequence_list = ast.literal_eval(sequence_str)
        if isinstance(sequence_list, list):
            return sequence_list
        else:
            raise ValueError("The provided string does not represent a list.")
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid input: {e}")

if __name__  == '__main__':
    sequence_str = "[['n', 100], ['s', 200]]"
    sequence_list = string_to_list(sequence_str)
    print(sequence_list[0])
