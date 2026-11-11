
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
st.caption("AI Research Assistant - Trợ lý nghiên cứu thông minh")


# =========================================================
# 2. ERROR HANDLING
# =========================================================

def get_friendly_error(exc: Exception) -> tuple[str, str]:
    """
    Chuyển lỗi kỹ thuật thành thông báo thân thiện với người dùng.
    """

    error_text = str(exc).lower()
    error_type = type(exc).__name__.lower()

    # API Key / Authentication
    if any(keyword in error_text for keyword in [
        "api key",
        "invalid api key",
        "unauthorized",
        "authentication",
        "401",
        "forbidden",
        "403",
    ]):
        return (
            "Không thể xác thực tài khoản",
            "API Key không hợp lệ hoặc chưa được cấu hình. "
            "Vui lòng kiểm tra lại thông tin kết nối của bạn."
        )

    # Rate limit
    if any(keyword in error_text for keyword in [
        "rate limit",
        "too many requests",
        "429",
        "quota exceeded",
        "resource_exhausted",
    ]):
        return (
            "Đã vượt quá giới hạn sử dụng",
            "Dịch vụ AI đang nhận quá nhiều yêu cầu hoặc đã hết hạn mức. "
            "Vui lòng chờ một chút rồi thử lại."
        )

    # Timeout
    if any(keyword in error_text for keyword in [
        "timeout",
        "timed out",
        "deadline exceeded",
    ]):
        return (
            "Yêu cầu mất quá nhiều thời gian",
            "Dịch vụ AI phản hồi chậm. "
            "Vui lòng thử lại sau."
        )

    # Connection
    if any(keyword in error_text for keyword in [
        "connection",
        "network",
        "connection refused",
        "name or service not known",
        "temporary failure",
    ]):
        return (
            "Không thể kết nối đến dịch vụ",
            "Vui lòng kiểm tra kết nối Internet hoặc trạng thái dịch vụ AI."
        )

    # Model not found
    if any(keyword in error_text for keyword in [
        "model not found",
        "model_not_found",
        "does not exist",
        "unknown model",
    ]):
        return (
            "Không tìm thấy mô hình AI",
            "Tên mô hình không hợp lệ hoặc mô hình không được nhà cung cấp hỗ trợ. "
            "Vui lòng kiểm tra lại cấu hình Model."
        )

    # File not found
    if isinstance(exc, FileNotFoundError):
        return (
            "Thiếu tệp cấu hình",
            "Hệ thống không tìm thấy một số tệp cần thiết. "
            "Vui lòng kiểm tra cấu trúc thư mục dự án."
        )

    # Invalid input/configuration
    if isinstance(exc, (ValueError, TypeError)):
        return (
            "Cấu hình chưa hợp lệ",
            "Một số thông tin đầu vào chưa đúng định dạng. "
            "Vui lòng kiểm tra lại cấu hình và thử lại."
        )

    # Fallback
    return (
        "Đã xảy ra lỗi",
        "Hệ thống chưa thể hoàn thành yêu cầu. "
        "Vui lòng thử lại hoặc liên hệ người quản trị."
    )


def display_friendly_error(exc: Exception):
    """
    Hiển thị lỗi thân thiện, không để lộ thông tin kỹ thuật.
    """

    title, description = get_friendly_error(exc)

    st.error(f"**{title}**\n\n{description}")

    # Lưu thông tin kỹ thuật trong terminal để developer debug
    print(
        f"[ERROR] {type(exc).__name__}: {str(exc)}"
    )


# =========================================================
# 3. AGENT RESPONSE HANDLING
# =========================================================

def get_agent_display_message(result: dict) -> tuple[str, str | None]:
    """
    Chuẩn hóa phản hồi của Agent theo từng trạng thái.
    """

    status = result.get("status", "answered")
    assistant_text = result.get("assistant_text") or ""

    if status == "waiting_for_user":
        message = assistant_text.strip()

        if not message:
            message = (
                "Tôi cần thêm một số thông tin để có thể tiếp tục "
                "thực hiện yêu cầu của bạn."
            )

        return message, "info"

    if status == "max_tool_rounds":
        message = (
            "Tôi chưa thể hoàn thành yêu cầu vì đã đạt giới hạn "
            "số lần thực hiện công cụ trong một lượt xử lý.\n\n"
            "Bạn có thể chia yêu cầu thành các bước nhỏ hơn "
            "hoặc thử lại với nội dung cụ thể hơn."
        )

        return message, "warning"

    if status == "answered":
        if not assistant_text.strip():
            assistant_text = (
                "Tôi chưa tạo được câu trả lời. "
                "Bạn vui lòng thử lại với một yêu cầu khác."
            )

        return assistant_text, None

    return (
        assistant_text or "Đã xảy ra vấn đề khi xử lý yêu cầu.",
        "warning",
    )


def has_tool_errors(result: dict) -> bool:
    """
    Kiểm tra xem có công cụ nào thực thi thất bại hay không.
    """

    for round_data in result.get("rounds", []):
        for event in round_data.get("tool_results", []):
            tool_result = event.get("result", {})

            if isinstance(tool_result, dict):
                if tool_result.get("error"):
                    return True

    return False


# =========================================================
# 4. SESSION INITIALIZATION
# =========================================================

def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()

    if not path.is_absolute():
        path = ROOT / path

    return path.resolve()


def create_new_session(settings: dict):
    """
    Khởi tạo một Agent session mới.
    """

    system_prompt_path = resolve_path(
        settings["system_prompt"]
    )

    tools_path = resolve_path(
        settings["tools"]
    )

    transcripts_dir = resolve_path(
        settings["transcripts_dir"]
    )

    # Kiểm tra cấu hình
    if not system_prompt_path.exists():
        raise FileNotFoundError(
            "System prompt configuration not found."
        )

    if not tools_path.exists():
        raise FileNotFoundError(
            "Tools configuration not found."
        )

    # Đọc system prompt
    system_prompt = system_prompt_path.read_text(
        encoding="utf-8"
    )

    # Load tool declarations
    tool_declarations = load_tool_declarations(
        tools_path
    )

    openai_tools = to_openai_tools(
        tool_declarations
    )

    # Khởi tạo provider
    provider = make_provider(
        settings["provider"]
    )

    selected_model = (
        settings["model"]
        or getattr(provider, "default_model", None)
    )

    # Tạo artifact version
    artifact_version = build_artifact_version(
        settings["version"],
        system_prompt_path,
        tools_path,
    )

    # Tạo transcript ID
    timestamp = datetime.now().strftime(
        "%Y%m%dT%H%M%S%f"
    )

    transcript_id = "_".join([
        safe_slug(settings["version"]),
        safe_slug(settings["provider"]),
        timestamp,
    ])

    # Tạo thư mục transcript nếu chưa tồn tại
    transcripts_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    transcript_path = (
        transcripts_dir
        / f"{transcript_id}.transcript.json"
    )

    # Transcript metadata
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

    # Lưu session state
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

    write_transcript(
        transcript_path,
        transcript,
    )


# =========================================================
# 5. SIDEBAR - AGENT CONFIGURATION
# =========================================================

st.sidebar.title("⚙️ Cấu hình Agent")

# ---------------------------------------------------------
# Provider
# ---------------------------------------------------------

st.sidebar.subheader("Nhà cung cấp AI")

provider_options = {
    "OpenRouter": "openrouter",
    "OpenAI": "openai",
    "Anthropic": "anthropic",
    "Google Gemini": "gemini",
    "Ollama (Local)": "ollama",
}

provider_display = st.sidebar.selectbox(
    "Provider",
    options=list(provider_options.keys()),
    index=0,
)

provider_name = provider_options[
    provider_display
]

model_name = st.sidebar.text_input(
    "Model",
    placeholder="Để trống nếu muốn sử dụng model mặc định",
    help="Nhập tên model được hỗ trợ bởi Provider đã chọn.",
)

st.sidebar.divider()

# ---------------------------------------------------------
# Artifact Version
# ---------------------------------------------------------

st.sidebar.subheader("Phiên bản Agent")

version = st.sidebar.selectbox(
    "Artifact Version",
    options=["v0", "v1", "v2", "v3"],
    index=0,
    help="Chọn phiên bản cấu hình Agent muốn sử dụng.",
)

st.sidebar.caption(
    "Phiên bản hiện sử dụng các tệp system_prompt.md "
    "và tools.yaml mặc định trong thư mục artifacts."
)

st.sidebar.divider()

# ---------------------------------------------------------
# Agent Parameters
# ---------------------------------------------------------

st.sidebar.subheader("Tham số xử lý")

history_window = st.sidebar.number_input(
    "History Window",
    min_value=0,
    max_value=50,
    value=5,
    step=1,
    help="Số cặp hội thoại trước đó được giữ lại trong ngữ cảnh.",
)

max_tool_rounds = st.sidebar.number_input(
    "Max Tool Rounds",
    min_value=1,
    max_value=20,
    value=4,
    step=1,
    help="Số vòng tối đa Agent được phép gọi công cụ trong một lượt.",
)

# Các đường dẫn được quản lý nội bộ, không hiển thị trên UI.
settings = {
    "provider": provider_name,
    "model": model_name.strip(),
    "version": version,

    "system_prompt": str(
        ARTIFACTS_DIR / "system_prompt.md"
    ),

    "tools": str(
        ARTIFACTS_DIR / "tools.yaml"
    ),

    "history_window": int(history_window),
    "max_tool_rounds": int(max_tool_rounds),

    "transcripts_dir": str(
        ROOT / "transcripts"
    ),
}

st.sidebar.divider()

# ---------------------------------------------------------
# Apply Configuration
# ---------------------------------------------------------

if st.sidebar.button(
    "🚀 Bắt đầu phiên chat mới",
    use_container_width=True,
    type="primary",
):

    try:
        create_new_session(settings)
        st.rerun()

    except Exception as exc:
        title, description = get_friendly_error(exc)

        st.sidebar.error(
            f"**{title}**\n\n{description}"
        )

        print(
            f"[SESSION ERROR] {type(exc).__name__}: {str(exc)}"
        )


# ---------------------------------------------------------
# Initialize first session
# ---------------------------------------------------------

if "provider" not in st.session_state:

    try:
        create_new_session(settings)

    except Exception as exc:
        st.error(
            "Không thể khởi tạo Research Agent."
        )

        title, description = get_friendly_error(exc)

        st.error(
            f"**{title}**\n\n{description}"
        )

        print(
            f"[INIT ERROR] {type(exc).__name__}: {str(exc)}"
        )

        st.stop()


# =========================================================
# 6. SIDEBAR - CURRENT SESSION
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("📊 Phiên làm việc hiện tại")

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
    f"Số lượt hội thoại: {st.session_state.turn_index}"
)

# ---------------------------------------------------------
# Clear conversation
# ---------------------------------------------------------

if st.sidebar.button(
    "🗑️ Xóa cuộc trò chuyện",
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
# 7. DISPLAY TOOL EXECUTION DETAILS
# =========================================================

def display_tool_details(message: dict):
    """
    Hiển thị chi tiết quá trình gọi Tool.
    Đặt trong expander để không làm rối giao diện chat.
    """

    rounds = message.get("rounds", [])

    if not rounds:
        return

    with st.expander(
        "🔧 Chi tiết thực thi công cụ",
        expanded=False,
    ):

        st.caption(
            "Thông tin kỹ thuật dành cho việc kiểm tra "
            "và đánh giá hoạt động của Agent."
        )

        for round_data in rounds:

            st.markdown(
                f"### Vòng thực thi {round_data.get('round', '?')}"
            )

            assistant_text = round_data.get(
                "assistant_text"
            )

            if assistant_text:

                st.markdown(
                    "**Thông điệp của Agent:**"
                )

                st.write(assistant_text)

            calls = round_data.get(
                "tool_calls",
                [],
            )

            if calls:

                st.markdown("**Các công cụ được gọi:**")

                for index, call in enumerate(calls, 1):

                    tool_name = call.get(
                        "name",
                        "Unknown Tool",
                    )

                    st.markdown(
                        f"Tool {index}: `{tool_name}`"
                    )

                    with st.expander(
                        f"Tham số Tool {index}",
                        expanded=False,
                    ):

                        st.json(
                            call.get("args", {})
                        )

            results = round_data.get(
                "tool_results",
                [],
            )

            if results:

                st.markdown("**Kết quả thực thi:**")

                for index, event in enumerate(results, 1):

                    tool_name = event.get(
                        "tool",
                        "Unknown Tool",
                    )

                    st.markdown(
                        f"Result {index}: `{tool_name}`"
                    )

                    with st.expander(
                        f"Xem kết quả {index}",
                        expanded=False,
                    ):

                        st.json(
                            event.get("result", {})
                        )


# =========================================================
# 8. DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.chat_messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

        if message["role"] == "assistant":

            if message.get("error"):
                st.warning(
                    "Lượt xử lý này chưa hoàn thành. "
                    "Bạn có thể thử gửi lại yêu cầu."
                )

            display_tool_details(message)


# =========================================================
# 9. CHAT INPUT AND AGENT EXECUTION
# =========================================================

user_text = st.chat_input(
    "Nhập câu hỏi hoặc yêu cầu của bạn..."
)

if user_text:

    # -----------------------------------------------------
    # Display user message
    # -----------------------------------------------------

    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_text,
    })

    with st.chat_message("user"):
        st.markdown(user_text)

    # -----------------------------------------------------
    # Prepare model messages
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Initialize turn record
    # -----------------------------------------------------

    turn_record = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    # -----------------------------------------------------
    # Run Agent
    # -----------------------------------------------------

    try:

        with st.chat_message("assistant"):

            with st.spinner(
                "🤖 Research Agent đang xử lý yêu cầu..."
            ):

                result = run_model_tool_loop(
                    provider=st.session_state.provider,
                    messages=messages,
                    tools=st.session_state.openai_tools,
                    model=active["model"] or None,
                    max_tool_rounds=active["max_tool_rounds"],
                )

            # Lưu kết quả gốc vào transcript
            turn_record.update(result)

            # Chuẩn hóa nội dung hiển thị
            assistant_text, message_type = (
                get_agent_display_message(result)
            )

            # Hiển thị phản hồi
            if message_type == "info":
                st.info(assistant_text)

            elif message_type == "warning":
                st.warning(assistant_text)

            else:
                st.markdown(assistant_text)

            # Cảnh báo nếu một số Tool thực thi thất bại
            if has_tool_errors(result):

                st.warning(
                    "Một số công cụ chưa thực thi thành công. "
                    "Kết quả trả về có thể chưa đầy đủ."
                )

            # Chi tiết Tool Execution
            display_tool_details(turn_record)

            # -------------------------------------------------
            # Update chat messages
            # -------------------------------------------------

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": assistant_text,
                "rounds": result.get("rounds", []),
                "status": result.get("status"),
            })

            # -------------------------------------------------
            # Update conversation history
            # -------------------------------------------------

            st.session_state.history.append({
                "role": "user",
                "content": user_text,
            })

            st.session_state.history.append({
                "role": "assistant",
                "content": assistant_text,
            })

    # -----------------------------------------------------
    # Handle errors
    # -----------------------------------------------------

    except Exception as exc:

        error_message = (
            f"{type(exc).__name__}: {str(exc)}"
        )

        # Lưu lỗi kỹ thuật vào transcript
        turn_record.update({
            "status": "provider_error",
            "error": error_message,
        })

        title, description = get_friendly_error(exc)

        friendly_message = (
            f"**{title}**\n\n{description}"
        )

        with st.chat_message("assistant"):

            st.error(friendly_message)

        # Không hiển thị lỗi kỹ thuật cho người dùng
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": friendly_message,
            "error": True,
        })

    # -----------------------------------------------------
    # Save transcript
    # -----------------------------------------------------

    finally:

        turn_record["ended_at"] = now_iso()

        st.session_state.transcript["turns"].append(
            turn_record
        )

        st.session_state.transcript["updated_at"] = now_iso()

        write_transcript(
            st.session_state.transcript_path,
            st.session_state.transcript,
        )

    st.rerun()
