"""web_search — the agent's window to the internet, via DuckDuckGo (ddgs).

No API key needed, which keeps the workshop friction at zero. Compare
this file to search.py: same shape, different data source. To the model
they are indistinguishable — every tool is just schema in, string out.
"""

from ddgs import DDGS

from strands import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return titles, URLs, and snippets.

    Args:
        query: The search query.
        max_results: Number of results to return (default 5).
    """
    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:  # network errors, rate limits
        return f"Web search failed: {e}"

    if not results:
        return f"No results for {query!r}."
    return "\n\n".join(
        f"{r['title']}\n{r['href']}\n{r['body']}" for r in results
    )
