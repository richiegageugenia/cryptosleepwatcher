import requests
import time
import json
import os
from datetime import datetime

ETHERSCAN_API = "https://api.ethplorer.io/getAddressTransactions/{}?apiKey=freekey"
BTC_API = "https://blockchain.info/rawaddr/{}"

MONITORED_ADDRESSES = {
    "ethereum": ["0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"],
    "bitcoin": ["1AJbsFZ64EpEfS5UAjAfcUG8pH8Jn3rn1F"]
}

LOG_FILE = "activity_log.json"
CHECK_INTERVAL = 60  # seconds

def load_previous():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def notify(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔔 {msg}")
    try:
        import platform
        if platform.system() == "Darwin":
            os.system(f"say '{msg}'")
        elif platform.system() == "Linux":
            os.system(f'paplay /usr/share/sounds/freedesktop/stereo/complete.oga')
        elif platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 500)
    except:
        pass

def check_eth_activity(address, previous):
    url = ETHERSCAN_API.format(address)
    resp = requests.get(url)
    if resp.status_code != 200:
        return previous.get(address, [])

    txs = resp.json()
    current_tx_hashes = [tx['hash'] for tx in txs]
    old_tx_hashes = previous.get(address, [])

    new_txs = [tx for tx in txs if tx['hash'] not in old_tx_hashes]
    if new_txs:
        notify(f"New ETH activity on {address}: {len(new_txs)} txs")
    return current_tx_hashes

def check_btc_activity(address, previous):
    url = BTC_API.format(address)
    resp = requests.get(url)
    if resp.status_code != 200:
        return previous.get(address, [])

    data = resp.json()
    current_tx_hashes = [tx['hash'] for tx in data['txs']]
    old_tx_hashes = previous.get(address, [])

    new_txs = [tx for tx in current_tx_hashes if tx not in old_tx_hashes]
    if new_txs:
        notify(f"New BTC activity on {address}: {len(new_txs)} txs")
    return current_tx_hashes

def main():
    print("🔍 Starting CryptoSleepWatcher...")
    previous_log = load_previous()

    while True:
        current_log = {}
        for eth_address in MONITORED_ADDRESSES['ethereum']:
            current_log[eth_address] = check_eth_activity(eth_address, previous_log)

        for btc_address in MONITORED_ADDRESSES['bitcoin']:
            current_log[btc_address] = check_btc_activity(btc_address, previous_log)

        save_log(current_log)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
