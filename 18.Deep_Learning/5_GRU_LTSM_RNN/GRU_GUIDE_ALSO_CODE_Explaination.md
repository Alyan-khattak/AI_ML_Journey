
# PART 3 — Keras Tokenizer

## What is Tokenizer?

Neural networks cannot read words. They need numbers.

```
"Naruto is a ninja"   →   [1, 2, 3, 4]
```

`Tokenizer` builds a **vocabulary** (word → integer mapping) and converts text to integer sequences.

---

## Creating and Fitting

```python
from tensorflow.keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer()
tokenizer.fit_on_texts([text])
```

`fit_on_texts()` reads the text and:
1. Finds all unique words
2. Assigns each word a unique integer
3. Words that appear more often get lower numbers (more frequent = lower index)

**Important:** `fit_on_texts()` expects a **list of strings**, not a plain string.

```python
tokenizer.fit_on_texts(text)    # WRONG — iterates character by character
tokenizer.fit_on_texts([text])  # CORRECT — treats whole text as one document
```

---

## `word_index`

```python
print(tokenizer.word_index)
```

Output:

```python
{
    "naruto":  1,   # most frequent
    "is":      2,
    "a":       3,
    "ninja":   4,
    "hokage":  5,
    ...
}
```

Total vocabulary size:

```python
total_words = len(tokenizer.word_index) + 1
# +1 because index 0 is reserved for padding
```

---

## `texts_to_sequences()`

Converts text into integer IDs using the learned vocabulary.

```python
tokenizer.texts_to_sequences(["Naruto is a ninja"])
# Output: [[1, 2, 3, 4]]

tokenizer.texts_to_sequences(["Naruto is a ninja"])[0]
# Output: [1, 2, 3, 4]   ← [0] removes outer list
```

**Unknown words** (not seen during fit) are silently dropped:

```python
tokenizer.texts_to_sequences(["Naruto is a wizard"])
# "wizard" not in vocab → dropped
# Output: [[1, 2, 3]]
```

To keep unknown words, use `oov_token`:

```python
tokenizer = Tokenizer(oov_token="<OOV>")
# Unknown words → replaced with "<OOV>" token
```

---

## `sequences_to_texts()`

Reverse operation — integers back to words:

```python
tokenizer.sequences_to_texts([[1, 2, 3, 4]])
# Output: ["naruto is a ninja"]
```

---

## `index_word` — reverse lookup

```python
tokenizer.index_word
# {1: "naruto", 2: "is", 3: "a", 4: "ninja", ...}

# Use at prediction time:
predicted_index = np.argmax(model.predict(input))
predicted_word  = tokenizer.index_word[predicted_index]
```

---

## `word_counts`

How many times each word appeared:

```python
tokenizer.word_counts
# {"naruto": 45, "is": 38, "a": 31, ...}
```

---

## `num_words` — Limit Vocabulary Size

```python
tokenizer = Tokenizer(num_words=5000)
```

Only keeps top 5000 most frequent words. Everything else treated as unknown. Useful for large datasets to reduce model size.

---

## Common Tokenizer Functions Summary

```
┌──────────────────────────┬──────────────────────────────────────────┐
│ Function                 │ What It Does                             │
├──────────────────────────┼──────────────────────────────────────────┤
│ fit_on_texts([text])     │ Build vocabulary from text               │
│ texts_to_sequences(text) │ Convert words → integer IDs             │
│ sequences_to_texts(seq)  │ Convert integer IDs → words             │
│ word_index               │ Dictionary: word → integer               │
│ index_word               │ Dictionary: integer → word (reverse)     │
│ word_counts              │ Dictionary: word → frequency count       │
│ num_words=N              │ Limit vocab to top N words               │
│ oov_token="<OOV>"        │ Token for unknown words                  │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

# PART 4 — Input Sequences (N-Gram Sequences)

## What Are They?

For next-word prediction, we need training pairs:

```
Input                 →   Target (next word)
"Naruto"              →   "is"
"Naruto is"           →   "a"
"Naruto is a"         →   "ninja"
```

N-gram sequences create these progressively growing inputs **automatically** from each sentence.

---

## The Code

```python
input_sequences = []

for line in text.split('\n'):
    token_list = tokenizer.texts_to_sequences([line])[0]

    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)
```

---

## Dry Run

```
text = "Naruto is a ninja\nHe became Hokage"
```

**Step 1:** Split by newline

```python
text.split('\n')
# ["Naruto is a ninja", "He became Hokage"]
```

**Step 2:** Line 1 → "Naruto is a ninja"

```python
token_list = [1, 2, 3, 4]

i=1 → token_list[:2] → [1, 2]       # "Naruto is"
i=2 → token_list[:3] → [1, 2, 3]    # "Naruto is a"
i=3 → token_list[:4] → [1, 2, 3, 4] # "Naruto is a ninja"
```

**Step 3:** Line 2 → "He became Hokage"

```python
token_list = [5, 6, 7]

i=1 → token_list[:2] → [5, 6]       # "He became"
i=2 → token_list[:3] → [5, 6, 7]    # "He became Hokage"
```

**Final `input_sequences`:**

```python
[
    [1, 2],
    [1, 2, 3],
    [1, 2, 3, 4],
    [5, 6],
    [5, 6, 7]
]
```

---

## Why Do This?

Each sequence teaches the model a different prediction:

```
[1, 2]       →  model learns: after "Naruto" comes "is"
[1, 2, 3]    →  model learns: after "Naruto is" comes "a"
[1, 2, 3, 4] →  model learns: after "Naruto is a" comes "ninja"
```

One sentence produces multiple training examples. This is how LSTM learns **context** — not just individual words.

---

## Why Split by Newline?

```python
# Split by newline (what we do)
text.split('\n')
# Each line = one sentence = one context boundary

# Split by space gives individual words — loses sentence structure
text.split(' ')
# ["Naruto", "is", "a", "ninja", "He", "became", "Hokage"]
```

Splitting by newline keeps **sentence-level context** — the model learns within a sentence, not across unrelated sentences.

---

# PART 5 — Padding

All sequences have different lengths. The model needs uniform input.

```python
from tensorflow.keras.preprocessing.sequence import pad_sequences

max_sequence_len = max(len(x) for x in input_sequences)

input_sequences = pad_sequences(
    input_sequences,
    maxlen=max_sequence_len,
    padding='pre'
)
```

**Before padding:**

```
[1, 2]
[1, 2, 3]
[1, 2, 3, 4]
```

**After `padding='pre'` (pad at the front):**

```
[0, 0, 1, 2]
[0, 1, 2, 3]
[1, 2, 3, 4]
```

`padding='pre'` — zeros at the front so the **actual words are always at the end**, closest to the prediction step.

This helps the LSTM because it processes left to right and the last hidden state carries the most recent context.

---

# PART 6 — X and y Split

After padding, every sequence's last column is the **target word**. Everything before it is the **input**.

```python
X = input_sequences[:, :-1]   # all columns except last
y = input_sequences[:, -1]    # last column only
```

**Example:**

```
padded sequence → [0, 0, 1, 2, 3]

X = [0, 0, 1, 2]   ← input ("Naruto is a")
y = 3               ← target ("ninja")
```

---

# PART 7 — to_categorical

`y` contains integer word indices. The output layer is:

```python
Dense(total_words, activation='softmax')
```

Softmax outputs **total_words probabilities** (one per word). We cannot compare a vector of 10000 numbers against 1 integer directly.

**Solution:**

```python
y = tf.keras.utils.to_categorical(y, num_classes=total_words)
```

**Before:**

```
y = 3   (integer — "ninja")
```

**After:**

```
y = [0, 0, 0, 1, 0, 0, ..., 0]
                ↑
            index 3 = 1
            total length = total_words
```

Now comparison works:

```
Predicted : [0.01, 0.02, 0.01, 0.87, 0.01, ...]   ← softmax output
Actual    : [0,    0,    0,    1,    0,    ...]     ← one-hot
```

**Loss formula:**

```
Loss = -log( predicted[correct_index] )
     = -log( 0.87 )
     = 0.07   ← low → model is correct
```

If model was wrong:

```
Loss = -log( 0.12 ) = 0.92   ← high → model needs to learn more
```

**Why not just use integer y directly?**

```
Predicted = 10000 numbers (vector)
Actual    = 1 number (integer)

Vector vs Integer → loss formula cannot compare them
to_categorical    → converts integer to vector → comparison works
```

**Alternative — no `to_categorical` needed:**

```python
model.compile(loss='sparse_categorical_crossentropy')
y = 3   # integer directly — does one-hot internally
```

For large vocabularies `sparse_categorical_crossentropy` saves RAM. Both produce the same trained model.

---

# PART 8 — How LSTM Predicts the Next Word

## Complete Example — Start to Finish

**Corpus:**

```
Naruto trained every day.
Naruto became Hokage.
```

---

### Step 1: Tokenize

```python
word_index = {
    "naruto":   1,
    "trained":  2,
    "every":    3,
    "day":      4,
    "became":   5,
    "hokage":   6,
}
total_words = 7   # 6 words + 1 for padding (index 0)
```

---

### Step 2: Create Sequences

```
"Naruto trained every day"  →  [1, 2, 3, 4]

N-gram sequences:
[1, 2]
[1, 2, 3]
[1, 2, 3, 4]

"Naruto became Hokage"  →  [1, 5, 6]

N-gram sequences:
[1, 5]
[1, 5, 6]
```

---

### Step 3: Pad

```
max_len = 4 (longest sequence)

[0, 0, 1, 2]
[0, 1, 2, 3]
[1, 2, 3, 4]
[0, 0, 1, 5]
[0, 1, 5, 6]
```

---

### Step 4: Split X and y

```
[0, 0, 1, 2]  →  X=[0, 0, 1]   y=2  ("trained")
[0, 1, 2, 3]  →  X=[0, 1, 2]   y=3  ("every")
[1, 2, 3, 4]  →  X=[1, 2, 3]   y=4  ("day")
[0, 0, 1, 5]  →  X=[0, 0, 1]   y=5  ("became")
[0, 1, 5, 6]  →  X=[0, 1, 5]   y=6  ("hokage")
```

---

### Step 5: to_categorical on y

```
y=2 → [0, 0, 1, 0, 0, 0, 0]
y=3 → [0, 0, 0, 1, 0, 0, 0]
y=4 → [0, 0, 0, 0, 1, 0, 0]
y=5 → [0, 0, 0, 0, 0, 1, 0]
y=6 → [0, 0, 0, 0, 0, 0, 1]
       length = total_words = 7
```

---

### Step 6: Model Architecture

```python
model = Sequential([
    Embedding(total_words, 64, input_length=max_len-1),
    LSTM(128),
    Dense(total_words, activation='softmax')
])
```

**LSTM processing — step by step for input `[0, 0, 1]` ("Naruto"):**

```
X = [0, 0, 1]
      ↓
Embedding
→ [zero_vec, zero_vec, naruto_vec]   each word = 64-dim vector
      ↓
LSTM step 1: x=zero_vec
  Forget gate  → forget nothing (padding, no info)
  Input gate   → write nothing (no content)
  C(1) ≈ 0 (empty memory)
  h(1) ≈ 0 (empty output)
      ↓
LSTM step 2: x=zero_vec
  Same → C(2) ≈ 0, h(2) ≈ 0
      ↓
LSTM step 3: x=naruto_vec
  Forget gate  → nothing to forget (memory is empty)
  Input gate   → write "naruto" info → i ≈ 0.9
  Candidate    → g = naruto representation
  C(3) = 0 + 0.9 × g = naruto memory
  Output gate  → expose naruto info
  h(3) = o × tanh(C(3)) → 128-dim vector representing "after Naruto"
      ↓
Dense(7, softmax)
→ [0.01, 0.03, 0.02, 0.01, 0.87, 0.05, 0.01]
                                  ↑
                              index 5 = "became" → 87% probability
      ↓
prediction = "became"
```

---

### Step 7: Prediction at Inference Time

```python
seed_text = "Naruto"
next_words = 3

for _ in range(next_words):
    # Tokenize input
    token_list = tokenizer.texts_to_sequences([seed_text])[0]

    # Pad to max_len - 1
    token_list = pad_sequences([token_list], maxlen=max_len-1, padding='pre')

    # Predict
    predicted_probs = model.predict(token_list, verbose=0)
    predicted_index = np.argmax(predicted_probs)

    # Convert index back to word
    predicted_word = tokenizer.index_word[predicted_index]

    # Append and continue
    seed_text += " " + predicted_word
```

**Running output:**

```
Input: "Naruto"
Step 1: predict → "became"  → seed = "Naruto became"
Step 2: predict → "hokage"  → seed = "Naruto became hokage"
Step 3: predict → "naruto"  → seed = "Naruto became hokage naruto"
```

`np.argmax` picks the index with highest probability. That index maps back to a word via `tokenizer.index_word`.

---

# PART 9 — Tokenizer vs word_tokenize vs Embedding

Three different things — do not confuse them:

```
┌────────────────────────┬──────────────────────────────────────────────┐
│ Tool                   │ Job                                          │
├────────────────────────┼──────────────────────────────────────────────┤
│ NLTK word_tokenize()   │ Split sentence into word tokens (strings)    │
│                        │ Output: ["Naruto", "is", "a", "ninja"]       │
│                        │ Does NOT create integer IDs                  │
├────────────────────────┼──────────────────────────────────────────────┤
│ Keras Tokenizer        │ Build vocab + convert words to integers      │
│                        │ Output: [1, 2, 3, 4]                         │
│                        │ Used for neural network input                │
├────────────────────────┼──────────────────────────────────────────────┤
│ Embedding Layer        │ Convert integer IDs to dense vectors         │
│                        │ Output: (sequence_len, embedding_dim)        │
│                        │ Learned during training                      │
└────────────────────────┴──────────────────────────────────────────────┘
```

---

# PART 10 — Complete Pipeline Visual

```
RAW TEXT
"Naruto trained every day. Naruto became Hokage."
      ↓
┌─────────────────┐
│  Tokenizer      │  fit_on_texts([text])
│  fit            │  → word_index = {"naruto":1, "trained":2, ...}
└─────────────────┘
      ↓
┌─────────────────┐
│  N-Gram         │  texts_to_sequences + loop
│  Sequences      │  → [[1,2], [1,2,3], [1,2,3,4], ...]
└─────────────────┘
      ↓
┌─────────────────┐
│  Padding        │  pad_sequences(padding='pre')
│                 │  → [[0,0,1,2], [0,1,2,3], [1,2,3,4], ...]
└─────────────────┘
      ↓
┌─────────────────┐
│  X / y Split    │  X = all but last column
│                 │  y = last column
└─────────────────┘
      ↓
┌─────────────────┐
│ to_categorical  │  y = one-hot vectors
│                 │  y=2 → [0,0,1,0,0,0,0]
└─────────────────┘
      ↓
┌─────────────────────────────────────────┐
│  MODEL                                  │
│  Embedding → LSTM → Dense(softmax)      │
│                                         │
│  Embedding : integer → dense vector     │
│  LSTM      : sequence → context state   │
│  Dense     : context → word probs       │
└─────────────────────────────────────────┘
      ↓
┌─────────────────┐
│  Loss           │  categorical_crossentropy
│  Backprop       │  -log(predicted[correct_index])
│  Update         │  weights updated → model learns
└─────────────────┘
      ↓
┌─────────────────┐
│  Predict        │  seed_text → tokenize → pad → model.predict
│                 │  → argmax → index_word → next word
└─────────────────┘
      ↓
"Naruto became Hokage"
```

---

# Quick Reference

```
LSTM gates:
  Forget    →  what to delete from memory        (sigmoid, 0 to 1)
  Input     →  how much new info to add          (sigmoid, 0 to 1)
  Candidate →  what the new info is              (tanh, -1 to 1)
  Output    →  what to expose as hidden state    (sigmoid, 0 to 1)

C(t) = f × C(t-1)  +  i × g   ← cell state (long memory)
h(t) = o × tanh(C(t))         ← hidden state (output)

Tokenizer:
  fit_on_texts([text])          → learn vocabulary
  texts_to_sequences([text])    → words to integers
  word_index                    → word → integer dict
  index_word                    → integer → word dict (for prediction)
  total_words = len(word_index) + 1   → +1 for padding token (index 0)

N-gram:
  one sentence → multiple training examples
  each example → (context, next_word) pair
  split by '\n' to keep sentence boundaries

Padding:
  padding='pre'  → zeros at front → actual words at end → best for LSTM

to_categorical:
  y = 4  → [0,0,0,0,1,0,...,0]
  needed because Dense output is a vector, not a scalar
  alternative: use sparse_categorical_crossentropy and skip to_categorical

Prediction:
  argmax(model.predict(padded_input)) → highest probability index
  tokenizer.index_word[index]         → convert back to word
```