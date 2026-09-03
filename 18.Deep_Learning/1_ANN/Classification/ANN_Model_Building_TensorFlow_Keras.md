# Building an ANN Model with TensorFlow / Keras

## 1. Import TensorFlow

TensorFlow provides Keras, which we can use to build and train Artificial Neural Networks (ANNs).

```python
import tensorflow as tf
```

---

# 2. Sequential Model

## What is a Sequential Model?

A `Sequential` model is the simplest way to build a neural network in Keras.

It means that we add layers **one after another in a fixed sequence**.

For example:

```text
Input
  ↓
Hidden Layer 1
  ↓
Hidden Layer 2
  ↓
Output Layer
```

Each layer receives the output of the previous layer.

### Syntax

```python
model = tf.keras.Sequential([
    layer1,
    layer2,
    layer3
])
```

### Example

```python
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])
```

Here, the ANN has three layers.

---

# 3. Dense Layer

## What is a Dense Layer?

A `Dense` layer is a **fully connected layer**.

Every neuron in a Dense layer is connected to every neuron in the previous layer.

```text
Previous Layer             Dense Layer

   ● ─────────────────────→ ●
   ● ─────────────────────→ ●
   ● ─────────────────────→ ●
   ● ─────────────────────→ ●
```

Each neuron performs approximately:

```text
z = Wx + b
activation(z)
```

The weights and bias are learned during training.

---

## Dense Syntax

```python
tf.keras.layers.Dense(
    units,
    activation="activation_function"
)
```

### `units`

`units` tells us how many neurons the layer should contain.

```python
Dense(64)
```

means:

```text
This layer contains 64 neurons.
```

### `activation`

The activation function determines how the neuron transforms its calculated value.

```python
Dense(64, activation="relu")
```

Common activation functions include:

```text
relu
sigmoid
tanh
softmax
```

---

# 4. Input Layer

The input layer represents the features that we give to the ANN.

Suppose our dataset has 10 input features:

```text
Feature 1
Feature 2
Feature 3
...
Feature 10
```

Then we can specify:

```python
input_shape=(10,)
```

Example:

```python
tf.keras.layers.Dense(
    64,
    activation="relu",
    input_shape=(10,)
)
```

This means the model expects **10 input features for each sample**.

---

# 5. Creating an ANN

For a binary classification problem, we can create:

```python
model = tf.keras.Sequential([

    # First hidden layer
    tf.keras.layers.Dense(
        64,
        activation="relu",
        input_shape=(10,)
    ),

    # Second hidden layer
    tf.keras.layers.Dense(
        32,
        activation="relu"
    ),

    # Output layer
    tf.keras.layers.Dense(
        1,
        activation="sigmoid"
    )
])
```

The architecture looks like:

```text
                 ANN

Input Layer
10 Features
     │
     ↓
Hidden Layer
64 Neurons
ReLU
     │
     ↓
Hidden Layer
32 Neurons
ReLU
     │
     ↓
Output Layer
1 Neuron
Sigmoid
     │
     ↓
Prediction
```

For binary classification, the output is usually a value between `0` and `1`.

For example:

```text
0.12 → likely class 0
0.87 → likely class 1
```

---

# 6. Model Summary

We can use:

```python
model.summary()
```

It gives us information about:

- Layers
- Output shapes
- Number of parameters
- Trainable parameters

Example:

```text
Layer              Output Shape       Parameters
-------------------------------------------------
Dense              (None, 64)         ...
Dense              (None, 32)         ...
Dense              (None, 1)          ...
```

---

# 7. Model Compilation

## What is Model Compilation?

Before training, we need to tell the ANN **how it should learn**.

Compilation mainly specifies:

```text
Optimizer
    +
Loss Function
    +
Metrics
```

Syntax:

```python
model.compile(
    optimizer=...,
    loss=...,
    metrics=[...]
)
```

---

# 8. Optimizer

The optimizer controls **how the model updates its weights** during training.

For example:

```python
optimizer = tf.keras.optimizers.Adam(
    learning_rate=0.001
)
```

Adam is a commonly used optimizer for neural networks.

The `learning_rate` controls how large each weight update is.

---

# 9. Loss Function

The loss function measures **how wrong the model's predictions are**.

For binary classification, we commonly use:

```python
loss="binary_crossentropy"
```

Conceptually:

```text
Actual Value
     +
Model Prediction
     ↓
Loss Function
     ↓
Loss
```

The training process tries to reduce this loss.

---

# 10. Metrics

Metrics help us evaluate model performance.

For example:

```python
metrics=["accuracy"]
```

This tells Keras to calculate accuracy while training.

---

# 11. Complete Model Compilation

```python
model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)
```

At this point:

```text
Architecture → Created
Optimizer    → Selected
Loss         → Selected
Metric       → Selected
```

The model is now ready for training.

---

# 12. Early Stopping

## What is Early Stopping?

Early Stopping automatically stops training when the model stops improving.

It is mainly used to:

- Reduce overfitting
- Avoid unnecessary epochs
- Save training time
- Keep the best model weights

Example:

```text
Epoch 1 → val_loss decreases
Epoch 2 → val_loss decreases
Epoch 3 → val_loss decreases
Epoch 4 → val_loss decreases
Epoch 5 → no improvement
Epoch 6 → no improvement
Epoch 7 → no improvement
       ↓
Training stops
```

---

## Early Stopping Syntax

```python
from tensorflow.keras.callbacks import EarlyStopping

early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)
```

### `monitor`

The metric that we want to watch.

```python
monitor="val_loss"
```

means:

> Watch the validation loss.

### `patience`

How many epochs to wait for improvement.

```python
patience=5
```

means:

> Allow 5 epochs without improvement before stopping.

### `restore_best_weights`

```python
restore_best_weights=True
```

means:

> After stopping, restore the weights from the epoch where the monitored metric was best.

---

# 13. TensorBoard

## What is TensorBoard?

TensorBoard is a visualization tool used to monitor the training process.

It can help us visualize things such as:

- Training loss
- Validation loss
- Accuracy
- Validation accuracy
- Weight/activation histograms

---

## Creating a TensorBoard Callback

```python
import datetime
from tensorflow.keras.callbacks import TensorBoard
```

Create a unique log directory:

```python
log_dir = "logs/fit/" + datetime.datetime.now().strftime(
    "%Y%m%d-%H%M%S"
)
```

Then create the callback:

```python
tensorboard_callback = TensorBoard(
    log_dir=log_dir,
    histogram_freq=1
)
```

The logs will be stored inside something similar to:

```text
logs/
└── fit/
    └── 20260903-153000/
```

---

# 14. Model Training

We train the ANN using:

```python
model.fit()
```

Basic syntax:

```python
model.fit(
    X_train,
    y_train,
    epochs=100
)
```

### `X_train`

Training features.

### `y_train`

Training labels.

### `epochs`

How many times the model can go through the training dataset.

---

# 15. Validation Data

We can provide validation data:

```python
validation_data=(X_test, y_test)
```

This allows Keras to evaluate the model after each epoch.

Example:

```python
model.fit(
    X_train,
    y_train,
    epochs=100,
    validation_data=(X_test, y_test)
)
```

Conceptually:

```text
Training Data
     ↓
   ANN
     ↓
Update Weights

Validation Data
     ↓
   ANN
     ↓
Evaluate Performance
```

The validation data helps us detect problems such as overfitting.

---

# 16. Training with Callbacks

Callbacks are additional functions that Keras can execute during training.

We can pass them using:

```python
callbacks=[...]
```

Example:

```python
history = model.fit(
    X_train,
    y_train,
    epochs=100,
    validation_data=(X_test, y_test),
    callbacks=[
        early_stopping,
        tensorboard_callback
    ]
)
```

Now:

```text
                 model.fit()
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
   Early Stopping          TensorBoard
          ↓                     ↓
  Stop when needed       Record training
```

---

# 17. Complete ANN Workflow

The complete process is:

```text
Dataset
   ↓
Preprocessing
   ↓
Train / Test Split
   ↓
Create Sequential Model
   ↓
Add Dense Layers
   ↓
Compile Model
   ↓
Create Callbacks
   ├── Early Stopping
   └── TensorBoard
   ↓
model.fit()
   ↓
Training
   ↓
Forward Propagation
   ↓
Calculate Loss
   ↓
Backpropagation
   ↓
Update Weights
   ↓
Validation
   ↓
Best Model
```

---

# 18. Complete Code

```python
import tensorflow as tf
import datetime

from tensorflow.keras.callbacks import EarlyStopping, TensorBoard


# ==================================================
# 1. CREATE ANN MODEL
# ==================================================

model = tf.keras.Sequential([

    # First hidden layer
    #
    # 64 = number of neurons
    # relu = activation function
    # input_shape=(10,) = 10 input features
    tf.keras.layers.Dense(
        64,
        activation="relu",
        input_shape=(10,)
    ),

    # Second hidden layer
    #
    # 32 neurons
    # ReLU activation
    tf.keras.layers.Dense(
        32,
        activation="relu"
    ),

    # Output layer
    #
    # 1 neuron because this is binary classification
    # Sigmoid gives an output between 0 and 1
    tf.keras.layers.Dense(
        1,
        activation="sigmoid"
    )
])


# ==================================================
# 2. VIEW MODEL ARCHITECTURE
# ==================================================

model.summary()


# ==================================================
# 3. COMPILE MODEL
# ==================================================

model.compile(

    # Adam controls how weights are updated
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),

    # Binary classification loss
    loss="binary_crossentropy",

    # Performance metric
    metrics=["accuracy"]
)


# ==================================================
# 4. CREATE EARLY STOPPING CALLBACK
# ==================================================

early_stopping = EarlyStopping(

    # Monitor validation loss
    monitor="val_loss",

    # Wait 5 epochs for improvement
    patience=5,

    # Restore weights from the best epoch
    restore_best_weights=True
)


# ==================================================
# 5. CREATE TENSORBOARD CALLBACK
# ==================================================

log_dir = "logs/fit/" + datetime.datetime.now().strftime(
    "%Y%m%d-%H%M%S"
)

tensorboard_callback = TensorBoard(

    # Where TensorBoard logs will be stored
    log_dir=log_dir,

    # Record histograms every epoch
    histogram_freq=1
)


# ==================================================
# 6. TRAIN THE MODEL
# ==================================================

history = model.fit(

    # Training features
    X_train,

    # Training labels
    y_train,

    # Maximum number of epochs
    epochs=100,

    # Data used for validation
    validation_data=(X_test, y_test),

    # Callbacks
    callbacks=[
        early_stopping,
        tensorboard_callback
    ]
)
```

---

# 19. The Whole Idea in Simple Words

```text
Sequential
    ↓
Build the ANN structure

Dense
    ↓
Create fully connected neurons

Compile
    ↓
Tell the ANN how to learn

Optimizer
    ↓
Controls weight updates

Loss Function
    ↓
Measures how wrong predictions are

Early Stopping
    ↓
Stops training when validation performance stops improving

TensorBoard
    ↓
Visualizes the training process

model.fit()
    ↓
Actually trains the ANN
```

## Remember

> **Build → Compile → Callbacks → Train**

```text
Build
  ↓
Compile
  ↓
Early Stopping + TensorBoard
  ↓
model.fit()
  ↓
Trained ANN
```
