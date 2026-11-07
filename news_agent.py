
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from dotenv import load_dotenv
from agno.models.groq import Groq
from news_toolkit import NewsToolkit


load_dotenv()


news_agent = Agent(
    name="Daily News Curator",

    model=Groq(id="openai/gpt-oss-120b"),

    tools=[
        NewsToolkit()
    ],

    instructions=[
        "You are an AI-powered news curation agent.",

        "Your responsibility is to collect and curate news "
        "from multiple configured sources.",

        "When the user requests news collection:",

        "1. Invoke collect_all_news().",

        "2. Wait for the collection and processing pipeline "
        "to finish.",

        "3. Report the total number of articles collected.",

        "4. Report the number of articles saved and skipped.",

        "5. Report the number of unique news clusters.",

        "6. Report the number of independent articles.",

        "7. Present the consolidated summaries generated "
        "by the processing pipeline.",

        "8. Include the original article sources and URLs.",

        "9. Clearly report any collection or processing errors.",

        "Never invent article information or statistics.",

        "Never claim that processing succeeded if the "
        "pipeline returned an error."
    ],

    tool_choice="required",
    tool_call_limit=1,
    markdown=True
)


if __name__ == "__main__":

    news_agent.print_response(
        "Collect the latest news from all configured sources.",
        stream=True
    )
