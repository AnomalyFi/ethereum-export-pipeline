from ethereumetl.utils import split_to_batches

# The below partitioning tries to make each partition of equal size.
# The first million blocks are in a single partition.
# The next 3 million blocks are in 100k partitions.
# The next 1 million blocks are in 10k partitions.
# Note that there is a limit in Data Pipeline on the number of objects, which can be
# increased in the Support Center
# https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-limits.html
EXPORT_PARTITIONS = [(start, end) for start, end in split_to_batches(9000000, 9999999, 1000)] + \
                    [(start, end) for start, end in split_to_batches(10000000, 10999999, 1000)] 


DEFAULT_BUCKET = "example.com"

EXPORT_BLOCKS_AND_TRANSACTIONS = True
EXPORT_RECEIPTS_AND_LOGS = True
EXPORT_CONTRACTS = False
EXPORT_TOKEN_TRANSFERS = False
EXPORT_TOKENS = False

IS_GETH = False

if IS_GETH:
    IPC_PATH = 'https://node.anomalyfi.com'
else:
    IPC_PATH = 'https://node.anomalyfi.com'
    

SETUP_COMMAND = \
    "cd /home/ec2-user/ethereum-etl && IPC_PATH={} && ".format(IPC_PATH) + \
    "PADDED_START=`printf \"%08d\" $1` && PADDED_END=`printf \"%08d\" $2`"

EXPORT_BLOCKS_AND_TRANSACTIONS_COMMAND = SETUP_COMMAND + ' && ' + \
    "python3 ethereumetl.py export_blocks_and_transactions -s $1 -e $2 -p $IPC_PATH -w 1 " + \
    "--blocks-output ${OUTPUT1_STAGING_DIR}/blocks_${PADDED_START}_${PADDED_END}.csv --transactions-output ${OUTPUT2_STAGING_DIR}/transactions_${PADDED_START}_${PADDED_END}.csv"

EXPORT_RECEIPTS_AND_LOGS_COMMAND = SETUP_COMMAND + ' && ' + \
    "python3 ethereumetl.py export_receipts_and_logs -s $1 -e $2 -p $IPC_PATH -w 1 " + \
    "--receipts-output ${OUTPUT1_STAGING_DIR}/receipts_${PADDED_START}_${PADDED_END}.csv --logs-output ${OUTPUT2_STAGING_DIR}/logs_${PADDED_START}_${PADDED_END}.csv && " 
    

EXPORT_CONTRACTS_COMMAND = SETUP_COMMAND + ' && ' + \
    "python3 ethereumetl.py extract_csv_column -i ${INPUT1_STAGING_DIR}/receipts_${PADDED_START}_${PADDED_END}.csv -o ${OUTPUT1_STAGING_DIR}/contract_addresses.csv.temp -c contract_address && " + \
    "python3 ethereumetl.py export_contracts --contract-addresses ${OUTPUT1_STAGING_DIR}/contract_addresses.csv.temp -p $IPC_PATH -w 1 " + \
    "--output ${OUTPUT1_STAGING_DIR}/contracts_${PADDED_START}_${PADDED_END}.csv && " + \
    "rm -f ${OUTPUT1_STAGING_DIR}/contract_addresses.csv.temp"

EXPORT_TOKEN_TRANSFERS_COMMAND = SETUP_COMMAND + ' && ' + \
    "python3 ethereumetl.py export_token_transfers -s $1 -e $2 -p $IPC_PATH -w 1 " + \
    "--output ${OUTPUT1_STAGING_DIR}/token_transfers_${PADDED_START}_${PADDED_END}.csv"

EXPORT_TOKENS_COMMAND = SETUP_COMMAND + ' && ' + \
    "python3 ethereumetl.py extract_csv_column -i ${INPUT1_STAGING_DIR}/token_transfers_${PADDED_START}_${PADDED_END}.csv -c token_address -o - | sort | uniq > ${OUTPUT1_STAGING_DIR}/token_addresses.csv.temp && " + \
    "python3 ethereumetl.py export_tokens --token-addresses ${OUTPUT1_STAGING_DIR}/token_addresses.csv.temp -p $IPC_PATH -w 5 " + \
    "--output ${OUTPUT1_STAGING_DIR}/tokens_${PADDED_START}_${PADDED_END}.csv && " + \
    "rm -f ${OUTPUT1_STAGING_DIR}/token_addresses.csv.temp"
