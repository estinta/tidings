# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'News', fields ['source', 'guid', 'ticker']
        db.delete_unique('scanner_news', ['source', 'guid', 'ticker'])

        # Deleting field 'News.ticker'
        db.delete_column('scanner_news', 'ticker')

        # Adding unique constraint on 'News', fields ['source', 'guid', 'stock']
        db.create_unique('scanner_news', ['source', 'guid', 'stock_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'News', fields ['source', 'guid', 'stock']
        db.delete_unique('scanner_news', ['source', 'guid', 'stock_id'])

        # Adding field 'News.ticker'
        db.add_column('scanner_news', 'ticker', self.gf('django.db.models.fields.CharField')(default='FAKE', max_length=15, db_index=True), keep_default=False)

        # Adding unique constraint on 'News', fields ['source', 'guid', 'ticker']
        db.create_unique('scanner_news', ['source', 'guid', 'ticker'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'scanner.news': {
            'Meta': {'unique_together': "(('source', 'stock', 'guid'),)", 'object_name': 'News'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '512'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'stock': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scanner.Stock']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'scanner.stock': {
            'Meta': {'object_name': 'Stock'},
            'briefing_last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'company_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '127', 'blank': 'True'}),
            'finviz_float': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'finviz_last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'google_last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'ibd_earnings_due_date': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'ibd_earnings_percentage_lastquarter': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'ibd_eps_rank': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'ibd_industry_group': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '127', 'blank': 'True'}),
            'ibd_industry_rank': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'ibd_last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'ibd_sales_percentage_lastquarter': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msn_last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'}),
            'ticker': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'yahoo_last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2000, 1, 1, 0, 0)'})
        },
        'scanner.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'briefing_password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'briefing_user': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'briefing_valid': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'ibd_password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'ibd_user': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'ibd_valid': ('django.db.models.fields.NullBooleanField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['scanner']
