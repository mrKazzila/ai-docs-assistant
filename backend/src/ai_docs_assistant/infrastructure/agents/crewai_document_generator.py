import asyncio

import structlog
from crewai import LLM, Agent, Crew, Task

from ai_docs_assistant.application.interfaces.document_generator import (
    DocumentGenerator,
)

logger = structlog.get_logger(__name__)


class CrewAIDocumentGenerator(DocumentGenerator):
    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str,
        temperature: float = 0.0,
        timeout: float = 60.0,
        max_tokens: int = 300,
    ) -> None:
        self._llm = LLM(
            model=model,
            base_url=base_url,
            temperature=temperature,
            timeout=timeout,
            max_tokens=max_tokens,
            api_key=api_key,
        )

    async def generate(self, query: str) -> str | None:
        logger.info(
            "document_generation_started",
            query=query,
        )

        raw_content = await asyncio.to_thread(
            self._generate_document,
            query,
        )

        if not raw_content:
            logger.error(
                "document_generation_empty_result",
                query=query,
            )
            return None

        is_valid = await asyncio.to_thread(
            self._validate_document,
            raw_content,
        )

        if not is_valid:
            logger.warning(
                "document_generation_validation_failed",
                query=query,
            )
            return None

        logger.info(
            "document_generation_succeeded",
            query=query,
        )
        return raw_content

    def _generate_document(self, query: str) -> str:
        generator = self._create_generator_agent()

        task = Task(
            description=f"Создай документацию для: {query}",
            expected_output="Документ в строгом формате. Ничего больше.",
            agent=generator,
        )

        crew = Crew(agents=[generator], tasks=[task])
        return str(crew.kickoff()).strip()

    def _validate_document(self, content: str) -> bool:
        validator = self._create_validator_agent()

        task = Task(
            description=f"Проверь документ:\n\n{content}",
            expected_output='Только "valid" или "invalid", без пояснений.',
            agent=validator,
        )

        crew = Crew(agents=[validator], tasks=[task])
        result = str(crew.kickoff()).strip().lower()

        return result == "valid"

    def _create_generator_agent(self) -> Agent:
        return Agent(
            role="API-документатор",
            goal="Генерировать документацию в строгом формате.",
            backstory=(
                "Ты специалист по API. "
                "Генерируй документацию ТОЛЬКО в формате:\n"
                "### МЕТОД /путь\n"
                "**Описание**: ... \n"
                "**Параметры**: ... \n"
                "**Ответ**:\n"
                "```json\n{...}\n```"
            ),
            llm=self._llm,
            verbose=False,
        )

    def _create_validator_agent(self) -> Agent:
        return Agent(
            role="Валидатор документации",
            goal="Проверять соответствие документа строгому формату.",
            backstory=(
                "Ты строгий QA-инженер. "
                "Ты должен проверить, что документ содержит:\n"
                '1. Строку вида "### МЕТОД /путь",\n'
                '2. Блок "**Описание**:",\n'
                '3. Блок "**Параметры" или "**Параметры пути**:",\n'
                '4. Блок "**Ответ**:" с JSON-примером в тройных кавычках.\n'
                'Если всё есть — ответь "valid". Иначе — "invalid".'
            ),
            llm=self._llm,
            verbose=False,
        )
