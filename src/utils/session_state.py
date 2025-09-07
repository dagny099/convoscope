"""Session state management utilities for Streamlit."""

import streamlit as st
from typing import Optional, Tuple, Any


def update_priming_text(priming_messages: dict, source: Optional[str] = None, new_value: Optional[Tuple[str, str]] = None) -> None:
    """
    Update the priming text based on the source of the change.
    
    Args:
        priming_messages: Dictionary of available priming messages
        source: Source of the update ('button' or None for selectbox)
        new_value: Tuple of (key, value) when source is 'button'
    """
    if source is None:
        # Update from selectbox
        st.session_state["priming_key"] = st.session_state.selectbox_choice
        st.session_state["priming_text"] = priming_messages[st.session_state.selectbox_choice]
    elif source == "button":
        # Update from random button
        if new_value:
            st.session_state["priming_key"] = new_value[0]
            st.session_state["priming_text"] = new_value[1]


def initialize_session_state(key: str, default_value: Any) -> None:
    """
    Initialize a session state variable if it doesn't exist.
    
    Args:
        key: Session state key
        default_value: Default value to set if key doesn't exist
    """
    if key not in st.session_state:
        st.session_state[key] = default_value


def get_session_state_value(key: str, default_value: Any = None) -> Any:
    """
    Safely get a value from session state.
    
    Args:
        key: Session state key
        default_value: Default value if key doesn't exist
        
    Returns:
        Session state value or default
    """
    return st.session_state.get(key, default_value)