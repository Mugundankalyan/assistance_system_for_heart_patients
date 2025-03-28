Real-Time ECG Arrhythmia Classification Using a Transformer Model

The detection of arrhythmias in ECG signals is crucial for diagnosing and preventing cardiac conditions. ECG signals provide valuable insights into heart function, and abnormalities in these signals can indicate life-threatening arrhythmias. This project aims to develop a deep learning model based on a transformer architecture to classify ECG signals in real-time.
Dataset Details
MIT-BIH Arrhythmia Database

The MIT-BIH Arrhythmia Database is used for training and evaluation. This dataset consists of:

    48 half-hour ECG recordings from 47 individuals (25 male, 22 female).

    Collected from the Beth Israel Hospital Arrhythmia Laboratory.

    Signals were sampled at 360 Hz with a resolution of 11 bits per sample.

Preprocessing Steps

    Loading ECG Signals: Extracted from the MIT-BIH dataset using wfdb and segmented into beats.

    Normalization: Standardized ECG signals using Z-score normalization for consistency.

    R-Peak Detection: Detected using the annotations provided in MIT-BIH.

    Windowing: Each heartbeat is extracted into 100-sample windows around R-peaks.

    Label Encoding: Arrhythmia labels are mapped to categorical values.

    Data Augmentation: Synthetic noise and random shifts are added to improve model generalization.

Dataset Split

    70% Training

    15% Validation

    15% Testing

Model Design

The model is a transformer-based neural network, designed for sequential ECG data processing. Unlike traditional CNN or LSTM models, transformers capture long-range dependencies effectively.
Key Components

    Input Layer: Accepts ECG sequences of shape (100, 1).

    Positional Encoding: Adds time-step information to account for sequence order.

    Transformer Encoder Layers:

        Multi-head self-attention to capture dependencies between time steps.

        Feedforward layers with ReLU activation.

        Layer normalization & dropout for stability and regularization.

    Flatten Layer: Converts sequence output into a dense representation.

    Fully Connected Layers:

        Dense (64 neurons, ReLU activation).

        Dropout (0.5) to prevent overfitting.

        Dense (5 output classes, softmax activation).

Training Parameters
Parameter	Value
Batch Size	32
Epochs	20
Dropout Rate	0.5
Optimizer	Adam
Loss Function	Categorical Cross-Entropy
Confusion Matrix Analysis

    High precision and recall for normal beats (N).

    Minor misclassifications between PVC and APC due to waveform similarity.

    LBBB and RBBB were well classified with high accuracy.

Testing and Inference

The trained model is deployed to classify real-time ECG data. The inference process involves:

    Retrieving ECG sequences from Firebase.

    Preprocessing the signals (normalization, segmentation).

    Feeding data into the transformer model for classification.

Observations

    Some APC beats were misclassified as Normal, possibly due to similar waveform morphology.

    PVC predictions were highly accurate, demonstrating the model’s robustness.
Running the Model

Clone this repository:

git clone https://github.com/yourusername/ecg-transformer-classification.git
cd ecg-transformer-classification

Install dependencies:

pip install -r requirements.txt
