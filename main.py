import csv
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any
import time

@dataclass
class Contract:
    address: str
    chain_id: str
    name: str = ""
    owner_project: str = ""
    usage_category: str = ""
    deployment_tx: str = ""
    deployer_address: str = ""
    deployment_date: str = ""
    verified_status: bool = False
    is_proxy_contract: bool = False
    proxy_address: str = ""
    implementation_address: str = ""
    source_repo_url: str = ""
    origin_key: str = ""

@dataclass
class BlockscoutResponse:
    address: str = ""
    name: str = ""
    is_verified: bool = False
    is_fully_verified: bool = False
    is_partially_verified: bool = False
    is_verified_via_sourcify: bool = False
    sourcify_repo_url: str = ""
    minimal_proxy_address_hash: str = ""
    compiler_version: str = ""
    evm_version: str = ""
    optimizer: str = ""
    verified_at: str = ""
    additional_fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.additional_fields = {}

    def __init__(self, **kwargs):
        self.__post_init__()  # Ensure additional_fields is initialized
        fields = set(field.name for field in self.__dataclass_fields__.values())
        for key, value in kwargs.items():
            if key in fields:
                setattr(self, key, value)
            else:
                self.additional_fields[key] = value

@dataclass
class ProcessingStats:
    total_contracts: int = 0
    processed_count: int = 0
    contracts_with_name: int = 0
    proxy_contracts: int = 0
    elapsed_time: str = ""

BLOCKSCOUT_APIS = {
    "optimism": "https://optimism.blockscout.com/api/v2/smart-contracts/",
    "polygon_zkevm": "https://zkevm.blockscout.com/api/v2/smart-contracts/",
    "mode": "https://explorer.mode.network/api/v2/smart-contracts/",
    "arbitrum": "https://arbitrum.blockscout.com//api/v2/smart-contracts/",
    "zora": "https://explorer.zora.energy/api/v2/smart-contracts/",
    "base": "https://base.blockscout.com/api/v2/smart-contracts/",
    "zksync_era": "https://zksync.blockscout.com/api/v2/smart-contracts/",
    "linea": "https://explorer.linea.build/api/v2/smart-contracts/",
    "redstone": "https://explorer.redstone.xyz/api/v2/smart-contracts/",
}

CHAIN_ID_MAP = {
    "optimism": "eip155-10",
    "polygon_zkevm": "eip155-1101",
    "mode": "eip155-34443",
    "arbitrum": "eip155-42161",
    "zora": "eip155-7777777",
    "base": "eip155-8453",
    "zksync_era": "eip155-324",
    "linea": "eip155-59144",
    "redstone": "eip155-17001",
}

def process_csv(file_path: str) -> List[Contract]:
    contracts = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            address = row['encode']
            if not address.startswith('0x'):
                address = '0x' + address
            contract = Contract(
                address=address,
                origin_key=row['origin_key'],
                chain_id=row['origin_key']  # Set ChainID to OriginKey for now
            )
            contracts.append(contract)
    return contracts

def fetch_blockscout_data(api_url: str, address: str) -> BlockscoutResponse:
    url = api_url + address
    max_retries = 3
    retry_delay = 1

    for _ in range(max_retries):
        response = requests.get(url)
        if response.status_code == 200:
            return BlockscoutResponse(**response.json())
        elif response.status_code == 404:
            raise ValueError("Contract not found")
        time.sleep(retry_delay)

    raise Exception(f"Failed to fetch data after {max_retries} retries")

def map_blockscout_to_open_labels(contract: Contract, blockscout_data: BlockscoutResponse) -> Contract:
    contract.name = blockscout_data.name
    contract.verified_status = any([
        blockscout_data.is_verified,
        blockscout_data.is_fully_verified,
        blockscout_data.is_partially_verified,
        blockscout_data.is_verified_via_sourcify
    ])
    contract.source_repo_url = blockscout_data.sourcify_repo_url

    contract.is_proxy_contract = bool(blockscout_data.minimal_proxy_address_hash)
    contract.proxy_address = blockscout_data.minimal_proxy_address_hash
    contract.implementation_address = blockscout_data.minimal_proxy_address_hash

    if not contract.is_proxy_contract:
        if 'proxy' in contract.name.lower() or 'erc1967' in contract.name.lower():
            contract.is_proxy_contract = True

    contract.chain_id = CHAIN_ID_MAP.get(contract.origin_key, contract.chain_id)

    if blockscout_data.verified_at:
        contract.deployment_date = blockscout_data.verified_at

    return contract

def process_contract(contract: Contract) -> Contract:
    api_url = BLOCKSCOUT_APIS.get(contract.origin_key)
    if not api_url:
        print(f"Unknown origin key for contract {contract.address}: {contract.origin_key}")
        return contract

    try:
        blockscout_data = fetch_blockscout_data(api_url, contract.address)
        return map_blockscout_to_open_labels(contract, blockscout_data)
    except ValueError:
        print(f"Contract not found on Blockscout for {contract.address} on {contract.origin_key}")
    except Exception as e:
        print(f"Error processing contract {contract.address}: {str(e)}")

    return contract

def process_contracts(contracts: List[Contract], max_queries: int = 0) -> (List[Contract], ProcessingStats):
    processed_contracts = []
    stats = ProcessingStats(total_contracts=len(contracts))
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_contract = {executor.submit(process_contract, contract): contract for contract in contracts[:max_queries or len(contracts)]}
        for future in as_completed(future_to_contract):
            contract = future.result()
            processed_contracts.append(contract)
            stats.processed_count += 1
            if contract.name:
                stats.contracts_with_name += 1
            if contract.is_proxy_contract:
                stats.proxy_contracts += 1
            stats.elapsed_time = f"{time.time() - start_time:.2f} seconds"
            print(f"Processed {stats.processed_count}/{stats.total_contracts} contracts")

    return processed_contracts, stats

def main():
    # Example usage
    csv_file_path = '/Users/ahoura/Desktop/unlabelled.csv'
    contracts = process_csv(csv_file_path)
    processed_contracts, stats = process_contracts(contracts, max_queries=2153)  # Process up to 100 contracts

    # Print stats
    print(json.dumps(asdict(stats), indent=2))

    # Save processed contracts to a JSON file
    with open('processed_contracts.json', 'w') as f:
        json.dump([asdict(c) for c in processed_contracts], f, indent=2)

if __name__ == "__main__":
    main()