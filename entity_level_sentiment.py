# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
from textblob import TextBlob
import re


# %%
articles = pd.read_csv("feeds/articles.csv", index_col=0, parse_dates=["published"])
articles


# %%
# Dictionary contains some banks with all kind of its names
bank = {
    "sbi": ["sbi", "state bank of india", "state bank"],
    "axis": ["axis", "axis bank"],
    "icici": ["icici"],
}


# %%
one_article = articles["entry_text"][4]
one_article


# %%
one_article = re.sub(r"\r", "", one_article)  # remove \r
one_article = re.sub(r"\n", " ", one_article)  # replace \n with space
one_article = one_article.lower()  # convert all words to lowercase
one_article


# %%
# replace dots that have numbers(ex.12.9), vs., i.e., .com around them with "[PROTECTED_DOT]"
string1_protected = re.sub(r"(\d)\.(\d)", r"\1[PROTECTED_DOT]\2", one_article)
string1_protected = re.sub(r"(i)\.(e)\.", r"\1[PROTECTED_DOT]\2", string1_protected)
string1_protected = re.sub(r"(v)(s)\.", r"\1[PROTECTED_DOT]\2", string1_protected)
string1_protected = re.sub(r"([a-z])\.(com)", r"\1[PROTECTED_DOT]\2", string1_protected)

# now split (and remove empty lines)
lines_protected = [line + "." for line in string1_protected.split(".") if line]

# now re-replace all "[PROTECTED_DOT]"s
lines = [line.replace("[PROTECTED_DOT]", ".") for line in lines_protected]
lines


# %%
# input given as sbi bank (input bank name should be in small letters, abbreviated form)
input_given = "icici"
bank_names = bank[input_given]
pol = 0
print("All lines having the given bank name:")
for i in range(len(lines)):
    for j in range(len(bank_names)):
        if bank_names[j] in lines[i]:
            print("Line " + str(i) + ": ")
            print(lines[i])
            print("Line polarity: " + str(TextBlob(lines[i]).sentiment.polarity))
            print("\n")
            pol = pol + TextBlob(lines[i]).sentiment.polarity

print("Overall Polarity: " + str(pol))

if pol > 0:
    print("Sentiment: 1")
elif pol == 0:
    print("Sentiment: 0")
else:
    print("Sentiment: -1")

# %%
