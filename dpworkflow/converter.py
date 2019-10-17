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
    if 'left' in value_dict and 'right' in value_dict:
        assignment_digger(value_dict['left'], global_op_list, global_stats_list)
        assignment_digger(value_dict['right'], global_op_list, global_stats_list)
        global_op_list.append(value_dict['op']['_type'])
    elif 'left' in value_dict:
        assignment_digger(value_dict['left'], global_op_list, global_stats_list)
    else:
        global_stats_list.append(get_name_num(value_dict))


def assignment_analyzer(line):
    global global_op_list
    global global_stats_list
    global_op_list = []
    global_stats_list = []
    if line['_type'] == 'Assign':
        assignment_digger(line['value'], global_op_list, global_stats_list)
    print(global_op_list, global_stats_list)


# Here we can deal with any kind of assignment
for line in script['body']:
    if line['_type'] == 'Assign':
        assignment_analyzer(line)
