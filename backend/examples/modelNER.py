from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer

# Автоматическая загрузка с safetensors
model_path = "./userdata/bert-base-NER-Russian"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)
nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple",
              ignore_labels=[])

text = "Меня зовут Сергей Иванович, я из Москвы."
results = nlp(text)
print("Labels модели:", model.config.id2label)
for entity in results:
    print(f"{entity['entity_group']}: {entity['word']} (score: {entity['score']:.2f})")
