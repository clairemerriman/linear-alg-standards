import pandas as pd
from pandas import DataFrame as df
import numpy as np

grade_path = 'Linear Algebra Example Grades.xlsx'
output_file = 'standardsMiniB.csv'

dataset = pd.read_excel(grade_path,
                sheet_name="Standards", 
                dtype=str)

column_list = ["Name","Last Name"]

# Combine first and last name
dataset["Name"] = dataset["Name"] + " " + dataset["Last Name"]

header_list = list(dataset.columns.values)


#importing all column headers as strings was failing
#this tests for integers and only adds integers to the column_list

for i in header_list:
    try:
        i = int(i)
        if i == int(i):
            j = header_list.index(i) #since i is the header, we need the index
            a=pd.isna(dataset.iloc[1,j]) #checks if empty
            if a == False: #if nonempty, add to list
                column_list.append(i)
    except ValueError:
        pass  # This skips any columns with type errors.

#there could be a lot of extra stuff in the excel sheet
#let's only import rows with names

row_list = []
for i in range(len(dataset)):
    a=dataset.iloc[i,1]
    if pd.isna(a):
        pass
    else:
        row_list.append(i)

dataset.iloc[row_list].to_csv(output_file,
                index_label='ID',
                columns=column_list)
            