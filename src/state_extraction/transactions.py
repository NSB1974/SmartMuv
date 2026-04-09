import requests
from configparser import ConfigParser
from urllib.parse import urlencode

config = ConfigParser()
config.read("config.ini")
tx_limit = int(config.get('transactions', 'tx_limit'))


def get_transactions(cont_addr, transactions, endpoint, api_key):
    page = 1
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    while len(transactions) < tx_limit:
        try:
            response = requests.get(endpoint.format(cont_addr, page, api_key), headers=headers).json()
            if response["status"] == "1":
                txs = response["result"]
                if len(txs) == 0:
                    break
                transactions.extend(txs)
                page += 1
            else:
                # print(response["message"])
                break
        except requests.exceptions.RequestException as e:
            print("Error occurred:", e)
            break
    print(f"Total transactions downloaded: {len(transactions)}")
    return transactions


def get_internal_transactions(cont_addr, transactions, endpoint, api_key):
    page = 1
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    while len(transactions) < tx_limit:
        try:
            response = requests.get(endpoint.format(cont_addr, page, api_key), headers=headers).json()
            if response["status"] == "1":
                txs = response["result"]
                if len(txs) == 0:
                    break
                transactions.extend(txs)
                page += 1
            else:
                # print(response["message"])
                break
        except requests.exceptions.RequestException as e:
            print("Error occurred:", e)
            break
    print(f"Total internal txs downloaded: {len(transactions)}")
    return transactions


def _normalize_blockscout_tx(tx):
    """Normalize a Blockscout v2 transaction to match the Etherscan response format
    expected by state_extractor.py (flat 'from', 'to', 'input' fields)."""
    normalized = {
        'hash': tx.get('hash', ''),
        'input': tx.get('raw_input', '0x'),
        'value': tx.get('value', '0'),
        'from': tx.get('from', {}).get('hash', '') if isinstance(tx.get('from'), dict) else tx.get('from', ''),
        'to': tx.get('to', {}).get('hash', '') if isinstance(tx.get('to'), dict) else tx.get('to', ''),
        'blockNumber': str(tx.get('block_number', '')),
        'timeStamp': tx.get('timestamp', ''),
        'gas': str(tx.get('gas_limit', '')),
        'gasUsed': str(tx.get('gas_used', '')),
        'gasPrice': str(tx.get('gas_price', '')),
        'isError': '0' if tx.get('result') == 'success' else '1',
        'nonce': str(tx.get('nonce', '')),
    }
    return normalized


def get_blockscout_transactions(cont_addr, transactions, endpoint, api_key):
    """Fetch transactions from the Blockscout v2 API with cursor-based pagination."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    params = {}
    if api_key:
        params['apikey'] = api_key

    while len(transactions) < tx_limit:
        try:
            url = endpoint + ('&' if '?' in endpoint else '?') + urlencode(params) if params else endpoint
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            if not items:
                break
            for tx in items:
                transactions.append(_normalize_blockscout_tx(tx))
            next_page = data.get('next_page_params')
            if not next_page:
                break
            params.update(next_page)
            if api_key:
                params['apikey'] = api_key
        except requests.exceptions.RequestException as e:
            print("Error occurred:", e)
            break
    print(f"Total transactions downloaded: {len(transactions)}")
    return transactions


def get_blockscout_internal_transactions(cont_addr, transactions, endpoint, api_key):
    """Fetch internal transactions from the Blockscout v2 API with cursor-based pagination."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    params = {}
    if api_key:
        params['apikey'] = api_key

    while len(transactions) < tx_limit:
        try:
            url = endpoint + ('&' if '?' in endpoint else '?') + urlencode(params) if params else endpoint
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            if not items:
                break
            for tx in items:
                transactions.append(_normalize_blockscout_tx(tx))
            next_page = data.get('next_page_params')
            if not next_page:
                break
            params.update(next_page)
            if api_key:
                params['apikey'] = api_key
        except requests.exceptions.RequestException as e:
            print("Error occurred:", e)
            break
    print(f"Total internal txs downloaded: {len(transactions)}")
    return transactions
