from google.cloud import storage 
import json
import gzip
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


class BaseExtractor:
    """
        This class is base for phase extractor all sources.
    """


    def __init__(self, bucket_name: str):
        load_dotenv()
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)


    def list_file(self, folder_name):
        """
        Lists all blobs (files) within a specific folder in the bucket.

        Args:
            folder_name (str): The prefix (folder path) of a blob.
        """
        
        blobs = self.client.list_blobs(self.bucket, prefix= folder_name) #create a list of blobs
        file_path = []

        for i in blobs:
            if not i.name.endswith('/'): # Filter out folder objects, keep only files
                file_path.append(i.name)
        return  file_path
    

    def extract_json_file(self, blob_path: str):
        # Get file
        blob = self.bucket.blob(blob_path)

        #Download as byte
        compressed_data = blob.download_as_bytes()
        decompressed_data = gzip.decompress(compressed_data)

        #Parse Json -> Table data
        data = json.loads(decompressed_data.decode("utf-8"))
        return data

