from base64 import standard_b64encode, standard_b64decode
import pickle
import sys

class RPC(object):
    def __init__(self, communicator):
        self.communicator = communicator
        self.handlers = {}

    def make_rpc_stub(self, func_name):
        def stub(*args):
            num_args = str(len(args))
            marshalled_args = [self.marshal(arg) for arg in args]
            rpc_call = ",".join([func_name, num_args] + marshalled_args)
            self.communicator.send(rpc_call)
            return self.receive_response(self.communicator.recv())
        return stub

    def register_rpc_handler(self, func_name, func):
        def handler(marshalled_args):
            args = map(self.unmarshal, marshalled_args)
            self.communicator.send(self.make_response(func(*args)))
        self.handlers[func_name] = handler

    def call_handler(self, rpc_call):
        pieces = rpc_call.split(",")
        func_name = pieces[0]
        num_args = int(pieces[1])
        marshalled_args = pieces[2:]
        try:
            assert len(marshalled_args) == num_args
        except AssertionError as e:
            self.communicator.send(self.make_error_response())
            return
        self.handlers[func_name](marshalled_args)

    def marshal(self, obj):
        return standard_b64encode("%s" % (pickle.dumps(obj),))

    def unmarshal(self, marshalled):
        return pickle.loads(standard_b64decode(marshalled))

    def make_response(self, obj):
        return self.marshal(obj)

    def make_error_response(self):
        return self.marshal("ERROR")
    
    def receive_response(self, response):
        return self.unmarshal(response)
