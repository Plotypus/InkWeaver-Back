 # Data Model

These are the data models for documents in the database.

## User

```json
{
  "_id": ObjectId,
  "username": "example_username",
  "password": "...",
  "name": "John Doe",
  "email": "johndoe@email.com",
  "pen_name": "",
  "stories": [ ObjectId ],
  "wikis": [ ObjectId ],
  "avatar": {...},
  "bio": {...},
  "preferences": {...},
  "statistics": {...}
}
```

| Field             | Description |
|-------------------|-------------|
| `_id`             | a unique id of the user |
| `username`        | the username of the user |
| `password`        | the salted hash of user's password |
| `name`            | the name of the user |
| `email`           | the email address of the user |
| `pen_name`        | the desired pen name of the user |
| `stories`         | the ids of stories the user has access to (*) |
| `wikis`           | the ids of wikis the user has access to (*) |
| `avatar`          | ** not yet implemented |
| `bio`             | ** not yet implemented |
| `preferences`     | ** not yet implemented |
| `statistics`      | ** not yet implemented |

## Story

```json
{
  "_id": ObjectId,
  "owner": {
    "user_id": ObjectId,
    "publication_name": "Spiderman"
  },
  "wiki_id": ObjectId,
  "collaborators": [ 
    {
      "user_id": ObjectId,
      "publication_name": "J. Jonah Jameson"
    }
  ],
  "title": "Example Story Title",
  "synopsis": "This is an example of a synopsis.",
  "head_chapter": ObjectId,
  "tail_chapter": ObjectId,
  "statistics": {...},
  "settings": {...}
}
```

| Field             | Description |
|-------------------|-------------|
| `_id`             | a unique id of the story |
| `owner`           | the unique id and publication name of the story owner |
| `wiki_id`         | the unique id of the associated wiki |
| `collaborators`   | the ids and publication names of other users with access to the story |
| `title`           | the title of the story |
| `synopsis`        | a brief summary of the story |
| `head_chapter`    | the unique id of the story's first chapter |
| `tail_chapter`    | the unique id of the story's last chapter |
| `chapters`        | ids of the story's chapters |
| `statistics`      | ** not yet implemented |
| `settings`        | ** not yet implemented |

## Chapter

```json
{
  "_id": ObjectId,
  "story_id": ObjectId,
  "head_paragraph": ObjectId,
  "tail_paragraph": ObjectId,
  "preceded_by": ObjectId,
  "succeeded_by": ObjectId,
  "title": "Chapter Twenty",
  "statistics": {...}
}
```

| Field             | Description |
|-------------------|-------------|
| `_id`             | a unique id of the chapter |
| `story_id`        | the unique id of the parent story |
| `head_paragraph`  | the unique id of the chapter's first paragraph |
| `tail_paragraph`  | the unique id of the chapter's last paragraph |
| `preceded_by`     | the unique id of the preceding chapter in the story |
| `succeeded_by`    | the unique id of the succeeding chapter in the story |
| `title`           | the title of the chapter |
| `statistics`      | ** not yet implemented |

## Paragraph

```json
{
  "_id": ObjectId,
  "chapter_id": ObjectId,
  "preceded_by": ObjectId,
  "succeeded_by": ObjectId,
  "text": "For as long as I could remember, ...",
  "statistics": {...}
}
```

| Field             | Description |
|-------------------|-------------|
| `_id`             | a unique id of the paragraph |
| `chapter_id`      | the unique id of the parent chapter |
| `preceded_by`     | the unique id of the preceding paragraph in the chapter |
| `succeeded_by`    | the unique id of the succeeding paragraph in the chapter |
| `text`            | the contents of the paragraph |
| `statistics`      | ** not yet implemented |

