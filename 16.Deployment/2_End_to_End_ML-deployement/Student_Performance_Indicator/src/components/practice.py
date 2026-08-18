import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer   # alag alag columns pe alag pipelines lagao
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer        # missing values handle karo
from sklearn.pipeline import Pipeline           # steps ko sequence mein chain karo

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object  


@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join("artifacts", "preprocessor.pkl")


class DataTransformation:
    def __int__(self):
        self.data_transformation_config = DataTransformation()

    def get_data_transformaer_object(self):

        try:
             numerical_features   = ["writing_score", "reading_score"]
            
                        # EDA notebook se pata tha ye cols categorical hain
             categorical_features = [
                            'gender',
                            'race_ethnicity',
                            'parental_level_of_education',
                            'lunch',
                            'test_preparation_course'
                        ]

             num_pipeline = Pipeline(
                 steps=[
                     ("imputer", SimpleImputer(strategy="medan")),
                     ('scaler', StandardScaler())
                 ]
             )

             cat_pipeline = Pipeline(
                 steps=[
                     ("imputer", SimpleImputer(strategy="most_frequest")),
                     ("OneHot",OneHotEncoder()),
                     ("scaler", StandardScaler())
                 ]
             )

             preprocessor = ColumnTransformer(transformers=[
                 ("num_pipeline", num_pipeline, numerical_features),
                 ("cat_pipeline", cat_pipeline, categorical_features)
             ])

             return preprocessor
            
        except:
            pass


    def initiate_data_transformation(self, train_path, test_path):


        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)

        preprocessor_obj = self.get_data_transformaer_object()

        target_col_name = "math_score"

        input_feature_train_df  = train_df.drop(target_col_name, axis=1)
        target_feature_train_df = train_df[target_col_name]
        
                    # ── TEST DATA SPLIT ───────────────────────────────────
        input_feature_test_df  = test_df.drop(target_col_name, axis=1)
        target_feature_test_df = test_df[target_col_name]


        input_f_train_arr = preprocessor_obj.fit_transform(input_feature_train_df)
        input_f_arr = preprocessor_obj.transform(input_feature_test_df)

        train_arr = np.c_[input_f_train_arr, np.array(target_feature_train_df)]

        save_object(file_path=self.data_transformation_config,
                    obj= preprocessor_obj)

        return (
            train_arr,
            test
        )