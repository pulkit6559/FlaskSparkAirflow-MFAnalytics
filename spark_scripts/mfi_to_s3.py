import requests
import json
from pyspark.sql import SparkSession, SQLContext
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql import functions as F
import os


def create_spark_context():
    conf = SparkConf()\
        .set("spark.jars.packages", "/usr/local/spark-3.5.0-bin-hadoop3/jars/aws-java-sdk-bundle-1.12.625.jar")\
        .set("spark.jars.packages", "/usr/local/spark-3.5.0-bin-hadoop3/jars/hadoop-aws-3.3.6.jar")\
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
        .set("com.amazonaws.services.s3.enableV4", True)\
        .set("spark.driver.extraJavaOptions", "-Dcom.amazonaws.services.s3.enableV4=true")\
        .set("spark.hadoop.fs.s3a.path.style.access", True)

    sc = SparkContext(conf=conf).getOrCreate()
    
    hadoop_conf = sc._jsc.hadoopConfiguration()
    hadoop_conf.set("fs.s3a.access.key", sc.getConf().get("spark.executorEnv.AWS_ACCESS_KEY_ID"))
    hadoop_conf.set("fs.s3a.secret.key", sc.getConf().get("spark.executorEnv.AWS_SECRET_ACCESS_KEY"))
    hadoop_conf.set("fs.s3a.endpoint", f"s3.{sc.getConf().get('spark.executorEnv.AWS_DEFAULT_REGION')}.amazonaws.com")
    hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    
    spark = SparkSession(sc).builder.getOrCreate()
    
    return spark


def download_api_data(spark, pth="/local_files"):
    response = requests.get("https://api.mfapi.in/mf/118550")
    data = response.json()
    json_formatted = json.dumps(data)

    with open(f"{pth}/api_data.json", "w") as data_file:
        data_file.write(json_formatted)
    
    raw_json_dataframe = spark.read.format("json") \
        .option("inferSchema", "true") \
        .load(f"{pth}/api_data.json")

    return raw_json_dataframe

def process_data(raw_json_dataframe, out_dir="s3a://iambucketnew/sparkoutputnew", debug=False):

    raw_json_dataframe.printSchema()
    raw_json_dataframe.createOrReplaceTempView("Mutual_benefit")

    dataframe = raw_json_dataframe.withColumn("data", F.explode(F.col("data"))) \
        .withColumn('meta', F.expr("meta")) \
        .select("data.*", "meta.*")
        
    if debug:
        return dataframe
    
    dataframe.show(10, False)
    dataframe.write.format('csv').option('header', 'true').save(f'{out_dir}/out', mode='overwrite')


if __name__ == "__main__":
    spark_context = create_spark_context()
    raw_json_dataframe = download_api_data(spark_context)
    process_data(raw_json_dataframe)
