# Recommendation System

Recommended to be used with PyCharm IDE.

Run below in the terminal to install the requirements and start the service:

```bash
# Install the requirements:
pip install -r requirements.txt

# Start the service:
uvicorn app:app --reload
```

Now you can load http://localhost:8000/docs in your browser ... but there won't be much to see until you've inserted
some data.

You can test with,

    existing_profile = "64315d86362c27c707fe155c"

    new_profile = "64315d86362c27c707fe152z"

    sentiment = "The restaurant provided updates on the status of our order, which was very helpful."

Repleace sentiment prediction part
Model
Requarement

For sentiment analyzis we created a model with keras.

First before training the model we cleaned data. We removed stop words, punctuations, numbers and converted all the
words to lower case.
Then lemmatization was done to convert words to their base form.
Then pos tagging was done to get the part of speech of each word.
Then we tokenized the words and converted them to sequences.

Then the model was created with 3 layers. First layer was embedding layer. Second layer was LSTM layer. Third layer was
dense layer with softmax.
Then the model was trained with 70 epochs.

Model is compiled with rmsprop optimizer and categorical_crossentropy loss function. with accuracy as the metric.

Then early stopping also added to stop training if no progress is showing.


_________________________________________________________________
Layer (type)                Output Shape              Param #
=================================================================
embedding_1 (Embedding)     (None, None, 20)          100000

lstm_1 (LSTM)               (None, 20)                3280

dense_1 (Dense)             (None, 3)                 63
                                                                 
=================================================================
Total params: 103,343
Trainable params: 103,343
Non-trainable params: 0
_________________________________________________________________


Then the model and tokenizer was saved.

Later they are loaded for prediction.

pip install "fastapi[all]"

pymongo==4.3.3
motor==3.1.2
dnspython==2.3.0
pydantic==1.10.7
fastapi==0.95.1
python-dotenv==1.0.0
pandas==2.0.0

pymongo==4.3.3
motor==3.1.2
dnspython==2.3.0
pydantic==1.10.7
fastapi==0.95.1
python-dotenv==1.0.0
pandas==2.0.0
matplotlib==3.8.0
python-dateutil==2.8.2
spacy==3.7.1
SQLAlchemy==1.3.24
mathparse==0.1.2
pytz==2023.3.post1
numpy==1.26.0
scipy==1.11.3
scikit-learn==1.3.1
nltk==3.8.1
networkx==3.1
geopy==2.4.0

PyYAML==6.0.1
googletrans==4.0.0rc1


pymongo.errors.ConfigurationError: The resolution lifetime expired after 21.216 seconds: Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.; Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.; Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.; Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.; Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.; Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.; Server 192.168.8.1 UDP port 53 answered The DNS operation timed out.
