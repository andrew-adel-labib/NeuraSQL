from backend.app.voice.speech_to_text import (
    transcribe_audio
)

from mcp_server.tools.sql_generator import (
    generate_sql
)

from mcp_server.tools.sql_validator import (
    validate
)

from mcp_server.tools.sql_executer import (
    execute_sql
)

from mcp_server.tools.answer_summarizer import (
    summarize_answer
)


class PipecatPipeline:
    """
    Enterprise realtime voice pipeline.

    Flow:
    Audio
    → Speech To Text
    → SQL Generation
    → SQL Validation
    → SQL Execution
    → AI Summary
    """

    async def process_audio(
        self,
        audio_bytes: bytes,
        provider: str = "claude"
    ):

        transcript = await transcribe_audio(
            audio_bytes
        )

        if not transcript:

            return {
                "success": False,
                "message": "No speech detected."
            }

        sql = generate_sql(
            question=transcript,
            model_provider=provider
        )

        validate(sql)

        rows, columns = execute_sql(
            sql
        )

        summary = summarize_answer(
            question=transcript,
            rows=rows,
            model_provider=provider
        )

        return {
            "success": True,

            "question": transcript,

            "provider": provider,

            "sql": sql,

            "columns": columns,

            "rows": rows,

            "summary": summary
        }


pipeline = PipecatPipeline()