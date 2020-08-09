from abc import ABCMeta

import ibm_boto3
import json
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.storage import Storage
from . import settings
from decouple import config as envconfig
from ibm_botocore.client import Config, ClientCreator, ClientError
from django.utils.deconstruct import deconstructible
from django.core.management.utils import get_random_string


def transform(content):
    if type(content) == TemporaryUploadedFile:
        return content
    temp_file = NamedTemporaryFile(delete=False)
    for block in content.chunks():
        # If no more file then stop
        if not block:
            break
        # Write image block to temporary file
        temp_file.write(block)

    temp_file.flush()
    return temp_file


@deconstructible
class IbmStorage(Storage):
    cos = None

    def __init__(self, option=None):
        super();
        if not option:
            option = settings.DEFAULT_FILE_STORAGE
        self.cos = ibm_boto3.client(
            "s3",
            ibm_api_key_id=envconfig('COS_API_KEY_ID'),
            ibm_service_instance_id=envconfig('COS_INSTANCE_CRN'),
            config=Config(signature_version='oauth'),
            endpoint_url=envconfig('COS_ENDPOINT'),
        )

    def _save(self, name, content):
        try:
            new_file = transform(content)
            with open(new_file.name, "rb") as f:
                self.cos.upload_fileobj(f, envconfig("COS_BUCKET_IBM"), name)
            new_file.close()
            return name
        except FileNotFoundError:
            raise FileNotFoundError
        except Exception as e:
            raise Exception

    def open(self , name ,  mode="rb"):
        return self._open(name , mode)

    def _open(self, name, mode="rb"):
        try:
            new_file = NamedTemporaryFile(delete=False)
            with open(new_file.name , "wb") as data:
                self.cos.download_fileobj(Bucket=envconfig("COS_BUCKET_IBM"), Key=name, Fileobj=data)
            return new_file
        except Exception as e:
            print(Exception , e)
            raise Exception

    def url(self,name):
        return name

    def path(self, name):
        raise NotImplementedError("not available")

    def exists(self, name):
        try:
            self.cos.get_object(Bucket=envconfig("COS_BUCKET_IBM"), Key=name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                return False

    def delete(self, name):
        if self.exists(name):
            try:
                response = self.cos.delete_object(Bucket=envconfig("COS_BUCKET_IBM"), Key=name)
                print(response)
            except Exception as e:
                raise Exception
        return False

    def get_available_name(self, name, max_length=None):
        return self.get_valid_name(name)

    def get_valid_name(self, name):
        if not self.exists(name=name):
            return name
        else:
            return name + get_random_string(7)

    def listdir(self, path):
        raise NotImplementedError

    def size(self, name):
        raise NotImplementedError
