
import pandas
import pandas as pd

unshuff = pandas.read_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/pol_sentences.tsv", names=('ID', 'Lang', 'Sentence'),
                       sep='\t')
translations = pandas.read_csv("C:/Users/Hubert/Desktop/sftp/sentences_base.csv", sep='\t', index_col=0, names=['ID', 'Translation'])
print(translations)

temp = translations.loc[11834555][0]

print(unshuff)
sentences = unshuff["Sentence"]
print(sentences)
reshuff = unshuff.sample(frac=1)
reshuff.reset_index(drop=True, inplace=True)
print(reshuff)
print("First Sentence: {}".format(reshuff['Sentence'][0]))

df2 = reshuff['ID']

mergey = reshuff.merge(translations, on='ID')
print(mergey)

mergey_filtered = mergey[mergey['Translation'] == 0]
print(mergey_filtered)

finalshuff = mergey_filtered.reset_index(drop=True)
finalshuff.drop(columns=['Translation'], inplace=True)

finalshuff.to_csv("C:/Users/Hubert/Desktop/sftp/HERKUSNEEZE/SlimPolaks.tsv", sep='\t')
pass
