from autogluon.tabular import TabularDataset, TabularPredictor
import os

train_data = TabularDataset('https://autogluon.s3.amazonaws.com/datasets/Inc/train.csv')
subsample_size = 500  # subsample subset of data for faster demo, try setting this to much larger values
train_data = train_data.sample(n=subsample_size, random_state=0)
label = 'class'
save_path = os.environ['SM_MODEL_DIR']  # specifies folder to store trained models
predictor = TabularPredictor(label=label, path=save_path).fit(train_data)

