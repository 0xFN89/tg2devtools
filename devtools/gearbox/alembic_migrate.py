"""
TurboGears migration

gearbox migrate command integrates alembic migrations into TurboGears 2.

"""
from __future__ import print_function
from gearbox.command import Command
import argparse

class MigrateCommand(Command):
    """Create and apply SQLAlchemy migrations
    Migrations will be managed inside the 'migration/versions' directory

    Usage: gearbox migrate COMMAND ...
    Use 'gearbox help migrate' to get list of commands and their usage
    """
    def get_description(self):
        return '''Create and apply SQLAlchemy migrations.

Migrations will be managed inside the 'migration/versions' directory
and applied to the database defined by sqlalchemy.url inside the
configuration file.

Create a new migration::

    $ gearbox migrate create 'Add New Things'

Apply migrations::

    $ gearbox migrate upgrade

Get current database version::

    $ gearbox migrate db_version

Downgrade version::

    $ gearbox migrate downgrade
'''

    def get_parser(self, prog_name):
        parser = super(MigrateCommand, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter

        parser.add_argument("-c", "--config",
            help='application config file to read (default: development.ini)',
            dest='config', default="development.ini")

        subparser = parser.add_subparsers(dest='command')

        create_parser = subparser.add_parser('create', add_help=False)
        create_parser.add_argument('name')

        db_version_parser = subparser.add_parser('db_version', add_help=False)

        upgrade_parser = subparser.add_parser('upgrade', add_help=False)
        upgrade_parser.add_argument('version', nargs='?', default='head')

        downgrade_parser = subparser.add_parser('downgrade', add_help=False)
        downgrade_parser.add_argument('version', nargs='?', default='-1')

        test_parser = subparser.add_parser('test', add_help=False)

        return parser

    def take_action(self, opts):
        from alembic.config import Config
        from alembic import command as alembic_commands

        self.alembic_commands = alembic_commands
        self.alembic_cfg = Config(opts.config, ini_section='app:main')
        self.alembic_cfg.set_main_option('script_location', 'migration')

        command = getattr(self, 'command_%s' % opts.command)
        command(opts)

    def command_create(self, opts):
        self.alembic_commands.revision(self.alembic_cfg, opts.name)

    def command_db_version(self, opts):
        self.alembic_commands.current(self.alembic_cfg)

    def command_upgrade(self, opts):
        self.alembic_commands.upgrade(self.alembic_cfg, opts.version)

    def command_downgrade(self, opts):
        self.alembic_commands.downgrade(self.alembic_cfg, opts.version)

    def command_test(self, opts):
        self.alembic_commands.upgrade(self.alembic_cfg, '+1')
        self.alembic_commands.downgrade(self.alembic_cfg, '-1')