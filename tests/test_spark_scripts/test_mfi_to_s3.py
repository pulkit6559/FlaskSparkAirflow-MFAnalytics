import unittest
from unittest.mock import patch, Mock, MagicMock
# from pyspark.testing import SparkTestCase
from pyspark.sql import SparkSession, SQLContext
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, LongType

import json

from spark_scripts.mfi_to_s3 import create_spark_context, download_api_data, process_data


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class TestScript(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.spark = SparkSession.builder.appName("MyApp").getOrCreate()

    
    def test_download_api_data(self):
        mock_response = MockResponse('{"success": true}', 200)

        patcher = patch('requests.get', return_value=mock_response)
        patcher.start()
        
        download_api_data(self.spark, "tmp")
        
        with open('tmp/api_data.json', 'r') as f:
            actual_contents = f.read()
            
        assert json.loads(actual_contents) == '{"success": true}'
        patcher.stop()
    
    
    def test_process_data(self):
        # Load the sample JSON data into a DataFrame
        template_data = {
                        "meta": {"fund_house": "Franklin Templeton Mutual Fund", 
                                  "scheme_type": "Open Ended Schemes", 
                                  "scheme_category": "Other Scheme - FoF Overseas", 
                                  "scheme_code": 118550, 
                                  "scheme_name": "Franklin India Feeder - Franklin U S Opportunities Fund - Direct - IDCW "},
                        "data": [{"date": "26-12-2023", "nav": "63.50720"}, {"date": "22-12-2023", "nav": "63.27370"}]
                        }
        
        with open(f"tmp/api_data.json", "w") as data_file:
            json.dump(template_data, data_file)
        
        
        df = self.spark.read.format("json") \
                .option("inferSchema", "true") \
                .load(f"tmp/api_data.json")
        
        # Call the method under test
        processed_df = process_data(df, out_dir="tmp", debug=True)

        # Define the overall schema
        expected_schema = StructType([
            StructField("date", StringType(), nullable=True),
            StructField("nav", StringType(), nullable=True),
            StructField("fund_house", StringType(), nullable=True),
            StructField("scheme_category", StringType(), nullable=True),
            StructField("scheme_code", LongType(), nullable=True),
            StructField("scheme_name", StringType(), nullable=True),
            StructField("scheme_type", StringType(), nullable=True)
        ])
        
        self.assertEqual(expected_schema, processed_df.schema)