from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# Автоматическая загрузка с safetensors
model_name = "./userdata/multilingual-sentiment-analysis"
# model_name = "tabularisai/multilingual-sentiment-analysis"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

text = "Я в этом не вижу никакого смысла."
results = classifier(text)
print("Labels модели:", model.config.id2label)

print(f"Emotion: {results[0]['label']} (score: {results[0]['score']:.2f})")
