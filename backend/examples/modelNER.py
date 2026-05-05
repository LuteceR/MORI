import pandas as pd
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
path_ds = 'F:/mori/backend/userdata/DATASETS/AlexKly/Detailed-NER-Dataset-RU-master/dataset/detailed-ner_dataset-ru.pickle'
train_df = pd.read_pickle(path_ds)
print(train_df["tokens"].values[:2])
train_df["orig"] = train_df["tokens"].apply(" ".join)


# Автоматическая загрузка с safetensors
model_path = "F:\\mori\\backend\\userdata\\MODELS\\aidarmusin/address-ner-ru"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)
nlp = pipeline("token-classification", model=model, tokenizer=tokenizer, ignore_labels=[])

print("Labels модели:", model.config.id2label)

for line in train_df["orig"].values[:2]:
    print(line)
    results = nlp(line)

    for entity in results:
        print(f"{entity['entity']}: {entity['word']} (score: {entity['score']:.2f})")



