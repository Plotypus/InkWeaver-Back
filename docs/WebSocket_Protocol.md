# WebSocket Protocol v2

The Loom API for WebSockets ("The LAW") defines a protocol for establishing connection with the Loom backend server and
manipulating user data to create stories and wikis within the Loom architecture. This document describes that protocol
in great detail to provide you (but mostly us) with comprehensive documentation.

## Table of Contents

...

## Reference

| Action                                                            | Description |
|-------------------------------------------------------------------|-------------|
| [`get_user_info`](#get-user-info)                                 | Get relevant information about the current user. |
| [`load_story`](#load-story)                                       | Load a specific story. |
| [`get_all_chapters`](#get-all-chapters)                           | Get a list of all chapters in the current story. |
| [`load_story_with_chapters`](#load-story-with-chapters)           | Load a specific story and get its chapters. |
| [`load_chapter`](#load-chapter)                                   | Load a specific chapter. |
| [`get_all_paragraphs`](#get-all-paragraphs)                       | Get a list of all paragraphs in the current chapter. |
| [`load_chapter_with_paragraphs`](#load-chapter-with-paragraphs)   | Load a specific chapter and get its paragraphs. |
| [`load_paragraph`](#load-paragraph)                               | Load a specific paragraph. |
| [`create_story`](#create-story)                                   | Create a new story owned by the current user. |
| [`create_chapter`](#create-chapter)                               | Create a new chapter in the current story. |
| [`create_end_chapter`](#create-end-chapter)                       | Create a new chapter at the end of the current story. |
| [`create_paragraph`](#create-paragraph)                           | Create a new paragraph in the current chapter. |
| [`create_end_paragraph`](#create-end-paragraph)                   | Create a new paragraph at the end of the current chapter. |
| [`update_story`](#update-story)                                   | Update an existing story. |
| [`update_current_story`](#update-current-story)                   | Update the current story. |
| [`update_chapter`](#update-chapter)                               | Update an existing chapter. |
| [`update_current_chapter`](#update-current-chapter)               | Update the current chapter. |
| [`replace_paragraph`](#replace-paragraph)                         | Replace the text in the current paragraph. |
| [`delete_story`](#delete-story)                                   | Delete an existing story. |
| [`delete_current_story`](#delete-current-story)                   | Delete the current story. |
| [`delete_chapter`](#delete-chapter)                               | Delete an existing chapter. |
| [`delete_current_chapter`](#delete-current-chapter)               | Delete the current chapter. |
| [`delete_paragraph`](#delete-paragraph)                           | Delete an existing paragraph. |
| [`delete_current_paragraph`](#delete-current-paragraph)           | Delete the current paragraph. |

#### Get User Info

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
  "pen_name": "Schmozo",
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

#### Load Story

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

#### Get All Chapters

Prerequisites: Logged-in, story loaded

```json
{
  "message_id": 1,
  "action": "get_all_chapters"
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

#### Load Chapter

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

#### Get All Paragraphs

Prerequisites: Logged-in, story loaded, chapter loaded

```json
{
  "message_id": 1,
  "action": "get_all_paragraphs"
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

#### Load Paragraph

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

#### Create End Chapter

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

#### Create End Paragraph

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
