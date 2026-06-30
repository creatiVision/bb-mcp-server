Title: 🧪 Add tests for bb_add_comment

Description:
🎯 **What:** The `bb_add_comment` function handles adding comments to receipts and transactions but lacked test coverage. A new file `tests/test_comments.py` was created to implement the required tests using `pytest` and `unittest.mock.patch`.
📊 **Coverage:** Covered the happy paths (payload formatting and calling the internal `_api_post` function correctly using `receipt_id_by_customer`, and similarly with `transaction_id_by_customer`) as well as the error condition when the simulated API connection raises an exception.
✨ **Result:** Improved test coverage and reliability for the comments functionality. This ensures that the comment creation logic correctly routes external API calls and gracefully handles errors, preventing future regressions.
