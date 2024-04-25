from codetoolkit import PairChecker
from codetoolkit import Delimiter
from nltk import word_tokenize

print(Delimiter.split_camel("SC_FORBIDDEN"))
print(PairChecker.check_abbr("status sode", "sc"))
print(word_tokenize("The status code of the response."))

