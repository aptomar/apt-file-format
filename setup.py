from distutils.core import setup


setup(name = 'aptofile',
      version = '0.1',
      description = 'Aptomar file tools',
      author = 'Jarle Bauck Hamar',
      author_email = 'jarle.hamar@aptomar.com',
      packages = ['aptofile'],
      package_dir = {'aptofile':'src'},
      package_data = {'aptofile':['apt.schema.json']}
      )
