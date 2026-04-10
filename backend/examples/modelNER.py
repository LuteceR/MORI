from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer

# Автоматическая загрузка с safetensors
model_name = "./userdata/bert-base-NER-Russian"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple",
              ignore_labels=[])

text = "Меня зовут Сергей Иванович из Москвы."
results = nlp(text)
print("Labels модели:", model.config.id2label)
for entity in results:
    print(f"{entity['entity_group']}: {entity['word']} (score: {entity['score']:.2f})")



# from git import Repo # pip install GitPython

# # Open an existing repository
# repo = Repo('path/to/repo')

# # Clone a repository
# cloned_repo = Repo.clone_from("https://github.com", "local/path")