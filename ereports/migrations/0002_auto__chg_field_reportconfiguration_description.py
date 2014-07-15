# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ReportConfiguration.description'
        db.alter_column(u'ereports_reportconfiguration', 'description', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True))

    def backwards(self, orm):

        # Changing field 'ReportConfiguration.description'
        db.alter_column(u'ereports_reportconfiguration', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ereports.reportconfiguration': {
            'Meta': {'object_name': 'ReportConfiguration'},
            'cache_key': ('django.db.models.fields.CharField', [], {'default': "'XKJO8Z83SF6UTT5TAHRPHEV1RYI8O2P3N9WSXDN213I6BEZX11KDKIXOJG37FCXG2ERMZ1DMR0Z456PQAOB04FQNMPCHVODXHR1H'", 'unique': 'True', 'max_length': '200'}),
            'columns': ('django.db.models.fields.TextField', [], {'default': "'id\\n'"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'filtering': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportGroup']"}),
            'groupby': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'ordering': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'select_related': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target_model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportTemplate']", 'null': 'True', 'blank': 'True'}),
            'ttl': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'use_distinct': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ereports.reportgroup': {
            'Meta': {'object_name': 'ReportGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportGroup']", 'null': 'True', 'blank': 'True'})
        },
        'ereports.reporttemplate': {
            'Meta': {'object_name': 'ReportTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['ereports']
