# -*- coding: utf-8 -*-
"""Untitled25.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Mnl-jre3gtWPDBWwxSWviJVyc8B-7r5O
"""

# !pip install transformers datasets evaluate accelerate
# !pip install parsivar

import pandas as pd
from parsivar import Normalizer
import re
# import torch
from datasets import Dataset
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer
from sklearn.metrics import precision_recall_fscore_support , accuracy_score
from transformers import pipeline

id2label = {
    0: "ANGRY",
    1: "FEAR",
    2: "HAPPY",
    3: "HATE",
    4: "OTHER",
    5: "SAD",
    6: "SURPRISE"
}
label2id = {label: id for id, label in id2label.items()}

classifier = pipeline("sentiment-analysis", model="soltaniali/my_awesome_model")
tokenizer = AutoTokenizer.from_pretrained('soltaniali/my_awesome_model')

text = input("enter onse sentence:")
print(classifier(text))
path_file = input("enter the path of ur file plz:")
# Read the TSV file into a DataFrame
df_test = pd.read_csv(path_file, sep='\t', header=None, names=['Sentence', 'Label'], encoding='utf-8')

# Initialize Parsivar normalizer
normalizer = Normalizer()

# Function to perform additional pre-processing steps
def additional_preprocessing(text):
    # Remove English characters
    text = re.sub(r'[a-zA-Z]', '', text)

    # Remove repeated letters more than twice in non-standard Persian words
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)

    # Remove Arabic diacritics
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

    # Remove remaining non-Persian characters
    text = re.sub(r'[^آ-ی۰-۹\s]', '', text)

    # Remove hashtag sign while preserving hashtag information
    text = re.sub(r'#(\w+)', r'\1', text)

    # Remove Persian numeric characters
    text = re.sub(r'[۰-۹]', '', text)

    return text

df_test['Sentence'] = df_test['Sentence'].apply(normalizer.normalize)
df_test['Sentence'] = df_test['Sentence'].apply(additional_preprocessing)
df_test = df_test.rename(columns={'Sentence': 'text', 'Label': 'label'})

df_test['label'] = [label2id[number] for number in df_test['label']]

dataset_test = Dataset.from_pandas(df_test)

def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True , padding=True)

dataset_yok = dataset_test.map(preprocess_function, batched=True)

somewhere = classifier(dataset_yok['text'])
df = pd.DataFrame(somewhere)
print(df.to_string(index=False))