# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ReportConfiguration.target_model'
        db.delete_column('ereports_reportconfiguration', 'target_model_id')


    def backwards(self, orm):
        # Adding field 'ReportConfiguration.target_model'
        db.add_column('ereports_reportconfiguration', 'target_model',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True),
                      keep_default=False)


    models = {
        'ereports.processqueue': {
            'Meta': {'object_name': 'ProcessQueue'},
            'configuration': ('django.db.models.fields.TextField', [], {}),
            'executed': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportConfiguration']"})
        },
        'ereports.reportconfiguration': {
            'Meta': {'object_name': 'ReportConfiguration'},
            'columns': ('django.db.models.fields.TextField', [], {'default': "'id\\n'"}),
            'customize_columns': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filtering': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportGroup']"}),
            'groupby': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'ordering': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportTemplate']", 'null': 'True', 'blank': 'True'})
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