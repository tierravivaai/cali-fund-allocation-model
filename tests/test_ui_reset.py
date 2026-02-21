import pytest
from streamlit.testing.v1 import AppTest

def test_reset_button_functionality():
    """
    Test that the 'Reset to default' button correctly resets the app state.
    """
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    
    # 1. Modify some values
    # Slider 0 is fund_size_bn, Slider 1 is iplc_share
    at.slider(key="fund_size_bn").set_value(5.0).run()
    at.toggle(key="use_thousands").set_value(True).run()
    at.checkbox(key="exclude_hi").set_value(False).run()
    
    # Verify modifications took place
    assert at.slider(key="fund_size_bn").value == 5.0
    assert at.toggle(key="use_thousands").value is True
    assert at.checkbox(key="exclude_hi").value is False
    
    # 2. Click the reset button
    # at.button returns a list, we filter it by label
    reset_button = [b for b in at.button if b.label == "Reset to default"][0]
    reset_button.click().run()
    
    # 3. Verify values are back to defaults
    assert at.slider(key="fund_size_bn").value == 1.0
    assert at.toggle(key="use_thousands").value is False
    assert at.checkbox(key="exclude_hi").value is True
    assert at.slider(key="iplc_share").value == 50
