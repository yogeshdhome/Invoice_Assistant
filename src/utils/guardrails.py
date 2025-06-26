from guardrails import Guard
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "guardrails_config.xml"

guard = Guard.from_rail(str(CONFIG_PATH))

def validate_input(user_input: str) -> bool:
    """Validate user input using guardrails config. Returns True if valid, False otherwise."""
    result = guard.validate(user_input, section="input")
    return result.valid  # type: ignore[attr-defined]

def validate_output(llm_output: str) -> bool:
    """Validate LLM output using guardrails config. Returns True if valid, False otherwise."""
    result = guard.validate(llm_output, section="output")
    return result.valid  # type: ignore[attr-defined]

def get_guardrails_errors(text: str, section: str = "input") -> list:
    result = guard.validate(text, section=section)
    return result.errors  # type: ignore[attr-defined]

def redact_pii(text: str) -> str:
    """Redact PII in the output using guardrails if enabled in config."""
    result = guard.validate(text, section="output")
    if hasattr(result, 'redacted_output') and result.redacted_output:  # type: ignore[attr-defined]
        return result.redacted_output  # type: ignore[attr-defined]
    return text

def check_invoice_number_format(invoice_number: str) -> bool:
    """Custom regex: Invoice number must be 10 digits."""
    import re
    return bool(re.fullmatch(r"\d{10}", invoice_number)) 