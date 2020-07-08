from django.db import migrations
from django.conf import settings
def load_data(apps, schema_editor):
    """
    添加用户为管理员
    """
    User = apps.get_model("account", "User")
    for name in settings.INIT_SUPERUSER:
        User.objects.update_or_create(
            username=name,
            defaults={'is_staff': True, 'is_active': True, 'is_superuser': True}
        )
class Migration(migrations.Migration):
    dependencies = [
        # 分别修改为django app名及最后一个migration文件名
      	# 例如：('home_application', '0001_initial')
        ('home_application', '0001_initial')
    ]
    operations = [
        migrations.RunPython(load_data)
    ]