import os
from pprint import pprint

import yaml
from autogluon.tabular import TabularDataset, TabularPredictor


def get_input_path(channel):
    path = os.environ[channel]
    file = os.listdir(path)[0]
    if len(os.listdir(path)) > 1:
        print(f'WARN: more than one file is found in {channel} directory')
    print(f'Using {file}')
    filename = f'{path}/{file}'
    return filename


if __name__ == '__main__':
    # ------------------------------------------------------------ Args parsing
    # See SageMaker-specific environment variables: https://sagemaker.readthedocs.io/en/stable/overview.html#prepare-a-training-script
    # TODO SM_NUM_GPUS
    model_save_path = os.environ['SM_MODEL_DIR']  # specifies folder to store trained models

    output_path = os.environ['SM_OUTPUT_DATA_DIR']
    os.makedirs(output_path, mode=0o777, exist_ok=True)

    config_file = get_input_path('SM_CHANNEL_CONFIG')
    with open(config_file) as f:
        config = yaml.safe_load(f)  # AutoGluon-specific config

    print('Running training job with the config:')
    pprint(config)

    # ---------------------------------------------------------------- Training

    train_file = get_input_path('SM_CHANNEL_TRAIN')
    train_data = TabularDataset(train_file)

    ag_predictor_args = config['ag_predictor_args']
    ag_predictor_args['path'] = model_save_path
    ag_fit_args = config['ag_fit_args']

    predictor = TabularPredictor(**ag_predictor_args).fit(train_data, **ag_fit_args)

    # --------------------------------------------------------------- Inference

    test_path = None
    if 'SM_CHANNEL_TEST' in os.environ:
        test_path = get_input_path('SM_CHANNEL_TEST')

    if test_path:
        test_file = get_input_path('SM_CHANNEL_TEST')
        test_data = TabularDataset(test_file)

        y_pred_proba = predictor.predict_proba(test_data)
        if config.get('output_prediction_format', 'csv') == 'parquet':
            y_pred_proba.to_parquet(f'{output_path}/predictions.parquet')
        else:
            y_pred_proba.to_csv(f'{output_path}/predictions.csv')

        if config.get('leaderboard', False):
            lb = predictor.leaderboard(test_data, silent=False)
            lb.to_csv(f'{output_path}/leaderboard.csv')

        if config.get('feature_importance', False):
            feature_importance = predictor.feature_importance(test_data)
            feature_importance.to_csv(f'{output_path}/feature_importance.csv')
    else:
        if config.get('leaderboard', False):
            lb = predictor.leaderboard(silent=False)
            lb.to_csv(f'{output_path}/leaderboard.csv')
