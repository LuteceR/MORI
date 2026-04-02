import spacy
from spacy.util import minibatch, compounding
import random

from spacy.lang.ru import Russian
from thinc.api import Config

config = Config().from_disk("./config.cfg")
nlp = Russian.from_config(config)

# Construction via add_pipe with default model
# Use 'textcat_multilabel' for multi-label classification
textcat = nlp.add_pipe("textcat", config=config)


# Construction from class
# Use 'MultiLabel_TextCategorizer' for multi-label classification
from spacy.pipeline import TextCategorizer
textcat = TextCategorizer(nlp.vocab, model, threshold=0.5)