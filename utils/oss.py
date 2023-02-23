# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            :
"""

import oss2


class OssClient:
    """
    阿里云oss客户端
    """

    def __init__(self, endpoint, access_key, secret_access, bucket_name):
        self.bucket_name = bucket_name
        auth = oss2.Auth(access_key, secret_access)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def put_object(self, key, video_name):
        """
        上传文件
        """
        put_result = self.bucket.put_object_from_file(key, video_name)
        if put_result.status == 200:
            return True
        return False

    def object_keys(self, prefix=''):
        """
        获取object keys
        """
        res_key = []
        for item in oss2.ObjectIterator(self.bucket, prefix=prefix):
            res_key.append(item.key)
        return res_key

    def oss_url(self, key):
        return f"oss://{self.bucket_name}/{key}"
