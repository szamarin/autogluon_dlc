from autogluon.tabular import TabularPredictor
import os
import json
from io import StringIO
import pandas as pd


def model_fn(model_dir):
    """loads model from previously saved artifact"""
    model = TabularPredictor.load(model_dir)
    globals()["column_names"] = model.feature_metadata_in.get_features()
    
    return model


def transform_fn(model, request_body, input_content_type, output_content_type="application/json"):
    
    if input_content_type == "text/csv":
        buf = StringIO(request_body)
        data = pd.read_csv(buf, header=None)
        num_cols = len(data.columns)
        
        if num_cols != len(column_names):
            raise Exception(f"Invalid data format. Input data has {num_cols} while the model expects {len(column_names)}")
        
        else:
            data.columns = column_names

    else: 
        raise Exception(f"{input_content_type} content type not supported")
   
    prediction = model.predict_proba(data, as_pandas=False)
    
    return json.dumps(prediction.tolist()), output_content_type


    