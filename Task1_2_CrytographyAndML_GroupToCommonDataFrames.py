#!/usr/bin/env python
# coding: utf-8

# In[42]:


'''
To user using this copy, main changes if user want to use this for a different file with different column
have to amend the column names accordingly in the python file

When run the .py file will prompt you for file name. (Filepath included)

'''
fn = input("What is your filename? : ") # dummydata_renamed_updated.xlsx"

import pandas as pd

dfADA = pd.read_excel(fn,converters ={'SFX':str, 'Corp CIN':str})
dfADA['Acc Number'] =dfADA['Acc Number'].str.strip()
dfADA['Acc Number'].tolist()
type(dfADA['Corp CIN'][1])


# In[43]:


'''
we filter by what the user wants to filter by, either by Corp CIN or ACC, if CIN, then we run the filter across the Corp CIN
'''
CINorAcc = input("Do you want to filter by 'Corp CIN' or 'ACC' Num? : ") # CIN or ACC
if CINorAcc == "ACC":
    accountNum = input("Please provide a list of account numbers separated by commas: ") #0001-003579-05-0,001-018760-01,001-003965-5
    #convert to list
    accountNum = accountNum.split(",")
    #To select rows whose column value is in the list
    dfADA = dfADA[dfADA['Acc Number'].isin(accountNum)]
    dfADA
elif CINorAcc=="Corp CIN":
    # To select rows whose column value is in list
    CorpCIN = input("Please provide a Corp CIN number: ") #1234567,1234568,1234569
    CorpCIN = CorpCIN.split(",")
    dfADA = dfADA[dfADA['Corp CIN'].isin(CorpCIN)]
else:
    print("Please enter a valid name")
dfADA


# In[44]:


'''
Because i want to make Acc Number the key later, we put it in the first column

'''
# change order of columns in a dataframe, 'Acc Number' put infront
dfAccNum = dfADA['Acc Number'].unique()
dfAccNum_list = dfAccNum.tolist()
print("List of account numbers unique : {}".format(dfAccNum_list))

# reorder the columns in the df before i do a join'_' on dfADA
new_order = [1,0,2,3,4,5]
dfADA = dfADA[dfADA.columns[new_order]]
print(dfADA.head())


# In[45]:


# Join all the columns separated by '_'
dfADA_str = dfADA.astype(str)
dfADA_str['joined'] = dfADA_str.apply('_'.join, axis =1 )
dfADA_str.head()


# In[46]:


'''
split back the 'Acc Number' because they key is only "joined" column, and does not need account number
'''
# Split away the Acc Number column as it will be "Key-like" for later use
split_list = []
for string in dfADA_str.joined:
    split_Acc = string.split("_",1)
    split_list.append(split_Acc)
    
split_list


# In[47]:


# convert the list of list back to a pandas dataframe
import pandas as pd
df = pd.DataFrame(split_list, columns = ['Acc Num','joined'])
df.head()


# In[48]:


'''
Sort each list (in each row by ascending order so when we join the Dataframe the long string of rows in dataframe is ordered)
The ultimate aim is a dataframe for each group of account numbers.
To compare if the dataframes are the same, need to append all the rows of each dataframe that belongs to each account number 
into one long string

In order for the strings to be correctly matched, we need to sort the rows first before join
'''
dfsort = df.sort_values('joined', ascending = False)


# In[49]:


'''
for each account number, join all the individual credential columns for each account number
'''
#https://stackoverflow.com/questions/22219004/grouping-rows-in-list-in-pandas-groupby
dfgrouped = dfsort.groupby('Acc Num')['joined'].apply(list)
dfgrouped1 = pd.DataFrame(dfgrouped,columns = ['joined'])
print(dfgrouped1.head())


# In[50]:


'''
To check if a dataframe is the same across a few accounts, we need to join (delimiter = '+') 
all the rows in the dataframe then check across
all the accounts
'''
appendlist= []
for item in dfgrouped:
    a = "+".join(item)
    appendlist.append(a)
print(type(appendlist))

dfgrouped1 = dfgrouped1.assign(joinedlistToAcc = appendlist)
dfgrouped1


# In[51]:


'''
Make a duplicate of index column
'''
dfgrouped1['Acc'] = dfgrouped1.index
dfgrouped1

dfgrouped.index[9]


# In[52]:


'''
Aggregate together the account numbers to each set of dataframe
'''  
dfgrouped2 = dfgrouped1.groupby('joinedlistToAcc')['Acc'].apply(list) # pandas series. Grouped by 'joinedlistToAcc'
dfgrouped3 = dfgrouped2.to_frame()
# make  'joinedlistToAcc' a duplicate since it is the index with no header name
dfgrouped3['joinedList_ToAcc'] = dfgrouped3.index


# In[53]:


'''
Split 'joinedlist_ToAcc' back to each column
'''
person = []
for row in dfgrouped3.iterrows():
    sentence = row[0]
    sentence1 = sentence.split("+")
    person.append(sentence1)
print(person)
print("Check number of blocks = {}".format(len(person)))

# cast list back to the dataframe
dfgrouped3 = dfgrouped3.assign(individual= person)
dfgrouped3


# In[54]:


'''
Drop unncecessary columns from pandas dataframe
'''
dfgrouped3.drop('joinedList_ToAcc',axis= 1 , inplace=True)
print(type(dfgrouped3))
dfgrouped3


# In[55]:


'''
Construct a new dataframe,actually because want to drop the index column and "Acc" column
'''
dfnew = pd.DataFrame(list(zip(dfgrouped3.Acc,dfgrouped3.individual)))
dfnew.columns = ['acc_num', 'listOfNames'] # rename fields
dfnew


# In[56]:


'''
Construct new dataframe for each set of "acc_num", just like in the task requirement
choose set_num, to view the output
'''
def choose_frame(set_num):
    # print('df_set{}'.format(set_num))
    dfsep = pd.DataFrame(dfnew.iloc[set_num]).T
    return(dfsep)


# In[57]:


'''
this func is to cast the columns to a df after splitting the listOfNames
'''
def my_function(row):
    # row is df
    # initialise a dataframe
    df = pd.DataFrame({'list_of_name': row['listOfNames']})
    new = df['list_of_name'].str.split("_", n=4 , expand = True)
    df['Corp CIN'] = new[0]
    df['Group'] = new[1]
    df['ind CIN'] = new[2]
    df['SFX'] = new[3]
    df['Name'] = new[4]
    df['account_no'] = [row['acc_num']]*df.shape[0] # repeat the col of acc_no
    return(df)


# In[58]:


'''
apply the function created on your dataframe 'dfnew'

this is because for each row in dfnew , we want to extract the elements in the credentials of the 
individuals in "listOf"
'''
w = dfnew.apply(my_function, axis =1)
w[2]


# In[59]:


'''
create the column called set_{}
'''
for i in range(0, len(w)):
    w[i]['Set'] = "Set" + str(i+1)
    
type(w)
w


# In[60]:


# change the series to list()
ww = w.tolist()
ww


# In[80]:


# concat list of dataframes
q = pd.concat(ww)
q


# In[84]:


# appended dataframe
q
# drop the column "list_of_name"
q1 = q.drop(columns= "list_of_name", axis = 1)
q1 = q1.reset_index() # remove the weird indexing
del q1['index']
q2 = q1.groupby(['Set','Group']).size()
q


# In[82]:


'''
Save the table as well as the count of each "Group" in separate sheets in the same xlsx file
'''
filename = 'task1n2_PL_R2_v2.xlsx'
writer = pd.ExcelWriter(filename)

# write to csv the output
q1.to_excel(writer,sheet_name = "Task2_Table")

# new column ; add a column of Groups as shown in tha sample
uniquesets = q1.Set.unique()
print(uniquesets)
q2 = q1.groupby(['Set','Group']).size()
q2.to_excel(writer,sheet_name = 'Groups')
writer.save()


# # After run task 2 will run task 1

# In[131]:


import pandas as pd
import itertools
# take only the account numbers left from task 2 to do task 1. Account number is the common key between both the datasets 
# SIG and ACC
listOfAccNumLeft = q.account_no.tolist()
listLeft = list(set(list(itertools.chain(*listOfAccNumLeft))))
print(listLeft)


# In[132]:


# call out the df we need to use
dfADA = pd.read_excel(fn, sheetname = "ACC", converters = {'SI':str,'Corp CIN':str})
dfTask2 =  pd.read_excel('task1n2_PL_R2_v2.xlsx',sheetname = "Task2_Table",converters = {'SI':str})

#type(dfTask2.account_no[0])
# dfADA['Account no'] = dfADA['Account no'].str.strip()
dfADA = dfADA[dfADA['Account no'].isin(listLeft)]
print(dfTask2['account_no'])

dfADA['SI'] = dfADA['SI'].astype(str)
dfADA


# In[133]:


'''
replacing na valyes in column "SR" with " " # the real data has some empty rows
'''
dfADA['SR'].fillna("", inplace = True)  # use " " or "" will also show empty.
dfADA


# In[134]:


'''
change order of columns in dataframe, Acc Number put infront
'''
dfAccNum = dfADA['Account no'].unique()
dfAccNum
dfAccNum_list = dfAccNum.tolist()
print("List of account numbers unique: {}".format(dfAccNum_list))
type(dfAccNum_list[0])


# In[135]:


'''
reorder the columns in the df before i do a join "_" on dfADA
'''
new_order = [1,0,2,3,4]
dfADA = dfADA[dfADA.columns[new_order]]
dfADA = dfADA.drop(columns = "Corp CIN", axis = 1)
print(dfADA.head())


# In[136]:


'''
Call out the account number and set number from Task 2
first list in task 2 is has a label "1" to all its elements corresponding to first list in the task 2 acc number and so on
'''
import re

setNum = dfTask2.Set
accNumTask2 = dfTask2.account_no.unique()

print(accNumTask2)
outputList = []
regStr = '[\\d-]+'
indexList = []
indexnum = 1
for outerLoop in accNumTask2:
    listofAccNum = re.findall(regStr , outerLoop)
    for accNum in listofAccNum:
        indexList.append(indexnum)
        outputList.append(accNum)
    indexnum = indexnum + 1
len(indexList)
len(outputList)

# One column is set num, 2nd column is account number
d = {'indexnum': indexList, 'accNum':outputList}
dfindexofInnerList = pd.DataFrame(data=d)
dfindexofInnerList


# In[137]:


'''
Join all the columns separated by '_'
'''
dfADA_str = dfADA.astype(str)
dfADA_str['joined'] = dfADA_str.apply('_'.join, axis =1)
dfADA_str.head()


# In[138]:


'''
Split away the Account no from the joined column as it is supposed to be key-like. Same reason as in Task 2 above
'''
split_list = []
for string in dfADA_str.joined:
    split_Acc = string.split("_",1)
    split_list.append(split_Acc)


# In[139]:


'''
convert the list of list back to a pandas dataframe for easier reading and handling
'''
import pandas as pd
df = pd.DataFrame(split_list, columns = ['Acc Num','joined'])
df.head()


# In[140]:


'''
Sort each list (in each row by ascending order so when we join the Dataframe the long string of rows in dataframe is ordered)
The ultimate aim is a dataframe for each group of account numbers.
To compare if the dataframes are the same, need to append all the rows of each dataframe that belongs to each account number 
into one long string

In order for the strings to be correctly matched, we need to sort the rows first before join
'''
dfsort = df.sort_values('joined',ascending = False)
dfsort


# In[142]:


# making Acc Num the key and show list of "joined" under this key
# https://stackoverflow.com/questions/22219004/grouping-rows-in-list-in-pandas-groupby
dfgrouped = dfsort.groupby('Acc Num')['joined'].apply(list)
type(dfgrouped)
dfgrouped1 = pd.DataFrame(dfgrouped, columns = ['joined'])
print(dfgrouped1.head())


# In[144]:


'''
To check if a dataframe is the same across a few accounts, we need to join all the rows in the dataframe (of "ACC" sheet)
then check across all the accounts
'''
appendlist = []
for item in dfgrouped:
    a = " ".join(item)
    appendlist.append(a)
type(appendlist)

dfgrouped1 = dfgrouped1.assign(joinedlistToAcc = appendlist) # make a column of list to a column of string
dfgrouped1


# In[145]:


'''
 make a duplicate of the index column so it has a header name because index has no header name
'''
dfgrouped1['Acc'] = dfgrouped1.index


# In[147]:


'''
According to the inspection on the previous output, we can see that the strings have spaces infront and behind the account numbers
and all the elements have different number of spaces. We now strip away the spaces
'''
acc= []
for row in dfgrouped1['Acc']:
    a = row.strip()
    acc.append(a)
    
dfgrouped1 = dfgrouped1.assign(Acc = acc)


# In[167]:


'''
Merge 2 df by account number, so we can also add the column of set number to dfgrouped1
'''
dfgrouped1_1 = pd.merge(dfgrouped1, dfindexofInnerList, how = "left", left_on = ['Acc'], right_on = ['accNum'])
dfgrouped1_1


# In[149]:


'''
First merge the column of set number with account number as key

then group by this key, and we join all the elements "joinedlistToAcc" with "|" and "Acc" with "|"
'''
# group by indexnum which is set number, then aggregate list for both "acc" and "joined"
dfgrouped1_1['indexnum_acc'] = dfgrouped1_1['indexnum'].map(str) + "_" + dfgrouped1_1['Acc']
dfgrouped2 = dfgrouped1_1.groupby(['indexnum_acc'],
                                 as_index = False)['joinedlistToAcc','Acc'].agg('|'.join) #.agg(lambda x: list(x))
print(type(dfgrouped2))
dfgrouped2


# In[150]:


'''
As there are many "," inside the column of joinedlistToAcc
we need to separate each entry into each row
other rows are replicated across the added rows
'''
# step 1 : start with creating a new dataframe from the series 
d = {'joinedlistToAcc': dfgrouped2.joinedlistToAcc.str.split('|').tolist()}
new_df = pd.DataFrame(data = d , index = dfgrouped2.indexnum_acc).stack()
# step 2: we now want to get rid of the secondary index
new_df =  new_df.reset_index([0, 'indexnum_acc'])
#step 3: the final step is to set the column names as we want them
new_df.columns = ['indexnum_acc','Acc']
new_df


# In[160]:


# create many dataframes based on each Set number
def my_function(row):
    # row is df
    # initialise a dataframe
    df = pd.DataFrame({'list_of_names':row['joinedlistToAcc'],
                      'indexnum_acc':row['indexnum_acc']}, index = [0]) # start the index with 0
    new1 = df['indexnum_acc'].str.split("_", n=1, expand=True)
    df['Set Num'] = new1[0]
    df['Account_no'] = new1[1]
    new = df['list_of_names'].str.split("_", n=2, expand = True)
    df['Type'] = new[0]
    df['SI'] = new[1]
    df['SR'] = new[2]
    
    return df


# In[161]:


# apply on dataframe dfgrouped2
dfgrouped3 = dfgrouped2.apply(my_function, axis =1)
print(type(dfgrouped3))
dfgrouped3


# In[163]:


# change pandas series to list()
ww = dfgrouped3.tolist()


# In[164]:


# concat list of dataframes
q = pd.concat(ww)
q


# In[165]:


# drop uneeded columns
q3 = q.drop(columns = ['list_of_names','indexnum_acc'])
q3


# In[166]:


'''
save the output to the dataframe we saved earlier 'task1n2_PL_R2_v2.xlsx', and add a new sheet to that dataframe called 'Task1_Table'
'''
from openpyxl import load_workbook
book = load_workbook(filename)
writer = pd.ExcelWriter(filename,engine = 'openpyxl')
writer.book = book
q3.to_excel(writer ,sheet_name ='Task1_Table')
writer.save()


# In[ ]:




