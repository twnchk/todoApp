from django.test import TransactionTestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection


class TestMigrations(TransactionTestCase):
    last_migration = ('todoBoard', '0008_alter_todolist_options_remove_todoitem_due_to')
    current_migration = ('todoBoard', '0009_adjust_existing_group_names')

    def setUp(self):
        super().setUp()
        assert self.last_migration and self.current_migration, "Migration names are not set"
        executor = MigrationExecutor(connection)

        # Reverse to last_migration
        executor.migrate([self.last_migration])
        self.apps = executor.loader.project_state(self.last_migration).apps

    def test_migration_changes_permission_group(self):
        Group = self.apps.get_model('auth', 'Group')
        board_editors, _ = Group.objects.get_or_create(name='Board editors')

        executor = MigrationExecutor(connection)
        executor.migrate([self.current_migration])

        self.apps = executor.loader.project_state(self.current_migration).apps

        Group = self.apps.get_model('auth', 'Group')
        expected_group_name = 'This app editors'
        group_after_migration = Group.objects.get(name=expected_group_name)

        self.assertEqual(group_after_migration.name, expected_group_name)
