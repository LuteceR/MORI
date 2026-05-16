from pandas import read_json, read_pickle
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import json
from torch import no_grad, softmax
# path_ds = 'F:/mori/backend/userdata/DATASETS/AlexKly/Detailed-NER-Dataset-RU-master/dataset/detailed-ner_dataset-ru.pickle'
path_ds = 'F:\\mori\\backend\\userdata\\DATASETS\\AlexKly\\Detailed-NER-Dataset-RU-master\dataset\\test.jsonl'
train_df = read_json(path_ds, lines=True)
train_df["orig"] = train_df["words"].apply(" ".join)
# train_df["orig"] = train_df["tokens"].apply(" ".join)


# Автоматическая загрузка с safetensors
model_path = "F:\\mori\\backend\\userdata\\MODELS\\aidarmusin/address-ner-ru"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)
nlp = pipeline("token-classification", model=model, tokenizer=tokenizer, ignore_labels=[])

def pred(words):
    enc = tokenizer(
        words,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True
    )

    with no_grad():
        outputs = model(**enc)

    logits = outputs.logits[0]
    probs = softmax(logits, dim=-1)
    pred_ids = probs.argmax(dim=-1).tolist()
    word_ids = enc.word_ids(batch_index=0)

    results = []
    seen_words = set()

    for token_idx, word_idx in enumerate(word_ids):
        if word_idx is None or word_idx in seen_words:
            continue

        seen_words.add(word_idx)

        pred_id = pred_ids[token_idx]
        label = model.config.id2label[pred_id]
        score = probs[token_idx, pred_id].item()

        results.append({
            "word": words[word_idx],
            "entity": label,
            "score": score
        })

    return results

# print("Labels модели:", model.config.id2label)
f = open("F:\\mori\\backend\\userdata\\DATASETS\\AlexKly\\Detailed-NER-Dataset-RU-master\dataset\\output.jsonl", "w", encoding="utf-8")
for i_line, line in enumerate(train_df["words"].values):
    results = pred(line)
    words = []
    ner = []
    scores = []
    for entity in results:
        words.append(entity['word'])
        ner.append(entity['entity'])
        scores.append(float(entity['score']))

    if len(words) != len(ner) or len(ner) != len(scores):
        print("Длина меток слов и оценок не совпадает:")
        print(words)
        print(ner)
        print(scores)
        break

    if len(words) != len(train_df["words"].values[i_line]):
        print(i_line)
        print(words)
        print(train_df["words"].values[i_line])
        print()
    # else:
        # f.write(json.dumps({"words": words, "ner": ner, "scores": scores}, ensure_ascii=False) + "\n")

    # for entity in results:
    #     print(f"{entity['entity']}: {entity['word']} (score: {entity['score']:.2f})")



