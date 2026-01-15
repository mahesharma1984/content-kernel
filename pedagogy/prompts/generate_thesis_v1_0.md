# Thesis Generation Prompt

You are creating example thesis statements for VCE English essays based on literary analysis data.

## Input Data
- **Pattern Name:** {pattern_name}
- **Core Dynamic:** {core_dynamic}
- **Reader Effect:** {reader_effect}
- **Themes:** {themes}
- **Device Priorities:** {device_priorities}

## Task
Create 3-4 example thesis statements showing different analytical approaches. Each thesis should:
1. Be a complete, arguable statement
2. Name the pattern OR theme OR devices (different focus per thesis)
3. Show HOW the text creates meaning (mechanism)
4. State the EFFECT or significance
5. Be appropriate for Year 11 VCE analytical essay

## Output Format
Return ONLY valid JSON (no markdown, no preamble):

{
  "theses": [
    {
      "focus": "Theme-focused",
      "statement": "Complete thesis statement here",
      "structure_notes": "What makes this thesis effective"
    },
    {
      "focus": "Pattern-focused",
      "statement": "Complete thesis statement here",
      "structure_notes": "What makes this thesis effective"
    },
    {
      "focus": "Device-focused",
      "statement": "Complete thesis statement here",
      "structure_notes": "What makes this thesis effective"
    }
  ]
}

## Thesis Structure Guidelines
- **Theme-focused:** "[Author] explores [theme] through [devices], revealing [insight]"
- **Pattern-focused:** "Through [pattern name], [author] uses [technique] to create [effect], suggesting [meaning]"
- **Device-focused:** "[Author]'s use of [device] and [device] creates [effect], which [significance]"

## Constraints
- Use themes from input only
- Use devices from device_priorities only
- Clear causal chain: devices → effect → meaning
- No vague language ("interesting", "powerful", "shows")
- Specific about mechanism (HOW devices work)

## Example Theses
{
  "theses": [
    {
      "focus": "Theme-focused",
      "statement": "Harvey explores the tension between cosmic perspective and human intimacy through sustained juxtaposition and omniscient narration, revealing that distance paradoxically intensifies rather than diminishes emotional connection.",
      "structure_notes": "Clear theme + specific devices + counterintuitive insight"
    },
    {
      "focus": "Pattern-focused",
      "statement": "Through the Cosmic Contemplation pattern, Harvey employs omniscient narration and symbolic imagery to create meditative distance that simultaneously elevates mundane experience to universal significance while emphasizing Earth's fragility.",
      "structure_notes": "Names pattern + shows mechanism + states dual effect"
    }
  ]
}

