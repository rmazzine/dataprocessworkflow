import pandas as pd

df = pd.read_csv('sample_data.csv', delimiter=';')

# Calculate the Age from the birth year
df['Age'] = 2019-df['Birth_Year']
print(df['Age'])

df['Monthly_Salary'] = df['Salary']/12

df['Monthly_Salary_by_Ed_Year'] = df['Monthly_Salary']/df['Years_Education']
df['Monthly_Salary_by_Age'] = df['Monthly_Salary']/df['Age']
