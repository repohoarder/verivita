"""
--------------------------------------------------------------------------------
Helper class that builds the FlowDroid model.

We follow the description in Section 3 "Precise Modeling of Lifecycle" of:
'FlowDroid: Precise Context, Flow, Field, Object-sensitive
and Lifecycle-aware Taint Analysis for Android Apps',
Artz et al, PLDI 14

and in particular the implementation in:
soot-infoflow/src/soot/jimple/infoflow/entryPointCreators/
AndroidEntryPointCreator.java
in the repo secure-software-engineering/FlowDroid,
commit a1438c2b38a6ba453b91e38b2f7927b6670a2702.

We encode the lifecylce of each component forcing that at most one component
can be active at each time.
For each component, there is a different definition of active. For example,
an activity component is active after the onResume and before the onPause
callbacks.

We follow the modeling where callbacks cannot happen if the component
that register them is not active.
We compute an over-approximation of the registration of components
from the trace.

We model the lifecycle for activity and fragment components since we
are interested in components that run in the UI thread.

As done in flowdroid, we encode the lifecycle component of fragment
inside their activity component.
"""

from cbverifier.traces.ctrace import CTrace, CCallback, CCallin, CValue, CTraceException
from cbverifier.encoding.flowdroid_model.lifecycle_constants import Activity, Fragment
from cbverifier.specs.spec_ast import get_node_type, CALL_ENTRY, CALL_EXIT, ID
from cbverifier.encoding.grounding import bottom_value
from cbverifier.encoding.model_properties import AttachRelation, RegistrationRelation

class FlowDroidModelBuilder:

    def __init__(self, ts_encoder):
        """ Initialize the model builder taking as input an instance
        of the ts_encoder (to use traces, other encoders...).
        """
        self.ts_encoder = ts_encoder

        # Populate the map of all components from the trace
        self.components_set = set([])
        FlowDroidModelBuilder._get_all_components(self.ts_encoder.trace,
                                                  self.components_set)

        # map from component address to its representation
        self.components_map = {}
        for c in self.components_set:
            self.components_map[c.get_inst_value()] = c

        # Finds the existing lifecycle messages in the trace
        FlowDroidModelBuilder._find_lifecycle_messages(self.ts_encoder.gs.trace_map,
                                                       self.components_set)

        root_components_ids = []
        for c in self.components_set:
            if isinstance(c, Activity):
                root_components_ids.append(c.get_inst_value())
        self.attach_rel = AttachRelation(ts_encoder.gs.trace_map,
                                         root_components_ids)
        self.register_rel = RegistrationRelation(ts_encoder.gs.trace_map,
                                                 root_components_ids)

        # List of messages used in the the model builder
        self.msgs = []

        return


        # Get an over-approximation of the objects that may
        # be attached to the activities/fragments
        self._get_attachment_overapprox()

        raise NotImplementedError("Initialization of the fd model")

    def get_calls(self):
        """ Get all the calls that are observed in the FlowDroid
        model.

        """
        raise NotImplementedError("get_calls not implemented")


    def get_components(self):
        return self.components_set

    @staticmethod
    def _get_all_components(trace, components):
        """ Populate the list of all components from the trace.
        """
        trace_stack = []
        for msg in trace.children:
            trace_stack.append(msg)

        # Finds all the components in the trace
        while (0 != len(trace_stack)):
            msg = trace_stack.pop()
            # Collect the list of compnents
            for value in msg.params:
                if Activity.is_class(value.type):
                    component = Activity(value.type, value)
                    components.add(component)
                if Fragment.is_class(value.type):
                    component = Fragment(value.type, value)
                    components.add(component)
            for child in msg.children:
                trace_stack.append(child)

    @staticmethod
    def _find_lifecycle_messages(trace_map, components):
        """ Finds the existing lifecycle messages in the trace
        """
        # Finds the lifecycle methods for each component
        for component in components:
            for (key, _) in component.get_class_cb():
                for call_ast in component.get_methods_names(key):
                    # find the concrete methods in the trace for the correct
                    # method name
                    msg_list = trace_map.find_methods(call_ast)
                    for m in msg_list:
                        component.add_trace_msg(key, m)


    def _get_registration_overapprox(self):
        """ Computes an over-approximate relation of the callback that can
        be registered at any point in time in the trace.

        Assume no components are attached, then build an over-approximation of
        attachment using the method calls seen in the trace.
        This is similar to theFlowDroid heuristic.

        TODO: check if we see or miss the registration in the XML.
        """
        raise NotImplementedError("_get_registered_overapprox not implemented")


    def encode(self):
        """ Create an encoding of the FlowDroid model
        """
        self._encode_lifecycle()
        self._encode_callbacks_in_lifecycle()

    def _encode_lifecycle(self):
        """ Encode the components' lifecylces

        For now we handle activities.
        """
        raise NotImplementedError("_encode_lifecycle not implemented")

    def _encode_callbacks_in_lifecycle(self):
        """ Encode the enabledness of the callbacks attached to
        Activities and Fragment
        """
        raise NotImplementedError("_encode_callbacks_in_lifecycle not implemented")


class ObjectRepr:
    """ Construct a backward representation from the object in the
    trace to their messages to messages. """

