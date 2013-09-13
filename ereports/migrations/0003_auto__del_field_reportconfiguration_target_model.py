# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'ProcessQueue'
        db.delete_table('ereports_processqueue')

        # Deleting field 'ReportConfiguration.customize_columns'
        db.delete_column('ereports_reportconfiguration', 'customize_columns')

        # Adding field 'ReportConfiguration.select_related'
        db.add_column('ereports_reportconfiguration', 'select_related',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ReportConfiguration.use_distinct'
        db.add_column('ereports_reportconfiguration', 'use_distinct',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ReportConfiguration.ttl'
        db.add_column('ereports_reportconfiguration', 'ttl',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'ReportConfiguration.cache_key'
        db.add_column('ereports_reportconfiguration', 'cache_key',
                      self.gf('django.db.models.fields.CharField')(default='Z2CDR7GKAXP2YKX18PXPYZCJRDJP4FYENVAONRGXQ2HHJ09FVKDW4YM70HKCDKGQHPULRT4AJUDA6ABHLW6O3OHRHKGPYXA3VLKK', unique=True, max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'ProcessQueue'
        db.create_table('ereports_processqueue', (
            ('executed', self.gf('django.db.models.fields.DateField')(default=None, null=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportConfiguration'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('configuration', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('ereports', ['ProcessQueue'])

        # Adding field 'ReportConfiguration.customize_columns'
        db.add_column('ereports_reportconfiguration', 'customize_columns',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'ReportConfiguration.select_related'
        db.delete_column('ereports_reportconfiguration', 'select_related')

        # Deleting field 'ReportConfiguration.use_distinct'
        db.delete_column('ereports_reportconfiguration', 'use_distinct')

        # Deleting field 'ReportConfiguration.ttl'
        db.delete_column('ereports_reportconfiguration', 'ttl')

        # Deleting field 'ReportConfiguration.cache_key'
        db.delete_column('ereports_reportconfiguration', 'cache_key')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ereports.reportconfiguration': {
            'Meta': {'object_name': 'ReportConfiguration'},
            'cache_key': ('django.db.models.fields.CharField', [], {'default': "'XG10FBE9BS42LAHGZXTCMXK8LWC5YAL6WAQPUX3GU5TNY41NE76S8785XY27F9INW6GDD3GEZ0XBYX70HW9W9FNLFKEDDVV1IYU8'", 'unique': 'True', 'max_length': '200'}),
            'columns': ('django.db.models.fields.TextField', [], {'default': "'id\\n'"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filtering': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportGroup']"}),
            'groupby': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'ordering': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'select_related': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target_model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportTemplate']", 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'use_distinct': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ereports.reportgroup': {
            'Meta': {'object_name': 'ReportGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportGroup']", 'null': 'True', 'blank': 'True'})
        },
        'ereports.reporttemplate': {
            'Meta': {'object_name': 'ReportTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['ereports']