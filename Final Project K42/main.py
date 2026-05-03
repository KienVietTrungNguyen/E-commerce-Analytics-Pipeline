import os
from google.cloud import storage 
from dotenv import load_dotenv


load_dotenv()
os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

client = storage.Client()

bucket_name = "minpy"
bucket = client.bucket(bucket_name)
print(bucket)

#list file các file trong GCS ra:
for i in bucket.list_blobs():
    print(i.name)


