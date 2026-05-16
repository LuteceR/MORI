import pandas as pd
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import json
path_ds = 'F:/mori/backend/userdata/DATASETS/AlexKly/Detailed-NER-Dataset-RU-master/dataset/detailed-ner_dataset-ru.pickle'
train_df = pd.read_pickle(path_ds)
# Поиск адекватных строк в датаете и сборка в один формат: {"words":[..], "ner":[..]}
cntr = 0
for line in train_df.values:
    out = json.loads("{}")
    words = list(line[0])
    ner = list(line[1])
    if len(words) > 10 and sum(1 for i in ner if i == 'O') / len(ner) < 0.7:
        out["words"] = words
        out["ner"] = ner
        print(out)
        cntr += 1
    if cntr > 50: break



