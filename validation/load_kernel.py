# validation/load_kernel.py

import json
import sys

def load_text_kernel(kernel_path):
    """Load and display key elements from text kernel."""
    
    with open(kernel_path, 'r') as f:
        kernel = json.load(f)
    
    # Extract metadata
    metadata = kernel.get('metadata', {})
    book_title = metadata.get('title', 'Unknown')
    kernel_version = metadata.get('kernel_version', 'Unknown')
    
    # Extract alignment pattern (v5.1 structure)
    alignment = kernel.get('alignment_pattern', {})
    pattern = alignment.get('pattern_name', 'Not found')
    core_dynamic = alignment.get('core_dynamic', 'Not found')
    reader_effect = alignment.get('reader_effect', 'Not found')
    
    # Extract devices (v5.1 uses 'micro_devices')
    devices = kernel.get('micro_devices', [])
    
    print("="*60)
    print(f"BOOK: {book_title}")
    print(f"KERNEL VERSION: {kernel_version}")
    print("="*60)
    
    # Extract key elements for reference
    print("\nALIGNMENT PATTERN:")
    print(f"  {pattern}")
    
    print("\nCORE DYNAMIC:")
    print(f"  {core_dynamic}")
    
    print("\nREADER EFFECT:")
    print(f"  {reader_effect}")
    
    print("\nDEVICES (priority order, top 8):")
    # Show devices in order, limiting to top 8
    device_priorities = alignment.get('device_priorities', [])
    shown_devices = set()
    count = 0
    
    # First show prioritized devices
    for device_name in device_priorities[:5]:
        if count >= 8:
            break
        # Find device details
        for device in devices:
            if device['name'] == device_name and device_name not in shown_devices:
                operational_layer = device.get('assigned_section', 'N/A')
                print(f"  - {device['name']} ({operational_layer})")
                shown_devices.add(device_name)
                count += 1
                break
    
    # Then show remaining devices if needed
    if count < 8:
        for device in devices:
            if device['name'] not in shown_devices and count < 8:
                operational_layer = device.get('assigned_section', 'N/A')
                print(f"  - {device['name']} ({operational_layer})")
                shown_devices.add(device['name'])
                count += 1
    
    print("\n" + "="*60)
    
    return kernel

# Usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        kernel_path = sys.argv[1]
    else:
        kernel_path = 'To_Kill_a_Mockingbird_kernel_v5_1.json'
    
    kernel = load_text_kernel(kernel_path)


