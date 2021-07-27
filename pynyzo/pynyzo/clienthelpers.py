"""
Helpers when dealing with Nyzo web clients
Defaults to client.nyzo.co

Most dupped from Nyzocli since it's likely to be required by more apps.
"""

from requests import get
import re
from time import time, sleep
from asyncio import sleep as async_sleep
from typing import Union, Tuple
from nyzostrings.nyzostringencoder import NyzoStringEncoder
from nyzostrings.nyzostringtransaction import NyzoStringTransaction
from nyzostrings.nyzostringpublicidentifier import NyzoStringPublicIdentifier
from pynyzo.keyutil import KeyUtil
from pynyzo.transaction import Transaction


class NyzoClient:

    def __init__(self, client: str="https://client.nyzo.co"):
        self.client = client

    def get_frozen(self):
        """Helper to fetch frozen edge from a client"""
        data = {}
        try:
            url = "{}/frozenEdge".format(self.client)
            res = get(url)
            data = self.fake_table_frozen_to_dict(res.text)
        except Exception as e:
            print(f"get_frozen, exception {e}")
        return data

    @staticmethod
    def fake_table_to_list(html: str):
        #
        test_header = re.search(r'<div class="header-row">([^"]*)</div><div class="data-row">', html)
        headers = []
        if test_header:
            headers = test_header.groups()[0].replace('<div>', '').split("</div>")[:-1]  # closing /div
        test_content = re.search(r'<div class="data-row">(.*)</div></div></div>', html)
        try:
            error_content = re.search(r'<p class="error">(.*)</p>', html).groups()[0]
        except Exception:
            error_content = None
        try:
            notice_content = re.search(r'<p class="notice">([^"]*)</p>', html).groups()
        except Exception:
            notice_content = []
        values = []
        if test_content:
            content = test_content.groups()[0].replace('<div>', '')\
                .replace('<div class="extra-wrap">', '') \
                .replace('<div class="data-row">', '') \
                .split("</div>")
            while len(content) >= len(headers):
                part = content[0:len(headers)]
                content = content[len(headers)+1:]
                temp = dict(zip(headers, part))
                if error_content:
                    temp["error"] = error_content
                temp["notice"] = notice_content
                values.append(temp)
        else:
            values = [{"notice": notice_content}]
            if error_content:
                values[0]["error"] = error_content
        return values

    @staticmethod
    def fake_table_frozen_to_dict(html: str):
        """Neither clean nor future proof, but that's the way client sends back the data"""
        try:
            height = re.search(r'<div>height</div><div>([^<]*)</div>', html).groups()[0]
        except Exception:
            height = 0
        try:
            the_hash = re.search(r'<div>hash</div><div[^>]*>([^<]*)</div>', html).groups()[0]
        except Exception:
            the_hash = b''
        try:
            timestamp = re.search(r'<div>verification timestamp \(ms\)</div><div>([^<]*)</div>', html).groups()[0]
        except Exception:
            timestamp = 0
        try:
            distance = re.search(r'<div>distance from open edge</div><div>([^<]*)</div>', html).groups()[0]
        except Exception:
            distance = 0
        values = {"height": int(height), "hash": the_hash.replace('-', ''),
                  "timestamp": timestamp, "distance": distance}
        return values

    @staticmethod
    def normalize_address(address: str, as_hex: bool = False) -> Union[Tuple[str, str], Tuple[str, bytes]]:
        """Takes an address as raw byte or id__ and provides both formats back"""
        try:
            # convert recipient to raw if provided as id__
            if address.startswith("id__"):
                address_raw = NyzoStringEncoder.decode(address).get_bytes().hex()
            else:
                raise RuntimeWarning("Not an id__")
        except Exception:
            address_raw = re.sub(r"[^0-9a-f]", "", address.lower())
            # print(address_raw)
            if len(address_raw) != 64:
                raise ValueError("Wrong address format. 64 bytes as hex or id_ nyzostring required")
            address = NyzoStringEncoder.encode(NyzoStringPublicIdentifier.from_hex(address_raw))
        # Here we should have both recipient and recipient_raw in all cases.
        if as_hex:
            return address, address_raw
        else:
            return address, bytes.fromhex(address_raw)

    def send(self, recipient: str, amount: float = 0, data: str = "", key_: str = ""):
        """
        Send Nyzo with data string to a RECIPIENT.
        """
        if key_ == "":
            raise ValueError("Need a key_")
        seed = NyzoStringEncoder.decode(key_).get_bytes()
        # convert key to address
        address = KeyUtil.private_to_public(seed.hex())

        recipient, recipient_raw = self.normalize_address(recipient, as_hex=True)
        frozen = self.get_frozen()
        # print (f"Sending {amount} to {recipient} since balance of {address} is > {above}.")
        # print(f"Frozen edge is at {frozen['height']}")
        # Create a tx
        timestamp = int(time() * 10) * 100 + 10000  # Fixed 10 sec delay for inclusion
        # print(timestamp, hex(timestamp))
        data_bytes = data[:32].encode("utf-8")
        transaction = Transaction(buffer=None, type=Transaction.type_standard, timestamp=timestamp,
                                  sender_identifier=bytes.fromhex(address), amount=int(amount * 1e6),
                                  receiver_identifier=bytes.fromhex(recipient_raw),
                                  previous_block_hash=bytes.fromhex(frozen["hash"]),
                                  previous_hash_height=frozen['height'],
                                  signature=b'', sender_data=data_bytes)
        # print(transaction.to_json())
        key, _ = KeyUtil.get_from_private_seed(seed.hex())
        to_sign = transaction.get_bytes(for_signing=True)
        sign = KeyUtil.sign_bytes(to_sign, key)
        tx = NyzoStringTransaction(Transaction.type_standard, timestamp, int(amount * 1e6),
                                   bytes.fromhex(recipient_raw),
                                   frozen['height'],
                                   bytes.fromhex(frozen["hash"]),
                                   bytes.fromhex(address), data_bytes,
                                   sign)
        tx__ = NyzoStringEncoder.encode(tx)
        # Send the tx
        url = "{}/forwardTransaction?transaction={}&action=run".format(self.client, tx__)
        res = get(url)
        # print(res.text)
        temp = self.fake_table_to_list(res.text)
        # print(temp)
        temp = temp[0]
        # Add tx to data
        temp["tx__"] = tx__
        return temp

    def safe_send(self, recipient: str, amount: float = 0, data: str = "", key_: str = "", max_tries=5, verbose=False):
        """
        Send Nyzo with data string to a RECIPIENT.
        Returns only after block is frozen or max_tries
        """
        attempt = 1
        while attempt <= max_tries:
            if verbose:
                print(f"Sending, try {attempt}")
            frozen = int(self.get_frozen().get('height', 0))
            res = self.send(recipient, amount, data, key_)
            # print(res)
            notice = res.get("notice", ("",))
            may_not_be_approved = "may not be approved" in notice[0] if len(notice) else False
            # print(may_not_be_approved)
            if str(res.get("forwarded", "false")).lower() == "false":
                if verbose:
                    print(f"Not forwarded")
                error = res.get("error", [])
                sent = {"sent": False, "try": attempt, "error": error, "notice": notice}
                return sent
            # Was forwarded, wait for freeze.
            while frozen < int(res['block height']):
                if verbose:
                    print(f"Waiting for frozen edge ({frozen}) to reach {res['block height']}")
                sleep(10)
                frozen = int(self.get_frozen().get('height', 0))
            print(f"Frozen edge is now {frozen}, querying tx")
            res_tx = self.query_tx(res['tx__'])
            if int(res_tx.get("height", 0)) == int(res['block height']):
                # transaction was frozen, return
                sent = {"sent": True, "height": int(res['block height']), "tx__": res['tx__'], "try": attempt}
                return sent
            if may_not_be_approved:
                error = res.get("error", [])
                sent = {"sent": False, "try": attempt, "error": error, "notice": notice}
                return sent
            attempt += 1
        sent = {"sent": False, "try": max_tries, "error": "",
                "notice": f"Forwarded but still not in chain after {max_tries} attempts."}
        return sent

    async def async_safe_send(self, recipient: str, amount: float = 0, data: str = "", key_: str = "",
                              max_tries=5, verbose=False):
        """
        Send Nyzo with data string to a RECIPIENT.
        Returns only after block is frozen or max_tries
        Async version
        """
        attempt = 1
        while attempt <= max_tries:
            if verbose:
                print(f"Sending, try {attempt}")
            frozen = int(self.get_frozen().get('height', 0))
            res = self.send(recipient, amount, data, key_)
            notice = res.get("notice", ("",))
            may_not_be_approved = "may not be approved" in notice[0] if len(notice) else False
            if str(res.get("forwarded", "false")).lower() == "false":
                if verbose:
                    print(f"Not forwarded")
                error = res.get("error", [])
                sent = {"sent": False, "try": max_tries, "error": error, "notice": notice}
                return sent
            # Was forwarded, wait for freeze.
            while frozen < int(res['block height']):
                if verbose:
                    print(f"Waiting for frozen edge ({frozen}) to reach {res['block height']}")
                await async_sleep(10)
                frozen = int(self.get_frozen().get('height', 0))
            print(f"Frozen edge is now {frozen}, querying tx")
            res_tx = self.query_tx(res['tx__'])
            if int(res_tx.get("height", 0)) == int(res['block height']):
                # transaction was frozen, return
                sent = {"sent": True, "height": int(res['block height']), "tx__": res['tx__'], "try": attempt}
                return sent
            if may_not_be_approved:
                error = res.get("error", [])
                sent = {"sent": False, "try": attempt, "error": error, "notice": notice}
                return sent
            attempt += 1
        sent = {"sent": False, "try": max_tries, "error": "",
                "notice": f"Forwarded but still not in chain after {max_tries} attempts."}
        return sent

    def query_tx(self, tx_: str = ""):
        """
        Query for a given tx__ (nyzostring) on chain.
        """
        url = "{}/transactionSearch?string={}&action=run".format(self.client, tx_)
        res = get(url)
        temp = self.fake_table_to_list(res.text)
        # print("temp", temp)
        return temp[0]
