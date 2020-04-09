import csv
import matplotlib.pyplot as plt
import pandas
file = 'singleparameterreport.csv'


df = pandas.read_csv(file, delimiter='\t', index_col="config #")
print(df)

x = df.index.values
y = df["score"]

# plot
plt.plot(x,y)
# # beautify the x-labels
# plt.gcf().autofmt_xdate()

plt.show()
