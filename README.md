# Emotion-Detection-Using-Text

![emoji-1920-x-1080-6cnao0nwrmho8cex (3)](https://github.com/ninadpatil09/Emotion-Detection-Using-Text/assets/60342946/2825bc40-d9ba-4df3-89a9-98140c545885)

## Overview

The goal is to tackle the growing challenge of analyzing emotions conveyed through text, particularly in the context of the vast amount of comments generated daily on social media platforms and reviews from various websites can provide valuable insights into customer sentiments and preferences. Emotions such as anger, sadness, joy, and fear often occur in these comments, making it crucial to develop tools that can accurately predict and classify these emotions

## Model Architecture
To address this challenge, we used deep learning techniques, leveraging the GloVe pre-trained word embeddings. Specifically, we utilize a Bidirectional Long Short-Term Memory (Bi-LSTM) architecture, known for its effectiveness in capturing contextual information in sequential data.

  - Embedding Layer: Utilizes pre-trained GloVe embeddings to represent words in a dense vector space.

  - Bi-LSTM Layer: Employs a bidirectional LSTM to capture both past and future context of each word.

  - Output Layer: A softmax layer for multi-class classification of emotions.

## Conclusion

Our experiments show that the Bi-LSTM model, with the help of GloVe pre-trained embeddings, gives good results. The model achieves a training accuracy of 95% and a testing accuracy around 91%, indicating its robustness in accurately predicting emotions from text data.

In conclusion, the utilization of deep learning techniques coupled with pre-trained word embeddings shows great potential in emotion detection from text, offering valuable insights for various applications in social media analysis and beyond. We can make it even better by trying out more advanced methods to improve its performance in real-life situations.
