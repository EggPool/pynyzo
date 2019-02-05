"""
NYZO
Get status test script
"""

import argparse
import sys

sys.path.append('../')
from pynyzo.messagetype import MessageType
from pynyzo.message import Message
from pynyzo.messageobject import EmptyMessageObject
# from pynyzo.messages.statusresponse import StatusResponse
from pynyzo.messages.blockrequest import BlockRequest
from pynyzo.connection import Connection
from pynyzo.helpers import tornado_logger
import pynyzo.config as config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Nyzo test')
    parser.add_argument("-I", "--ip", type=str, default='127.0.0.1', help="IP to query (default 127.0.0.1)")
    parser.add_argument("-v", "--verbose", action="count", default=False, help='Be verbose.')
    parser.add_argument("-a", "--action", type=str, default='status', help='Action (status, block)')
    args = parser.parse_args()

    app_log = tornado_logger()

    config.load()

    connection = Connection(args.ip, app_log=app_log, verbose=args.verbose)

    if args.action == 'status':
        empty = EmptyMessageObject(app_log=app_log)
        message = Message(MessageType.StatusRequest17, empty, app_log=app_log)
        res = connection.fetch(message)
        print(res.to_json())
    elif args.action == 'block':
        # test. Use a block high enough so it's not frozen.
        # TODO: get last block from  reference verifiers
        request = BlockRequest(start_height=1695400, end_height=1695400+2, include_balance_list=True, app_log=app_log)
        message = Message(MessageType.BlockRequest11, request, app_log=app_log)
        res = connection.fetch(message)
        print(res.to_json())


