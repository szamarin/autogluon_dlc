from autogluon.tabular import TabularDataset, TabularPredictor
from autogluon.tabular.models.knn.knn_rapids_model import KNNRapidsModel
from autogluon.tabular.models.lr.lr_rapids_model import LinearRapidsModel
import os


save_path = os.environ['SM_MODEL_DIR'] 
train_path = os.environ['SM_CHANNEL_TRAIN']
test_path = os.environ['SM_CHANNEL_TEST']
output_path = os.environ['SM_OUTPUT_DATA_DIR']

train_data = TabularDataset(f'{train_path}/train.csv')
test_data = TabularDataset(f'{test_path}/test.csv')

label = 'target'

predictor = TabularPredictor(
    label=label,
    eval_metric='log_loss',
    learner_kwargs={'ignored_columns': ['id']},
    path=save_path
).fit(
    train_data,
    presets='best_quality',
    hyperparameters={
        KNNRapidsModel: {},
        LinearRapidsModel: {},
        'RF': {},
        'XGB': {'ag_args_fit': {'num_gpus': 1}},
        'CAT': {'ag_args_fit': {'num_gpus': 1}},
    },
)

leaderboard = predictor.leaderboard(silent=True)
leaderboard.to_csv(f"{output_path}/leaderboard.csv")