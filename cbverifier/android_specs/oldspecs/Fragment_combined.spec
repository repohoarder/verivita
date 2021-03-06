//*** Enable Disable Rules ***
//Initial disable rules
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle) ALIASES android.app.Fragment.onCreate = [android.app.Fragment.onCreate, android.support.v4.app.Fragment.onCreate]; 
SPEC FALSE[*] |-  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle)ALIASES android.app.Fragment.onCreateView = [android.app.Fragment.onCreateView, android.support.v4.app.Fragment.onCreateView]; 
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onViewCreated(# : android.view.View,# : android.os.Bundle) ALIASES android.app.Fragment.onViewCreated = [android.app.Fragment.onViewCreated] //TODO: you were here
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onStart();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onResume();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onPause();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle);
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onStop();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroy();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onDetach();
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onActivityCreated(# : android.os.Bundle);
SPEC FALSE[*] |- [CB] [ENTRY] [f] void android.app.Fragment.onAttach(# : android.app.Activity);


SPEC TRUE[*]; [CI] [ENTRY] [f] void android.app.Fragment.<init>() |+ [CB] [ENTRY] [f] void android.app.Fragment.onAttach(# : android.app.Activity);

SPEC TRUE[*]; [CI] [EXIT] [f] void android.app.Fragment.<init>() |- [CI] [EXIT] [f] void android.app.Fragment.<init>();



SPEC TRUE[*];[CB] [ENTRY] [f] void android.app.Fragment.onAttach(# : android.app.Activity) |- [CB] [ENTRY] [f] void android.app.Fragment.onAttach(# : android.app.Activity) 
	ALIASES android.app.Fragment.onAttach = [android.support.v4.app.Fragment.onAttach,android.app.Fragment.onAttach];
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onAttach(# : android.app.Activity) |+ [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle) ALIASES android.app.Fragment.onCreate = [android.app.Fragment.onCreate, android.support.v4.app.Fragment.onCreate], android.app.Fragment.onAttach = [android.app.Fragment.onAttach,android.support.v4.app.Fragment.onAttach]; 
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle) |+  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle) 
	ALIASES android.app.Fragment.onCreate = [android.app.Fragment.onCreate, android.support.v4.app.Fragment.onCreate], android.app.Fragment.onCreateView = [android.app.Fragment.onCreateView, android.support.v4.app.Fragment.onCreateView, android.support.v4.app.ListFragment.onCreateView];
SPEC TRUE[*];  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle) |-  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle);
SPEC TRUE[*];  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(# : android.view.LayoutInflater,# : android.view.ViewGroup,# : android.os.Bundle) |+ [CB] [ENTRY] [f] void android.app.Fragment.onViewCreated(# : android.view.View,# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onViewCreated(# : android.view.View,# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onViewCreated(# : android.view.View,# : android.os.Bundle);

//TODO: onActivityCreated and onViewStateRestored conditional on init, for now left unspecified
//When added in the below rule will also need to know whether its in the starting cycle.

SPEC TRUE[*];  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(# : android.view.LayoutInflater,# : android.view.ViewGroup,# : android.os.Bundle) |+ [CB] [ENTRY] [f] void android.app.Fragment.onActivityCreated(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onActivityCreated(# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onActivityCreated(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStart() |- [CB] [ENTRY] [f] void android.app.Fragment.onActivityCreated(# : android.os.Bundle);


SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onViewCreated(# : android.view.View,# : android.os.Bundle) |+ [CB] [ENTRY] [f] void android.app.Fragment.onStart();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStart() |- [CB] [ENTRY] [f] void android.app.Fragment.onStart();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStart() |+ [CB] [ENTRY] [f] void android.app.Fragment.onResume();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onResume() |- [CB] [ENTRY] [f] void android.app.Fragment.onResume();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onResume() |+ [CB] [ENTRY] [f] void android.app.Fragment.onPause();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onPause() |- [CB] [ENTRY] [f] void android.app.Fragment.onPause();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onPause() |+ [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onPause() |+ [CB] [ENTRY] [f] void android.app.Fragment.onStop();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onPause() |+ [CB] [ENTRY] [f] void android.app.Fragment.onResume();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onResume() |- [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onResume();
//SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle) |+ [CB] [ENTRY] [f] void android.app.Fragment.onStop();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onSaveInstanceState(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStop() |- [CB] [ENTRY] [f] void android.app.Fragment.onStop();

//onStop branching control flow
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStop() |+ [CB] [ENTRY] [f] void android.app.Fragment.onStart();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStop() |+ [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStop() |+ [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView();

SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStart() |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onStart() |- [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView() |- [CB] [ENTRY] [f] void android.app.Fragment.onStart();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView() |- [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle);
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onStart();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onCreate(# : android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView();


//onDstroyView branching control
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView() |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView() |+ [CB] [ENTRY] [f] void android.app.Fragment.onDestroy();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroyView() |+  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle);

SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroy() |-  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle);
SPEC TRUE[*];  [CB] [ENTRY] [f] android.view.View android.app.Fragment.onCreateView(#:android.view.LayoutInflater,#:android.view.ViewGroup,#:android.os.Bundle) |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroy();


SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroy() |- [CB] [ENTRY] [f] void android.app.Fragment.onDestroy();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDestroy() |+ [CB] [ENTRY] [f] void android.app.Fragment.onDetach();
SPEC TRUE[*]; [CB] [ENTRY] [f] void android.app.Fragment.onDetach() |+ [CB] [ENTRY] [f] void android.app.Fragment.onDetach()
