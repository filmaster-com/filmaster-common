# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Settings'
        db.create_table(u'settings_settings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('namespace', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'settings', ['Settings'])

        # Adding unique constraint on 'Settings', fields ['namespace', 'key']
        db.create_unique(u'settings_settings', ['namespace', 'key'])


    def backwards(self, orm):
        # Removing unique constraint on 'Settings', fields ['namespace', 'key']
        db.delete_unique(u'settings_settings', ['namespace', 'key'])

        # Deleting model 'Settings'
        db.delete_table(u'settings_settings')


    models = {
        u'settings.settings': {
            'Meta': {'unique_together': "[('namespace', 'key')]", 'object_name': 'Settings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'namespace': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'value': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['settings']