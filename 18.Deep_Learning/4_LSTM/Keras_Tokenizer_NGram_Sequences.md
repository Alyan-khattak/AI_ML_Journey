# Keras Tokenizer + N-Gram Input Sequences

## What is `Tokenizer`?

`Tokenizer` is a Keras utility used to **convert words/text into integer IDs**.

Example:

```text
"I love Naruto"

        ↓ Tokenizer

I       → 1
love    → 2
naruto  → 3
```

The numbers are assigned automatically when the tokenizer learns the vocabulary.

---

## Why Do We Need It?

Neural networks cannot directly understand:

```text
"I love Naruto"
```

They need numerical input.

So we convert:

```text
Text
 ↓
Words
 ↓
Integer Token IDs
 ↓
Neural Network
```

---

# Creating a Tokenizer

```python
from tensorflow.keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer()
```

This creates an empty tokenizer.

At this point, it does not know any words.

---

# `fit_on_texts()`

```python
tokenizer.fit_on_texts([text])
```

This tells the tokenizer:

> "Read this text and build a vocabulary from its words."

### Important

`fit_on_texts()` expects a **list of strings**.

```python
tokenizer.fit_on_texts([text])
```

Here:

```python
[text]
```

means:

```python
[
    "the complete text..."
]
```

You can also give multiple sentences:

```python
tokenizer.fit_on_texts([
    "I love Naruto",
    "Naruto is a ninja",
    "Sasuke is Naruto's friend"
])
```

---

# `word_index`

After fitting:

```python
tokenizer.word_index
```

returns a dictionary:

```text
word → integer ID
```

Example:

```python
{
    "naruto": 1,
    "is": 2,
    "a": 3,
    "ninja": 4
}
```

So:

```text
naruto → 1
is     → 2
a      → 3
ninja  → 4
```

---

# `texts_to_sequences()`

This converts text into its integer representation.

```python
tokenizer.texts_to_sequences(["Naruto is a ninja"])
```

Example output:

```python
[[1, 2, 3, 4]]
```

The text:

```text
Naruto is a ninja
```

becomes:

```text
[1, 2, 3, 4]
```

---

# Important Tokenizer Functions

## 1. `fit_on_texts()`

Builds the vocabulary.

```python
tokenizer.fit_on_texts(texts)
```

```text
Text
 ↓
Tokenizer learns vocabulary
 ↓
word_index
```

---

## 2. `texts_to_sequences()`

Converts text into integer IDs.

```python
tokenizer.texts_to_sequences(texts)
```

Example:

```python
tokenizer.texts_to_sequences(["Naruto is a ninja"])
```

Output:

```python
[[1, 2, 3, 4]]
```

---

## 3. `word_index`

Shows the vocabulary.

```python
tokenizer.word_index
```

Example:

```python
{
    "naruto": 1,
    "is": 2,
    "a": 3,
    "ninja": 4
}
```

---

# Understanding the Code

```python
from tensorflow.keras.preprocessing.text import Tokenizer

# Create the tokenizer
tokenizer = Tokenizer()

# Learn vocabulary from the text
# fit_on_texts() expects a list of strings
tokenizer.fit_on_texts([text])

# Display word → integer mapping
print(tokenizer.word_index)
```

Now the tokenizer knows how to convert words into numbers.

---

# Creating Input Sequences

```python
input_sequence = []
```

This creates an empty list where we will store our generated sequences.

Then:

```python
for line in text.split('\n'):
```

### What does this do?

`text.split('\n')` splits the complete text wherever a **new line** occurs.

For example:

```text
Naruto is a ninja
He lives in Konoha
Sasuke is his friend
```

becomes:

```python
[
    "Naruto is a ninja",
    "He lives in Konoha",
    "Sasuke is his friend"
]
```

The loop processes one line at a time.

---

# Converting Each Line to Numbers

```python
token_list = tokenizer.texts_to_sequences([line])[0]
```

Suppose:

```text
line = "Naruto is a ninja"
```

and:

```python
word_index = {
    "naruto": 1,
    "is": 2,
    "a": 3,
    "ninja": 4
}
```

Then:

```python
tokenizer.texts_to_sequences([line])
```

returns:

```python
[[1, 2, 3, 4]]
```

The `[0]` removes the outer list:

```python
[1, 2, 3, 4]
```

So:

```python
token_list
```

contains:

```text
[1, 2, 3, 4]
```

---

# Generating N-Gram Sequences

Now:

```python
for i in range(1, len(token_list)):
```

If:

```python
token_list = [1, 2, 3, 4]
```

then:

```python
len(token_list)
```

is:

```text
4
```

Therefore:

```python
range(1, 4)
```

produces:

```text
1
2
3
```

---

## This Line

```python
n_gram_sequence = token_list[:i+1]
```

takes progressively larger parts of the sequence.

For:

```text
token_list = [1, 2, 3, 4]
```

we get:

### First iteration

```python
i = 1

token_list[:2]
```

Result:

```text
[1, 2]
```

### Second iteration

```python
i = 2

token_list[:3]
```

Result:

```text
[1, 2, 3]
```

### Third iteration

```python
i = 3

token_list[:4]
```

Result:

```text
[1, 2, 3, 4]
```

Therefore:

```text
[1, 2]
[1, 2, 3]
[1, 2, 3, 4]
```

These are our generated **n-gram sequences**.

---

# Complete Code

```python
from tensorflow.keras.preprocessing.text import Tokenizer


# Create the tokenizer
tokenizer = Tokenizer()


# Learn the vocabulary from the text
# fit_on_texts() expects a list of strings
tokenizer.fit_on_texts([text])


# Display word → integer mapping
print(tokenizer.word_index)


# Store generated n-gram sequences
input_sequence = []


# Process each line separately
for line in text.split('\n'):

    # Convert the current line into integer token IDs
    token_list = tokenizer.texts_to_sequences([line])[0]

    # Generate progressively longer sequences
    for i in range(1, len(token_list)):

        # Take the first i+1 tokens
        n_gram_sequence = token_list[:i+1]

        # Store the generated sequence
        input_sequence.append(n_gram_sequence)
```

---

# Complete Dry Run

Suppose:

```text
Naruto is a ninja
He lives in Konoha
```

Assume the tokenizer creates:

```python
{
    "naruto": 1,
    "is": 2,
    "a": 3,
    "ninja": 4,
    "he": 5,
    "lives": 6,
    "in": 7,
    "konoha": 8
}
```

## Line 1

```text
Naruto is a ninja
```

becomes:

```text
[1, 2, 3, 4]
```

Generated sequences:

```text
[1, 2]
[1, 2, 3]
[1, 2, 3, 4]
```

## Line 2

```text
He lives in Konoha
```

becomes:

```text
[5, 6, 7, 8]
```

Generated sequences:

```text
[5, 6]
[5, 6, 7]
[5, 6, 7, 8]
```

Final:

```python
input_sequence = [
    [1, 2],
    [1, 2, 3],
    [1, 2, 3, 4],
    [5, 6],
    [5, 6, 7],
    [5, 6, 7, 8]
]
```

---

# Why Are We Doing This?

This is commonly used when preparing data for **next-word prediction**.

For example:

```text
[1, 2]
```

could represent:

```text
Naruto is
```

The model can learn:

```text
Naruto is → a
```

Then:

```text
[1, 2, 3]
```

represents:

```text
Naruto is a
```

The model can learn:

```text
Naruto is a → ninja
```

So the training idea becomes:

```text
Input              Target

Naruto is     →    a
Naruto is a   →    ninja
```

---

# How Is This Different From Our Previous ANN/RNN Approach?

Earlier, we were mainly doing:

```text
Text
 ↓
Token IDs
 ↓
Pad Sequences
 ↓
Embedding Layer
 ↓
RNN
```

For example:

```python
[4339, 3308, 2026]
```

We used `pad_sequences()` to make sequences the same length.

---

# Previous Approach

The main purpose was:

> **Convert existing sentences into fixed-size inputs for the neural network.**

```text
Sentence
   ↓
Tokenization
   ↓
Token IDs
   ↓
Padding
   ↓
Embedding
   ↓
RNN
```

---

# Current Approach

Now we are creating **multiple training sequences from each sentence**.

```text
Sentence
   ↓
Tokenizer
   ↓
Token IDs
   ↓
N-Gram Sequences
   ↓
Padding
   ↓
Input + Target
   ↓
Embedding
   ↓
RNN
```

The important difference:

> `pad_sequences()` makes sequences the **same length**.

> The n-gram loop creates **multiple sequences from a sentence**, usually for tasks such as next-word prediction.

---

# Tokenizer vs `word_tokenize()`

Do not confuse these two.

## NLTK `word_tokenize()`

```python
from nltk.tokenize import word_tokenize

words = word_tokenize(text)
```

Main purpose:

```text
Sentence
 ↓
Individual tokens
```

Example:

```text
"Naruto is awesome"
        ↓
["Naruto", "is", "awesome"]
```

It does **not automatically create the word → integer mapping used by your Keras model**.

---

## Keras `Tokenizer`

```python
from tensorflow.keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer()
tokenizer.fit_on_texts([text])
```

Main purpose:

```text
Words
 ↓
Vocabulary
 ↓
Integer IDs
```

Example:

```text
Naruto  → 1
is      → 2
awesome → 3
```

---

# Tokenizer vs Padding vs Embedding

These three have different jobs:

```text
              TEXT
               ↓
        ┌──────────────┐
        │  Tokenizer   │
        └──────────────┘
               ↓
          Token IDs
        [1, 2, 3, 4]
               ↓
        ┌──────────────┐
        │   Padding    │
        └──────────────┘
               ↓
       Fixed-length IDs
        [0, 1, 2, 3, 4]
               ↓
        ┌──────────────┐
        │  Embedding   │
        └──────────────┘
               ↓
        Dense Vectors
               ↓
              RNN
```

### Remember

**Tokenizer:**

> "Convert words into numbers."

**Padding:**

> "Make sequences the same length."

**Embedding:**

> "Convert token IDs into learned dense vectors."

**RNN:**

> "Process the sequence and learn from the order/context of the tokens."

---

# One-Line Memory Trick

```text
Tokenizer → Words → Numbers

Padding   → Different lengths → Same length

Embedding → Numbers → Dense vectors

RNN       → Sequence → Context/patterns
```
