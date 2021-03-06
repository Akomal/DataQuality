
import pydeequ
from pydeequ.analyzers import *
from pydeequ.checks import *
from pydeequ.verification import *
from pyspark.sql import SparkSession
import io
from google.colab import files

spark = (SparkSession
    .builder
    .config("spark.jars.packages", pydeequ.deequ_maven_coord)
    .config("spark.jars.excludes", pydeequ.f2j_maven_coord)
    .getOrCreate())

data = files.upload()

data_file= spark.read.csv('heart.csv',header='true',inferSchema='true')

analysisResult = AnalysisRunner(spark) \
                    .onData(data_file) \
                    .addAnalyzer(Size()) \
                    .addAnalyzer(Completeness("RestingBP")) \
                    .addAnalyzer(Completeness("HeartDisease")) \
                    .addAnalyzer(Maximum("Cholesterol"))\
                    .run()

analysisResult_df = AnalyzerContext.successMetricsAsDataFrame(spark, analysisResult)
analysisResult_df.show()

check = Check(spark, CheckLevel.Warning, "Review Check")

checkResult = VerificationSuite(spark) \
    .onData(data_file) \
    .addCheck(
        check.isComplete("HeartDisease")  \
        .isUnique("Cholesterol")  \
        .isContainedIn("RestingECG", ["Normal", "ST", "LVH"])) \
    .run()

checkResult_df = VerificationResult.checkResultsAsDataFrame(spark, checkResult)
checkResult_df.show()
