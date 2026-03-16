from ask_sdk_core.dispatch_components import AbstractExceptionHandler, AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model import Response
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import ALEXA_NAME, ALEXA_SKILL_ID
from app.services.gemini_service import GeminiService

router = APIRouter()


def respond(handler_input: HandlerInput, text: str, end_session: bool = True) -> Response:
    return (
        handler_input.response_builder
        .speak(text)
        .set_should_end_session(end_session)
        .response
    )


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return respond(handler_input, f"Wat is je vraag voor {ALEXA_NAME}?", end_session=False)


class GeminiChatHandler(AbstractRequestHandler):
    def __init__(self):
        self.gemini_service = GeminiService()

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("CatchAllIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        slots = handler_input.request_envelope.request.intent.slots
        user_query = ""

        if slots and "query" in slots and slots["query"].value:
            user_query = slots["query"].value
        else:
            return respond(handler_input, "Ik heb je niet gehoord. Wat zei je?", end_session=False)

        try:
            ai_text = self.gemini_service.generate(prompt=user_query)
            return respond(handler_input, ai_text)

        except Exception as e:
            print(f"Gemini Error: {e}")
            return respond(handler_input, "Fout bij Google Service, ik kan je vraag nu niet beantwoorden.")


class StopCancelHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            is_intent_name("AMAZON.StopIntent")(handler_input) or
            is_intent_name("AMAZON.CancelIntent")(handler_input)
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        return respond(handler_input, f"Tot de volgende keer, dit was {ALEXA_NAME}!")


class HelpHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return respond(handler_input, f"Stel een vraag en {ALEXA_NAME} zal antwoorden.", end_session=False)


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        request = handler_input.request_envelope.request
        if hasattr(request, "intent") and request.intent:
            print(f"[{type(exception).__name__}] Intent: {request.intent.name} — {exception}")
        else:
            print(f"[{type(exception).__name__}] Request: {request.object_type} — {exception}")

        return respond(handler_input, "Er is iets misgegaan, probeer het opnieuw.")


def build_skill_handler():
    sb = SkillBuilder()
    sb.skill_id = ALEXA_SKILL_ID
    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(GeminiChatHandler())
    sb.add_request_handler(StopCancelHandler())
    sb.add_request_handler(HelpHandler())
    sb.add_request_handler(SessionEndedRequestHandler())
    sb.add_exception_handler(CatchAllExceptionHandler())
    skill_handler = WebserviceSkillHandler(skill=sb.create())
    return skill_handler


@router.post("/alexa")
async def alexa_endpoint(request: Request):
    body_str = (await request.body()).decode("utf-8")
    try:
        skill_handler = build_skill_handler()
        json_response = skill_handler.verify_request_and_dispatch(
            http_request_headers=dict(request.headers),
            http_request_body=body_str
        )
        return JSONResponse(content=json_response)
    except Exception as e:
        print(f"[{type(e).__name__}] Alexa dispatch failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid Request Signature") from e
