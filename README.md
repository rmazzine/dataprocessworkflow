# Pandas Data Process Workflow

This script analyzes a Pandas script and its operations and converts it to a worflow/graph.

The script is currently in a very early version, but updates are made constantly. :smiley:

**YOU NEED TO INSTALL THE GRAPHVIZ SOFTWARE AND PYTHON PACKAGE BEFORE USING THIS SCRIPT.**

The main objective its to have a better picture of data processing using the Pandas package. This is specially useful when large datasets have multiple and complex operations that make difficult to have a clear understanding of data transformation. 

For now it only supports very simple operations, like a DataFrame column assignment. But it's planned to support complex operations.

A simple example is shown below:

For a script named test_df.py

```python
import pandas as pd
df = pd.read_csv('test.csv')
df['c'] = df['a']+df['b']
df['b'] = df['b']+1
df['d'] = 10
```

We simply put it in the root directory and run the converter.py script. It will outputs a view on browser like that one:

![Example image of script output](img/example1.png?raw=true "Output Example")
