# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReportGroup'
        db.create_table('ereports_reportgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportGroup'], null=True, blank=True)),
        ))
        db.send_create_signal('ereports', ['ReportGroup'])

        # Adding model 'ReportTemplate'
        db.create_table('ereports_reporttemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('system', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ereports', ['ReportTemplate'])

        # Adding model 'ReportConfiguration'
        db.create_table('ereports_reportconfiguration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportGroup'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportTemplate'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('report_class', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('target_model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('columns', self.gf('django.db.models.fields.TextField')(default='id\n')),
            ('filtering', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('groupby', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('ereports', ['ReportConfiguration'])

        # Adding model 'ProcessQueue'
        db.create_table('ereports_processqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ereports.ReportConfiguration'])),
            ('configuration', self.gf('django.db.models.fields.TextField')()),
            ('executed', self.gf('django.db.models.fields.DateField')(default=None, null=True)),
        ))
        db.send_create_signal('ereports', ['ProcessQueue'])


    def backwards(self, orm):
        # Deleting model 'ReportGroup'
        db.delete_table('ereports_reportgroup')

        # Deleting model 'ReportTemplate'
        db.delete_table('ereports_reporttemplate')

        # Deleting model 'ReportConfiguration'
        db.delete_table('ereports_reportconfiguration')

        # Deleting model 'ProcessQueue'
        db.delete_table('ereports_processqueue')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filtering': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ereports.ReportGroup']"}),
            'groupby': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'ordering': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'report_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'target_model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
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