// setEnabled(true) enables the button click if it has been registered
SPEC TRUE[*];
     [CI] [ENTRY] [b] void android.view.View.setOnClickListener(l : android.view.View$OnClickListener);
     ( ! [CI] [ENTRY] [b] void android.view.View.setOnClickListener(l2 : android.view.View$OnClickListener) ) [*];
     [CI] [ENTRY] [b] void android.widget.TextView.setEnabled(1 : boolean) |+ [CB] [ENTRY] [l] void android.view.View$OnClickListener.onClick(b : android.view.View);

// if now setEnable(false) is triggered then the onClickListener enables the on Click
SPEC TRUE[*];
     ( ! [CI] [ENTRY] [b] void android.widget.TextView.setEnabled(0 : boolean))[*];
     [CI] [ENTRY] [b] void android.view.View.setOnClickListener(l : android.view.View$OnClickListener)
     |+
      [CB] [ENTRY] [l] void android.view.View$OnClickListener.onClick(b : android.view.View);

// setEnabled(false) disables the button regardless of what else has happened
SPEC TRUE[*];
     [CI] [ENTRY] [b] void android.widget.TextView.setEnabled(0 : boolean) |- [CB] [ENTRY] [l] void android.view.View$OnClickListener.onClick(b : android.view.View);

// onClick is initially disabled
SPEC FALSE[*] |- [CB] [ENTRY] [l] void android.view.View$OnClickListener.onClick(b : android.view.View)
