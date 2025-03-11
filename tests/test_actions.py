import unittest
from unittest.mock import Mock, MagicMock
from googleapiclient.errors import HttpError
from actions import mark_as_read, mark_as_unread, move_message

class TestGmailActions(unittest.TestCase):

    def test_mark_as_read(self):
        # Mock the Gmail API service
        mock_service = Mock()
        mock_batch_modify = mock_service.users().messages().batchModify
        mock_batch_modify.return_value.execute.return_value = {}

        message_ids = ['123', '456']
        mark_as_read(mock_service, message_ids)

        mock_batch_modify.assert_called_once_with(
            userId='me',
            body={
                'ids': message_ids,
                'removeLabelIds': ['UNREAD']
            }
        )

    def test_mark_as_unread(self):
        # Mock the Gmail API service
        mock_service = Mock()
        mock_batch_modify = mock_service.users().messages().batchModify
        mock_batch_modify.return_value.execute.return_value = {}

        message_ids = ['123', '456']
        mark_as_unread(mock_service, message_ids)

        mock_batch_modify.assert_called_once_with(
            userId='me',
            body={
                'ids': message_ids,
                'addLabelIds': ['UNREAD']
            }
        )

    def test_move_message_to_promotions(self):
        # Mock the Gmail API service
        mock_service = Mock()
        mock_batch_modify = mock_service.users().messages().batchModify
        mock_batch_modify.return_value.execute.return_value = {}

        message_ids = ['123', '456']
        move_message(mock_service, message_ids, "Promotions")

        mock_batch_modify.assert_called_once_with(
            userId='me',
            body={
                'ids': message_ids,
                'addLabelIds': ['CATEGORY_PROMOTIONS'],
                'removeLabelIds': ['INBOX']
            }
        )

if __name__ == '__main__':
    unittest.main()
