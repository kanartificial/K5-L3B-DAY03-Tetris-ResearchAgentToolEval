
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import (
    ROOT,
    ARTIFACTS_DIR,
    now_iso,
    safe_slug,
    trim_history,
    run_model_tool_loop,
    write_transcript,
)

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Research Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 Research Agent")
st.caption("AI-powered Research Assistant with Tool Calling")

# =========================================================
# 2. SESSION INITIALIZATION
# =========================================================

def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def create_new_session(settings: dict):
    """Initialize a new Agent session."""

    system_prompt_path = resolve_path(settings["system_prompt"])
    tools_path = resolve_path(settings["tools"])
    transcripts_dir = resolve_path(settings["transcripts_dir"])

    if not system_prompt_path.exists():
        raise FileNotFoundError(
            f"System prompt not found: {system_prompt_path}"
        )

    if not tools_path.exists():
        raise FileNotFoundError(
            f"Tools configuration not found: {tools_path}"
        )

    system_prompt = system_prompt_path.read_text(
        encoding="utf-8"
    )

    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)

    provider = make_provider(settings["provider"])

    selected_model = (
        settings["model"]
        or getattr(provider, "default_model", None)
    )

    artifact_version = build_artifact_version(
        settings["version"],
        system_prompt_path,
        tools_path,
    )

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")

    transcript_id = "_".join([
        safe_slug(settings["version"]),
        safe_slug(settings["provider"]),
        timestamp,
    ])

    transcript_path = (
        transcripts_dir
        / f"{transcript_id}.transcript.json"
    )

    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": settings["provider"],
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": settings["history_window"],
        "max_tool_rounds": settings["max_tool_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    st.session_state.provider = provider
    st.session_state.system_prompt = system_prompt
    st.session_state.openai_tools = openai_tools
    st.session_state.selected_model = selected_model

    st.session_state.history = []
    st.session_state.chat_messages = []
    st.session_state.turn_index = 0

    st.session_state.transcript = transcript
    st.session_state.transcript_path = transcript_path
    st.session_state.active_settings = settings.copy()

    write_transcript(transcript_path, transcript)


# =========================================================
# 3. SIDEBAR - AGENT CONFIGURATION
# =========================================================

st.sidebar.title("⚙️ Agent Configuration")

st.sidebar.subheader("Provider")

provider_name = st.sidebar.selectbox(
    "Select Provider",
    options=[
        "openrouter",
        "openai",
        "anthropic",
        "gemini",
        "ollama",
    ],
    index=0,
)

model_name = st.sidebar.text_input(
    "Model",
    placeholder="Leave empty to use default model",
    help="Enter the model name supported by your provider.",
)

st.sidebar.divider()

st.sidebar.subheader("Artifact Configuration")

version = st.sidebar.text_input(
    "Artifact Version",
    value="v0",
)

system_prompt_path = st.sidebar.text_input(
    "System Prompt Path",
    value=str(ARTIFACTS_DIR / "system_prompt.md"),
)

tools_path = st.sidebar.text_input(
    "Tools Configuration Path",
    value=str(ARTIFACTS_DIR / "tools.yaml"),
)

st.sidebar.divider()

st.sidebar.subheader("Agent Parameters")

history_window = st.sidebar.number_input(
    "History Window",
    min_value=0,
    max_value=50,
    value=5,
    step=1,
    help="Number of previous user/assistant pairs kept in context.",
)

max_tool_rounds = st.sidebar.number_input(
    "Max Tool Rounds",
    min_value=1,
    max_value=20,
    value=4,
    step=1,
)

transcripts_dir = st.sidebar.text_input(
    "Transcripts Directory",
    value=str(ROOT / "transcripts"),
)

settings = {
    "provider": provider_name,
    "model": model_name.strip(),
    "version": version,
    "system_prompt": system_prompt_path,
    "tools": tools_path,
    "history_window": int(history_window),
    "max_tool_rounds": int(max_tool_rounds),
    "transcripts_dir": transcripts_dir,
}

# Apply configuration and create a new session
if st.sidebar.button(
    "🚀 Apply Configuration / New Chat",
    use_container_width=True,
    type="primary",
):
    try:
        create_new_session(settings)
        st.rerun()
    except Exception as exc:
        st.sidebar.error(
            f"{type(exc).__name__}: {exc}"
        )

# Automatically initialize the first session
if "provider" not in st.session_state:
    try:
        create_new_session(settings)
    except Exception as exc:
        st.error(
            f"Cannot initialize Agent: {type(exc).__name__}: {exc}"
        )
        st.stop()


# =========================================================
# 4. SIDEBAR - SESSION INFORMATION
# =========================================================

st.sidebar.divider()
st.sidebar.subheader("📊 Current Session")

active = st.session_state.active_settings

st.sidebar.markdown(
    f"""
    **Provider:** `{active['provider']}`

    **Model:** `{st.session_state.selected_model or 'Default'}`

    **Version:** `{active['version']}`

    **History Window:** `{active['history_window']}`

    **Max Tool Rounds:** `{active['max_tool_rounds']}`
    """
)

st.sidebar.caption(
    f"Transcript: {st.session_state.transcript['transcript_id']}"
)

if st.sidebar.button(
    "📁 Open Transcript Location",
    use_container_width=True,
):
    st.sidebar.code(
        str(st.session_state.transcript_path.parent)
    )

if st.sidebar.button(
    "🗑️ Clear Conversation",
    use_container_width=True,
):
    st.session_state.chat_messages = []
    st.session_state.history = []
    st.session_state.turn_index = 0

    st.session_state.transcript["turns"] = []
    write_transcript(
        st.session_state.transcript_path,
        st.session_state.transcript,
    )

    st.rerun()


# =========================================================
# 5. DISPLAY CHAT HISTORY
# =========================================================

def display_tool_details(message: dict):
    """Display tool calls and their results."""

    rounds = message.get("rounds", [])

    if not rounds:
        return

    with st.expander(
        "🔧 View Agent Tool Execution",
        expanded=False,
    ):
        for round_data in rounds:

            st.markdown(
                f"### Round {round_data['round']}"
            )

            assistant_text = round_data.get("assistant_text")

            if assistant_text:
                st.markdown("**Agent reasoning / message:**")
                st.write(assistant_text)

            calls = round_data.get("tool_calls", [])

            if calls:
                st.markdown("**Tool Calls:**")

                for index, call in enumerate(calls, 1):
                    st.markdown(
                        f"Tool {index}: `{call['name']}`"
                    )
                    st.json(call.get("args", {}))

            results = round_data.get("tool_results", [])

            if results:
                st.markdown("**Tool Results:**")

                for index, event in enumerate(results, 1):
                    st.markdown(
                        f"Result {index}: `{event['tool']}`"
                    )

                    st.json(event.get("result", {}))


for message in st.session_state.chat_messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":
            display_tool_details(message)


# =========================================================
# 6. CHAT INPUT AND AGENT EXECUTION
# =========================================================

user_text = st.chat_input(
    "Ask Research Agent anything..."
)

if user_text:

    # Display user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_text,
    })

    with st.chat_message("user"):
        st.markdown(user_text)

    # Prepare model messages
    messages = [
        {
            "role": "system",
            "content": st.session_state.system_prompt,
        },
        *trim_history(
            st.session_state.history,
            active["history_window"],
        ),
        {
            "role": "user",
            "content": user_text,
        },
    ]

    st.session_state.turn_index += 1

    turn_record = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        with st.chat_message("assistant"):

            with st.spinner(
                "🤖 Research Agent is processing..."
            ):

                result = run_model_tool_loop(
                    provider=st.session_state.provider,
                    messages=messages,
                    tools=st.session_state.openai_tools,
                    model=active["model"] or None,
                    max_tool_rounds=active["max_tool_rounds"],
                )

            turn_record.update(result)

            assistant_text = result["assistant_text"]

            if result["status"] == "waiting_for_user":
                st.info("Agent needs additional information.")

            elif result["status"] == "max_tool_rounds":
                st.warning(
                    "Agent reached the maximum number of tool rounds."
                )

            st.markdown(assistant_text)

            # Show tool execution details
            display_tool_details(turn_record)

            # Update chat UI
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": assistant_text,
                "rounds": result.get("rounds", []),
                "status": result["status"],
            })

            # Update conversation history
            st.session_state.history.append({
                "role": "user",
                "content": user_text,
            })

            st.session_state.history.append({
                "role": "assistant",
                "content": assistant_text,
            })

    except Exception as exc:

        error_message = (
            f"{type(exc).__name__}: {str(exc)}"
        )

        turn_record.update({
            "status": "provider_error",
            "error": error_message,
        })

        with st.chat_message("assistant"):
            st.error(f"Agent Error: {error_message}")

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": f"Agent Error: {error_message}",
        })

    finally:

        turn_record["ended_at"] = now_iso()

        st.session_state.transcript["turns"].append(
            turn_record
        )

        write_transcript(
            st.session_state.transcript_path,
            st.session_state.transcript,
        )

    st.rerun()
