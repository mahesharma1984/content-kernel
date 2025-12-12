#!/usr/bin/env python3
"""
KERNEL EXTRACTION - Stage 1
Version: 1.0

Extracts all data required by Stage 2 Content Taxonomy.
Pure extraction — no API calls, no transformation.

Usage:
    python extract_kernel_v1_0.py Orbital_kernel_v5_0.json -o outputs/
"""

import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    SCHEMA_VERSION = "1.0"
    OUTPUTS_DIR = Path("outputs")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_nested(obj: dict, path: str, default: Any = None) -> Any:
    """
    Get nested value from dict using dot notation.
    
    Example:
        get_nested(kernel, 'alignment_pattern.pattern_name')
    """
    keys = path.split('.')
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key, default)
        else:
            return default
    return obj if obj is not None else default


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    return text


# =============================================================================
# EXTRACTION CLASS
# =============================================================================

class KernelExtractor:
    """Extracts Stage 2 required data from kernel JSON."""
    
    # Required paths — extraction fails if missing
    REQUIRED_PATHS = [
        'metadata.title',
        'metadata.author',
        'alignment_pattern.pattern_name',
        'alignment_pattern.core_dynamic',
        'alignment_pattern.reader_effect',
        'macro_variables.narrative.voice',
        'macro_variables.rhetoric.voice.tone',
        'micro_devices',
    ]
    
    # Optional paths — warn if missing but continue
    OPTIONAL_PATHS = [
        'alignment_pattern.device_priorities',
        'macro_variables.device_mediation.summary',
        'macro_variables.narrative.voice.pov_description',
        'macro_variables.narrative.voice.focalization_description',
        'text_structure.total_chapters_estimate',
    ]
    
    def __init__(self, kernel_path: str, output_dir: Optional[str] = None):
        self.kernel_path = Path(kernel_path)
        self.output_dir = Path(output_dir) if output_dir else Config.OUTPUTS_DIR
        self.kernel = None
        self.extraction = None
        self.warnings = []
    
    def load_kernel(self) -> bool:
        """Load kernel JSON file."""
        print(f"\n📖 Loading kernel: {self.kernel_path.name}")
        
        if not self.kernel_path.exists():
            print(f"❌ Error: Kernel file not found: {self.kernel_path}")
            return False
        
        try:
            with open(self.kernel_path, 'r', encoding='utf-8') as f:
                self.kernel = json.load(f)
            print(f"   ✓ Loaded successfully")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON: {e}")
            return False
    
    def validate_required(self) -> bool:
        """Check all required paths exist."""
        print(f"\n🔍 Validating required fields...")
        
        missing = []
        for path in self.REQUIRED_PATHS:
            value = get_nested(self.kernel, path)
            if value is None or (isinstance(value, (list, dict, str)) and len(value) == 0):
                missing.append(path)
        
        if missing:
            print(f"❌ Missing required fields:")
            for path in missing:
                print(f"   - {path}")
            return False
        
        print(f"   ✓ All required fields present")
        return True
    
    def check_optional(self):
        """Warn about missing optional fields."""
        print(f"\n📋 Checking optional fields...")
        
        for path in self.OPTIONAL_PATHS:
            value = get_nested(self.kernel, path)
            if value is None or (isinstance(value, (list, dict, str)) and len(value) == 0):
                self.warnings.append(f"Optional field missing: {path}")
                print(f"   ⚠️  {path} — missing (will use fallback)")
            else:
                print(f"   ✓ {path}")
    
    def extract_metadata(self) -> dict:
        """Extract metadata section."""
        title = get_nested(self.kernel, 'metadata.title', '').strip()
        author = get_nested(self.kernel, 'metadata.author', '').strip()
        
        return {
            "title": title,
            "author": author,
            "book_slug": slugify(title)
        }
    
    def extract_pattern(self) -> dict:
        """Extract alignment pattern section."""
        ap = self.kernel.get('alignment_pattern', {})
        
        # Get device priorities, fallback to extracting from micro_devices
        device_priorities = ap.get('device_priorities', [])
        if not device_priorities:
            # Fallback: count devices and take top 5
            device_counts = {}
            for d in self.kernel.get('micro_devices', []):
                name = d.get('name', '')
                device_counts[name] = device_counts.get(name, 0) + 1
            device_priorities = sorted(device_counts.keys(), 
                                       key=lambda x: device_counts[x], 
                                       reverse=True)[:5]
            self.warnings.append("device_priorities derived from micro_devices counts")
        
        return {
            "name": ap.get('pattern_name', ''),
            "core_dynamic": ap.get('core_dynamic', ''),
            "reader_effect": ap.get('reader_effect', ''),
            "device_priorities": device_priorities
        }
    
    def extract_macro_variables(self) -> dict:
        """Extract macro variables section."""
        narrative = get_nested(self.kernel, 'macro_variables.narrative', {})
        rhetoric = get_nested(self.kernel, 'macro_variables.rhetoric', {})
        voice = narrative.get('voice', {})
        structure = narrative.get('structure', {})
        rhet_voice = rhetoric.get('voice', {})
        
        return {
            "voice": {
                "pov": voice.get('pov', ''),
                "pov_description": voice.get('pov_description', ''),
                "focalization": voice.get('focalization', ''),
                "focalization_description": voice.get('focalization_description', '')
            },
            "structure": {
                "total_chapters": get_nested(self.kernel, 'text_structure.total_chapters_estimate'),
                "chronology": structure.get('chronology', ''),
                "pacing": structure.get('pacing', ''),
                "chapter_structure": structure.get('chapter_structure', '')
            },
            "rhetoric": {
                "tone": rhet_voice.get('tone', ''),
                "register": rhet_voice.get('register', ''),
                "stance": rhet_voice.get('stance', '')
            }
        }
    
    def extract_device_mediation(self) -> dict:
        """Extract device mediation summary."""
        summary = get_nested(self.kernel, 'macro_variables.device_mediation.summary', '')
        return {
            "summary": summary
        }
    
    def extract_micro_devices(self) -> list:
        """Extract micro devices array."""
        devices = []
        for d in self.kernel.get('micro_devices', []):
            devices.append({
                "name": d.get('name', ''),
                "anchor_phrase": d.get('anchor_phrase', ''),
                "effect": d.get('effect', ''),
                "section": d.get('assigned_section', ''),
                "chapter": d.get('chapter')
            })
        return devices
    
    def build_validation(self, pattern: dict, devices: list) -> dict:
        """Build validation summary."""
        sections = list(set(d['section'] for d in devices if d['section']))
        quotes_ok = all(d['anchor_phrase'] for d in devices)
        
        return {
            "pattern_present": bool(pattern['name']),
            "device_count": len(devices),
            "sections_covered": sections,
            "quotes_available": quotes_ok
        }
    
    def extract(self) -> bool:
        """Run full extraction."""
        print("\n" + "="*60)
        print("STAGE 1: KERNEL EXTRACTION")
        print("="*60)
        
        # Load
        if not self.load_kernel():
            return False
        
        # Validate required
        if not self.validate_required():
            return False
        
        # Check optional
        self.check_optional()
        
        # Extract sections
        print(f"\n📦 Extracting data...")
        
        metadata = self.extract_metadata()
        print(f"   ✓ Metadata: {metadata['title']} by {metadata['author']}")
        
        pattern = self.extract_pattern()
        print(f"   ✓ Pattern: {pattern['name']}")
        
        macro_variables = self.extract_macro_variables()
        print(f"   ✓ Macro variables: voice, structure, rhetoric")
        
        device_mediation = self.extract_device_mediation()
        print(f"   ✓ Device mediation: {len(device_mediation['summary'])} chars")
        
        micro_devices = self.extract_micro_devices()
        print(f"   ✓ Micro devices: {len(micro_devices)} devices")
        
        validation = self.build_validation(pattern, micro_devices)
        print(f"   ✓ Validation: {validation['device_count']} devices, {len(validation['sections_covered'])} sections")
        
        # Assemble extraction
        self.extraction = {
            "schema_version": Config.SCHEMA_VERSION,
            "extraction_date": datetime.now().isoformat(),
            "source_kernel": self.kernel_path.name,
            "metadata": metadata,
            "pattern": pattern,
            "macro_variables": macro_variables,
            "device_mediation": device_mediation,
            "micro_devices": micro_devices,
            "validation": validation
        }
        
        # Report warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"   - {w}")
        
        return True
    
    def save(self) -> bool:
        """Save extraction to JSON file."""
        if not self.extraction:
            print("❌ Error: No extraction to save")
            return False
        
        # Create output directory
        book_slug = self.extraction['metadata']['book_slug']
        output_path = self.output_dir / book_slug
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save file
        output_file = output_path / "stage1_extraction.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.extraction, f, indent=2)
        
        print(f"\n💾 Saved: {output_file}")
        print(f"   Size: {output_file.stat().st_size:,} bytes")
        
        return True
    
    def run(self) -> bool:
        """Run extraction and save."""
        if not self.extract():
            return False
        if not self.save():
            return False
        
        print(f"\n✅ Stage 1 complete")
        return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Extract Stage 2 required data from kernel JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_kernel_v1_0.py Orbital_kernel_v5_0.json
    python extract_kernel_v1_0.py Orbital_kernel_v5_0.json -o outputs/
        """
    )
    parser.add_argument('kernel', help='Path to kernel JSON file')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: outputs/)')
    
    args = parser.parse_args()
    
    extractor = KernelExtractor(args.kernel, args.output_dir)
    success = extractor.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

