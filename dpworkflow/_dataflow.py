
import ast

import pandas as pd


class dataFlow:

    def __init__(self, csv_path):
        self.log = []
        self.model = []
        self.df = pd.read_csv(csv_path)
        self._log_action(f'CSV {csv_path} loaded')

    def _log_action(self, action):
        self.log.append(f"{len(self.log)} - {action}")

    def add(self, n, col=None):
        self._log_action(f'Adding {n} to {col if col else "entire dataframe"}')
        self.model.append(['add', [n, col]])
        if not col:
            self.df = self.df.add(n)
            return
        self.df[col] = self.df[col].add(n)

    def save_model(self, model_namepath):
        open(model_namepath, 'w').write(str(self.model))

    def load_model(self, model_namepath):

        command_list = ast.literal_eval(open(model_namepath, 'r').read())

        for command in command_list:
            if command[0] == 'add':
                self.add(command[1][0], command[1][1])


