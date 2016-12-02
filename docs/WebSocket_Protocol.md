# WebSocket Protocol v2

The Loom API for WebSockets ("The LAW") defines a protocol for establishing connection with the Loom backend server and
manipulating user data to create stories and wikis within the Loom architecture. This document describes that protocol
in great detail to provide you (but mostly us) with comprehensive documentation.

## Table of Contents

...

## Reference

| Action | Description |
|--------|-------------|

---

#### Load User Info

Prerequisite: Logged-in

When a user logs in, the server sends them back their own user information.

```json
{
  "message_id": 1,
  "action": "get_user_info"
}
```

```json
{
  "reply_to": 1,
  "username": "user123",
  "avatar": "user123.jpg",
  "email": "user123@email.com",
  "name": "Joe Schmoe",
  "stories": [
    {story-summary}
  ],
  "wikis": [
    {wiki-summary}
  ],
  "bio": {...},
  "statistics": {...},
  "preferences": {...}
}
```

#### Load Story (Without Chapters)

Prerequisite: Logged-in

```json
{
  "message_id": 1,
  "action": "load_story",
  "story": {...}
}
```

```json
{
  "reply_to": 1,
  "title": "My Great Story",
  "owner": {...},
  "coauthors": [
    {...}
  ],
  "statistics": {...},
  "settings": {...},
  "synopsis": {...},
  "wiki": {...}
}
```

#### Get All Chapters in Story

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "get_chapters"
}
```

```json
{
  "reply_to": 1,
  "chapters": [
    {...}
  ]
}
```

#### Load Story (With Chapters)

Prerequisite: Logged-in

```json
{
  "message_id": 1,
  "action": "load_story_with_chapters",
  "story": {...}
}
```

```json
{
  "reply_to": 1,
  "title": "My Great Story",
  "owner": {...},
  "coauthors": [
    {...}
  ],
  "statistics": {...},
  "settings": {...},
  "synopsis": {...},
  "wiki": {...},
  "chapters": [
    {...}
  ]
}
```

#### Load Chapter (Without Paragraphs)

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "load_chapter",
  "chapter": {...}
}
```

```json
{
  "reply_to": 1,
  "title": "Chapter 1",
  "statistics": {...}
}
```

#### Load All Paragraphs in Chapter

Prerequisites: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "get_paragraphs"
}
```

```json
{
  "reply_to": 1,
  "paragraphs": [
    {...}
  ]
}
```

#### Load Chapter (With Paragraphs)

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "load_chapter_with_paragraphs",
  "chapter": {...}
}
```

```json
{
  "reply_to": 1,
  "title": "Chapter 1",
  "statistics": {...},
  "paragraphs": [
    {...}
  ]
}
```

#### Load Paragraph (Without Text)

Prerequisites: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "load_paragraph",
  "paragraph": {...}
}
```

```json
{
  "reply_to": 1,
  "paragraph": {...}
}
```

#### Load Paragraph (With Text)

(Unimplemented)

#### Create Story

Prerequisites: Logged-in

```json
{
  "message_id": 1,
  "action": "create_story",
  "story": {
    "title": "My Great Story 2",
    "synopsis": {...},
    "publication_name": "John Doe",
    "settings": {...},
    "wiki": {...}
  }
}
```

Note: See [Load Story (Without Chapters)](#load-story-without-chapters) for the response.

#### Create Chapter

Prerequisites: Logged-in, story loaded, (chapter loaded)

Note: If a chapter is loaded, inserts chapter after current chapter. If a chapter is not loaded, inserts chapter at the
end of the story.

```json
{
  "message_id": 1,
  "action": "create_chapter",
  "title": "Chapter 1"
}
```

Note: See [Load Chapter (Without Paragraphs)](#load-chapter-without-paragraphs) for the response.

#### Create Chapter at End of Story

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "create_end_chapter",
  "title": "Chapter 7"
}
```

Note: See [Load Chapter (Without Paragraphs)](#load-chapter-without-paragraphs) for the response.

#### Create Paragraph

Prerequisites: Logged-in, story loaded, chapter loaded, (paragraph loaded)

Note: If a paragraph is loaded, inserts paragraph after current paragraph. If a paragraph is not loaded, inserts
paragraph at the end of the chapter.

```json
{
  "message_id": 1,
  "action": "create_paragraph"
}
```

Note: See [Load Paragraph (Without Text)](#load-paragraph-without-text)

#### Create Paragraph at End of Chapter

Prerequisites: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "create_end_paragraph"
}
```

Note: See [Load Paragraph (Without Text)](#load-paragraph-without-text)

#### Update Story

Prerequisites: Logged-in

```json
{
  "message_id": 1,
  "action": "update_story",
  "story": {...},
  "changes": {...}
}
```

#### Update Current Story

Prerequisite: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "update_current_story",
  "changes": {...}
}
```

#### Update Chapter

Prerequisite: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "update_chapter",
  "chapter": {...},
  "changes": {...}
}
```

#### Update Current Chapter

Prerequisite: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "update_current_chapter",
  "changes": {...}
}
```

#### Update Paragraph

(unimplemented)

#### Replace Paragraph

Prerequisite: Logged-in, story loaded, chapter loaded, paragraph loaded

```json
{
  "message_id": 1,
  "action": "replace_paragraph",
  "text": "Some text for the paragraph."
}
```

#### Delete Story

Prerequisites: Logged-in

```json
{
  "message_id": 1,
  "action": "delete_story",
  "story": {...}
}
```

#### Delete Current Story

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "delete_current_story"
}
```

#### Delete Chapter

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "delete_chapter",
  "chapter": {...}
}
```

#### Delete Current Chapter

Prerequisites: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "delete_current_chapter"
}
```

#### Delete Paragraph

Prerequisites: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "delete_paragraph",
  "paragraph": {...}
}
```

#### Delete Paragraph

Prerequisites: Logged-in, story loaded, chapter loaded, paragraph loaded

```json
{
  "message_id": 1,
  "action": "delete_current_paragraph"
}
```
