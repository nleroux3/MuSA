from dask.distributed import LocalCluster, Client

cluster = None
client = None

def close_cluster():
    global cluster, client
    if client is not None:
        client.close()
        client = None
    if cluster is not None:
        cluster.close()
        cluster = None

def start_cluster():
    global cluster, client

    cluster = LocalCluster(n_workers=40, threads_per_worker=1)
    client = Client(cluster)

    return client


