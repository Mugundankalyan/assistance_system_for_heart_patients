REAL-TIME ECG ARRHYTHMIA CLASSIFICATION USING A TRANSFORMER MODEL:
The detection of arrhythmias in ECG signals is crucial for diagnosing and preventing cardiac conditions. ECG signals provide valuable insights into heart function, and abnormalities in these signals can indicate life-threatening arrhythmias. This project aims to develop a deep learning model based on a transformer architecture to classify ECG signals in real-time.

DATASET DETAILS
MIT-BIH Arrhythmia Database
The MIT-BIH Arrhythmia Database is used for training and evaluation. This dataset consists of 48 half-hour ECG recordings from 47 individuals (25 male, 22 female) and was collected from the Beth Israel Hospital Arrhythmia Laboratory. The signals were sampled at 360 Hz with a resolution of 11 bits per sample.
Classes Used for Training:
Class Label
Description
N
Normal Beat
V
Premature Ventricular Contraction
A
Atrial Premature Contraction (APC)
L
Left Bundle Branch Block (LBBB)
R
Right Bundle Branch Block (RBBB)

Preprocessing Steps:
    • Loading ECG Signals: Extracted from the MIT-BIH dataset using wfdb and segmented into beats.
    • Normalization: Standardized ECG signals using Z-score normalization to ensure consistency.
    • R-Peak Detection: Detected using the annotations provided in MIT-BIH.
    • Windowing: Each heartbeat is extracted into 100-sample windows around R-peaks.
    • Label Encoding: Arrhythmia labels are mapped to categorical values.
    • Data Augmentation: Synthetic noise and random shifts are added to improve model generalization.
Training Data Distribution
Class
Number of Samples
Normal (N)
~75,000
PVC (V)
~7,000
APC (A)
~2,500
LBBB (L)
~5,000
RBBB (R)
~6,000
The dataset was split into 70% training, 15% validation, and 15% testing.
MODEL DESIGN
The model is a transformer-based neural network, designed for sequential ECG data processing. Unlike traditional CNN or LSTM models, transformers capture long-range dependencies effectively.
Key Components
    1. Input Layer: Accepts ECG sequences of shape (100,1).
    2. Positional Encoding: Adds time-step information to account for sequence order.
    3. Transformer Encoder Layers:
        ◦ Multi-head self-attention to capture dependencies between time steps.
        ◦ Feedforward layers with ReLU activation.
        ◦ Layer normalization & dropout for stability and regularization.
    4. Flatten Layer: Converts sequence output into a dense representation.
    5. Fully Connected Layers:
        ◦ Dense (64 neurons, ReLU activation)
        ◦ Dropout (0.5) to prevent overfitting
        ◦ Dense (5 output classes, softmax activation)

Layer Name
Output Shape
Number of Parameters
Input Layer
(100, 1)
0
Multi-Head Attention
(100, 64)
12,352
Dropout
(100, 64)
0
Layer Normalization
(100, 64)
128
Residual Connection
(100, 64)
0
Dense (ReLU)
(100, 128)
8,320
Dropout
(100, 128)
0
Layer Normalization
(100, 128)
256
Residual Connection
(100, 128)
0
Global Average Pooling 1D
(128)
0
Dense (ReLU)
(64)
8,256
Dropout
(64)
0
Output Layer (Softmax)
(5)
325

2. Hyperparameters

Parameter
Value
Optimizer
Adam
Learning Rate
0.001
Batch Size
32
Dropout Rate
0.3
Number of Epochs
20
Training Parameters
    • Batch Size: 32
    • Epochs: 20
    • Dropout Rate: 0.5
    • Optimizer: Adam
    • Loss Function: Categorical Cross-Entropy
Performance Metrics
Metric
Training
Validation
Testing
Accuracy
98%
96%
95%
Loss
0.08
0.12
0.15
Confusion Matrix Analysis
    • High precision and recall for normal beats (N).
    • Minor misclassifications between PVC and APC due to waveform similarity.
    • LBBB and RBBB were well classified with high accuracy.

TESTING AND INFERENCE
The trained model is deployed to classify real-time ECG data. The inference process involves:
    1. Retrieving ECG sequences from Firebase.
    2. Preprocessing the signals (normalization, segmentation).
    3. Feeding data into the transformer model for classification.
Test Case
Prediction
Confidence (%)
Normal
Normal
99.2%
PVC
PVC
96.4%
APC
Misclassified as Normal
85.6%
LBBB
LBBB
98.7%
RBBB
RBBB
97.1%

Observations:
    • Some APC beats were misclassified as Normal, possibly due to similar waveform morphology.
    • PVC predictions were highly accurate, demonstrating the model’s robustness.

