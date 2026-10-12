import unittest

from pydantic import ValidationError

from app.schemas.classes import ClassCreate, ClassResponse, SubclassResponse


class ClassSchemaTests(unittest.TestCase):
    def test_class_create_trims_names_and_accepts_root_id(self) -> None:
        request = ClassCreate(
            parent_id=0,
            parent_name="  首頁 ",
            name=" 校務  ",
        )

        self.assertEqual(request.parent_id, 0)
        self.assertEqual(request.parent_name, "首頁")
        self.assertEqual(request.name, "校務")

    def test_class_create_rejects_negative_parent_id_and_blank_names(self) -> None:
        with self.assertRaises(ValidationError):
            ClassCreate(parent_id=-1, parent_name="首頁", name="校務")
        with self.assertRaises(ValidationError):
            ClassCreate(parent_id=0, parent_name="首頁", name="   ")

    def test_class_responses_validate_expected_fields(self) -> None:
        created = ClassResponse(
            cid=1,
            name="校務",
            idpath="0/1",
            namepath="首頁/校務",
        )
        child = SubclassResponse(
            pcid=0,
            parent_name="首頁",
            cid=1,
            child_name="校務",
        )

        self.assertEqual(created.idpath, "0/1")
        self.assertEqual(child.child_name, "校務")

    def test_openapi_contains_w5_endpoints(self) -> None:
        from app.main import app

        paths = app.openapi()["paths"]

        self.assertIn("/api/classes", paths)
        self.assertIn("/api/subclass/pcid/{parent_id}", paths)


if __name__ == "__main__":
    unittest.main()
