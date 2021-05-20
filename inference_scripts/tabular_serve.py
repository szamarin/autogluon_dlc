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

def input_fn(request_body, request_content_type):
    
    if request_content_type == "text/csv":
        num_cols = len(request_body.split(","))
        if num_cols != len(column_names):
            raise Exception(f"Invalid data format. Input data has {num_cols} while the model expects {len(column_names)}")
        else:    
            buf = StringIO(request_body)
            data = pd.read_csv(buf_csv, header=None, names=column_names)
    
    elif request_content_type == "application/json":
        
        
    
    request = json.loads(request_body.decode("utf8"))

    future = pd.DataFrame(pd.date_range(start=request["start"], 
                                        end=request["end"], 
                                        freq="D"), 
                          columns=["ds"])
    return future


def predict_fn(input_object, model):
    
    """Takes the output from input_fn and passes it to the model"""
    
    prediction = model.predict(input_object)
    
    return prediction

def output_fn(prediction, content_type):
    
    """Takes the ouput of predict_fn and converts it into the final format for serving
    The output format is as follows:
    [
        {"ds":1/1/2016, "yhat_lower": 5,"yhat_upper": 20, "yhat": 12},
        ...
    ]
    Essentially a json list of predictions for each day
    """
    
    return_cols = ["ds","yhat_lower","yhat_upper","yhat"]
    prediction["ds"] = prediction["ds"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    
    predictions = prediction[return_cols].apply(lambda x: dict(zip(return_cols, x.values)), axis=1).values.tolist()
    
    return json.dumps(predictions).encode("utf8")
    