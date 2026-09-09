# Embedding Layer in Simple RNN 🧠

## What is an Embedding Layer?

An **Embedding Layer** converts integer/token IDs into **dense numerical vectors**.

```text
Token ID
   ↓
Embedding Layer
   ↓
Dense Word Vector
   ↓
Simple RNN
   ↓
Output
```

Instead of representing a word using a large one-hot vector, the Embedding Layer represents it using a smaller vector of learned numbers.

---

## Example

Suppose:

```text
the   → 4339
glass → 3308
milk  → 2026
```

The Embedding Layer may convert:

```text
4339 → [0.21, -0.45, 0.73, 0.11]
3308 → [0.82,  0.14, -0.31, 0.56]
2026 → [-0.12, 0.91, 0.33, -0.27]
```

These vectors are **learned during training**.

---

# Why Do We Use Embedding?

One-hot encoding creates large and sparse vectors:

```text
[0, 0, 0, 0, 0, 0, 1, 0, 0, ...]
```

Embedding creates a smaller and dense representation:

```text
[0.21, -0.45, 0.73, 0.11]
```

### Benefits

- Reduces dimensionality
- Creates dense representations
- Learns useful word relationships
- More efficient than large one-hot vectors
- Can capture semantic relationships

---

# Embedding Layer Syntax

```python
Embedding(
    vocab_size,
    dimensions,
    input_length=sent_length
)
```

### `vocab_size`

Number of unique words/tokens in the vocabulary.

```python
vocab_size = 10000
```

### `dimensions`

Number of values in the embedding vector for each word.

```python
dimensions = 100
```

This means every token is represented using a **100-dimensional vector**.

### `input_length`

Number of tokens in each input sequence.

If every sentence has been padded to 4 tokens:

```python
sent_length = 4
```

---

# Creating the Embedding Layer

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding

model = Sequential()

model.add(
    Embedding(
        vocab_size,
        dimensions,
        input_length=sent_length
    )
)
```

---

# Embedding + Simple RNN

The Embedding Layer is **not the RNN**.

The Embedding Layer converts token IDs into vectors, and the Simple RNN processes those vectors in sequence.

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN

model = Sequential()

model.add(
    Embedding(
        vocab_size,
        dimensions,
        input_length=sent_length
    )
)

model.add(
    SimpleRNN(32)
)
```

Architecture:

```text
Token IDs
    ↓
Embedding Layer
    ↓
Word Vectors
    ↓
Simple RNN
    ↓
Output
```

---

# Example with Our Padded Sequences

Suppose:

```python
[
    [4339, 3308, 2026, 2978],
    [4339, 3308, 2026, 1322],
    [2807, 4416, 8406, 9343],
    [0, 2807, 1582, 7757],
    [3989, 2816, 4339, 7342]
]
```

The Embedding Layer takes each token ID and converts it into a vector.

For example:

```text
[4339, 3308, 2026, 2978]

        ↓ Embedding

[
  vector for 4339,
  vector for 3308,
  vector for 2026,
  vector for 2978
]
```

If:

```python
dimensions = 100
```

then each token becomes a vector containing 100 numbers.

Therefore:

```text
4 tokens × 100 dimensions
        ↓
      4 × 100
```

---

# Compiling the Model

After creating the model:

```python
model.compile(
    optimizer="adam",
    loss="mse"
)
```

### `optimizer`

```python
optimizer="adam"
```

Adam controls how the model updates its weights during training.

### `loss`

```python
loss="mse"
```

MSE means **Mean Squared Error**.

> The loss function depends on the task. `mse` is commonly used for regression. Classification usually uses losses such as `binary_crossentropy` or `categorical_crossentropy`.

---

# Complete Example

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN

# Vocabulary size
vocab_size = 10000

# Number of values in each word vector
dimensions = 100

# Number of tokens in each padded sentence
sent_length = 4


# Create Sequential Model
model = Sequential()


# Embedding Layer
# Converts token IDs into dense vectors
model.add(
    Embedding(
        vocab_size,
        dimensions,
        input_length=sent_length
    )
)


# Simple RNN Layer
# Processes the sequence of word vectors
model.add(
    SimpleRNN(32)
)


# Compile the model
model.compile(
    optimizer="adam",
    loss="mse"
)
```

---

# Remember

```text
Token ID
   ↓
Embedding Layer
   ↓
Dense Word Vector
   ↓
Simple RNN
   ↓
Output
```

> **Embedding = converts token IDs into learned dense vectors.**

> **Simple RNN = processes those vectors while considering the order of the words.**
