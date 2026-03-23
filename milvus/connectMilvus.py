# -*- coding: utf-8 -*-
from pymilvus import MilvusClient

URI = "https://in03-1851ecb2e488379.serverless.ali-cn-hangzhou.cloud.zilliz.com.cn"
API_KEY = "5ff61f05e3e185768526b3000b5793b3fe485e5e443b35950bbffe97376aac86c5b0a1f691290bd5f348a303f538d6513e8c70a0"
USER = "db_1851ecb2e488379"
PASSWORD = "Ws1996@1"


# 创建客户端（使用用户名密码认证）
client = MilvusClient(uri=URI, user=USER, password=PASSWORD)

# 测试连接：列出所有集合
collections = client.list_collections()
print("Collections:", collections)

