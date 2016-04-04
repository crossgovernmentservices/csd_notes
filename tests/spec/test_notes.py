from app.blueprints.notes.models import Note


class WhenUpdatingANote(object):

    def it_stores_the_previous_version(self, db_session):
        note = Note.create('Test note')
        assert len(note.history) == 0

        note.update('Test note edited')
        assert len(note.history) == 1

        assert note.history[0].content == 'Test note'
        assert note.history[0].version == 1


class WhenANoteHasHistory(object):

    def it_can_be_reverted_to_a_previous_version(self, db_session):
        note = Note.create('Test note')
        note.update('Test note edited')
        note.update('Test note edited again')
        assert len(note.history) == 2
        assert note.history[0].version == 0
        assert note.history[1].version == 1

        note.revert()

        assert len(note.history) == 3
        assert note.content == 'Test note edited'

        note.revert(version=2)

        assert len(note.history) == 4
        assert note.content == 'Test note edited again'
