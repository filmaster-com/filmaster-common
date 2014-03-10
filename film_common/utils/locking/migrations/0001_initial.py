# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lock'
        db.create_table(u'locking_lock', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'locking', ['Lock'])


    def backwards(self, orm):
        # Deleting model 'Lock'
        db.delete_table(u'locking_lock')


    models = {
        u'locking.lock': {
            'Meta': {'object_name': 'Lock'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'primary_key': 'True'})
        }
    }

    complete_apps = ['locking']