terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = ">= 1.0.0"
    }
  }
}

provider "databricks" {
  # Databricks workspace host URL
  host  = "https://<your-databricks-instance>.azuredatabricks.net"
  
  # Databricks PAT token for authentication
  token = "<your-databricks-personal-access-token>"
}

resource "databricks_cluster" "my_cluster" {
  cluster_name            = "my-terraform-cluster"
  spark_version           = "13.2.x-scala2.12"       # Use an available runtime version
  node_type_id            = "Standard_DS3_v2"        # Pick Azure VM SKU
  autotermination_minutes = 20                       # Auto-terminate after 20 mins of inactivity
  num_workers             = 2

  autoscale {
    min_workers = 1
    max_workers = 3
  }

  spark_conf = {
    "spark.databricks.delta.preview.enabled" = "true"
  }
}
