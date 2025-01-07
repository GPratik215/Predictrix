# xml_helper.py
import xml.etree.ElementTree as ET

def extract_sid_from_xml(xml_text, namespace):
    try:
        tree = ET.ElementTree(ET.fromstring(xml_text))
        root = tree.getroot()
        sid = root.find(".//s:key[@name='sid']", namespace).text
        return sid
    except Exception as e:
        raise ValueError(f"Error parsing XML for SID extraction: {e}")

def extract_dispatch_state_from_xml(xml_text, namespace):
    try:
        tree = ET.ElementTree(ET.fromstring(xml_text))
        root = tree.getroot()
        dispatch_state = root.find(".//s:key[@name='dispatchState']", namespace).text
        return dispatch_state
    except Exception as e:
        raise ValueError(f"Error parsing XML for dispatch state: {e}")
