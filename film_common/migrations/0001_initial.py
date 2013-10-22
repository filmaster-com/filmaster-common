# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RedisCacheDumps'
        db.create_table('film_common_rediscachedumps', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('dump', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('film_common', ['RedisCacheDumps'])


    def backwards(self, orm):
        # Deleting model 'RedisCacheDumps'
        db.delete_table('film_common_rediscachedumps')


    models = {
        'film_common.rediscachedumps': {
            'Meta': {'object_name': 'RedisCacheDumps'},
            'dump': ('django.db.models.fields.TextField', [], {}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256', 'primary_key': 'True'})
        }
    }

    complete_apps = ['film_common']
