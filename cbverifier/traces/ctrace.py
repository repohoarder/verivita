""" Concrete trace data structure and parsing.


A concrete trace is represented as a forest, where each tree has
messages as nodes and leaves.

Assumptions:
  - all the roots must be callbacks.

"""

import logging
import json # for reading the traces from file
import re

import cbverifier.traces.tracemsg_pb2
from  cbverifier.traces.tracemsg_pb2 import TraceMsgContainer

# Read a message from Java's writeDelimitedTo:
import google.protobuf.internal.decoder as decoder


import tracemsg_pb2

class MalformedTraceException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class CMessage(object):
    """ Base class that represents a concrete message.
    """

    def __init__(self):
        self.message_id = -1
        self.thread_id = None
        self.signature = None
        self.method_name = None
        self.params = []
        self.return_value = None

        # messages called inside this message
        self.children = []

    def _print(self, stream, sep):
        stream.write("%s[%d] %s(" % (sep, self.message_id, self.signature))

        for i in range(len(self.params)):
            if (i != 0): stream.write(",")
            stream.write("%s" % self.params[i])
        stream.write(")\n")

        for child in self.children:
            child._print(stream, "  ")


class CCallback(CMessage):
    """ Represents a callback message
    """
    def __init__(self):
        super(CCallback, self).__init__()

        self.method_parameter_types = []
        self.overrides = []
        self.receiver_first_framework_super = []


class CCallin(CMessage):
    """ Represents a callin message
    """
    def __init__(self):
        super(CCallin, self).__init__()

class AppInfo(object):
    """ Info of the app."""
    def __init__(self, app_name):
        self.app_name = app_name


class CValue(object):
    """ Represent the concrete value of an object recorded in a
    concrete trace
    """
    def __init__(self, value_msg):
        # True if it is null
        self.is_null = value_msg.is_null
        # name of the type of the paramter
        self.type = value_msg.type
        # name of the first framework type of the parameter
        self.fmwk_type = value_msg.fmwk_type
        # Id of the object
        self.object_id = value_msg.object_id
        # Value of the object
        self.value = value_msg.value

        # at least one must be set
        assert (not ((self.is_null is None or not self.is_null) and
                     self.value is None and
                     self.object_id is None))


    def __repr__(self):
        #repr = ""
        def enc(value):
            if isinstance(value, str):
                return value
            elif isinstance(value, unicode):
                return value.encode('utf-8').strip()
            else:
                return str(value)

        repr = "[%s]" % ",".join([enc(self.value), enc(self.object_id),
                                  enc(self.is_null), enc(self.fmwk_type)])

        # if self.value is not None:
        #     repr = self.value
        # elif self.object_id is not None:
        #     repr = self.object_id
        # elif self.is_null is not None:
        #     if self.is_null:
        #         repr = "NULL"

        # if self.fmwk_type is not None and self.fmwk_type != "":
        #     repr = repr + " : " + self.fmwk_type

        return repr


class CTrace:
    def __init__(self):
        # forest of message trees
        self.children = []
        self.app_info = None


    def print_trace(self, stream):
        """ Print the trace """
        for child in self.children:
            child._print(stream, "")


class CTraceSerializer:
    """
    Utility functions used to create a trace that can be used by the
    verifier from a trace recorded by trace runner.


    Usage:
    trace = CTraceSerializer.read_trace(<trace_file))

    Exception types are not handled now (they should not be produced
    by TraceRunner.
    """

    @staticmethod
    def read_trace_file_name(trace_file_name):
        trace_file = open(trace_file_name, "rb")
        return CTraceSerializer.read_trace(trace_file)


    @staticmethod
    def read_trace(trace_file):
        trace = CTrace()

        reader = CTraceDelimitedReader(trace_file)
        message_stack = []
        for tm_container in reader:
            assert None != tm_container

            recorded_message = tm_container.msg

            if CTraceSerializer.is_app_message(recorded_message):
                # DO NOTHING for now
                # TODO: the APP type of message is NOT used as the
                # other types in the protobuf.
                # To be clarified with Shawn
                trace.app_info = trace.app_info
            if CTraceSerializer.is_entry_message(recorded_message):
                # create the trace message
                trace_message = CTraceSerializer.create_trace_message(recorded_message)
                message_stack.append(trace_message)
            else:
                assert CTraceSerializer.is_exit_message(recorded_message)
                # remove the message from the stack
                trace_message = message_stack.pop()

                # Check the signature to be the same as the recorded message

                # update trace_message with recorded_message
                CTraceSerializer.update_trace_message(trace_message, recorded_message)

                if (len(message_stack) == 0):
                    assert (isinstance(trace_message, CCallback))
                    trace.children.append(trace_message)
                else:
                    last_message = message_stack[len(message_stack)-1]

                    last_message.children.append(trace_message)

        assert len(message_stack) == 0
        return trace


    @staticmethod
    def is_app_message(msg):
        return TraceMsgContainer.TraceMsg.APP == msg.type

    @staticmethod
    def is_entry_message(msg):
        return (TraceMsgContainer.TraceMsg.CALLIN_ENTRY == msg.type or
                TraceMsgContainer.TraceMsg.CALLBACK_ENTRY == msg.type)

    @staticmethod
    def is_exit_message(msg):
        return (TraceMsgContainer.TraceMsg.CALLIN_EXIT == msg.type or
                TraceMsgContainer.TraceMsg.CALLBACK_EXIT == msg.type)

    @staticmethod
    def create_trace_message(msg):
        assert CTraceSerializer.is_entry_message(msg)

        trace_msg = None

        if (TraceMsgContainer.TraceMsg.CALLIN_ENTRY == msg.type):
            trace_msg = CCallin()
            ci = msg.callinEntry

            trace_msg.message_id = msg.message_id
            trace_msg.thread_id = msg.thread_id

            trace_msg.signature = ci.signature
            trace_msg.method_name = ci.method_name
            trace_msg.params = CTraceSerializer.get_params(ci.param_list)
            trace_msg.return_value = None
        elif (TraceMsgContainer.TraceMsg.CALLBACK_ENTRY == msg.type):
            trace_msg = CCallback()
            cb = msg.callbackEntry

            trace_msg.message_id = msg.message_id
            trace_msg.thread_id = msg.thread_id

            trace_msg.signature = cb.signature
            trace_msg.method_name = cb.method_name
            trace_msg.params = CTraceSerializer.get_params(cb.param_list)
            trace_msg.return_value = None

            for meth_type in cb.method_parameter_types:
                trace_msg.method_parameter_types.append(meth_type)

            trace_msg.method_returnType = cb.method_returnType

            # TODO: handle the overrides
            # for overrides in cb.framework_overrides:
            #     trace_msg.overrides.append(None)
            # trace_msg.receiver_first_framework_super = cb.receiver_first_framework_super
        else:
            err = "%s msg type cannot be used to create a node" % msg.type
            raise MalformedTraceException(err)

        return trace_msg


    @staticmethod
    def update_trace_message(trace_msg, msg):
        """ Update trace_msg with the exit message msg.

        The function assumes that msg is either a callin exit or a
        callback exit.

        The function assumes that msg is the exit message for
        trace_msg (an assertion fails if the name and signature of
        trace_msg and msg do not match
        """


        def check_malformed_trace(trace_msg, msg_exit, expected_class, expected_name):
            if (not isinstance(trace_msg, expected_class)):
                raise MalformedTraceException("Found %s for method %s, " \
                                              "while the last message in the stack " \
                                              "is of type %s\n" % (expected_name,
                                                                   msg_exit.method_name,
                                                                   str(type(trace_msg))))
            elif (not trace_msg.signature == msg_exit.signature):
                raise MalformedTraceException("Found exit for signature %s, " \
                                              "while expecting it for signature " \
                                              "%s\n" % (msg_exit.signature,
                                                        trace_msg.signature))
                # TODO: re-enable after fix in tracerunner
            #elif (not trace_msg.method_name == msg_exit.method_name):
                # raise MalformedTraceException("Found exit for method %s, " \
                #                               "while expecting it for method " \
                #                               "%s\n" % (msg_exit.method_name,
                #                                         trace_msg.method_name))

        def check_malformed_trace_msg(trace_msg, msg):
            if (trace_msg.thread_id != msg.thread_id):
                raise MalformedTraceException("Found thread id %d for " \
                                              "while the last message in the stack " \
                                              "has thread id %d\n" % (msg.thread_id,
                                                                      trace_msg.thread_id))


        assert CTraceSerializer.is_exit_message(msg)

        check_malformed_trace_msg(trace_msg, msg)
        if (TraceMsgContainer.TraceMsg.CALLIN_EXIT == msg.type):
            callin_exit = msg.callinExit

            check_malformed_trace(trace_msg, callin_exit, CCallin,
                                  "CALLIN_EXIT")

            trace_msg.return_value = CTraceSerializer.read_value_msg(callin_exit.return_value)
        elif (TraceMsgContainer.TraceMsg.CALLBACK_EXIT == msg.type):
            callback_exit = msg.callbackExit

            check_malformed_trace(trace_msg, callback_exit, CCallback,
                                  "CALLBACK_EXIT")

            trace_msg.return_value = CTraceSerializer.read_value_msg(callback_exit.return_value)
        else:
            err = "%s msg type cannot be used to update a node" % msg.type
            raise MalformedTraceException(err)


    @staticmethod
    def get_params(param_list):
        new_param_list = []
        for param in param_list:
            new_param_list.append(CTraceSerializer.read_value_msg(param))
        return new_param_list

    @staticmethod
    def read_value_msg(value_msg):
        value = CValue(value_msg)
        return value


class CTraceDelimitedReader(object):
    """
    Read a delimited stream containing trace messages.

    We have to do the hard work, since this does not seem supported
    for python ina clean way:

    https://github.com/google/protobuf/issues/54

    https://groups.google.com/forum/#!topic/protobuf/zjWySHr1L04
    parseDelimitedTo(),


    USAGE:
    ifile = open(protofile, "rb")
    reader = CTraceDelimitedReader(ifile)
    for m in reader:
      m is the message

    """
    def __init__(self,trace_file):
        # ISSUE: read all the data at once
        # limited by _DecodeVarint implementation
        self.data = trace_file.read()
        self.size = len(self.data)
        self.position = 0

    def __iter__(self):
        return self

    def next(self):
        """ Read a single trace msg container object from the input
        file.

        The input file is a fixed-size (?!) file, where each
        fixed-sized message
        """

        if (self.position >= self.size):
            raise StopIteration()

        (size, self.position) = decoder._DecodeVarint(self.data, self.position)

        raw_data = self.data[self.position:self.position + size]
        self.position = self.position + size

        trace_msg_container = tracemsg_pb2.TraceMsgContainer()
        trace_msg_container.ParseFromString(raw_data)

        if trace_msg_container == None:
            raise StopIteration()
        else:
            return trace_msg_container

