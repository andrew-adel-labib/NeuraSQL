from fastapi import APIRouter

from fastapi import HTTPException

from pydantic import BaseModel

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


router = APIRouter()



class AskRequest(BaseModel):

    question: str

    provider: str = "claude"



@router.post("/ask")
async def ask_question(
    payload: AskRequest
):

    try:

        question = (
            payload.question.strip()
        )

        provider = (
            payload.provider.lower()
        )

        if not question:

            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty."
            )


        sql = generate_sql(
            question=question,
            model_provider=provider
        )


        validate(sql)


        rows, columns = execute_sql(
            sql
        )


        summary = summarize_answer(
            question=question,
            rows=rows,
            model_provider=provider
        )


        return {

            "success": True,

            "question": question,

            "provider": provider,

            "sql": sql,

            "columns": columns,

            "rows": rows,

            "summary": summary
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,

            detail=str(e)
        )