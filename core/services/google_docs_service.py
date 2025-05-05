"""Google Docs Service Module with Google API integration.

Key features:
- Document ID extraction from Google Docs URLs
- Full document content replacement
- Integration with the unified Google authentication system

This implementation treats all content as plain text when writing to Google Docs,
meaning that markdown or other formatting in the input text will not be rendered
as rich formatting in the resulting document.

Authors:
    - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
"""

import re
from typing import Optional

from core.services.google_service import get_google_service


def extract_google_docs_id_from_url(url: str) -> Optional[str]:
    """Extract the document ID from a Google Docs URL.

    Parses a Google Docs URL to retrieve the unique document identifier that can
    be used with the Google Docs API. Supports standard Google Docs sharing and
    editing URLs.

    Args:
        url (str): The complete Google Docs URL from which to extract the ID.
            Example: 'https://docs.google.com/document/d/1ABC123def456XYZ/edit'

    Returns:
        Optional[str]: The extracted document ID if found in the URL, or None if
            the URL does not contain a valid Google Docs document identifier.
    """
    match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None


def update_google_docs_content(doc_id: str, text_content: str) -> None:
    """Replace all content in a Google Docs document with new text.

    Completely overwrites the content of the specified Google Docs document with
    the provided text. This operation first clears all existing content from the
    document (except for a required trailing newline character as per the Google
    Docs API requirements), then inserts the new content starting from the beginning
    of the document.

    This method is useful for scenarios where a complete refresh of document content
    is needed, such as report generation or content archiving workflows.

    Args:
        doc_id (str): The unique Google Docs document ID to update. This can be
            extracted from a Google Docs URL using extract_doc_id_from_url().
        text_content (str): The new content to write to the document. Any formatting
            including markdown will be treated as plain text and not rendered with
            Google Docs styling.

    Raises:
        googleapiclient.errors.HttpError: If the API request fails due to authentication,
            permission, or other Google API issues.
    """
    service = get_google_service('docs', 'v1')
    doc = service.documents().get(documentId=doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])
    if body_content:
        end_index = body_content[-1].get('endIndex', 1)
        clear_end_index = max(1, end_index - 1)
    else:
        clear_end_index = 1

    requests = [
        {
            "deleteContentRange": {
                "range": {
                    "startIndex": 1,
                    "endIndex": clear_end_index
                }
            }
        },
        {
            "insertText": {
                "location": {"index": 1},
                "text": text_content
            }
        }
    ]
    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
