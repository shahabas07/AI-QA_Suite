import json
import pytest
import re
import os
import sys
import ast

# Ensure utils is discoverable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_client import generate_code

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "..", "prompts.json")

def load_prompts():
    try:
        with open(PROMPTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

TEST_DATA = load_prompts()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@pytest.fixture(scope="session")
def ai_responses() -> dict:
    """
    Session-level fixture that fetches AI responses exactly ONCE per prompt.
    Caches the results to prevent duplicate API requests across different test parameters.
    """
    responses = {}
    print("\n\n=== BEGINNING AI GENERATION BATCH ===")
    for case in TEST_DATA:
        prompt_id = case["id"]
        # Print status directly to standard out to bypass Pytest logging limitations
        print(f"-> Generating code for prompt {prompt_id}: {case['prompt'][:40]}...")
        sys.stdout.flush() 
        
        # Make the API call once per session
        code = generate_code(case["prompt"])
        responses[prompt_id] = code
        
        # Store physical copy on disk locally
        output_file = os.path.join(OUTPUT_DIR, f"prompt_{prompt_id}.txt")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(code)
        
        print(f"<- Received response for prompt {prompt_id}")
        sys.stdout.flush()
        
    print("=== FINISHED AI BATCH. BEGINNING TESTS ===\n")
    yield responses
    
    # --- TEARDOWN / MEMORY CLEANUP PHASE ---
    # Once Pytest finishes all validations, this block runs automatically
    print("\n--- TEARDOWN: Clearing cached AI responses from memory ---")
    responses.clear()
    
    # Force Python's Garbage Collector to free the RAM immediately
    import gc
    gc.collect()

# =====================================================
# 1. Syntax + Safe Execution Validation
# =====================================================

@pytest.mark.parametrize("test_case", TEST_DATA)
def test_code_validity(test_case, ai_responses):
    """
    Checks whether generated code:

    1. Exists
    2. Has valid Python syntax
    3. Can execute safely
    """

    prompt_id = test_case["id"]
    code = ai_responses.get(prompt_id, "")

    assert code.strip(), (
        f"No code generated for prompt {prompt_id}"
    )

    # Syntax validation
    try:
        ast.parse(code)

    except SyntaxError as e:
        pytest.fail(
            f"Syntax Error: {e}"
        )

    # Restricted execution environment
    safe_globals = {
        "__builtins__": {
            "range": range,
            "len": len,
            "print": print,
            "str": str,
            "int": int,
            "list": list,
            "max": max,
            "min": min
        }
    }

    namespace = {}

    try:
        exec(
            code,
            safe_globals,
            namespace
        )

    except Exception as e:
        pytest.fail(
            f"Execution failed: {e}"
        )


# =====================================================
# 2. Functional Correctness
# =====================================================

@pytest.mark.parametrize("test_case", TEST_DATA)
def test_functional_correctness(
    test_case,
    ai_responses
):
    """
    Runs simple expected behavior checks
    for common AI-generated tasks.
    """

    prompt_id = test_case["id"]

    code = ai_responses.get(
        prompt_id,
        ""
    )

    namespace = {}

    safe_globals = {
        "__builtins__": {
            "range": range,
            "len": len,
            "print": print,
            "str": str,
            "int": int,
            "list": list,
            "max": max,
            "min": min
        }
    }

    exec(
        code,
        safe_globals,
        namespace
    )

    prompt = test_case["prompt"].lower()


    # Detect function by prompt type

    try:

        if "sum" in prompt or "add" in prompt:

            func = namespace.get(
                "add_numbers"
            )

            assert func is not None
            assert func(2,3) == 5


        elif "even" in prompt:

            func = namespace.get(
                "is_even"
            )

            assert func is not None
            assert func(4) is True


        elif "reverse" in prompt:

            func = namespace.get(
                "reverse"
            )

            assert func is not None
            assert func("abc")=="cba"


        elif "factorial" in prompt:

            func = namespace.get(
                "factorial"
            )

            assert func is not None
            assert func(5)==120


        elif "largest" in prompt:

            func = namespace.get(
                "find_largest"
            )

            assert func is not None
            assert func(
                [1,5,3,9,2]
            )==9


    except AssertionError:

        pytest.fail(
            f"Functional validation failed for prompt {prompt_id}"
        )


# =====================================================
# 3. Security Audit
# =====================================================

@pytest.mark.parametrize("test_case", TEST_DATA)
def test_security_audit(
    test_case,
    ai_responses
):
    """
    Detect dangerous patterns
    in generated AI code.
    """

    prompt_id = test_case["id"]

    code = ai_responses.get(
        prompt_id,
        ""
    )


    dangerous_patterns = {

        "Hardcoded Password":
        r'(?i)(password|pwd|pass)\s*[:=]\s*["\'][^"\']+["\']',

        "Hardcoded API Key":
        r'(?i)(api_key|apikey|secret|token)\s*[:=]\s*["\'][^"\']+["\']',

        "Unsafe eval/exec":
        r'\b(eval|exec)\s*\(',

        "OS command execution":
        r'os\.system|subprocess|Popen|__import__'
    }


    for test_name, pattern in dangerous_patterns.items():

        match = re.search(
            pattern,
            code
        )

        assert not match, (
            f"{test_name} detected:"
            f" {match.group()}"
        )