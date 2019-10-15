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

# Get simple df operations giving the df name
for line in script['body']:
    if line['_type'] == 'Assign':
        if len(line['targets']) == 1 and line['targets'][0]['_type'] == 'Subscript':
            # ONLY WORKS FOR SINGLE ASSIGNMENT
            if 'slice' in line['targets'][0]:
                # HERE WE KNOW IT IS A SLICED ASSIGNMENT
                df_assignment_column = line['targets'][0]['slice']['value']['s']
            if df_csv_assignment in line['targets'][0]['value']['id']:
                # HERE WE KNOW WE HAVE A ASSIGNMENT TO A DF
                if 'left' in line['value']:
                    # Here we verify which df it is assigning to
                    df_is_equal_to = line['value']['left']['value']['id']
                    if 'slice' in line['value']['left']:
                        # HERE WE KNOW IT IS A SLICED ASSIGNMENT
                        df_added_column = line['value']['left']['slice']['value']['s']
                if 'op' in line['value']:
                    # Here we verify if any operation is assigned
                    df_operation = line['value']['op']['_type']
                    if 'n' in line['value']['right']:
                        # It is a simple number operation to df
                        number_operation = line['value']['right']['n']

print(df_added_column)