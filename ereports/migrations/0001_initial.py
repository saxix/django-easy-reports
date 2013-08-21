# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReportGroup'
        db.create_table(u'ereports_reportgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportGroup'], null=True, blank=True)),
        ))
        db.send_create_signal('ereports', ['ReportGroup'])

        # Adding model 'ReportTemplate'
        db.create_table(u'ereports_reporttemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('system', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ereports', ['ReportTemplate'])

        # Adding model 'ReportConfiguration'
        db.create_table(u'ereports_reportconfiguration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportGroup'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportTemplate'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('report_class', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('target_model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('select_related', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('use_distinct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('columns', self.gf('django.db.models.fields.TextField')(default='id\n')),
            ('filtering', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('groupby', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ttl', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cache_key', self.gf('django.db.models.fields.CharField')(default='2EJJFA0ADGXV71I9HPWIB7CTW3I8RF7N231CY0TGMOUDRDBIRVN3PDT9MRAPYLE8XTJAA0M1MY65Z8NOAOAH64D9OEIICTGD2FW2', unique=True, max_length=200)),
        ))
        db.send_create_signal('ereports', ['ReportConfiguration'])


    def backwards(self, orm):
        # Deleting model 'ReportGroup'
        db.delete_table(u'ereports_reportgroup')

        # Deleting model 'ReportTemplate'
        db.delete_table(u'ereports_reporttemplate')

        # Deleting model 'ReportConfiguration'
        db.delete_table(u'ereports_reportconfiguration')


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
            'cache_key': ('django.db.models.fields.CharField', [], {'default': "'7MXAC9UFJH32B9A2IVK07IKNDY18Z2YNNM2DR9S9GPQFOGUI0Q21T1YIX9CWMKRO60WX9IGNDF1STL8EP95O5IB0I6LMAI2IF200'", 'unique': 'True', 'max_length': '200'}),
            'columns': ('django.db.models.fields.TextField', [], {'default': "'id\\n'"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
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
