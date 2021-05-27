# Subtree Metric Package
This package provides an NLTK-like interface to measure the STM score of the given hypothesis and ideal translations.

There is also a web-app available with a GUI which includes the metrics provided in this package.

URL: http://nlp-metrics.herokuapp.com

## Usage example

```
import spacy
from subtree_metric import stm

nlp: spacy.Language = spacy.load('en_core_web_md')
ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
hyp = 'It is a guide to action which ensures that the military always obeys the commands of the party'
print(stm.sentence_stm(ref,
                       hyp,
                       nlp))

ref = 'It is a guide to action that ensures that the military will forever heed Party commands'
hyp = 'It is to insure the troops forever hearing the activity guidebook that party direct'
print(stm.sentence_stm(ref,
                       hyp,
                       nlp))

```
