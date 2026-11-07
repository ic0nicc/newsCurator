
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
        "You are an AI-powered news collection agent.",

        "Your primary responsibility is to collect news "
        "from multiple configured sources.",

        "When the user requests news collection:",
        "1. You MUST invoke collect_all_news().",
        "2. The tool collects articles from NewsAPI and RSS feeds.",
        "3. Wait for the tool execution to finish.",
        "4. Analyse the returned collection statistics.",
        "5. Report the number of articles collected.",
        "6. Report the number of articles saved.",
        "7. Report the number of duplicate articles skipped.",

        "If one source fails, report the error and "
        "the results from the other source.",

        "Never invent article information or statistics.",
        "Preserve original article titles, URLs and source names.",
        "Do not claim that an article was saved unless "
        "the tool reports successful database insertion."
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
