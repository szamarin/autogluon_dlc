import os
from pprint import pprint

import yaml
from autogluon.tabular import TabularDataset, TabularPredictor

if __name__ == '__main__':
    # ------------------------------------------------------------ Args parsing
    # See SageMaker-specific environment variables: https://sagemaker.readthedocs.io/en/stable/overview.html#prepare-a-training-script
    # TODO SM_NUM_GPUS
    model_save_path = os.environ['SM_MODEL_DIR']  # specifies folder to store trained models
    print(f'model_save_path: {model_save_path}')

    train_path = os.environ['SM_CHANNEL_TRAIN']
    print(f'train_path: {train_path}')

    output_path = os.environ['SM_OUTPUT_DATA_DIR']
    print(f'output_path: {output_path}')
    os.makedirs(output_path, mode=0o777, exist_ok=True)

    test_path = None
    if os.environ['SM_CHANNEL_TEST']:
        test_path = os.environ['SM_CHANNEL_TEST']
        print(f'test_path: {test_path}')

    with open(os.environ['SM_CONFIG_FILE']) as f:
        config = yaml.load(f)  # AutoGluon-specific config

    print('Running training job with the config:')
    pprint(config)

    # ---------------------------------------------------------------- Training

    train_data = TabularDataset(train_path)

    ag_predictor_args = config['ag_predictor_args']
    ag_predictor_args['path'] = model_save_path
    ag_fit_args = config['ag_fit_args']

    predictor = TabularPredictor(**ag_predictor_args).fit(train_data, **ag_fit_args)

    # --------------------------------------------------------------- Inference

    if test_path:
        test_data = TabularDataset(test_path)

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
