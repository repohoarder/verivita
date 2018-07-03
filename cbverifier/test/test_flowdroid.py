""" Test the creation of the flowdroid model """

import sys
import logging
import unittest

from cbverifier.traces.ctrace import CTrace, CCallback, CCallin, CValue, CTraceException
from cbverifier.test.test_grounding import TestGrounding
from cbverifier.encoding.encoder import TSEncoder
from cbverifier.encoding.flowdroid_model.lifecycle_constants import Activity, Fragment
from cbverifier.encoding.flowdroid_model.flowdroid_model_builder import FlowDroidModelBuilder

from cStringIO import StringIO

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class TestFlowDroid(unittest.TestCase):

    def setUp(self):
        # Reset the obj id before each test
        self._obj_id_ = 0

    def get_obj_id(self):
        self._obj_id_ += 1
        return self._obj_id_

    def test_const_classes(self):
        """ Test the creation of ad-hoc classes used to lookup methods """

        inst_value = TestGrounding._get_obj("1","android.app.Activity")
        activity = Activity("android.app.Activity", inst_value)
        self.assertTrue(activity.has_methods_names(Activity.INIT))
        "[CB] [ENTRY] [l]  android.app.Activity <init>()" in activity.get_methods_names(Activity.INIT)

        inst_value = TestGrounding._get_obj("1","android.support.v4.app.FragmentActivity")
        activity = Activity("android.support.v4.app.FragmentActivity", inst_value)
        self.assertTrue(activity.has_methods_names(Activity.INIT))
        "[CB] [ENTRY] [l]  android.support.v4.app.FragmentActivity <init>()" in activity.get_methods_names(Activity.INIT)


    def _get_sample_trace(self):
        spec_list = []
        ctrace = CTrace()

        cb = CCallback(1, 1, "", "void android.app.Activity.<init>()",
                       [TestGrounding._get_obj("d8ad51d","android.app.Activity")],
                       None,
                       [TestGrounding._get_fmwkov("void android.app.Activity","<init>()", False)])
        ctrace.add_msg(cb)

        cb = CCallback(1, 1, "", "void android.app.Fragment.<init>()",
                       [TestGrounding._get_obj("eae2341","android.app.Fragment")],
                       None,
                       [TestGrounding._get_fmwkov("void android.app.Fragment","<init>()", False)])
        ctrace.add_msg(cb)

        ts_enc = TSEncoder(ctrace, spec_list)
        return ts_enc


    def test_component_construction(self):
        enc = self._get_sample_trace()
        fd_builder = FlowDroidModelBuilder(enc.trace, enc.gs.trace_map, set([]))

        # check that it finds the activity component
        components_set = fd_builder.get_components()
        self.assertTrue(2 == len(components_set))

        activity = None
        fragment = None
        for elem in components_set:
            if (isinstance(elem, Activity)):
                activity = elem
            if (isinstance(elem, Fragment)):
                fragment = elem
        self.assertTrue(activity is not None)
        self.assertTrue(fragment is not None)

        self.assertTrue(isinstance(activity, Activity))
        activity.has_methods_names(Activity.INIT)
        activity.has_trace_msg(Activity.INIT)
        trace_msg = activity.get_trace_msgs(Activity.INIT)
        self.assertTrue (isinstance(trace_msg, CCallin) or
                         isinstance(trace_msg, CCallback))

        self.assertTrue(isinstance(fragment, Fragment))
        fragment.has_methods_names(Fragment.INIT)
        fragment.has_trace_msg(Fragment.INIT)
        trace_msg = fragment.get_trace_msgs(Fragment.INIT)
        self.assertTrue (isinstance(trace_msg, CCallin) or
                         isinstance(trace_msg, CCallback))


    def test_cb_approx(self):
        # Attachment relation:
        #
        # activity_1
        # activity_2
        #
        trace = CTrace()
        (cb1, act1) = self._create_activity()
        (cb2, act2) = self._create_activity()
        trace.add_msg(cb1)
        trace.add_msg(cb2)

        fd = self._get_fdm(trace)

        # No "free messages"
        self.assertTrue(len(fd.free_msg) == 0)

        self.assertTrue(act1 in fd.compid2msg_keys)
        self.assertTrue(0 < fd.compid2msg_keys[act1])
        self.assertTrue(act2 in fd.compid2msg_keys)
        self.assertTrue(0 < fd.compid2msg_keys[act2])
        self.assertTrue(fd.compid2msg_keys[act1].isdisjoint(fd.compid2msg_keys[act2]))


    def test_fragment_in_act(self):
        # Attachment relation:
        #
        # activity_1
        #   frag1
        # activity_2
        #   frag2
        trace = CTrace()
        (cb1, act1) = self._create_activity()
        (cb2, act2) = self._create_activity()
        (cb3, frag1) = self._create_fragment()
        (cb3, frag2) = self._create_fragment()
        cb5 = self._attach_fragment_to_activity(act1, frag1)
        cb6 = self._attach_fragment_to_activity(act1, frag2)
        trace.add_msg(cb1)
        trace.add_msg(cb2)
        trace.add_msg(cb3)
        trace.add_msg(cb4)
        trace.add_msg(cb5)
        trace.add_msg(cb6)

        fd = self._get_fdm(trace)

        self.assertTrue(act1 in fd.compid2msg_keys)
        self.assertTrue(0 < fd.compid2msg_keys[act1])

        self.assertTrue(act2 in fd.compid2msg_keys)
        self.assertTrue(0 < fd.compid2msg_keys[act2])

        self.assertTrue(frag1 in fd.compid2msg_keys)
        self.assertTrue(0 < fd.compid2msg_keys[frag1])

        self.assertTrue(frag2 in fd.compid2msg_keys)
        self.assertTrue(0 < fd.compid2msg_keys[frag2])


        self.assertTrue(fd.compid2msg_keys[act1].isdisjoint(fd.compid2msg_keys[act2]))
        self.assertTrue(fd.compid2msg_keys[act1].isdisjoint(fd.compid2msg_keys[frag1]))
        self.assertTrue(fd.compid2msg_keys[act1].isdisjoint(fd.compid2msg_keys[frag2]))

        self.assertTrue(fd.compid2msg_keys[act2].isdisjoint(fd.compid2msg_keys[frag1]))
        self.assertTrue(fd.compid2msg_keys[act2].isdisjoint(fd.compid2msg_keys[frag2]))

        self.assertTrue(fd.compid2msg_keys[frag1].isdisjoint(fd.compid2msg_keys[frag2]))


    def _get_fdm(self, trace):
        enc = TSEncoder(trace, [])
        fd_builder = FlowDroidModelBuilder(enc.trace,
                                           enc.gs.trace_map,
                                           set([]))
        return fd_builder


    def _create_activity(self):
        obj_id = TestGrounding._get_obj("objid_%d" % self.get_obj_id(), "android.app.Activity")
        cb = CCallback(1, 1, "", "void android.app.Activity.<init>()",
                       [obj_id],
                       None,
                       [TestGrounding._get_fmwkov("void android.app.Activity","<init>()", False)])
        return (cb, obj_id)

    def _create_fragment(self):
        obj_id = TestGrounding._get_obj("objid_%d" % self.get_obj_id(), "android.app.Fragment")
        cb = CCallback(1, 1, "", "void android.app.Fragment.<init>()",
                       [obj_id],
                       None,
                       [TestGrounding._get_fmwkov("void android.app.Fragment","<init>()", False)])
        return (cb, obj_id)

    def _create_view(self):
        obj_id = TestGrounding._get_obj("objid_%d" % self.get_obj_id(),"android.view.View")
        cb = CCallback(1, 1, "", "void android.view.View.<init>()",
                       [obj_id],
                       None,
                       [TestGrounding._get_fmwkov("void android.view.View","<init>()", False)])
        return (cb, obj_id)

    def _attach_fragment_to_activity(self, activity, fragment):
        # public void onAttach (Context context)
        cb = CCallback(1, 1, "", "void android.app.Fragment.onAttach(android.app.Activity)",
                       [fragment, activity],
                       None,
                       [TestGrounding._get_fmwkov("void android.app.Fragment","onAttach(android.app.Activity)", False)])
        return cb

    def _attach_view(self, parent, child):
        cb = None
        return cb

