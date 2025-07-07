import requests
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType

# Azure Identity imports for Key Vault access
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# 1. Read Databricks API token from Azure Key Vault

# Key Vault details
key_vault_name = "<your-keyvault-name>"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

# Secret name where token is stored
secret_name = "<your-databricks-token-secret-name>"

# Authenticate with Azure (will use managed identity or environment configured credentials)
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Get the secret (Databricks token)
retrieved_secret = client.get_secret(secret_name)
databricks_token = retrieved_secret.value

# 2. Call Databricks API to read catalogs

DATABRICKS_INSTANCE = "https://<your-databricks-instance>.cloud.databricks.com"
url = f"{DATABRICKS_INSTANCE}/api/2.1/unity-catalog/catalogs"

headers = {
    "Authorization": f"Bearer {databricks_token}"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Databricks API failed with status {response.status_code}: {response.text}")

catalogs_json = response.json().get("catalogs", [])

# 3. Convert JSON to Spark DataFrame

spark = SparkSession.builder.getOrCreate()

schema = StructType([
    StructField("name", StringType(), True),
    StructField("comment", StringType(), True),
    StructField("owner", StringType(), True),
    StructField("metastore_id", StringType(), True),
    StructField("catalog_type", StringType(), True),
])

catalogs_data = [
    (
        c.get("name"),
        c.get("comment"),
        c.get("owner"),
        c.get("metastore_id"),
        c.get("catalog_type"),
    ) for c in catalogs_json
]

df_catalogs = spark.createDataFrame(catalogs_data, schema)
df_catalogs.show(truncate=False)
