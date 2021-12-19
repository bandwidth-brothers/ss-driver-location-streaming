
KINESIS_DEFAULT_RECORDS_PER_REQUEST: int = 100
KINESIS_DEFAULT_STREAM_NAME: str = 'DriverLocationStream'
KINESIS_DEFAULT_DELAY: float = 0.2
KINESIS_DEFAULT_FAILURE_DIR = './tmp/kinesis/failures'
KINESIS_DEFAULT_FAILURE_MAX_FILE_SIZE_MB = 25
KINESIS_DYNAMODB_FAILURE_TABLE_NAME = "DriverLocationKinesisFailure"

PRODUCER_DEFAULT_MAX_THREADS: int = 10
PRODUCER_DEFAULT_BUFFER_SIZE: int = 2000
PRODUCER_DEFAULT_DELAY: float = 0.0

GEO_DEFAULT_DATA_DIR: str = "./tmp"
GEO_DEFAULT_METERS_PER_PING: int = 20
GEO_DEFAULT_POINTS_DIR: str = "points"
GEO_DEFAULT_MAPS_DIR: str = "maps"
GEO_MAX_MARKERS: int = 40
