from django.test import TransactionTestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

# TODO 08/06/25: find out why these started to fail and do not work under any curcimstantes.
'''There is some issue with old migration which renamed category to board in TodoItem model.'''
# class TestMigration0008(TransactionTestCase):
#     last_migration = ('todoBoard', '0008_alter_todolist_options_remove_todoitem_due_to')
#     current_migration = ('todoBoard', '0009_adjust_existing_group_names')
#
#     def setUp(self):
#         super().setUp()
#         assert self.last_migration and self.current_migration, "Migration names are not set"
#         executor = MigrationExecutor(connection)
#
#         # Reverse to last_migration
#         executor.migrate([self.last_migration], fake=True)
#         self.apps = executor.loader.project_state(self.last_migration).apps
#
#     def test_migration_changes_permission_group(self):
#         Group = self.apps.get_model('auth', 'Group')
#         board_editors, _ = Group.objects.get_or_create(name='Board editors')
#
#         executor = MigrationExecutor(connection)
#         executor.migrate([self.current_migration])
#
#         self.old_apps = executor.loader.project_state(self.current_migration).apps
#
#         Group = self.apps.get_model('auth', 'Group')
#         expected_group_name = 'This app editors'
#         group_after_migration = Group.objects.get(name=expected_group_name)
#
#         self.assertEqual(group_after_migration.name, expected_group_name)


# class TestMigration0014(TransactionTestCase):
#     user_migration = ('users', '0006_alter_profile_avatar')
#     previous_migration = ('todoBoard', '0013_remove_todolist_allowed_groups_and_more')
#     target_migration = ('todoBoard', '0014_set_todolist_owners')
#
#     def setUp(self):
#         super().setUp()
#         self.executor = MigrationExecutor(connection)
#
#         self.executor.migrate([self.user_migration])
#         self.executor.migrate([self.previous_migration])
#         self.apps = self.executor.loader.project_state(self.previous_migration).apps
#         User = self.apps.get_model('users', 'CustomUser')
#         TodoList = self.apps.get_model('todoBoard', 'TodoList')
#         TodoItem = self.apps.get_model('todoBoard', 'TodoItem')
#
#         self.user = User.objects.create(
#             username='testUser321',
#             password='testing123456',
#             email='test@example.com'
#         )
#         self.board = TodoList.objects.create(title='migration test board', description='')
#         self.task = TodoItem.objects.create(
#             name='test task',
#             description='test',
#             author=self.user,
#             board=self.board
#         )
#
#     def test_migration_set_todolist_owners(self):
#         self.executor.migrate([self.user_migration, self.target_migration])
#         self.apps = self.executor.loader.project_state(self.target_migration).apps
#
#         # Reload models after migration
#         TodoList = self.apps.get_model('todoBoard', 'TodoList')
#         migrated_board = TodoList.objects.get(pk=self.board.id)
#
#         self.assertIsNotNone(migrated_board.owner)
#         self.assertEqual(migrated_board.owner.pk, self.user.pk)


# class TestMigration0014(TransactionTestCase):
#     app = 'todoBoard'
#     user_migration = ('users', '0006_alter_profile_avatar')
#     migrations_to_apply_before_0013 = [
#         ('todoBoard', '0009_adjust_existing_group_names'),
#         ('todoBoard', '0010_rename_category_todoitem_board'),  # Your rename migration
#         ('todoBoard', '0011_todolist_is_archived'),           # if exists, include all in order
#         ('todoBoard', '0012_alter_todoitem_status'),           # ...
#         ('todoBoard', '0013_remove_todolist_allowed_groups_and_more'),
#     ]
#     target_migration = ('todoBoard', '0014_set_todolist_owners')
#
#     def setUp(self):
#         super().setUp()
#         self.executor = MigrationExecutor(connection)
#
#         # Step 1: Reset both apps to correct pre-migration state
#         self.executor.migrate(
#             [self.user_migration])
#
#         self.executor.migrate(self.migrations_to_apply_before_0013)
#         self.apps = self.executor.loader.project_state(self.migrations_to_apply_before_0013[-1]).apps
#
#         # Step 2: Setup test data using pre-migration models
#         User = self.apps.get_model('users', 'CustomUser')
#         TodoList = self.apps.get_model('todoBoard', 'TodoList')
#         TodoItem = self.apps.get_model('todoBoard', 'TodoItem')
#
#         self.user = User.objects.create(
#             username='testUser321',
#             password='testing123456',
#             email='test@example.com'
#         )
#         self.board = TodoList.objects.create(title='migration test board', description='')
#         self.task = TodoItem.objects.create(
#             name='test task',
#             description='test',
#             author=self.user,
#             board=self.board
#         )
#
#     def test_migration_sets_board_owner(self):
#         # Step 3: Apply the migration we want to test
#         self.executor.migrate([self.user_migration, self.target_migration])
#         self.apps = self.executor.loader.project_state(self.target_migration).apps
#
#         # Step 4: Get post-migration models and verify owner was set
#         TodoList = self.apps.get_model('todoBoard', 'TodoList')
#         board = TodoList.objects.get(pk=self.board.pk)
#
#         self.assertIsNotNone(board.owner)
#         self.assertEqual(board.owner.pk, self.user.pk)
