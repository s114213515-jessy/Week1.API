import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from app.schemas.note import NoteCreate, NoteResponse
from app.schemas.taxonomy import CategoryCreate, TagCreate


class NoteSchemaTests(unittest.TestCase):
    def test_existing_note_payload_remains_valid(self) -> None:
        note = NoteCreate(title="  REST API  ", content="Notes")

        self.assertEqual(note.title, "REST API")
        self.assertIsNone(note.category_id)
        self.assertEqual(note.tag_ids, [])

    def test_relationship_ids_are_accepted(self) -> None:
        note = NoteCreate(
            title="Relational design",
            category_id=2,
            tag_ids=[3, 4],
        )

        self.assertEqual(note.category_id, 2)
        self.assertEqual(note.tag_ids, [3, 4])

    def test_duplicate_tag_ids_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            NoteCreate(title="Duplicate", tag_ids=[1, 1])

    def test_non_positive_relationship_ids_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            NoteCreate(title="Invalid category", category_id=0)
        with self.assertRaises(ValidationError):
            NoteCreate(title="Invalid tag", tag_ids=[-1])

    def test_more_than_fifty_tags_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            NoteCreate(title="Too many", tag_ids=list(range(1, 52)))

    def test_note_response_contains_nested_relationships(self) -> None:
        note = NoteResponse.model_validate(
            {
                "id": 1,
                "title": "Relational design",
                "content": None,
                "created_at": datetime.now(timezone.utc),
                "category": {"id": 2, "name": "Course"},
                "tags": [{"id": 3, "name": "PostgreSQL"}],
            }
        )

        self.assertEqual(note.category.name, "Course")
        self.assertEqual(note.tags[0].name, "PostgreSQL")


class TaxonomySchemaTests(unittest.TestCase):
    def test_category_and_tag_names_are_trimmed(self) -> None:
        category = CategoryCreate(name="  Course  ")
        tag = TagCreate(name="  PostgreSQL  ")

        self.assertEqual(category.name, "Course")
        self.assertEqual(tag.name, "PostgreSQL")

    def test_empty_taxonomy_names_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            CategoryCreate(name="   ")
        with self.assertRaises(ValidationError):
            TagCreate(name="   ")


if __name__ == "__main__":
    unittest.main()
