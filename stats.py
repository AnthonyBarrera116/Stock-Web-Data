import numpy as np
import tensorflow as tf

print("NumPy version:", np.__version__)
print("TF version:", tf.__version__)
print("GPU:", tf.config.list_physical_devices("GPU"))
