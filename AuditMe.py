import pandas as pd
with open("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/DownInBaskervilles.txt", "r", encoding='utf-8') as file:
    lines = [line.strip() for line in file.readlines()]
pass
lines = list(filter(None, lines))

df = pd.DataFrame(lines, columns = ['Sentence'])
print(df)
df.to_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/BaskervillesHorror.tsv", sep='\t')
pass