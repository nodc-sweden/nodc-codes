import nodc_codes


def test_get_translate_code_object():
    """Simple test to make sure that the default translation codes can be loaded."""
    translate_codes = nodc_codes.get_translate_codes_object()
    assert translate_codes
