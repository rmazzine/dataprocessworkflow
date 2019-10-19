import json
import ast
from ast2json import ast2json

data = open('../venv/test_df.py', 'r').read()

script = ast2json(ast.parse(data))

for line in script['body']:
    print(line)

# Get import name
return_pandas_import_name = ''
for line in script['body']:
    if line['_type']=='Import':
        for s_import in line['names']:
            if s_import['name'] == 'pandas':
                return_pandas_import_name = s_import['name'] if not s_import['asname'] else \
                    s_import['asname']

# Get CSV DF creation
df_csv_assignment = ''
for line in script['body']:
    if line['_type'] == 'Assign' and 'func' in line['value']:
        if 'value' in line['value']['func']:
            if line['value']['func']['value']['id'] == return_pandas_import_name:
                # REFERENCE TO PD NAME return_pandas_import_name
                if line['value']['func']['attr'] == 'read_csv' and len(line['targets']) == 1:
                    # ONLY WORKS FOR SINGLE ASSIGNMENT
                    df_csv_assignment = line['targets'][0]['id']


def get_slice(dict_ver):
    """Tries to get the column of context dataframe

    Args:
        dict_ver (dict): Dictionary to be analyzed

    Returns (str): The column value

    """
    if 'slice' in dict_ver:
        return dict_ver['slice']['value']['s']


def get_name_num(edge_dict):
    """

    Args:
        edge_dict: A dictionary that is either a name or value

    Returns (tuple): The assigned df name and its respective column
    """
    output = {'kind': {'Name': {'id': None, 's': None}, 'Num': None}}
    if edge_dict['_type'] == 'Name':
        output['kind']['Name']['id'] = edge_dict['id']
    if edge_dict['_type'] == 'Subscript':
        output['kind']['Name']['id'] = edge_dict['value']['id']
        if 's' in edge_dict['slice']['value']:
            output['kind']['Name']['s'] = edge_dict['slice']['value']['s']
        if 'n' in edge_dict['slice']['value']:
            output['kind']['Name']['s'] = edge_dict['slice']['value']['n']
    if edge_dict['_type'] == 'Num':
        output['kind']['Num'] = edge_dict['n']

    return output


# This recursion function needs a global var list to hold values

def assignment_digger(value_dict, global_op_list, global_stats_list):
    """Gets the operations and assignment variables of a script assignment

    Args:
        value_dict: Dictionary with the assignment values
        global_op_list: A list with the operations of the assignment variables
        global_stats_list: A list with dictionaries about the assignment variables
    """
    if 'left' in value_dict and 'right' in value_dict:
        assignment_digger(value_dict['left'], global_op_list, global_stats_list)
        assignment_digger(value_dict['right'], global_op_list, global_stats_list)
        global_op_list.append(value_dict['op']['_type'])
    elif 'left' in value_dict:
        assignment_digger(value_dict['left'], global_op_list, global_stats_list)
    else:
        global_stats_list.append(get_name_num(value_dict))


def assignment_analyzer(line):
    """Analyze a line, if assignment type, and get the target and operations,assignments

    Args:
        line (dict): The script line

    Returns:
        (dict, list, list): A dictionary with the target variables, a list with the assignment
        operations and a list with dictionaries with the assign variables
    """
    global global_op_list
    global global_stats_list
    global_op_list = []
    global_stats_list = []
    target = None
    if line['_type'] == 'Assign':
        if 'elts' in line['targets'][0]:
            raise RuntimeError('This package only supports simple assignments')
        target = get_name_num(line['targets'][0])
        assignment_digger(line['value'], global_op_list, global_stats_list)
    return target, global_op_list, global_stats_list


# Here we can deal with any kind of assignment
assignment_history = []
for line in script['body']:
    if line['_type'] == 'Assign':
        assignment_history.append(assignment_analyzer(line))

# Create a very simple graph to separate target assignments
dict_graph = {}
for asgn in assignment_history:
    idt = asgn[0]['kind']['Name']['id']
    if idt not in dict_graph:
        dict_graph[idt] = [asgn]
    else:
        dict_graph[idt].append(asgn)

print(dict_graph)

